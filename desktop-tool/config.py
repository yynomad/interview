import os
from dotenv import load_dotenv

# 根据环境变量加载对应的配置文件
env = os.getenv('ENVIRONMENT', 'development')
if env == 'production':
    load_dotenv('.env.production')
elif env == 'development':
    load_dotenv('.env.development')
else:
    load_dotenv()  # 默认加载 .env

class Config:
    # 后端服务器配置
    BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:5001')
    
    # 音频配置
    SAMPLE_RATE = int(os.getenv('SAMPLE_RATE', 16000))
    CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', 1024))
    CHANNELS = int(os.getenv('CHANNELS', 1))
    
    # 语音识别配置
    SPEECH_PROVIDER = os.getenv('SPEECH_PROVIDER', 'local_whisper')  # local_whisper, openai, tencent, aliyun, baidu

    # 本地 Whisper 配置
    WHISPER_MODEL = os.getenv('WHISPER_MODEL', 'base')  # tiny, base, small, medium, large

    # OpenAI Whisper API 配置
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')

    # 腾讯云语音识别配置
    TENCENT_SECRET_ID = os.getenv('TENCENT_SECRET_ID', '')
    TENCENT_SECRET_KEY = os.getenv('TENCENT_SECRET_KEY', '')
    TENCENT_REGION = os.getenv('TENCENT_REGION', 'ap-beijing')

    # 阿里云语音识别配置
    ALIYUN_ACCESS_KEY_ID = os.getenv('ALIYUN_ACCESS_KEY_ID', '')
    ALIYUN_ACCESS_KEY_SECRET = os.getenv('ALIYUN_ACCESS_KEY_SECRET', '')
    ALIYUN_APP_KEY = os.getenv('ALIYUN_APP_KEY', '')

    # 百度云语音识别配置
    BAIDU_API_KEY = os.getenv('BAIDU_API_KEY', '')
    BAIDU_SECRET_KEY = os.getenv('BAIDU_SECRET_KEY', '')

    # 语音识别通用配置
    SPEECH_LANGUAGE = os.getenv('SPEECH_LANGUAGE', 'zh-CN')  # zh-CN, en-US, etc.
    
    # 快捷键配置
    HOTKEY_COMBINATION = os.getenv('HOTKEY_COMBINATION', 'cmd+shift+n')  # macOS
    # HOTKEY_COMBINATION = os.getenv('HOTKEY_COMBINATION', 'ctrl+shift+n')  # Windows/Linux
    
    # 录音配置
    SILENCE_THRESHOLD = float(os.getenv('SILENCE_THRESHOLD', 0.01))  # 静音阈值
    SILENCE_DURATION = float(os.getenv('SILENCE_DURATION', 2.0))     # 静音持续时间（秒）
    MIN_RECORDING_DURATION = float(os.getenv('MIN_RECORDING_DURATION', 1.0))  # 最小录音时长
    
    # 环境配置
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

    # 调试配置
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    SAVE_AUDIO_FILES = os.getenv('SAVE_AUDIO_FILES', 'False').lower() == 'true'

    @classmethod
    def is_development(cls):
        """检查是否为开发环境"""
        return cls.ENVIRONMENT == 'development'

    @classmethod
    def is_production(cls):
        """检查是否为生产环境"""
        return cls.ENVIRONMENT == 'production'
