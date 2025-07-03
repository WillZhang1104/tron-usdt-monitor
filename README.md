# Tron链USDT监控Telegram机器人

一个用于监控Tron区块链上USDT转账的Telegram机器人，支持实时通知、余额查询、交易历史等功能。

## 🆕 最新更新 (v2.0)

### 修复的问题
1. **✅ 修复监控通知问题** - 改进了交易检查逻辑，使用更可靠的TronGrid API
2. **✅ 修复余额显示问题** - 添加了缓存机制和重试逻辑，解决余额显示为0的问题
3. **✅ 修复401错误** - 改进了Telegram API错误处理，添加了详细的异常处理

### 新增功能
1. **🆕 最新交易查询** - `/latest` 命令显示每个地址的最新转入交易
2. **🆕 地址管理** - `/add`、`/remove`、`/list` 命令管理监控地址
3. **🆕 改进的错误处理** - 更好的API重试机制和错误提示
4. **🆕 余额缓存** - 30秒缓存机制，提高查询效率

## 🚀 功能特性

- 🔔 **实时监控** - 自动监控指定地址的USDT入账
- 📱 **Telegram通知** - 实时发送交易通知到Telegram
- 💰 **余额查询** - 快速查询地址USDT余额
- 📊 **交易历史** - 查看最新交易记录
- ⚙️ **地址管理** - 动态添加/删除监控地址
- 🔧 **系统服务** - 支持systemd服务管理
- 📈 **性能优化** - 网络优化和流量监控

## 📋 可用命令

| 命令 | 功能 | 示例 |
|------|------|------|
| `/start` | 显示欢迎信息 | `/start` |
| `/help` | 显示帮助信息 | `/help` |
| `/status` | 查看监控状态 | `/status` |
| `/balance` | 查看地址余额 | `/balance` |
| `/latest` | 查看最新交易 | `/latest` |
| `/list` | 查看地址列表 | `/list` |
| `/add` | 添加监控地址 | `/add TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t` |
| `/remove` | 删除监控地址 | `/remove TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t` |
| `/settings` | 查看设置 | `/settings` |

## 🛠️ 安装部署

### 环境要求
- Ubuntu 20.04+
- Python 3.8+
- 2GB+ RAM
- 稳定的网络连接

### 快速部署

1. **克隆项目**
```bash
git clone <项目地址>
cd 地址监控
```

2. **运行部署脚本**
```bash
sudo bash deploy_ubuntu.sh
```

3. **配置环境变量**
```bash
nano .env
```

4. **启动服务**
```bash
sudo systemctl start usdt-monitor
```

### 手动安装

1. **安装依赖**
```bash
sudo apt update
sudo apt install python3 python3-pip git
pip3 install -r requirements.txt
```

2. **配置环境变量**
```bash
cp config.env.example .env
nano .env
```

3. **运行程序**
```bash
python3 main.py
```

## ⚙️ 配置说明

### 环境变量配置 (.env)

```env
# Telegram配置
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# 监控配置
MONITOR_ADDRESSES=address1,address2,address3
MONITOR_INTERVAL=30

# Tron网络配置
TRON_NODE_URL=https://api.trongrid.io
USDT_CONTRACT_ADDRESS=TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t

# 日志配置
LOG_LEVEL=INFO
```

### 获取Telegram Bot Token

1. 在Telegram中搜索 `@BotFather`
2. 发送 `/newbot` 创建新机器人
3. 按提示设置机器人名称
4. 获取Bot Token

### 获取Chat ID

1. 将机器人添加到群组或直接与机器人对话
2. 发送消息给机器人
3. 访问 `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
4. 查找 `chat.id` 字段

## 🔧 服务管理

### 使用管理脚本
```bash
# 启动服务
sudo /opt/usdt-monitor/manage.sh start

# 停止服务
sudo /opt/usdt-monitor/manage.sh stop

# 重启服务
sudo /opt/usdt-monitor/manage.sh restart

# 查看状态
sudo /opt/usdt-monitor/manage.sh status

# 查看日志
sudo /opt/usdt-monitor/manage.sh logs

# 查看应用日志
sudo /opt/usdt-monitor/manage.sh app-logs

# 运行测试
sudo /opt/usdt-monitor/manage.sh test

# 备份配置
sudo /opt/usdt-monitor/manage.sh backup

# 查看流量
sudo /opt/usdt-monitor/manage.sh traffic

# 系统优化
sudo /opt/usdt-monitor/manage.sh optimize
```

### 使用systemctl
```bash
# 启动服务
sudo systemctl start usdt-monitor

# 停止服务
sudo systemctl stop usdt-monitor

# 重启服务
sudo systemctl restart usdt-monitor

# 查看状态
sudo systemctl status usdt-monitor

# 查看日志
sudo journalctl -u usdt-monitor -f

# 设置开机自启
sudo systemctl enable usdt-monitor
```

## 🧪 测试功能

运行测试脚本验证功能：
```bash
python3 test_fixes.py
```

## 📊 监控和日志

### 日志文件
- 应用日志: `/opt/usdt-monitor/monitor.log`
- 系统日志: `journalctl -u usdt-monitor`

### 流量监控
```bash
# 查看实时流量
vnstat -l

# 查看日流量
vnstat -d

# 查看月流量
vnstat -m
```

## 🔍 故障排除

### 常见问题

1. **监控地址有交易但没有通知**
   - 检查网络连接
   - 验证Telegram Bot Token和Chat ID
   - 查看日志文件

2. **余额显示为0**
   - 程序已添加缓存和重试机制
   - 多查询几次应该会显示正确余额
   - 检查地址是否正确

3. **401 Unauthorized错误**
   - 检查Bot Token是否正确
   - 确认机器人没有被禁用
   - 验证Chat ID是否正确

4. **服务启动失败**
   - 检查配置文件语法
   - 验证Python依赖是否安装完整
   - 查看系统日志

### 调试模式

设置日志级别为DEBUG：
```env
LOG_LEVEL=DEBUG
```

## 📈 性能优化

### 网络优化
- 启用BBR拥塞控制
- 优化TCP参数
- 配置流量监控

### 系统优化
- 创建swap文件
- 配置日志轮转
- 自动备份配置

## 🔒 安全建议

1. **定期更新**
   - 保持系统和依赖包最新
   - 定期检查安全更新

2. **访问控制**
   - 限制服务器SSH访问
   - 使用强密码和密钥认证

3. **监控告警**
   - 设置系统监控
   - 配置异常告警

## 📝 更新日志

### v2.0 (当前版本)
- ✅ 修复监控通知问题
- ✅ 修复余额显示问题  
- ✅ 修复401错误
- 🆕 添加最新交易查询功能
- 🆕 添加地址管理功能
- 🆕 改进错误处理和重试机制
- 🆕 添加余额缓存机制

### v1.0
- 🎉 初始版本发布
- 🔔 基础监控功能
- 📱 Telegram通知
- 💰 余额查询

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 📞 支持

如有问题，请通过以下方式联系：
- 提交GitHub Issue
- 发送邮件至支持邮箱

---

**注意**: 请确保遵守相关法律法规，本工具仅用于合法的监控目的。 