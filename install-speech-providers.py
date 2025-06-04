#!/usr/bin/env python3
"""
语音识别提供商 SDK 安装脚本
根据用户选择安装对应的 SDK
"""

import subprocess
import sys
import os

def install_package(package_name, description=""):
    """安装 Python 包"""
    try:
        print(f"📦 安装 {description or package_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"✅ {description or package_name} 安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description or package_name} 安装失败: {e}")
        return False

def install_basic_requirements():
    """安装基础依赖"""
    print("📋 安装基础依赖...")
    
    basic_packages = [
        ("pyaudio", "音频处理库"),
        ("pynput", "全局快捷键库"),
        ("requests", "HTTP 请求库"),
        ("python-dotenv", "环境变量管理"),
        ("keyboard", "键盘监听库"),
    ]
    
    success_count = 0
    for package, desc in basic_packages:
        if install_package(package, desc):
            success_count += 1
    
    print(f"📊 基础依赖安装完成: {success_count}/{len(basic_packages)}")
    return success_count == len(basic_packages)

def install_speech_providers():
    """安装语音识别提供商 SDK"""
    print("\n🎤 选择要安装的语音识别提供商 SDK:")
    print("1. 本地 Whisper (推荐，免费)")
    print("2. OpenAI API")
    print("3. 腾讯云语音识别")
    print("4. 阿里云语音识别")
    print("5. 百度云语音识别")
    print("6. 全部安装")
    print("0. 跳过")
    
    choice = input("\n请输入选择 (0-6) [默认: 1]: ").strip()
    
    providers = {
        '1': [("openai-whisper", "本地 Whisper")],
        '2': [("openai>=1.3.0", "OpenAI API")],
        '3': [("tencentcloud-sdk-python", "腾讯云 SDK")],
        '4': [("alibabacloud_nls_meta20190103", "阿里云语音识别 SDK")],
        '5': [("baidu-aip", "百度云 SDK")],
        '6': [
            ("openai-whisper", "本地 Whisper"),
            ("openai>=1.3.0", "OpenAI API"),
            ("tencentcloud-sdk-python", "腾讯云 SDK"),
            ("alibabacloud_nls_meta20190103", "阿里云语音识别 SDK"),
            ("baidu-aip", "百度云 SDK"),
        ]
    }
    
    if choice == '0':
        print("⏭️  跳过语音识别 SDK 安装")
        return True
    
    selected_providers = providers.get(choice, providers['1'])
    
    print(f"\n📦 安装选定的语音识别 SDK...")
    success_count = 0
    
    for package, desc in selected_providers:
        if install_package(package, desc):
            success_count += 1
    
    print(f"📊 语音识别 SDK 安装完成: {success_count}/{len(selected_providers)}")
    return success_count > 0

def check_system_requirements():
    """检查系统要求"""
    print("🔍 检查系统要求...")
    
    # 检查 Python 版本
    python_version = sys.version_info
    if python_version < (3, 8):
        print(f"❌ Python 版本过低: {python_version.major}.{python_version.minor}")
        print("   需要 Python 3.8 或更高版本")
        return False
    
    print(f"✅ Python 版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # 检查 pip
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "--version"], 
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✅ pip 可用")
    except subprocess.CalledProcessError:
        print("❌ pip 不可用")
        return False
    
    return True

def show_installation_guide():
    """显示安装后指南"""
    print("\n" + "=" * 50)
    print("🎉 安装完成！")
    print("\n📝 下一步:")
    print("1. 运行配置向导: python setup-config.py")
    print("2. 配置 API 密钥（如果使用云服务）")
    print("3. 测试系统: python test-system.py")
    print("4. 启动系统: ./start-all.sh")
    
    print("\n💡 提示:")
    print("- 如果使用本地 Whisper，首次运行会下载模型文件")
    print("- 云服务提供商需要配置相应的 API 密钥")
    print("- 确保麦克风权限已开启")
    
    print("\n🔗 获取 API 密钥:")
    print("- OpenAI: https://platform.openai.com/api-keys")
    print("- 腾讯云: https://console.cloud.tencent.com/cam/capi")
    print("- 阿里云: https://ram.console.aliyun.com/manage/ak")
    print("- 百度云: https://console.bce.baidu.com/iam/#/iam/accesslist")

def main():
    """主函数"""
    print("🚀 面试助手系统 - 语音识别提供商安装脚本")
    print("=" * 50)
    
    # 检查系统要求
    if not check_system_requirements():
        print("❌ 系统要求检查失败，请解决上述问题后重试")
        sys.exit(1)
    
    # 安装基础依赖
    if not install_basic_requirements():
        print("❌ 基础依赖安装失败，请检查网络连接和权限")
        sys.exit(1)
    
    # 安装语音识别提供商 SDK
    if not install_speech_providers():
        print("⚠️  语音识别 SDK 安装失败，但可以稍后手动安装")
    
    # 显示安装后指南
    show_installation_guide()

if __name__ == "__main__":
    main()
