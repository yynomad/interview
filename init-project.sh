#!/bin/bash

# 面试助手系统 - 项目初始化脚本
# 用于新开发者快速设置开发环境

set -e

echo "🚀 面试助手系统 - 项目初始化"
echo "================================"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印彩色消息
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

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        print_error "$1 未安装，请先安装 $1"
        return 1
    fi
    return 0
}

# 检查系统要求
check_requirements() {
    print_info "检查系统要求..."
    
    # 检查 Python
    if check_command python3; then
        python_version=$(python3 --version | cut -d' ' -f2)
        print_success "Python: $python_version"
    else
        print_error "请安装 Python 3.8 或更高版本"
        exit 1
    fi
    

    
    # 检查 Git
    if check_command git; then
        git_version=$(git --version | cut -d' ' -f3)
        print_success "Git: $git_version"
    else
        print_warning "Git 未安装，建议安装以便版本控制"
    fi
}

# 创建环境配置文件
setup_env_files() {
    print_info "设置环境配置文件..."
    
    # 后端环境配置
    if [ ! -f "backend/.env" ]; then
        if [ -f "backend/.env.development" ]; then
            cp backend/.env.development backend/.env
            print_success "已创建 backend/.env（基于开发环境模板）"
        elif [ -f "backend/.env.example" ]; then
            cp backend/.env.example backend/.env
            print_success "已创建 backend/.env（基于示例模板）"
        else
            print_warning "未找到后端环境配置模板"
        fi
    else
        print_info "backend/.env 已存在，跳过"
    fi
    
    # 电脑端工具环境配置
    if [ ! -f "desktop-tool/.env" ]; then
        if [ -f "desktop-tool/.env.development" ]; then
            cp desktop-tool/.env.development desktop-tool/.env
            print_success "已创建 desktop-tool/.env（基于开发环境模板）"
        elif [ -f "desktop-tool/.env.example" ]; then
            cp desktop-tool/.env.example desktop-tool/.env
            print_success "已创建 desktop-tool/.env（基于示例模板）"
        else
            print_warning "未找到电脑端工具环境配置模板"
        fi
    else
        print_info "desktop-tool/.env 已存在，跳过"
    fi
    

}

# 安装依赖
install_dependencies() {
    print_info "安装项目依赖..."
    
    # 询问是否安装依赖
    read -p "是否安装项目依赖？(y/n) [默认: y]: " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        # 询问是否安装 Python 依赖
        read -p "是否安装 Python 依赖？(y/n) [默认: y]: " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            # 建议创建虚拟环境
            print_info "建议创建 Python 虚拟环境"
            read -p "是否创建虚拟环境？(y/n) [默认: y]: " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Nn]$ ]]; then
                python3 -m venv venv
                print_success "虚拟环境已创建"
                print_info "激活虚拟环境: source venv/bin/activate"
            fi
            
            # 安装后端依赖
            if [ -f "backend/requirements.txt" ]; then
                print_info "安装后端依赖..."
                pip install -r backend/requirements.txt
                print_success "后端依赖安装完成"
            fi
            
            # 安装电脑端工具依赖
            if [ -f "desktop-tool/requirements.txt" ]; then
                print_info "安装电脑端工具依赖..."
                pip install -r desktop-tool/requirements.txt
                print_success "电脑端工具依赖安装完成"
            fi
        fi
    fi
}

# 设置 Git hooks（如果使用 Git）
setup_git_hooks() {
    if [ -d ".git" ]; then
        print_info "设置 Git hooks..."
        
        # 创建 pre-commit hook 检查敏感文件
        cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# 检查是否意外提交敏感文件

# 检查 .env 文件
if git diff --cached --name-only | grep -E "\.env$|\.env\.local$"; then
    echo "❌ 错误: 尝试提交 .env 文件"
    echo "请确保 .env 文件在 .gitignore 中"
    exit 1
fi

# 检查大文件
large_files=$(git diff --cached --name-only | xargs -I {} find {} -size +10M 2>/dev/null)
if [ ! -z "$large_files" ]; then
    echo "❌ 错误: 尝试提交大文件 (>10MB):"
    echo "$large_files"
    echo "请考虑使用 Git LFS 或将文件添加到 .gitignore"
    exit 1
fi

exit 0
EOF
        
        chmod +x .git/hooks/pre-commit
        print_success "Git pre-commit hook 已设置"
    fi
}

# 显示下一步指导
show_next_steps() {
    echo ""
    echo "🎉 项目初始化完成！"
    echo "===================="
    echo ""
    print_info "下一步操作："
    echo "1. 📝 配置 API 密钥："
    echo "   - 编辑 backend/.env 设置 GEMINI_API_KEY"
    echo "   - 编辑 desktop-tool/.env 设置语音识别 API 密钥"
    echo ""
    echo "2. 🎤 选择语音识别提供商："
    echo "   python install-speech-providers.py"
    echo ""
    echo "3. ⚙️  运行配置向导："
    echo "   python setup-config.py"
    echo ""
    echo "4. 🧪 测试系统："
    echo "   python test-system.py"
    echo ""
    echo "5. 🚀 启动系统："
    echo "   ./start-all.sh"
    echo ""
    print_info "文档和帮助："
    echo "- README.md - 详细使用说明"
    echo "- GITIGNORE_GUIDE.md - Git 忽略文件说明"
    echo ""
    print_warning "重要提醒："
    echo "- 不要提交 .env 文件到版本控制系统"
    echo "- 定期更新 API 密钥"
    echo "- 确保麦克风权限已开启"
}

# 主函数
main() {
    # 检查是否在项目根目录
    if [ ! -f "README.md" ] || [ ! -d "backend" ] || [ ! -d "desktop-tool" ]; then
        print_error "请在项目根目录运行此脚本"
        exit 1
    fi
    
    # 执行初始化步骤
    check_requirements
    setup_env_files
    install_dependencies
    setup_git_hooks
    show_next_steps
}

# 运行主函数
main "$@"
