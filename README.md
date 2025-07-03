# Tron地址监控机器人

一个简化的Tron链USDT监控Telegram机器人，支持地址监控、余额查询、转账功能。

## 功能特性

- 🔍 **地址监控**: 自动监控指定地址的USDT入账
- 💰 **余额查询**: 查询监控地址和钱包余额
- 📊 **交易记录**: 查看最新交易信息
- 💸 **安全转账**: 支持向白名单地址转账
- 🔒 **权限控制**: 只允许授权用户使用
- 📱 **Telegram通知**: 实时发送交易通知

## 快速开始

### 1. 环境要求

- Python 3.8+
- Ubuntu 20.04+ (推荐)
- 稳定的网络连接

### 2. 安装依赖

```bash
# 安装Python依赖
pip install -r requirements.txt

# 或使用安装脚本
chmod +x setup_chinese.sh
./setup_chinese.sh
```

### 3. 配置环境变量

创建 `.env` 文件并配置以下变量：

```bash
# Telegram机器人配置
TELEGRAM_BOT_TOKEN=your_bot_token_here
ALLOWED_USERS=your_telegram_user_id

# Tron网络配置
TRON_NODE_URL=https://api.trongrid.io
USDT_CONTRACT_ADDRESS=TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t

# 监控配置
MONITOR_ADDRESSES=address1,address2,address3
MONITOR_INTERVAL=30

# 白名单地址配置（用于转账）
WHITELIST_ADDRESSES=地址1=别名1,描述1|地址2=别名2,描述2

# 钱包配置（可选，用于转账功能）
WALLET_PRIVATE_KEY=your_encrypted_private_key
```

### 4. 启动服务

```bash
# 启动监控和机器人
python main.py

# 或后台运行
nohup python main.py > monitor.log 2>&1 &
```

## 配置说明

### 白名单地址配置

在 `.env` 文件中配置 `WHITELIST_ADDRESSES`：

```bash
# 格式：地址=别名,描述|地址=别名,描述
WHITELIST_ADDRESSES=TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t=USDT合约,官方USDT合约|TYourAddressHere=我的钱包,个人钱包地址
```

### 监控地址配置

在 `.env` 文件中配置 `MONITOR_ADDRESSES`：

```bash
# 用逗号分隔多个地址，不能有空格
MONITOR_ADDRESSES=TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t,TYourAddressHere
```

## Telegram机器人命令

### 基础命令
- `/start` - 显示帮助信息
- `/help` - 显示详细帮助
- `/status` - 显示监控状态

### 监控命令
- `/balance` - 查询监控地址余额
- `/latest` - 显示最新交易记录
- `/whitelist` - 显示白名单地址

### 钱包命令
- `/wallet_balance` - 查询钱包余额
- `/transfer` - 转账到白名单地址

### 转账使用示例

```bash
# 按序号转账
/transfer 1 100 测试转账

# 按别名转账
/transfer 我的钱包 50

# 按地址转账
/transfer TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t 25
```

## 安全配置

### 私钥加密存储

1. 安装GPG：
```bash
sudo apt update
sudo apt install gnupg
```

2. 生成密钥对：
```bash
gpg --gen-key
```

3. 加密私钥：
```bash
echo "your_private_key_here" | gpg --encrypt --recipient your_email@example.com > wallet_key.gpg
```

4. 在 `.env` 中配置：
```bash
WALLET_PRIVATE_KEY=wallet_key.gpg
```

### 自动化加密设置

使用提供的脚本：
```bash
chmod +x setup_encrypted_wallet.sh
./setup_encrypted_wallet.sh
```

## 服务器部署

### Ubuntu 20.04 部署

```bash
# 下载部署脚本
wget https://raw.githubusercontent.com/your-repo/地址监控/main/deploy_ubuntu.sh

# 执行部署
chmod +x deploy_ubuntu.sh
./deploy_ubuntu.sh
```

### 手动部署步骤

1. 更新系统：
```bash
sudo apt update && sudo apt upgrade -y
```

2. 安装Python：
```bash
sudo apt install python3 python3-pip python3-venv -y
```

3. 创建项目目录：
```bash
mkdir -p ~/tron_monitor
cd ~/tron_monitor
```

4. 下载代码：
```bash
git clone https://github.com/your-repo/地址监控.git .
```

5. 安装依赖：
```bash
pip3 install -r requirements.txt
```

6. 配置环境变量：
```bash
cp .env.example .env
nano .env
```

7. 启动服务：
```bash
python3 main.py
```

## 故障排除

### 常见问题

1. **机器人无响应**
   - 检查 `TELEGRAM_BOT_TOKEN` 是否正确
   - 确认机器人已启动并与用户对话

2. **余额显示为0**
   - 检查网络连接
   - 确认地址格式正确
   - 查看日志文件

3. **转账失败**
   - 确认目标地址在白名单中
   - 检查钱包余额是否充足
   - 验证私钥是否正确解密

4. **监控不工作**
   - 检查 `MONITOR_ADDRESSES` 配置
   - 确认网络连接正常
   - 查看监控日志

### 日志查看

```bash
# 查看实时日志
tail -f tron_monitor.log

# 查看错误日志
grep ERROR tron_monitor.log
```

## 更新指南

### 从GitHub更新

```bash
# 备份当前配置
cp .env .env.backup

# 拉取最新代码
git pull origin main

# 恢复配置
cp .env.backup .env

# 重启服务
pkill -f main.py
python3 main.py
```

## 文件结构

```
地址监控/
├── main.py                 # 主程序
├── telegram_bot.py         # Telegram机器人
├── tron_monitor.py         # Tron监控模块
├── wallet_operations.py    # 钱包操作模块
├── address_manager.py      # 地址管理模块
├── requirements.txt        # Python依赖
├── .env                    # 环境变量配置
├── setup_chinese.sh        # 中文安装脚本
├── deploy_ubuntu.sh        # Ubuntu部署脚本
├── setup_encrypted_wallet.sh # 钱包加密设置脚本
└── README.md              # 说明文档
```

## 许可证

MIT License

## 支持

如有问题，请查看：
- [快速修复指南](QUICK_FIX_GUIDE.md)
- [钱包安全指南](WALLET_SECURITY_GUIDE.md)
- [Ubuntu部署指南](ubuntu_deploy_guide.md) 