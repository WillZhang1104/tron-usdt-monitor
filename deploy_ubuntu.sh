#!/bin/bash

# Ubuntu 20.04 USDT监控机器人简化部署脚本

set -e

echo "🚀 Ubuntu 20.04 USDT监控机器人部署脚本"
echo "======================================"

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo "❌ 请使用root用户运行此脚本"
    exit 1
fi

# 检查系统
if ! command -v apt &> /dev/null; then
    echo "❌ 此脚本仅支持Ubuntu/Debian系统"
    exit 1
fi

# 检查Ubuntu版本
UBUNTU_VERSION=$(lsb_release -rs)
echo "📋 检测到Ubuntu版本: $UBUNTU_VERSION"

# 更新系统
echo "📦 更新系统包..."
apt update && apt upgrade -y

# 安装中文支持
echo "🇨🇳 安装中文语言支持..."
apt install -y language-pack-zh-hans language-pack-zh-hans-base
apt install -y fonts-wqy-microhei fonts-wqy-zenhei

# 生成中文locale
locale-gen zh_CN.UTF-8

# 设置系统语言为中文
update-locale LANG=zh_CN.UTF-8 LC_ALL=zh_CN.UTF-8

# 安装必要软件
echo "📦 安装必要软件..."
apt install -y python3 python3-pip python3-venv git curl wget nano htop vnstat unzip

# 创建项目目录
PROJECT_DIR="/opt/usdt-monitor"
echo "📁 创建项目目录: $PROJECT_DIR"
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

# 检查当前目录是否有项目文件
if [ ! -f "main.py" ]; then
    echo "📥 项目文件不存在，请确保在项目目录中运行此脚本"
    echo "或者将项目文件上传到服务器后再运行"
    exit 1
fi

# 安装Python依赖
echo "📦 安装Python依赖..."
pip3 install -r requirements.txt

# 安装性能优化包
echo "⚡ 安装性能优化包..."
pip3 install uvloop

# 创建环境变量文件
if [ ! -f ".env" ]; then
    echo "📝 创建环境变量文件..."
    cp config.env.example .env
    echo "✅ 已创建 .env 文件，请编辑配置信息"
    echo "📋 使用命令: nano .env"
fi

# 创建系统服务
echo "🔧 创建系统服务..."
cat > /etc/systemd/system/usdt-monitor.service << EOF
[Unit]
Description=USDT Monitor Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$PROJECT_DIR
ExecStart=/usr/bin/python3 $PROJECT_DIR/main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
Environment=LANG=zh_CN.UTF-8
Environment=LC_ALL=zh_CN.UTF-8

[Install]
WantedBy=multi-user.target
EOF

# 设置文件权限
chmod +x main.py

# 重新加载systemd
systemctl daemon-reload

# 启用服务
systemctl enable usdt-monitor

# 创建日志轮转配置
echo "📋 配置日志轮转..."
cat > /etc/logrotate.d/usdt-monitor << EOF
$PROJECT_DIR/monitor.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 root root
    postrotate
        systemctl reload usdt-monitor
    endscript
}
EOF

# 创建备份目录
mkdir -p /opt/backups

# 创建管理脚本
cat > /opt/usdt-monitor/manage.sh << 'EOF'
#!/bin/bash

case "$1" in
    start)
        systemctl start usdt-monitor
        echo "✅ 服务已启动"
        ;;
    stop)
        systemctl stop usdt-monitor
        echo "🛑 服务已停止"
        ;;
    restart)
        systemctl restart usdt-monitor
        echo "🔄 服务已重启"
        ;;
    status)
        systemctl status usdt-monitor
        ;;
    logs)
        journalctl -u usdt-monitor -f
        ;;
    app-logs)
        tail -f /opt/usdt-monitor/monitor.log
        ;;
    test)
        cd /opt/usdt-monitor
        python3 test_bot.py
        ;;
    backup)
        cp /opt/usdt-monitor/.env /opt/backups/usdt-monitor-$(date +%Y%m%d_%H%M%S).env
        echo "✅ 配置文件已备份"
        ;;
    traffic)
        echo "📊 流量使用情况："
        vnstat -d
        echo ""
        echo "📈 月度流量："
        vnstat -m
        ;;
    optimize)
        echo "⚡ 开始系统优化..."
        
        # 优化TCP参数
        cat >> /etc/sysctl.conf << 'SYSCTL_EOF'
net.core.default_qdisc=fq
net.ipv4.tcp_congestion_control=bbr
net.ipv4.tcp_window_scaling=1
net.ipv4.tcp_timestamps=1
net.ipv4.tcp_sack=1
SYSCTL_EOF
        
        sysctl -p
        echo "✅ 网络参数已优化"
        
        # 创建swap文件（如果不存在）
        if [ ! -f /swapfile ]; then
            fallocate -l 1G /swapfile
            chmod 600 /swapfile
            mkswap /swapfile
            swapon /swapfile
            echo '/swapfile none swap sw 0 0' >> /etc/fstab
            echo "✅ Swap文件已创建"
        fi
        
        # 启动vnstat服务
        systemctl enable vnstat
        systemctl start vnstat
        echo "✅ 流量监控已启动"
        ;;
    update)
        echo "📦 更新系统和包..."
        apt update && apt upgrade -y
        pip3 install --upgrade -r requirements.txt
        systemctl restart usdt-monitor
        echo "✅ 系统已更新，服务已重启"
        ;;
    *)
        echo "用法: $0 {start|stop|restart|status|logs|app-logs|test|backup|traffic|optimize|update}"
        echo ""
        echo "命令说明:"
        echo "  start     - 启动服务"
        echo "  stop      - 停止服务"
        echo "  restart   - 重启服务"
        echo "  status    - 查看服务状态"
        echo "  logs      - 查看系统日志"
        echo "  app-logs  - 查看应用日志"
        echo "  test      - 运行测试"
        echo "  backup    - 备份配置文件"
        echo "  traffic   - 查看流量使用情况"
        echo "  optimize  - 优化系统性能"
        echo "  update    - 更新系统和包"
        exit 1
        ;;
esac
EOF

chmod +x /opt/usdt-monitor/manage.sh

# 创建自动备份脚本
cat > /opt/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# 备份配置文件
cp /opt/usdt-monitor/.env $BACKUP_DIR/usdt-monitor-$DATE.env

# 备份日志文件
if [ -f /opt/usdt-monitor/monitor.log ]; then
    cp /opt/usdt-monitor/monitor.log $BACKUP_DIR/monitor-$DATE.log
fi

# 保留最近7天的备份
find $BACKUP_DIR -name "usdt-monitor-*.env" -mtime +7 -delete
find $BACKUP_DIR -name "monitor-*.log" -mtime +7 -delete

echo "✅ 自动备份完成: $DATE"
EOF

chmod +x /opt/backup.sh

# 设置自动备份（每天凌晨2点）
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/backup.sh") | crontab -

# 启动vnstat服务
systemctl enable vnstat
systemctl start vnstat

# 设置系统优化
echo "⚡ 应用系统优化..."

# 优化系统参数
cat >> /etc/sysctl.conf << 'SYSCTL_EOF'
# 网络优化
net.core.default_qdisc=fq
net.ipv4.tcp_congestion_control=bbr
net.ipv4.tcp_window_scaling=1
net.ipv4.tcp_timestamps=1
net.ipv4.tcp_sack=1

# 内存优化
vm.swappiness=10
vm.dirty_ratio=15
vm.dirty_background_ratio=5
SYSCTL_EOF

sysctl -p

echo ""
echo "🎉 Ubuntu 20.04部署完成！"
echo "=========================="
echo ""
echo "🇨🇳 中文支持已启用"
echo "📋 下一步操作："
echo "1. 编辑配置文件:"
echo "   nano $PROJECT_DIR/.env"
echo ""
echo "2. 优化系统性能:"
echo "   $PROJECT_DIR/manage.sh optimize"
echo ""
echo "3. 测试机器人:"
echo "   $PROJECT_DIR/manage.sh test"
echo ""
echo "4. 启动服务:"
echo "   $PROJECT_DIR/manage.sh start"
echo ""
echo "5. 查看状态:"
echo "   $PROJECT_DIR/manage.sh status"
echo ""
echo "6. 查看流量:"
echo "   $PROJECT_DIR/manage.sh traffic"
echo ""
echo "📖 管理命令:"
echo "   $PROJECT_DIR/manage.sh {start|stop|restart|status|logs|app-logs|test|backup|traffic|optimize|update}"
echo ""
echo "🔧 服务信息:"
echo "   - 服务名称: usdt-monitor"
echo "   - 项目目录: $PROJECT_DIR"
echo "   - 日志文件: $PROJECT_DIR/monitor.log"
echo "   - 配置文件: $PROJECT_DIR/.env"
echo "   - 备份目录: /opt/backups"
echo ""
echo "⚡ Ubuntu优化:"
echo "   - 已安装uvloop性能优化"
echo "   - 已配置流量监控(vnstat)"
echo "   - 已设置自动备份"
echo "   - 已优化系统参数"
echo "   - 已启用中文支持"
echo ""
echo "⚠️  重要提醒："
echo "   - 请务必编辑 .env 文件并填写正确的配置信息"
echo "   - 建议定期检查流量使用情况"
echo "   - 服务已设置为开机自启"
echo "   - 自动备份已设置为每天凌晨2点执行" 