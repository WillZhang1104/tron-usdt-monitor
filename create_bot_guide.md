# Telegram机器人创建详细指南

## 第一步：创建Telegram机器人

### 1. 找到BotFather
1. 打开Telegram应用
2. 在搜索框中输入 `@BotFather`
3. 点击进入BotFather聊天

### 2. 创建新机器人
1. 发送 `/start` 命令给BotFather
2. 发送 `/newbot` 命令
3. 输入机器人名称（例如：USDT监控机器人）
4. 输入机器人用户名（必须以bot结尾，例如：usdt_monitor_bot）
5. BotFather会返回机器人的token，格式类似：
   ```
   123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   ```

### 3. 保存Token
将获得的token复制并保存，稍后需要填入配置文件。

## 第二步：获取Chat ID

### 方法一：与机器人私聊
1. 搜索你创建的机器人用户名
2. 点击开始聊天
3. 发送 `/start` 命令
4. 访问以下URL（替换YOUR_BOT_TOKEN）：
   ```
   https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
   ```
5. 在返回的JSON中找到 `chat.id` 字段，这就是你的Chat ID

### 方法二：使用@userinfobot
1. 在Telegram中搜索 `@userinfobot`
2. 发送 `/start` 命令
3. 机器人会返回你的Chat ID

### 方法三：群组Chat ID
如果你想在群组中接收通知：
1. 将机器人添加到群组
2. 在群组中发送一条消息
3. 访问上述URL获取群组的Chat ID（通常是负数）

## 第三步：配置环境变量

1. 复制 `config.env.example` 文件为 `.env`
2. 编辑 `.env` 文件，填写以下信息：

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

## 第四步：测试机器人

1. 运行安装脚本：
   ```bash
   python setup.py
   ```

2. 启动机器人：
   ```bash
   python main.py
   ```

3. 在Telegram中向机器人发送 `/start` 命令测试

## 常见问题

### Q: 机器人没有响应？
A: 检查以下几点：
- Token是否正确
- Chat ID是否正确
- 机器人是否已启动
- 网络连接是否正常

### Q: 如何监控多个地址？
A: 在 `MONITOR_ADDRESSES` 中用逗号分隔多个地址：
```
MONITOR_ADDRESSES=TRxxxxxxxxx,TRyyyyyyyyy,TRzzzzzzzzz
```

### Q: 如何调整监控频率？
A: 修改 `MONITOR_INTERVAL` 参数（单位：秒）：
```
MONITOR_INTERVAL=60  # 每60秒检查一次
```

### Q: 如何查看日志？
A: 日志文件保存在 `monitor.log` 中，也可以查看控制台输出。

## 安全提示

1. 不要将 `.env` 文件提交到版本控制系统
2. 定期更换机器人token
3. 不要在公开场合分享你的Chat ID
4. 建议使用私有Tron节点以提高安全性 