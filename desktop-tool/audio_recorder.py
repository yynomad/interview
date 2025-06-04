import pyaudio
import wave
import threading
import time
import numpy as np
from typing import Callable, Optional
import logging
from config import Config

logger = logging.getLogger(__name__)

class AudioRecorder:
    def __init__(self, on_audio_ready: Callable[[str], None]):
        """
        音频录制器
        
        Args:
            on_audio_ready: 当音频文件准备好时的回调函数，参数为音频文件路径
        """
        self.on_audio_ready = on_audio_ready
        self.is_recording = False
        self.audio_thread: Optional[threading.Thread] = None
        
        # 音频配置
        self.sample_rate = Config.SAMPLE_RATE
        self.chunk_size = Config.CHUNK_SIZE
        self.channels = Config.CHANNELS
        self.format = pyaudio.paInt16
        
        # 静音检测配置
        self.silence_threshold = Config.SILENCE_THRESHOLD
        self.silence_duration = Config.SILENCE_DURATION
        self.min_recording_duration = Config.MIN_RECORDING_DURATION
        
        # 初始化 PyAudio
        self.audio = pyaudio.PyAudio()
        
        # 检查麦克风
        self._check_microphone()
    
    def _check_microphone(self):
        """检查麦克风是否可用"""
        try:
            # 获取默认输入设备信息
            default_device = self.audio.get_default_input_device_info()
            logger.info(f"默认麦克风设备：{default_device['name']}")
            
            # 测试录音
            stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            # 读取一小段音频测试
            data = stream.read(self.chunk_size)
            stream.stop_stream()
            stream.close()
            
            logger.info("麦克风测试成功")
            
        except Exception as e:
            logger.error(f"麦克风检查失败：{str(e)}")
            raise RuntimeError(f"无法访问麦克风：{str(e)}")
    
    def start_recording(self):
        """开始录音"""
        if self.is_recording:
            logger.warning("录音已在进行中")
            return
        
        self.is_recording = True
        self.audio_thread = threading.Thread(target=self._record_audio)
        self.audio_thread.daemon = True
        self.audio_thread.start()
        logger.info("开始录音")
    
    def stop_recording(self):
        """停止录音"""
        if not self.is_recording:
            return
        
        self.is_recording = False
        if self.audio_thread:
            self.audio_thread.join(timeout=5.0)
        logger.info("停止录音")
    
    def _record_audio(self):
        """录音主循环"""
        stream = None
        try:
            stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            frames = []
            silence_start = None
            recording_start = time.time()
            
            logger.info("录音流已启动，等待语音...")
            
            while self.is_recording:
                try:
                    data = stream.read(self.chunk_size, exception_on_overflow=False)
                    frames.append(data)
                    
                    # 计算音频强度
                    audio_data = np.frombuffer(data, dtype=np.int16)
                    volume = np.sqrt(np.mean(audio_data**2))
                    normalized_volume = volume / 32768.0  # 归一化到 0-1
                    
                    # 静音检测
                    if normalized_volume < self.silence_threshold:
                        if silence_start is None:
                            silence_start = time.time()
                        elif time.time() - silence_start > self.silence_duration:
                            # 检测到足够长的静音，结束当前录音
                            recording_duration = time.time() - recording_start
                            if recording_duration >= self.min_recording_duration and len(frames) > 0:
                                self._save_and_process_audio(frames)
                            
                            # 重置状态，准备下一段录音
                            frames = []
                            silence_start = None
                            recording_start = time.time()
                    else:
                        silence_start = None
                    
                except Exception as e:
                    logger.error(f"录音过程中出错：{str(e)}")
                    break
            
            # 处理最后一段音频
            if len(frames) > 0:
                recording_duration = time.time() - recording_start
                if recording_duration >= self.min_recording_duration:
                    self._save_and_process_audio(frames)
        
        except Exception as e:
            logger.error(f"录音失败：{str(e)}")
        
        finally:
            if stream:
                stream.stop_stream()
                stream.close()
    
    def _save_and_process_audio(self, frames):
        """保存音频文件并触发处理"""
        try:
            # 生成临时文件名
            timestamp = int(time.time() * 1000)
            audio_file = f"temp_audio_{timestamp}.wav"
            
            # 保存音频文件
            with wave.open(audio_file, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.audio.get_sample_size(self.format))
                wf.setframerate(self.sample_rate)
                wf.writeframes(b''.join(frames))
            
            logger.info(f"音频文件已保存：{audio_file}")
            
            # 触发回调
            self.on_audio_ready(audio_file)
            
        except Exception as e:
            logger.error(f"保存音频文件失败：{str(e)}")
    
    def cleanup(self):
        """清理资源"""
        self.stop_recording()
        if self.audio:
            self.audio.terminate()
        logger.info("音频录制器已清理")
