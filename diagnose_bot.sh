#!/bin/bash

# Telegram机器人诊断脚本
# 使用方法: ./diagnose_bot.sh

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

echo "🔍 诊断Telegram机器人问题..."

# 检查当前目录
echo "📁 当前目录: $(pwd)"

# 检查文件是否存在
echo "📄 检查关键文件:"
ls -la *.py *.sh 2>/dev/null || echo "❌ 未找到Python文件"

# 检查telegram_bot.py的导入语句
echo "🔍 检查telegram_bot.py导入语句:"
if [ -f "telegram_bot.py" ]; then
    echo "第19行内容:"
    sed -n '19p' telegram_bot.py
    echo ""
    echo "导入语句检查:"
    grep -n "from wallet_operations import" telegram_bot.py
else
    echo "❌ telegram_bot.py 不存在"
fi

# 检查wallet_operations.py的类定义
echo "🔍 检查wallet_operations.py类定义:"
if [ -f "wallet_operations.py" ]; then
    echo "类定义检查:"
    grep -n "class.*:" wallet_operations.py
else
    echo "❌ wallet_operations.py 不存在"
fi

# 检查Python环境
echo "🐍 检查Python环境:"
python3 --version 2>/dev/null || echo "❌ Python3 未安装"

# 检查依赖
echo "📦 检查依赖:"
pip3 list | grep -E "(telegram|tronpy|python-dotenv)" 2>/dev/null || echo "❌ 缺少关键依赖"

# 测试导入
echo "🧪 测试Python导入:"
python3 -c "
try:
    from wallet_operations import TronWallet
    print('✅ TronWallet 导入成功')
except ImportError as e:
    print(f'❌ TronWallet 导入失败: {e}')
    print('尝试导入WalletOperations...')
    try:
        from wallet_operations import WalletOperations
        print('⚠️ 发现旧的WalletOperations类')
    except ImportError as e2:
        print(f'❌ WalletOperations 也不存在: {e2}')
" 2>/dev/null

echo "🔍 诊断完成"

# 检查.env文件
log_info "1. 检查配置文件..."
if [ -f ".env" ]; then
    log_info "✅ .env 文件存在"
    
    # 检查关键配置
    if grep -q "TELEGRAM_BOT_TOKEN" .env; then
        TOKEN=$(grep "TELEGRAM_BOT_TOKEN" .env | cut -d'=' -f2)
        if [ -n "$TOKEN" ] && [ "$TOKEN" != "your_telegram_bot_token_here" ]; then
            log_info "✅ TELEGRAM_BOT_TOKEN 已配置"
            log_debug "Token: ${TOKEN:0:10}...${TOKEN: -10}"
        else
            log_error "❌ TELEGRAM_BOT_TOKEN 未正确配置"
        fi
    else
        log_error "❌ 未找到 TELEGRAM_BOT_TOKEN 配置"
    fi
    
    if grep -q "ALLOWED_USERS" .env; then
        USERS=$(grep "ALLOWED_USERS" .env | cut -d'=' -f2)
        if [ -n "$USERS" ] && [ "$USERS" != "your_telegram_user_id" ]; then
            log_info "✅ ALLOWED_USERS 已配置"
            log_debug "用户: $USERS"
        else
            log_error "❌ ALLOWED_USERS 未正确配置"
        fi
    else
        log_error "❌ 未找到 ALLOWED_USERS 配置"
    fi
    
    if grep -q "MONITOR_ADDRESSES" .env; then
        ADDRESSES=$(grep "MONITOR_ADDRESSES" .env | cut -d'=' -f2)
        if [ -n "$ADDRESSES" ]; then
            log_info "✅ MONITOR_ADDRESSES 已配置"
            log_debug "地址: $ADDRESSES"
        else
            log_error "❌ MONITOR_ADDRESSES 为空"
        fi
    else
        log_error "❌ 未找到 MONITOR_ADDRESSES 配置"
    fi
else
    log_error "❌ .env 文件不存在"
fi

# 检查服务状态
log_info "2. 检查服务状态..."
if pgrep -f "python3.*main.py" > /dev/null; then
    PID=$(pgrep -f "python3.*main.py")
    log_info "✅ 服务正在运行，PID: $PID"
else
    log_error "❌ 服务未运行"
fi

# 检查日志文件
log_info "3. 检查日志文件..."
if [ -f "monitor.log" ]; then
    log_info "✅ 日志文件存在"
    
    # 显示最近的错误
    echo
    log_info "最近的错误日志:"
    grep -i error monitor.log | tail -5 || log_info "无错误日志"
    
    echo
    log_info "最近的启动日志:"
    tail -10 monitor.log
else
    log_error "❌ 日志文件不存在"
fi

# 测试网络连接
log_info "4. 测试网络连接..."
if command -v curl &> /dev/null; then
    if curl -s --connect-timeout 5 https://api.telegram.org > /dev/null; then
        log_info "✅ Telegram API 连接正常"
    else
        log_error "❌ 无法连接到 Telegram API"
    fi
else
    log_warn "⚠️  curl 未安装，跳过网络测试"
fi

# 测试机器人Token
log_info "5. 测试机器人Token..."
if [ -n "$TOKEN" ] && [ "$TOKEN" != "your_telegram_bot_token_here" ]; then
    if command -v curl &> /dev/null; then
        RESPONSE=$(curl -s "https://api.telegram.org/bot$TOKEN/getMe")
        if echo "$RESPONSE" | grep -q '"ok":true'; then
            BOT_NAME=$(echo "$RESPONSE" | grep -o '"username":"[^"]*"' | cut -d'"' -f4)
            log_info "✅ 机器人Token有效"
            log_info "机器人用户名: @$BOT_NAME"
        else
            log_error "❌ 机器人Token无效"
            log_debug "响应: $RESPONSE"
        fi
    else
        log_warn "⚠️  curl 未安装，跳过Token测试"
    fi
else
    log_warn "⚠️  Token未配置，跳过测试"
fi

# 检查Python依赖
log_info "6. 检查Python依赖..."
if command -v python3 &> /dev/null; then
    log_info "✅ Python3 已安装"
    
    # 检查关键模块
    if python3 -c "import telegram" 2>/dev/null; then
        log_info "✅ python-telegram-bot 已安装"
    else
        log_error "❌ python-telegram-bot 未安装"
    fi
    
    if python3 -c "import tronpy" 2>/dev/null; then
        log_info "✅ tronpy 已安装"
    else
        log_error "❌ tronpy 未安装"
    fi
    
    if python3 -c "import dotenv" 2>/dev/null; then
        log_info "✅ python-dotenv 已安装"
    else
        log_error "❌ python-dotenv 未安装"
    fi
else
    log_error "❌ Python3 未安装"
fi

# 提供解决方案
echo
echo "🔧 解决方案建议:"
echo "=================="

if ! pgrep -f "python3.*main.py" > /dev/null; then
    log_info "1. 启动服务:"
    echo "   ./manage.sh start"
fi

if ! grep -q "TELEGRAM_BOT_TOKEN" .env || grep -q "your_telegram_bot_token_here" .env; then
    log_info "2. 配置机器人Token:"
    echo "   nano .env"
    echo "   设置 TELEGRAM_BOT_TOKEN=你的真实Token"
fi

if ! grep -q "ALLOWED_USERS" .env || grep -q "your_telegram_user_id" .env; then
    log_info "3. 配置用户ID:"
    echo "   nano .env"
    echo "   设置 ALLOWED_USERS=你的Telegram用户ID"
fi

if ! grep -q "MONITOR_ADDRESSES" .env; then
    log_info "4. 配置监控地址:"
    echo "   nano .env"
    echo "   设置 MONITOR_ADDRESSES=地址1,地址2"
fi

log_info "5. 查看详细日志:"
echo "   ./manage.sh logs"

log_info "6. 重新启动服务:"
echo "   ./manage.sh restart"

echo
echo "📞 如果问题仍然存在，请提供以下信息:"
echo "   - 诊断脚本的完整输出"
echo "   - monitor.log 文件内容"
echo "   - .env 文件配置（隐藏敏感信息）" 