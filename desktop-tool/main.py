import logging
import signal
import sys
import time
import requests
import json
from typing import Optional
import threading
from pynput import keyboard
import platform

from config import Config
from audio_recorder import AudioRecorder
from speech_client import SpeechRecognitionClient

# 配置日志
logging.basicConfig(
    level=logging.INFO if Config.DEBUG else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class InterviewAssistant:
    def __init__(self):
        """初始化面试助手"""
        self.is_running = False
        self.ai_mode_enabled = False  # 控制是否将文本传给 AI
        
        # 初始化组件
        self.speech_client = SpeechRecognitionClient()
        self.audio_recorder = AudioRecorder(self.on_audio_ready)
        
        # 快捷键监听器
        self.hotkey_listener: Optional[keyboard.GlobalHotKeys] = None
        
        # 设置信号处理
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def on_audio_ready(self, audio_file_path: str):
        """当音频文件准备好时的回调"""
        try:
            logger.info(f"处理音频文件：{audio_file_path}")
            
            # 转录音频
            text = self.speech_client.transcribe_audio(audio_file_path)
            
            if text:
                logger.info(f"转录结果：{text}")
                
                # 发送到后端服务器
                self.send_to_backend(text, self.ai_mode_enabled)
            else:
                logger.warning("转录结果为空")
                
        except Exception as e:
            logger.error(f"处理音频时出错：{str(e)}")
    
    def send_to_backend(self, question: str, generate_answer: bool = True):
        """发送问题到后端服务器"""
        try:
            url = f"{Config.BACKEND_URL}/api/question"
            data = {
                "question": question,
                "generate_answer": generate_answer
            }
            
            response = requests.post(
                url,
                json=data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if generate_answer:
                    logger.info("问题已发送并生成回答")
                else:
                    logger.info("问题已发送（未生成回答）")
            else:
                logger.error(f"发送失败，状态码：{response.status_code}")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"网络请求失败：{str(e)}")
        except Exception as e:
            logger.error(f"发送到后端时出错：{str(e)}")
    
    def toggle_ai_mode(self):
        """切换 AI 模式"""
        self.ai_mode_enabled = not self.ai_mode_enabled
        status = "启用" if self.ai_mode_enabled else "禁用"
        logger.info(f"AI 回答模式已{status}")
        print(f"\n🤖 AI 回答模式：{status}")
        print("按 Cmd+Shift+N (macOS) 或 Ctrl+Shift+N (Windows/Linux) 切换模式")
    
    def setup_hotkeys(self):
        """设置全局快捷键"""
        try:
            # 根据操作系统设置快捷键
            if platform.system() == "Darwin":  # macOS
                hotkey_combo = '<cmd>+<shift>+n'
            else:  # Windows/Linux
                hotkey_combo = '<ctrl>+<shift>+n'
            
            self.hotkey_listener = keyboard.GlobalHotKeys({
                hotkey_combo: self.toggle_ai_mode
            })
            
            self.hotkey_listener.start()
            logger.info(f"全局快捷键已设置：{hotkey_combo}")
            
        except Exception as e:
            logger.error(f"设置快捷键失败：{str(e)}")
            print("⚠️  快捷键设置失败，请手动控制 AI 模式")
    
    def test_backend_connection(self) -> bool:
        """测试后端连接"""
        try:
            url = f"{Config.BACKEND_URL}/health"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                logger.info("后端服务器连接成功")
                logger.info(f"Gemini 可用性：{data.get('gemini_available', False)}")
                return True
            else:
                logger.error(f"后端服务器响应异常：{response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"无法连接到后端服务器：{str(e)}")
            return False
    
    def start(self):
        """启动面试助手"""
        try:
            logger.info("启动面试助手...")
            
            # 测试后端连接
            if not self.test_backend_connection():
                print("❌ 无法连接到后端服务器，请确保后端服务正在运行")
                return
            
            # 测试语音识别
            if not self.speech_client.test_connection():
                print("❌ 语音识别服务连接测试失败")
                return

            # 显示语音识别提供商信息
            provider_info = self.speech_client.get_provider_info()
            print(f"🎤 语音识别提供商: {provider_info['provider']}")
            print(f"🌐 语言设置: {provider_info['language']}")
            if provider_info['model']:
                print(f"🤖 模型: {provider_info['model']}")
            
            # 设置快捷键
            self.setup_hotkeys()
            
            # 开始录音
            self.audio_recorder.start_recording()
            
            self.is_running = True
            
            print("\n🎤 面试助手已启动！")
            print("📝 正在监听麦克风...")
            print(f"🤖 AI 回答模式：{'启用' if self.ai_mode_enabled else '禁用'}")
            print("⌨️  按 Cmd+Shift+N (macOS) 或 Ctrl+Shift+N (Windows/Linux) 切换 AI 模式")
            print("🛑 按 Ctrl+C 退出")
            
            # 主循环
            while self.is_running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("收到中断信号")
        except Exception as e:
            logger.error(f"启动失败：{str(e)}")
        finally:
            self.stop()
    
    def stop(self):
        """停止面试助手"""
        logger.info("正在停止面试助手...")
        
        self.is_running = False
        
        # 停止录音
        if self.audio_recorder:
            self.audio_recorder.cleanup()
        
        # 停止快捷键监听
        if self.hotkey_listener:
            self.hotkey_listener.stop()
        
        print("\n👋 面试助手已停止")
    
    def signal_handler(self, signum, frame):
        """信号处理器"""
        logger.info(f"收到信号：{signum}")
        self.stop()
        sys.exit(0)

def main():
    """主函数"""
    try:
        assistant = InterviewAssistant()
        assistant.start()
    except Exception as e:
        logger.error(f"程序异常退出：{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
