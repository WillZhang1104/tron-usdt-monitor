#!/bin/bash

# 加密钱包设置脚本
# 用于安全地设置Tron钱包私钥的加密存储

set -e

echo "🔐 Tron钱包加密存储设置脚本"
echo "================================"

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo "❌ 请使用root用户运行此脚本"
    exit 1
fi

# 检查GPG是否安装
if ! command -v gpg &> /dev/null; then
    echo "📦 安装GPG..."
    apt update && apt install -y gnupg
fi

# 检查是否已有GPG密钥
if ! gpg --list-keys &> /dev/null; then
    echo "🔑 生成GPG密钥对..."
    echo "请按提示操作："
    echo "1. 选择 'RSA and RSA' (默认)"
    echo "2. 密钥长度选择 4096"
    echo "3. 密钥永不过期 (0)"
    echo "4. 输入你的邮箱地址"
    echo "5. 输入真实姓名"
    echo "6. 输入注释（可选）"
    echo "7. 确认信息"
    echo "8. 输入密码（重要！记住这个密码）"
    echo ""
    
    gpg --full-generate-key
else
    echo "✅ 检测到现有GPG密钥"
    gpg --list-keys
fi

# 获取用户邮箱
read -p "📧 请输入你的邮箱地址: " user_email

# 检查邮箱对应的密钥是否存在
if ! gpg --list-keys "$user_email" &> /dev/null; then
    echo "❌ 未找到邮箱 $user_email 对应的GPG密钥"
    echo "请检查邮箱地址或重新生成密钥"
    exit 1
fi

echo "✅ 找到GPG密钥: $user_email"

# 获取私钥
echo ""
echo "🔑 请输入你的Tron钱包私钥（十六进制格式）:"
echo "⚠️  注意：私钥将不会显示在屏幕上"
read -s -p "私钥: " tron_private_key

if [ -z "$tron_private_key" ]; then
    echo "❌ 私钥不能为空"
    exit 1
fi

# 创建临时私钥文件
echo "$tron_private_key" > /tmp/private_key.txt

# 加密私钥文件
echo "🔐 加密私钥文件..."
gpg --encrypt --recipient "$user_email" /tmp/private_key.txt

# 移动加密文件到项目目录
PROJECT_DIR="/opt/usdt-monitor"
if [ -d "$PROJECT_DIR" ]; then
    mv /tmp/private_key.txt.gpg "$PROJECT_DIR/"
    echo "✅ 加密文件已保存到: $PROJECT_DIR/private_key.txt.gpg"
else
    mv /tmp/private_key.txt.gpg ./
    echo "✅ 加密文件已保存到: ./private_key.txt.gpg"
fi

# 删除临时文件
rm -f /tmp/private_key.txt

# 设置文件权限
if [ -d "$PROJECT_DIR" ]; then
    chmod 600 "$PROJECT_DIR/private_key.txt.gpg"
    chown root:root "$PROJECT_DIR/private_key.txt.gpg"
else
    chmod 600 ./private_key.txt.gpg
fi

# 更新.env文件
echo ""
echo "📝 更新环境变量配置..."

if [ -d "$PROJECT_DIR" ] && [ -f "$PROJECT_DIR/.env" ]; then
    env_file="$PROJECT_DIR/.env"
elif [ -f ".env" ]; then
    env_file=".env"
else
    echo "❌ 未找到.env文件"
    exit 1
fi

# 注释掉原有的TRON_PRIVATE_KEY行
sed -i 's/^TRON_PRIVATE_KEY=/#TRON_PRIVATE_KEY=/' "$env_file"

# 添加新的配置
if ! grep -q "TRON_PRIVATE_KEY_FILE" "$env_file"; then
    echo "" >> "$env_file"
    echo "# 加密私钥文件路径" >> "$env_file"
    echo "TRON_PRIVATE_KEY_FILE=private_key.txt.gpg" >> "$env_file"
fi

echo "✅ 环境变量已更新"

# 测试解密
echo ""
echo "🧪 测试解密功能..."
if [ -d "$PROJECT_DIR" ]; then
    cd "$PROJECT_DIR"
fi

if gpg --decrypt private_key.txt.gpg > /dev/null 2>&1; then
    echo "✅ 解密测试成功"
else
    echo "❌ 解密测试失败"
    exit 1
fi

echo ""
echo "🎉 加密存储设置完成！"
echo ""
echo "📋 配置总结："
echo "- 私钥已加密存储在: private_key.txt.gpg"
echo "- 使用GPG密钥: $user_email"
echo "- 环境变量已更新"
echo "- 文件权限已设置"
echo ""
echo "⚠️  重要提醒："
echo "1. 记住你的GPG密码"
echo "2. 备份加密文件到安全位置"
echo "3. 定期更换私钥"
echo "4. 监控转账活动"
echo ""
echo "🚀 现在可以重启服务测试转账功能："
echo "sudo systemctl restart usdt-monitor" 