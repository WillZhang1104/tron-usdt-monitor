#!/bin/bash

echo "🔧 修复导入问题..."

# 备份原文件
echo "📦 备份原文件..."
cp telegram_bot.py telegram_bot.py.backup 2>/dev/null || echo "⚠️ 无法备份telegram_bot.py"

# 检查并修复导入语句
echo "🔍 检查导入语句..."
if grep -q "from wallet_operations import WalletOperations" telegram_bot.py 2>/dev/null; then
    echo "❌ 发现错误的导入语句，正在修复..."
    sed -i 's/from wallet_operations import WalletOperations/from wallet_operations import TronWallet/g' telegram_bot.py
    echo "✅ 导入语句已修复"
else
    echo "✅ 导入语句正确"
fi

# 检查并修复类实例化
echo "🔍 检查类实例化..."
if grep -q "self.wallet_operations = WalletOperations()" telegram_bot.py 2>/dev/null; then
    echo "❌ 发现错误的类实例化，正在修复..."
    sed -i 's/self.wallet_operations = WalletOperations()/self.wallet_operations = TronWallet()/g' telegram_bot.py
    echo "✅ 类实例化已修复"
else
    echo "✅ 类实例化正确"
fi

# 测试修复结果
echo "🧪 测试修复结果..."
python3 -c "
try:
    from telegram_bot import TelegramBot
    print('✅ TelegramBot 导入成功')
    print('✅ 所有导入问题已修复')
except Exception as e:
    print(f'❌ 仍有问题: {e}')
" 2>/dev/null

echo "🔧 修复完成" 