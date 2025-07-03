# Ubuntu 20.04 简化部署指南

## 系统要求

- **操作系统**: Ubuntu 20.04 LTS
- **内存**: 最少 1GB RAM
- **硬盘**: 最少 20GB 可用空间
- **网络**: 稳定的网络连接

## 快速部署步骤

### 第一步：上传项目文件

```bash
# 在本地执行，上传项目文件到服务器
scp -r ./* root@your_server_ip:/opt/usdt-monitor/
```

### 第二步：SSH连接并运行部署脚本

```bash
# SSH连接到服务器
ssh root@your_server_ip

# 进入项目目录
cd /opt/usdt-monitor

# 设置执行权限
chmod +x deploy_ubuntu.sh

# 运行部署脚本
./deploy_ubuntu.sh
```

### 第三步：配置环境变量

```bash
# 编辑配置文件
nano .env
```

填写以下配置信息：
```env
# Telegram Bot配置
TELEGRAM_BOT_TOKEN=你的机器人token
TELEGRAM_CHAT_ID=你的聊天ID

# Tron网络配置
TRON_NODE_URL=https://api.trongrid.io
USDT_CONTRACT_ADDRESS=TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t

# 监控配置
MONITOR_ADDRESSES=你要监控的Tron地址1,你要监控的Tron地址2
MONITOR_INTERVAL=30

# 日志配置
LOG_LEVEL=INFO
```

### 第四步：测试和启动

```bash
# 优化系统性能
/opt/usdt-monitor/manage.sh optimize

# 测试机器人
/opt/usdt-monitor/manage.sh test

# 启动服务
/opt/usdt-monitor/manage.sh start

# 查看状态
/opt/usdt-monitor/manage.sh status
```

## 中文支持

部署脚本会自动安装和配置中文支持：

- 安装中文语言包
- 安装中文字体
- 设置系统语言为中文
- 配置SSH环境变量

## 管理命令

### 基本管理
```bash
# 启动服务
/opt/usdt-monitor/manage.sh start

# 停止服务
/opt/usdt-monitor/manage.sh stop

# 重启服务
/opt/usdt-monitor/manage.sh restart

# 查看状态
/opt/usdt-monitor/manage.sh status
```

### 日志查看
```bash
# 查看系统日志
/opt/usdt-monitor/manage.sh logs

# 查看应用日志
/opt/usdt-monitor/manage.sh app-logs

# 实时查看日志
tail -f /opt/usdt-monitor/monitor.log
```

### 系统维护
```bash
# 备份配置
/opt/usdt-monitor/manage.sh backup

# 查看流量使用
/opt/usdt-monitor/manage.sh traffic

# 优化系统
/opt/usdt-monitor/manage.sh optimize

# 更新系统
/opt/usdt-monitor/manage.sh update
```

## 故障排除

### 1. 服务无法启动
```bash
# 查看详细错误
journalctl -u usdt-monitor -n 50

# 手动测试
cd /opt/usdt-monitor
python3 main.py
```

### 2. 权限问题
```bash
# 检查文件权限
ls -la /opt/usdt-monitor/

# 修复权限
chmod +x /opt/usdt-monitor/main.py
chmod +x /opt/usdt-monitor/manage.sh
```

### 3. 网络问题
```bash
# 测试网络连接
ping api.telegram.org
ping api.trongrid.io
```

### 4. 中文显示问题
```bash
# 检查locale设置
locale

# 重新设置中文环境
export LANG=zh_CN.UTF-8
export LC_ALL=zh_CN.UTF-8
```

## 性能监控

### 系统资源
```bash
# 查看CPU和内存使用
htop

# 查看磁盘使用
df -h

# 查看网络连接
netstat -tulpn
```

### 流量监控
```bash
# 查看流量统计
vnstat -d
vnstat -m

# 查看实时流量
vnstat -l
```

## 自动功能

### 自动备份
- 每天凌晨2点自动备份配置文件
- 保留最近7天的备份
- 备份文件保存在 `/opt/backups/`

### 日志轮转
- 每天自动轮转日志文件
- 保留最近7天的日志
- 自动压缩旧日志

### 开机自启
- 服务已设置为开机自动启动
- 系统重启后自动恢复服务

## 推荐配置

### 最小配置
- CPU: 1核
- 内存: 1GB
- 硬盘: 20GB
- 网络: 1Mbps

### 推荐配置
- CPU: 2核
- 内存: 2GB
- 硬盘: 40GB
- 网络: 5Mbps

## 常见问题

### Q: 如何查看系统版本？
A: 
```bash
lsb_release -a
```

### Q: 如何设置时区？
A: 
```bash
timedatectl set-timezone Asia/Shanghai
```

### Q: 如何查看系统负载？
A: 
```bash
uptime
top
htop
```

### Q: 如何重启系统？
A: 
```bash
reboot
```

## 安全建议

1. **定期更新系统**
   ```bash
   /opt/usdt-monitor/manage.sh update
   ```

2. **定期备份配置**
   ```bash
   /opt/usdt-monitor/manage.sh backup
   ```

3. **监控流量使用**
   ```bash
   /opt/usdt-monitor/manage.sh traffic
   ```

4. **检查服务状态**
   ```bash
   /opt/usdt-monitor/manage.sh status
   ```

## 联系支持

如果遇到问题，可以：

1. 查看日志文件
2. 运行测试命令
3. 检查配置文件
4. 重启服务

Ubuntu 20.04是一个稳定可靠的选择，适合长期运行USDT监控机器人。 