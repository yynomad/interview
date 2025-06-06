import os
from dotenv import load_dotenv

# 根据环境变量加载对应的配置文件
env = os.getenv('FLASK_ENV', 'development')
if env == 'production':
    load_dotenv('.env.production')
elif env == 'development':
    load_dotenv('.env.development')
else:
    load_dotenv()  # 默认加载 .env

class Config:
    # Gemini API 配置
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    
    # Flask 配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # 服务器配置
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5001))
    
    # CORS 配置
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    
    # Gemini 模型配置
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-pro')
    
    # 环境配置
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')

    # 日志配置
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    # 对话历史配置
    SAVE_CONVERSATION_HISTORY = os.getenv('SAVE_CONVERSATION_HISTORY', 'True').lower() == 'true'
    MAX_CONVERSATION_HISTORY = int(os.getenv('MAX_CONVERSATION_HISTORY', 100))

    # 安全配置
    RATE_LIMIT_ENABLED = os.getenv('RATE_LIMIT_ENABLED', 'False').lower() == 'true'
    MAX_REQUESTS_PER_MINUTE = int(os.getenv('MAX_REQUESTS_PER_MINUTE', 60))

    # 面试助手的系统提示词
    SYSTEM_PROMPT = """你是一个专业的面试助手。你的任务是帮助用户回答面试问题。

请遵循以下原则：
1. 提供简洁、专业的回答
2. 突出关键技能和经验
3. 使用具体的例子说明
4. 保持自信但不夸大
5. 回答要有逻辑性和条理性

请根据面试官的问题，给出一个合适的回答建议。"""

    @classmethod
    def is_development(cls):
        """检查是否为开发环境"""
        return cls.FLASK_ENV == 'development'

    @classmethod
    def is_production(cls):
        """检查是否为生产环境"""
        return cls.FLASK_ENV == 'production'
