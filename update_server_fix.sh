#!/bin/bash

echo "🚀 服务器更新和修复脚本"
echo "=========================="

# 设置变量
GITHUB_RAW_BASE="https://raw.githubusercontent.com/你的用户名/你的仓库名/main"
SERVER_DIR="/opt/usdt-monitor"

echo "📁 目标目录: $SERVER_DIR"

# 检查是否在服务器上
if [ ! -d "$SERVER_DIR" ]; then
    echo "❌ 未找到服务器目录，请确保在正确的服务器上运行"
    exit 1
fi

# 进入服务器目录
cd "$SERVER_DIR" || {
    echo "❌ 无法进入服务器目录"
    exit 1
}

echo "📦 备份当前文件..."
cp telegram_bot.py telegram_bot.py.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null || echo "⚠️ 无法备份telegram_bot.py"

echo "🔄 下载最新文件..."

# 下载核心文件
files=(
    "telegram_bot.py"
    "wallet_operations.py"
    "tron_monitor.py"
    "address_manager.py"
    "main.py"
    "requirements.txt"
    "manage.sh"
    "diagnose_bot.sh"
    "fix_import.sh"
)

for file in "${files[@]}"; do
    echo "📥 下载 $file..."
    if curl -s -o "$file" "$GITHUB_RAW_BASE/$file"; then
        echo "✅ $file 下载成功"
    else
        echo "❌ $file 下载失败"
    fi
done

echo "🔧 修复导入问题..."
chmod +x fix_import.sh
./fix_import.sh

echo "🔍 运行诊断..."
chmod +x diagnose_bot.sh
./diagnose_bot.sh

echo "🔄 重启服务..."
chmod +x manage.sh
./manage.sh restart

echo "📊 检查服务状态..."
./manage.sh status

echo "✅ 更新完成！"
echo ""
echo "💡 如果仍有问题，请运行:"
echo "   ./diagnose_bot.sh"
echo "   tail -f /var/log/usdt-monitor.log" 