#!/bin/bash

# 面试助手系统启动脚本

echo "🚀 启动面试助手系统..."

# 检查是否安装了必要的依赖
check_dependencies() {
    echo "📋 检查依赖..."
    
    # 检查 Python
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python3 未安装"
        exit 1
    fi
    
    # 检查 Node.js
    if ! command -v node &> /dev/null; then
        echo "❌ Node.js 未安装"
        exit 1
    fi
    
    # 检查 npm
    if ! command -v npm &> /dev/null; then
        echo "❌ npm 未安装"
        exit 1
    fi
    
    echo "✅ 依赖检查完成"
}

# 安装依赖
install_dependencies() {
    echo "📦 安装依赖..."
    
    # 安装后端依赖
    echo "安装后端依赖..."
    cd backend
    if [ ! -f ".env" ]; then
        echo "⚠️  请先配置 backend/.env 文件（参考 .env.example）"
        exit 1
    fi
    pip install -r requirements.txt
    cd ..
    
    # 安装前端依赖
    echo "安装前端依赖..."
    cd frontend
    npm install
    cd ..
    
    # 安装电脑端工具依赖
    echo "安装电脑端工具依赖..."
    cd desktop-tool
    if [ ! -f ".env" ]; then
        echo "⚠️  请先配置 desktop-tool/.env 文件（参考 .env.example）"
        exit 1
    fi
    pip install -r requirements.txt
    cd ..
    
    echo "✅ 依赖安装完成"
}

# 启动服务
start_services() {
    echo "🔧 启动服务..."
    
    # 启动后端服务器
    echo "启动后端服务器..."
    cd backend
    python app.py &
    BACKEND_PID=$!
    cd ..
    
    # 等待后端启动
    sleep 3
    
    # 启动前端
    echo "启动前端..."
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    
    # 等待前端启动
    sleep 5
    
    echo "✅ 服务启动完成"
    echo ""
    echo "📱 前端地址: http://localhost:3000"
    echo "🔧 后端地址: http://localhost:5001"
    echo ""
    echo "🎤 现在可以运行电脑端工具："
    echo "   cd desktop-tool && python main.py"
    echo ""
    echo "🛑 按 Ctrl+C 停止所有服务"
    
    # 等待用户中断
    trap "echo ''; echo '🛑 正在停止服务...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT
    wait
}

# 主函数
main() {
    check_dependencies
    
    # 询问是否安装依赖
    read -p "是否需要安装/更新依赖？(y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        install_dependencies
    fi
    
    start_services
}

# 运行主函数
main
