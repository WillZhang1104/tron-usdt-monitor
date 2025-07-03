#!/bin/bash

# Tron监控项目 - 从GitHub重新下载脚本
# 使用方法: ./reset_from_github.sh

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_debug() {
    echo -e "${BLUE}[DEBUG]${NC} $1"
}

# GitHub仓库信息
GITHUB_REPO="https://raw.githubusercontent.com/WillZhang1104/tron-usdt-monitor/master"

# 需要下载的文件列表
FILES=(
    "main.py"
    "telegram_bot.py"
    "tron_monitor.py"
    "wallet_operations.py"
    "address_manager.py"
    "requirements.txt"
    "manage.sh"
    "setup_chinese.sh"
    "setup_encrypted_wallet.sh"
    "deploy_ubuntu.sh"
    "README.md"
    "QUICK_FIX_GUIDE.md"
    "WALLET_SECURITY_GUIDE.md"
    "ubuntu_deploy_guide.md"
    "create_bot_guide.md"
    "config.env.example"
)

# 需要执行权限的脚本文件
EXECUTABLE_SCRIPTS=(
    "manage.sh"
    "setup_chinese.sh"
    "setup_encrypted_wallet.sh"
    "deploy_ubuntu.sh"
)

echo "🚀 Tron监控项目 - 从GitHub重新下载"
echo "=================================="

# 检查当前目录
if [ ! -f ".env" ]; then
    log_warn "当前目录下没有找到 .env 文件"
    log_info "请确保在正确的项目目录中运行此脚本"
    read -p "是否继续？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "操作已取消"
        exit 1
    fi
fi

# 备份 .env 文件
if [ -f ".env" ]; then
    cp .env .env.backup
    log_info "✅ .env 文件已备份到 .env.backup"
else
    log_warn "⚠️  未找到 .env 文件，将使用 config.env.example"
fi

# 停止现有服务
log_info "停止现有服务..."
pkill -f main.py 2>/dev/null || true
sleep 2

# 清理旧文件
log_info "清理旧文件..."
rm -f *.py *.sh *.md *.txt *.log *.pid 2>/dev/null || true
rm -rf __pycache__ 2>/dev/null || true
log_info "✅ 旧文件已清理"

# 检查下载工具
if command -v wget &> /dev/null; then
    DOWNLOAD_CMD="wget -O"
    log_info "使用 wget 下载文件"
elif command -v curl &> /dev/null; then
    DOWNLOAD_CMD="curl -o"
    log_info "使用 curl 下载文件"
else
    log_error "❌ 未找到 wget 或 curl，无法下载文件"
    exit 1
fi

# 下载文件
log_info "开始下载文件..."
success_count=0
total_count=${#FILES[@]}

for file in "${FILES[@]}"; do
    log_info "下载: $file"
    if $DOWNLOAD_CMD "$file" "$GITHUB_REPO/$file"; then
        log_info "✅ $file 下载成功"
        ((success_count++))
    else
        log_error "❌ $file 下载失败"
    fi
done

echo
log_info "下载完成: $success_count/$total_count 个文件"

# 给脚本文件执行权限
log_info "设置脚本执行权限..."
for script in "${EXECUTABLE_SCRIPTS[@]}"; do
    if [ -f "$script" ]; then
        chmod +x "$script"
        log_info "✅ $script 已设置执行权限"
    fi
done

# 验证关键文件
log_info "验证关键文件..."
if [ -f "main.py" ] && grep -q "TronUSDTMonitor" main.py; then
    log_info "✅ main.py 验证通过"
else
    log_error "❌ main.py 验证失败"
fi

if [ -f "telegram_bot.py" ] && grep -q "TronUSDTMonitor" telegram_bot.py; then
    log_info "✅ telegram_bot.py 验证通过"
else
    log_error "❌ telegram_bot.py 验证失败"
fi

if [ -f "manage.sh" ]; then
    log_info "✅ manage.sh 验证通过"
else
    log_error "❌ manage.sh 验证失败"
fi

# 恢复 .env 文件
if [ -f ".env.backup" ]; then
    cp .env.backup .env
    log_info "✅ .env 文件已恢复"
else
    log_warn "⚠️  未找到 .env.backup，请手动配置 .env 文件"
    if [ -f "config.env.example" ]; then
        cp config.env.example .env
        log_info "✅ 已复制 config.env.example 为 .env"
    fi
fi

# 安装依赖
log_info "检查Python依赖..."
if [ -f "requirements.txt" ]; then
    log_info "安装Python依赖..."
    pip3 install -r requirements.txt
    log_info "✅ 依赖安装完成"
fi

# 启动服务
echo
log_info "🚀 启动服务..."
if [ -f "manage.sh" ]; then
    ./manage.sh start
    echo
    log_info "📊 服务状态:"
    ./manage.sh status
else
    log_error "❌ manage.sh 不存在，无法启动服务"
fi

echo
echo "🎉 重新下载完成！"
echo "=================================="
echo "📋 可用命令:"
echo "  ./manage.sh start    # 启动服务"
echo "  ./manage.sh stop     # 停止服务"
echo "  ./manage.sh restart  # 重启服务"
echo "  ./manage.sh status   # 查看状态"
echo "  ./manage.sh logs     # 查看日志"
echo "  ./manage.sh update   # 更新服务"
echo
echo "📝 配置文件:"
echo "  .env                 # 环境变量配置"
echo "  .env.backup          # 备份的配置文件"
echo
echo "📚 文档文件:"
echo "  README.md            # 使用说明"
echo "  QUICK_FIX_GUIDE.md   # 快速修复指南"
echo "  WALLET_SECURITY_GUIDE.md # 钱包安全指南" 