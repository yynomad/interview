#!/bin/bash

# 端口冲突修复脚本
# 专门处理面试助手系统的端口冲突问题

set -e

echo "🔧 面试助手系统 - 端口冲突修复"
echo "================================"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 检查端口是否被占用
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # 端口被占用
    else
        return 1  # 端口可用
    fi
}

# 获取占用端口的进程信息
get_port_process() {
    local port=$1
    lsof -Pi :$port -sTCP:LISTEN | tail -n +2
}

# 终止指定端口的进程
kill_port_process() {
    local port=$1
    local pids=$(lsof -ti :$port)
    
    if [ -n "$pids" ]; then
        echo "终止端口 $port 上的进程: $pids"
        kill -9 $pids 2>/dev/null || true
        sleep 2
        
        if check_port $port; then
            print_error "无法终止端口 $port 上的进程"
            return 1
        else
            print_success "端口 $port 已释放"
            return 0
        fi
    else
        print_info "端口 $port 没有进程占用"
        return 0
    fi
}

# 检查并修复端口冲突
fix_port_conflicts() {
    print_info "检查端口使用情况..."
    
    # 检查后端端口 5001
    if check_port 5001; then
        print_warning "端口 5001 被占用"
        echo "占用进程:"
        get_port_process 5001
        
        read -p "是否终止占用端口 5001 的进程？(y/n) [默认: n]: " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            kill_port_process 5001
        fi
    else
        print_success "端口 5001 可用"
    fi
    

    
    # 检查 macOS 控制中心占用的端口 5000
    if check_port 5000; then
        print_warning "端口 5000 被占用（通常是 macOS 控制中心）"
        echo "占用进程:"
        get_port_process 5000
        
        print_info "macOS 控制中心占用端口 5000 是正常现象"
        print_info "我们已将后端配置为使用端口 5001"
    fi
}

# 验证配置文件
verify_config_files() {
    print_info "验证配置文件..."
    
    # 检查后端配置
    if [ -f "backend/.env" ]; then
        backend_port=$(grep "^PORT=" backend/.env | cut -d'=' -f2)
        if [ "$backend_port" = "5001" ]; then
            print_success "后端配置正确: 端口 $backend_port"
        else
            print_warning "后端配置可能有问题: 端口 $backend_port"
        fi
    else
        print_warning "后端配置文件 backend/.env 不存在"
    fi
    
    # 检查电脑端工具配置
    if [ -f "desktop-tool/.env" ]; then
        backend_url=$(grep "^BACKEND_URL=" desktop-tool/.env | cut -d'=' -f2)
        if [[ "$backend_url" == *":5001"* ]]; then
            print_success "电脑端工具配置正确: $backend_url"
        else
            print_warning "电脑端工具配置可能有问题: $backend_url"
        fi
    else
        print_warning "电脑端工具配置文件 desktop-tool/.env 不存在"
    fi
}

# 提供解决方案
provide_solutions() {
    echo ""
    print_info "解决方案:"
    echo "1. 🔄 使用不同端口:"
    echo "   export PORT=5001 && python backend/app.py"
    echo ""
    echo "2. 🛑 终止冲突进程:"
    echo "   sudo lsof -ti :5001 | xargs kill -9"
    echo ""
    echo "3. ⚙️  修改配置文件:"
    echo "   编辑 backend/.env 设置 PORT=5001"
    echo "   编辑 desktop-tool/.env 设置 BACKEND_URL=http://localhost:5001"
    echo ""
    echo "4. 🔍 查找可用端口:"
    echo "   for port in {5001..5010}; do ! nc -z localhost \$port && echo \$port; done"
    echo ""
    print_warning "注意: 不要终止 macOS 控制中心进程（端口 5000）"
}

# 自动修复配置
auto_fix_config() {
    print_info "自动修复配置文件..."
    
    # 确保后端使用端口 5001
    if [ -f "backend/.env" ]; then
        sed -i '' 's/^PORT=5000/PORT=5001/' backend/.env 2>/dev/null || true
        print_success "已更新 backend/.env 使用端口 5001"
    fi
    
    # 确保电脑端工具连接到端口 5001
    if [ -f "desktop-tool/.env" ]; then
        sed -i '' 's|BACKEND_URL=http://localhost:5000|BACKEND_URL=http://localhost:5001|' desktop-tool/.env 2>/dev/null || true
        print_success "已更新 desktop-tool/.env 连接到端口 5001"
    fi
    

}

# 测试端口连接
test_ports() {
    print_info "测试端口连接..."
    
    # 测试后端端口
    if nc -z localhost 5001 2>/dev/null; then
        print_success "后端端口 5001 可连接"
    else
        print_warning "后端端口 5001 无法连接（服务可能未启动）"
    fi
    

}

# 主函数
main() {
    # 检查是否在项目根目录
    if [ ! -f "README.md" ] || [ ! -d "backend" ]; then
        print_error "请在项目根目录运行此脚本"
        exit 1
    fi
    
    # 检查是否有必要的命令
    if ! command -v lsof &> /dev/null; then
        print_error "lsof 命令不可用，无法检查端口占用"
        exit 1
    fi
    
    # 执行修复步骤
    fix_port_conflicts
    echo ""
    verify_config_files
    echo ""
    
    # 询问是否自动修复配置
    read -p "是否自动修复配置文件？(y/n) [默认: y]: " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        auto_fix_config
        echo ""
    fi
    
    test_ports
    echo ""
    provide_solutions
    
    print_success "端口冲突检查完成！"
    print_info "现在可以运行: ./start-all.sh"
}

# 运行主函数
main "$@"
