# 🚀 快速修复指南 - v2.0

本指南将帮助你快速应用v2.0版本的修复和新功能。

## 📋 修复内容概览

### ✅ 已修复的问题
1. **监控通知问题** - 改进了交易检查逻辑
2. **余额显示问题** - 添加了缓存和重试机制
3. **401错误** - 改进了Telegram API错误处理

### 🆕 新增功能
1. **最新交易查询** - `/latest` 命令
2. **地址管理** - `/add`、`/remove`、`/list` 命令
3. **改进的错误处理** - 更好的重试机制
4. **余额缓存** - 30秒缓存机制

## 🔧 快速更新步骤

### 方法一：完整更新（推荐）

1. **备份当前配置**
```bash
cp .env .env.backup
```

2. **更新代码文件**
```bash
# 下载新的代码文件
wget -O tron_monitor.py https://raw.githubusercontent.com/your-repo/main/tron_monitor.py
wget -O telegram_bot.py https://raw.githubusercontent.com/your-repo/main/telegram_bot.py
wget -O main.py https://raw.githubusercontent.com/your-repo/main/main.py
```

3. **重启服务**
```bash
sudo systemctl restart usdt-monitor
```

### 方法二：手动更新

1. **更新 tron_monitor.py**
- 替换整个文件内容
- 主要改进：API请求重试、余额缓存、地址管理

2. **更新 telegram_bot.py**
- 替换整个文件内容
- 主要改进：错误处理、新命令支持

3. **重启服务**
```bash
sudo systemctl restart usdt-monitor
```

## 🧪 测试修复效果

### 1. 测试余额查询
```bash
# 在Telegram中发送
/balance
```
**预期结果**: 余额应该正确显示，不再出现0的情况

### 2. 测试最新交易查询
```bash
# 在Telegram中发送
/latest
```
**预期结果**: 显示每个地址的最新转入交易

### 3. 测试地址管理
```bash
# 查看当前地址列表
/list

# 添加新地址（替换为你的地址）
/add TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t

# 删除地址
/remove TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t
```

### 4. 运行测试脚本
```bash
python3 test_fixes.py
```

## 🔍 验证修复

### 检查日志
```bash
# 查看应用日志
tail -f /opt/usdt-monitor/monitor.log

# 查看系统日志
sudo journalctl -u usdt-monitor -f
```

### 检查服务状态
```bash
sudo systemctl status usdt-monitor
```

## 📊 新功能使用说明

### 1. 最新交易查询 (`/latest`)
- 显示每个监控地址的最新转入交易
- 包含金额、发送方、时间、交易哈希等信息
- 如果没有交易记录会显示"暂无交易记录"

### 2. 地址管理功能

#### 添加地址 (`/add <地址>`)
```bash
/add TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t
```
- 自动验证地址格式（T开头，34位长度）
- 检查地址是否已存在
- 自动更新.env文件

#### 删除地址 (`/remove <地址>`)
```bash
/remove TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t
```
- 从监控列表中删除指定地址
- 自动更新.env文件

#### 查看地址列表 (`/list`)
```bash
/list
```
- 显示所有监控地址
- 显示每个地址的当前余额

### 3. 改进的余额查询
- 30秒缓存机制，提高查询效率
- 自动重试机制，解决网络问题
- 备用API调用，提高成功率

## 🚨 故障排除

### 如果更新后出现问题

1. **恢复备份**
```bash
cp .env.backup .env
sudo systemctl restart usdt-monitor
```

2. **检查依赖**
```bash
pip3 install -r requirements.txt
```

3. **检查日志**
```bash
sudo journalctl -u usdt-monitor -n 50
```

### 常见问题解决

1. **余额仍然显示为0**
   - 多查询几次，缓存机制需要时间生效
   - 检查网络连接
   - 查看日志中的错误信息

2. **新命令不工作**
   - 确认服务已重启
   - 检查Telegram机器人权限
   - 查看应用日志

3. **401错误仍然出现**
   - 检查Bot Token是否正确
   - 确认机器人没有被禁用
   - 验证Chat ID

## 📈 性能改进

### 缓存机制
- 余额查询结果缓存30秒
- 减少API调用频率
- 提高响应速度

### 重试机制
- API请求失败时自动重试
- 指数退避策略
- 提高成功率

### 错误处理
- 详细的错误分类
- 更好的错误提示
- 自动恢复机制

## 🔄 回滚方案

如果需要回滚到之前的版本：

1. **恢复文件**
```bash
git checkout HEAD~1 -- tron_monitor.py telegram_bot.py main.py
```

2. **重启服务**
```bash
sudo systemctl restart usdt-monitor
```

3. **验证回滚**
```bash
sudo systemctl status usdt-monitor
```

## 📞 获取帮助

如果遇到问题：

1. 查看日志文件
2. 运行测试脚本
3. 检查配置文件
4. 提交Issue或联系支持

---

**注意**: 更新前请务必备份配置文件，以防意外情况。 