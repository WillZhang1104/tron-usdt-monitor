#!/bin/bash

# 快速设置中文支持脚本

echo "🇨🇳 设置中文支持..."
echo "=================="

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo "❌ 请使用root用户运行此脚本"
    exit 1
fi

# 安装中文语言包
echo "📦 安装中文语言包..."
apt update
apt install -y language-pack-zh-hans language-pack-zh-hans-base

# 安装中文字体
echo "📝 安装中文字体..."
apt install -y fonts-wqy-microhei fonts-wqy-zenhei

# 生成中文locale
echo "🔧 生成中文locale..."
locale-gen zh_CN.UTF-8

# 设置系统语言为中文
echo "⚙️ 设置系统语言..."
update-locale LANG=zh_CN.UTF-8 LC_ALL=zh_CN.UTF-8

# 设置当前会话的语言环境
export LANG=zh_CN.UTF-8
export LC_ALL=zh_CN.UTF-8

# 创建SSH环境配置文件
echo "📋 配置SSH环境..."
cat > /etc/environment << 'EOF'
LANG=zh_CN.UTF-8
LC_ALL=zh_CN.UTF-8
LC_CTYPE=zh_CN.UTF-8
EOF

# 配置SSH服务
if grep -q "AcceptEnv LANG LC_\*" /etc/ssh/sshd_config; then
    echo "✅ SSH环境变量配置已存在"
else
    echo "AcceptEnv LANG LC_*" >> /etc/ssh/sshd_config
    echo "✅ SSH环境变量配置已添加"
fi

# 重启SSH服务
systemctl restart sshd

echo ""
echo "🎉 中文支持设置完成！"
echo "===================="
echo ""
echo "📋 设置内容："
echo "✅ 已安装中文语言包"
echo "✅ 已安装中文字体"
echo "✅ 已生成中文locale"
echo "✅ 已设置系统语言为中文"
echo "✅ 已配置SSH环境变量"
echo ""
echo "🔄 请重新SSH连接以应用中文设置"
echo "📝 测试中文显示："
echo "你好世界！"
echo ""
echo "🔧 如果中文显示不正常，请运行："
echo "export LANG=zh_CN.UTF-8"
echo "export LC_ALL=zh_CN.UTF-8" 