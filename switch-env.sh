#!/bin/bash

# 环境切换脚本
# 用法: ./switch-env.sh [development|production]

set -e

ENVIRONMENT=${1:-development}

if [ "$ENVIRONMENT" != "development" ] && [ "$ENVIRONMENT" != "production" ]; then
    echo "❌ 错误: 环境参数必须是 'development' 或 'production'"
    echo "用法: $0 [development|production]"
    exit 1
fi

echo "🔄 切换到 $ENVIRONMENT 环境..."

# 切换后端环境
echo "📁 配置后端环境..."
cd backend

if [ -f ".env.$ENVIRONMENT" ]; then
    cp ".env.$ENVIRONMENT" ".env"
    echo "✅ 后端环境配置已更新: .env.$ENVIRONMENT -> .env"
else
    echo "⚠️  警告: 后端环境配置文件 .env.$ENVIRONMENT 不存在"
fi

cd ..

# 切换电脑端工具环境
echo "📁 配置电脑端工具环境..."
cd desktop-tool

if [ -f ".env.$ENVIRONMENT" ]; then
    cp ".env.$ENVIRONMENT" ".env"
    echo "✅ 电脑端工具环境配置已更新: .env.$ENVIRONMENT -> .env"
else
    echo "⚠️  警告: 电脑端工具环境配置文件 .env.$ENVIRONMENT 不存在"
fi

cd ..

# 设置环境变量
export FLASK_ENV=$ENVIRONMENT
export ENVIRONMENT=$ENVIRONMENT

echo ""
echo "🎉 环境切换完成!"
echo "📋 当前环境: $ENVIRONMENT"
echo ""

if [ "$ENVIRONMENT" = "production" ]; then
    echo "⚠️  生产环境注意事项:"
    echo "   - 确保已设置正确的 API 密钥"
    echo "   - 确保已设置强密码的 SECRET_KEY"
    echo "   - 检查 CORS 域名配置"
    echo "   - 确保服务器地址配置正确"
else
    echo "🛠️  开发环境已就绪:"
    echo "   - DEBUG 模式已启用"
    echo "   - 详细日志已启用"
    echo "   - 音频文件保存已启用"
fi

echo ""
echo "🚀 现在可以启动服务:"
echo "   ./start-all.sh"
