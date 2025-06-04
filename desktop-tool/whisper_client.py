import whisper
import openai
import os
import logging
from typing import Optional
from config import Config

logger = logging.getLogger(__name__)

class WhisperClient:
    def __init__(self):
        """初始化 Whisper 客户端"""
        self.use_openai_api = Config.USE_OPENAI_API
        
        if self.use_openai_api:
            # 使用 OpenAI API
            if not Config.OPENAI_API_KEY:
                raise ValueError("使用 OpenAI API 需要设置 OPENAI_API_KEY")
            openai.api_key = Config.OPENAI_API_KEY
            logger.info("使用 OpenAI Whisper API")
        else:
            # 使用本地 Whisper 模型
            try:
                logger.info(f"加载本地 Whisper 模型：{Config.WHISPER_MODEL}")
                self.model = whisper.load_model(Config.WHISPER_MODEL)
                logger.info("本地 Whisper 模型加载成功")
            except Exception as e:
                logger.error(f"加载本地 Whisper 模型失败：{str(e)}")
                raise
    
    def transcribe_audio(self, audio_file_path: str) -> Optional[str]:
        """
        将音频文件转录为文本
        
        Args:
            audio_file_path: 音频文件路径
            
        Returns:
            转录的文本，如果失败返回 None
        """
        try:
            if not os.path.exists(audio_file_path):
                logger.error(f"音频文件不存在：{audio_file_path}")
                return None
            
            if self.use_openai_api:
                return self._transcribe_with_openai_api(audio_file_path)
            else:
                return self._transcribe_with_local_model(audio_file_path)
                
        except Exception as e:
            logger.error(f"音频转录失败：{str(e)}")
            return None
        finally:
            # 清理临时音频文件
            self._cleanup_audio_file(audio_file_path)
    
    def _transcribe_with_openai_api(self, audio_file_path: str) -> Optional[str]:
        """使用 OpenAI API 进行转录"""
        try:
            with open(audio_file_path, 'rb') as audio_file:
                response = openai.Audio.transcribe(
                    model="whisper-1",
                    file=audio_file,
                    language="zh"  # 指定中文，可以根据需要调整
                )
            
            text = response.get('text', '').strip()
            if text:
                logger.info(f"OpenAI API 转录成功：{text[:50]}...")
                return text
            else:
                logger.warning("OpenAI API 返回空文本")
                return None
                
        except Exception as e:
            logger.error(f"OpenAI API 转录失败：{str(e)}")
            return None
    
    def _transcribe_with_local_model(self, audio_file_path: str) -> Optional[str]:
        """使用本地模型进行转录"""
        try:
            # 使用 Whisper 转录
            result = self.model.transcribe(
                audio_file_path,
                language="zh",  # 指定中文，可以根据需要调整
                fp16=False  # 避免在某些设备上的兼容性问题
            )
            
            text = result.get('text', '').strip()
            if text:
                logger.info(f"本地模型转录成功：{text[:50]}...")
                return text
            else:
                logger.warning("本地模型返回空文本")
                return None
                
        except Exception as e:
            logger.error(f"本地模型转录失败：{str(e)}")
            return None
    
    def _cleanup_audio_file(self, audio_file_path: str):
        """清理临时音频文件"""
        try:
            if not Config.SAVE_AUDIO_FILES and os.path.exists(audio_file_path):
                os.remove(audio_file_path)
                logger.debug(f"已删除临时音频文件：{audio_file_path}")
        except Exception as e:
            logger.warning(f"删除临时音频文件失败：{str(e)}")
    
    def test_transcription(self) -> bool:
        """
        测试转录功能
        
        Returns:
            测试是否成功
        """
        try:
            # 创建一个简单的测试音频文件（静音）
            import wave
            import numpy as np
            
            test_file = "test_audio.wav"
            
            # 生成 1 秒的静音
            sample_rate = Config.SAMPLE_RATE
            duration = 1.0
            samples = int(sample_rate * duration)
            audio_data = np.zeros(samples, dtype=np.int16)
            
            # 保存测试音频
            with wave.open(test_file, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                wf.writeframes(audio_data.tobytes())
            
            # 尝试转录
            result = self.transcribe_audio(test_file)
            
            # 清理测试文件
            if os.path.exists(test_file):
                os.remove(test_file)
            
            logger.info("转录功能测试完成")
            return True
            
        except Exception as e:
            logger.error(f"转录功能测试失败：{str(e)}")
            return False
