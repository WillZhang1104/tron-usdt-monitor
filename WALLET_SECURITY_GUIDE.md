# 🔐 钱包安全配置指南

⚠️ **重要警告**: 转账功能涉及真实资金，请务必谨慎配置和使用！

## 🚨 安全风险提示

1. **私钥安全**: 私钥是访问钱包的唯一凭证，泄露将导致资金损失
2. **服务器安全**: 服务器被攻击可能导致私钥泄露
3. **操作风险**: 错误的转账操作可能导致资金损失
4. **网络风险**: 网络攻击可能导致交易被篡改

## 🔧 安全配置步骤

### 1. 创建专用钱包

**强烈建议**创建一个专门用于机器人的钱包，不要使用主要资金钱包：

1. 在TronLink中创建新钱包
2. 只转入少量资金用于测试
3. 导出私钥（十六进制格式）

### 2. 配置环境变量

在 `.env` 文件中添加以下配置：

```env
# 钱包配置（⚠️ 安全风险）
TRON_PRIVATE_KEY=your_private_key_here

# 转账限制（安全设置）
MAX_TRX_AMOUNT=100
MAX_USDT_AMOUNT=1000

# 白名单地址（可选，但强烈建议）
ALLOWED_ADDRESSES=address1,address2,address3
```

### 3. 私钥安全存储

**方法一：环境变量（基础安全）**
```bash
# 在服务器上设置环境变量
export TRON_PRIVATE_KEY="your_private_key_here"
```

**方法二：加密存储（推荐）**
```bash
# 使用gpg加密私钥
echo "your_private_key_here" | gpg --encrypt --recipient your_email@example.com > private_key.gpg
```

**方法三：硬件钱包（最安全）**
- 使用硬件钱包进行签名
- 私钥永不离开硬件设备

### 4. 设置转账限制

```env
# 最大转账金额（根据你的风险承受能力设置）
MAX_TRX_AMOUNT=50      # 最大TRX转账金额
MAX_USDT_AMOUNT=500    # 最大USDT转账金额

# 白名单地址（只允许向这些地址转账）
ALLOWED_ADDRESSES=TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t,TRxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## 🛡️ 安全最佳实践

### 1. 服务器安全

```bash
# 设置文件权限
chmod 600 .env
chown root:root .env

# 禁用不必要的服务
systemctl disable ssh
systemctl enable ufw
ufw allow from your_ip only
```

### 2. 监控和日志

```bash
# 启用详细日志
LOG_LEVEL=DEBUG

# 监控转账活动
tail -f /opt/usdt-monitor/monitor.log | grep "transfer"
```

### 3. 定期备份

```bash
# 备份配置文件
cp .env /opt/backups/wallet-config-$(date +%Y%m%d).env

# 备份私钥（加密）
gpg --encrypt --recipient your_email@example.com private_key.txt
```

## 📋 使用说明

### 转账命令

```bash
# 查看钱包余额
/wallet_balance

# 转账TRX
/transfer_trx TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t 10

# 转账USDT
/transfer_usdt TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t 100
```

### 安全验证

每次转账前，系统会验证：
- ✅ 地址格式是否正确
- ✅ 转账金额是否在限制范围内
- ✅ 目标地址是否在白名单中
- ✅ 钱包余额是否充足

## 🚨 紧急情况处理

### 1. 私钥泄露

如果怀疑私钥泄露：
1. 立即转移所有资金到安全钱包
2. 停止机器人服务
3. 删除服务器上的私钥文件
4. 重新生成新的私钥

### 2. 服务器被攻击

```bash
# 立即停止服务
sudo systemctl stop usdt-monitor

# 断开网络连接
sudo ufw deny all

# 备份重要数据
cp .env /tmp/backup.env

# 联系安全专家
```

### 3. 错误转账

如果发生错误转账：
1. 记录交易哈希
2. 联系接收方（如果可能）
3. 检查交易状态
4. 学习经验，改进安全措施

## 🔍 测试建议

### 1. 小额测试

在正式使用前：
1. 创建测试钱包
2. 转入少量资金（如1 TRX, 1 USDT）
3. 进行多次小额转账测试
4. 验证所有安全限制是否生效

### 2. 功能测试

```bash
# 测试余额查询
/wallet_balance

# 测试小额转账
/transfer_trx TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t 0.1
/transfer_usdt TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t 1

# 测试安全限制
/transfer_trx TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t 1000  # 应该失败
```

## 📞 技术支持

如果遇到问题：
1. 查看日志文件
2. 检查配置文件
3. 验证网络连接
4. 联系技术支持

---

**⚠️ 免责声明**: 使用转账功能存在资金风险，请自行承担风险。建议在充分了解风险的情况下谨慎使用。 