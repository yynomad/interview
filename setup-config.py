#!/usr/bin/env python3
"""
面试助手系统配置脚本
自动生成安全的配置文件
"""

import os
import secrets
import shutil

def generate_secret_key():
    """生成安全的 SECRET_KEY"""
    return secrets.token_hex(32)

def setup_backend_config():
    """设置后端配置"""
    print("🔧 配置后端环境...")
    
    # 生成安全的 SECRET_KEY
    secret_key = generate_secret_key()
    
    # 获取用户输入
    gemini_api_key = input("请输入 Gemini API Key: ").strip()
    
    if not gemini_api_key:
        print("⚠️  警告: 未设置 Gemini API Key，请稍后手动配置")
        gemini_api_key = "your_gemini_api_key_here"
    
    # 读取开发环境模板
    dev_template = """# 开发环境配置
FLASK_ENV=development

# Gemini API 配置
GEMINI_API_KEY={gemini_api_key}

# Flask 配置
SECRET_KEY={secret_key}
DEBUG=True

# 服务器配置
HOST=0.0.0.0
PORT=5000

# CORS 配置 - 开发环境允许本地访问
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001

# Gemini 模型配置
GEMINI_MODEL=gemini-pro

# 日志配置 - 开发环境详细日志
LOG_LEVEL=DEBUG

# 开发环境特定配置
SAVE_CONVERSATION_HISTORY=True
MAX_CONVERSATION_HISTORY=100
""".format(gemini_api_key=gemini_api_key, secret_key=secret_key)
    
    # 写入开发环境配置
    with open('backend/.env.development', 'w', encoding='utf-8') as f:
        f.write(dev_template)
    
    # 复制为当前配置
    shutil.copy('backend/.env.development', 'backend/.env')
    
    print("✅ 后端配置完成")
    print(f"   - SECRET_KEY: {secret_key[:16]}...")
    print(f"   - GEMINI_API_KEY: {'已设置' if gemini_api_key != 'your_gemini_api_key_here' else '未设置'}")

def setup_desktop_config():
    """设置电脑端工具配置"""
    print("\n🎤 配置电脑端工具...")

    # 选择语音识别提供商
    print("\n请选择语音识别提供商:")
    print("1. 本地 Whisper (免费，需要本地计算资源)")
    print("2. OpenAI Whisper API (付费，高质量)")
    print("3. 腾讯云语音识别 (付费，中文优化)")
    print("4. 阿里云语音识别 (付费，中文优化)")
    print("5. 百度云语音识别 (付费，中文优化)")

    choice = input("请输入选择 (1-5) [默认: 1]: ").strip()

    provider_map = {
        '1': 'local_whisper',
        '2': 'openai',
        '3': 'tencent',
        '4': 'aliyun',
        '5': 'baidu'
    }

    speech_provider = provider_map.get(choice, 'local_whisper')

    # 根据选择的提供商配置相应的 API 密钥
    api_configs = {}

    if speech_provider == 'openai':
        api_key = input("请输入 OpenAI API Key: ").strip()
        api_configs['OPENAI_API_KEY'] = api_key if api_key else "your_openai_api_key_here"

    elif speech_provider == 'tencent':
        secret_id = input("请输入腾讯云 Secret ID: ").strip()
        secret_key = input("请输入腾讯云 Secret Key: ").strip()
        region = input("请输入腾讯云地域 [默认: ap-beijing]: ").strip()

        api_configs['TENCENT_SECRET_ID'] = secret_id if secret_id else "your_tencent_secret_id_here"
        api_configs['TENCENT_SECRET_KEY'] = secret_key if secret_key else "your_tencent_secret_key_here"
        api_configs['TENCENT_REGION'] = region if region else "ap-beijing"

    elif speech_provider == 'aliyun':
        access_key_id = input("请输入阿里云 Access Key ID: ").strip()
        access_key_secret = input("请输入阿里云 Access Key Secret: ").strip()
        app_key = input("请输入阿里云 App Key: ").strip()

        api_configs['ALIYUN_ACCESS_KEY_ID'] = access_key_id if access_key_id else "your_aliyun_access_key_id_here"
        api_configs['ALIYUN_ACCESS_KEY_SECRET'] = access_key_secret if access_key_secret else "your_aliyun_access_key_secret_here"
        api_configs['ALIYUN_APP_KEY'] = app_key if app_key else "your_aliyun_app_key_here"

    elif speech_provider == 'baidu':
        api_key = input("请输入百度云 API Key: ").strip()
        secret_key = input("请输入百度云 Secret Key: ").strip()

        api_configs['BAIDU_API_KEY'] = api_key if api_key else "your_baidu_api_key_here"
        api_configs['BAIDU_SECRET_KEY'] = secret_key if secret_key else "your_baidu_secret_key_here"
    
    # 生成配置模板
    dev_template = f"""# 开发环境配置
ENVIRONMENT=development

# 后端服务器配置
BACKEND_URL=http://localhost:5000

# 音频配置
SAMPLE_RATE=16000
CHUNK_SIZE=1024
CHANNELS=1

# 语音识别配置
SPEECH_PROVIDER={speech_provider}
SPEECH_LANGUAGE=zh-CN

# 本地 Whisper 配置
WHISPER_MODEL=base

# OpenAI Whisper API 配置
OPENAI_API_KEY={api_configs.get('OPENAI_API_KEY', 'your_openai_api_key_here')}

# 腾讯云语音识别配置
TENCENT_SECRET_ID={api_configs.get('TENCENT_SECRET_ID', 'your_tencent_secret_id_here')}
TENCENT_SECRET_KEY={api_configs.get('TENCENT_SECRET_KEY', 'your_tencent_secret_key_here')}
TENCENT_REGION={api_configs.get('TENCENT_REGION', 'ap-beijing')}

# 阿里云语音识别配置
ALIYUN_ACCESS_KEY_ID={api_configs.get('ALIYUN_ACCESS_KEY_ID', 'your_aliyun_access_key_id_here')}
ALIYUN_ACCESS_KEY_SECRET={api_configs.get('ALIYUN_ACCESS_KEY_SECRET', 'your_aliyun_access_key_secret_here')}
ALIYUN_APP_KEY={api_configs.get('ALIYUN_APP_KEY', 'your_aliyun_app_key_here')}

# 百度云语音识别配置
BAIDU_API_KEY={api_configs.get('BAIDU_API_KEY', 'your_baidu_api_key_here')}
BAIDU_SECRET_KEY={api_configs.get('BAIDU_SECRET_KEY', 'your_baidu_secret_key_here')}

# 快捷键配置（macOS）
HOTKEY_COMBINATION=cmd+shift+n
# 快捷键配置（Windows/Linux）
# HOTKEY_COMBINATION=ctrl+shift+n

# 录音配置 - 开发环境更敏感的设置
SILENCE_THRESHOLD=0.005
SILENCE_DURATION=1.5
MIN_RECORDING_DURATION=0.5

# 调试配置 - 开发环境保存音频文件用于调试
DEBUG=True
SAVE_AUDIO_FILES=True
"""
    
    # 写入开发环境配置
    with open('desktop-tool/.env.development', 'w', encoding='utf-8') as f:
        f.write(dev_template)
    
    # 复制为当前配置
    shutil.copy('desktop-tool/.env.development', 'desktop-tool/.env')
    
    print("✅ 电脑端工具配置完成")
    print(f"   - 语音识别提供商: {speech_provider}")
    print(f"   - 语言设置: zh-CN")
    print(f"   - 调试模式: 启用")

def main():
    """主函数"""
    print("🎤 面试助手系统配置向导")
    print("=" * 40)
    
    # 检查目录结构
    if not os.path.exists('backend') or not os.path.exists('desktop-tool'):
        print("❌ 错误: 请在项目根目录运行此脚本")
        return
    
    # 设置后端配置
    setup_backend_config()
    
    # 设置电脑端工具配置
    setup_desktop_config()
    
    print("\n" + "=" * 40)
    print("🎉 配置完成！")
    print("\n📝 下一步:")
    print("1. 如果未设置 API 密钥，请编辑相应的 .env 文件")
    print("2. 运行测试: python test-system.py")
    print("3. 启动系统: ./start-all.sh")
    print("\n💡 提示:")
    print("- 可以使用 ./switch-env.sh 切换环境")
    print("- 生产环境需要额外配置安全设置")

if __name__ == "__main__":
    main()
