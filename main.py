#!/usr/bin/env python3
"""
简化主程序
只启动监控和机器人，不提供编辑功能
"""

import os
import sys
import time
import signal
import logging
import asyncio
from datetime import datetime
from dotenv import load_dotenv
import threading
from telegram import BotCommand, InlineKeyboardButton, InlineKeyboardMarkup

# 导入自定义模块
from tron_monitor import TronUSDTMonitor
from telegram_bot import TelegramBot

# 加载环境变量
load_dotenv()

class TronMonitorApp:
    """Tron监控应用"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.running = False
        
        # 初始化组件
        self.tron_monitor = TronUSDTMonitor()
        self.telegram_bot = TelegramBot()
        
        # 设置信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.logger.info("简化Tron监控应用初始化完成")
    
    def _signal_handler(self, signum, frame):
        """信号处理器"""
        self.logger.info(f"收到信号 {signum}，正在停止应用...")
        self.running = False
    
    async def start_monitoring(self):
        """启动监控"""
        try:
            self.logger.info("启动Tron链监控...")
            
            # 获取监控地址
            monitor_addresses = os.getenv('MONITOR_ADDRESSES', '').split(',')
            monitor_addresses = [addr.strip() for addr in monitor_addresses if addr.strip()]
            
            if not monitor_addresses:
                self.logger.warning("未配置监控地址")
                return
            
            self.logger.info(f"开始监控 {len(monitor_addresses)} 个地址")
            
            # 启动监控循环
            while self.running:
                try:
                    for address in monitor_addresses:
                        if not self.running:
                            break
                        
                        try:
                            # 检查新交易
                            new_transfers = self.tron_monitor.check_new_transfers()
                            new_transactions = [tx for tx in new_transfers if tx.get('to') == address]
                            
                            if new_transactions:
                                for tx in new_transactions:
                                    # 发送通知
                                    await self._send_transaction_notification(tx)
                            
                            # 短暂延迟
                            await asyncio.sleep(1)
                            
                        except Exception as e:
                            self.logger.error(f"监控地址 {address} 时出错: {e}")
                            continue
                    
                    # 等待下次检查
                    monitor_interval = int(os.getenv('MONITOR_INTERVAL', '30'))
                    await asyncio.sleep(monitor_interval)
                    
                except Exception as e:
                    self.logger.error(f"监控循环出错: {e}")
                    await asyncio.sleep(10)  # 出错后等待10秒再重试
            
        except Exception as e:
            self.logger.error(f"启动监控失败: {e}")
            raise
    
    async def _send_transaction_notification(self, transaction):
        """发送交易通知"""
        try:
            # 格式化时间戳
            txid = transaction.get('txid', 'unknown')
            amount = transaction.get('amount', 0)
            from_address = transaction.get('from', 'unknown')
            to_address = transaction.get('to', 'unknown')
            timestamp = transaction.get('timestamp', 'unknown')
            if isinstance(timestamp, (int, float)) and timestamp > 1e10:
                timestamp = int(timestamp / 1000)
            if isinstance(timestamp, (int, float)):
                from datetime import datetime
                time_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
            else:
                time_str = str(timestamp)
            msg = f"📍 {to_address[:10]}...{to_address[-10:] if to_address else ''}\n"
            msg += f"🕐 时间: {time_str}\n"
            msg += f"💰 金额: {amount} USDT\n"
            msg += f"🔗 交易哈希: {txid[:20]}..."
            keyboard = [[InlineKeyboardButton("在区块链浏览器查看", url=f"https://tronscan.org/#/transaction/{txid}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            # 获取允许的用户列表
            allowed_users = os.getenv('ALLOWED_USERS', '').split(',')
            allowed_users = [user.strip() for user in allowed_users if user.strip()]
            if not allowed_users:
                self.logger.warning("未配置允许的用户，跳过通知")
                return
            for user_id in allowed_users:
                try:
                    await self.telegram_bot.application.bot.send_message(
                        chat_id=user_id,
                        text=msg,
                        reply_markup=reply_markup
                    )
                    self.logger.info(f"通知已发送给用户 {user_id}")
                except Exception as e:
                    self.logger.error(f"发送通知给用户 {user_id} 失败: {e}")
                    continue
            self.logger.info(f"已发送交易通知: {transaction.get('txid', 'unknown')}")
        except Exception as e:
            self.logger.error(f"发送交易通知失败: {e}")
    
    async def run(self):
        self.running = True
        self.logger.info("启动简化Tron监控应用...")

        await self.telegram_bot.application.initialize()
        await self.telegram_bot.application.start()

        # 启动后主动推送监控信息
        await self.telegram_bot.send_startup_info()

        monitor_task = asyncio.create_task(self.start_monitoring())
        try:
            await monitor_task
        finally:
            await self.telegram_bot.application.stop()
            await self.telegram_bot.application.shutdown()

def start_monitoring_task(app):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(app.start_monitoring())

async def on_startup(application):
    # 注册BotCommand，支持/自动补全
    commands = [
        BotCommand("start", "显示此帮助信息"),
        BotCommand("help", "显示详细帮助"),
        BotCommand("status", "显示监控状态"),
        BotCommand("balance", "查询监控地址余额"),
        BotCommand("latest", "显示最新交易"),
        BotCommand("whitelist", "显示白名单地址"),
        BotCommand("wallet_balance", "查询钱包余额"),
        BotCommand("transfer", "转账到白名单地址")
    ]
    await application.bot.set_my_commands(commands)
    # 调用telegram_bot的send_startup_info方法
    bot = application.bot_data.get("telegram_bot_instance")
    if bot:
        await bot.send_startup_info()

def main():
    """主函数"""
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('tron_monitor.log', encoding='utf-8')
        ]
    )
    
    logger = logging.getLogger(__name__)
    
    try:
        # 检查环境变量
        required_vars = [
            'TELEGRAM_BOT_TOKEN',
            'MONITOR_ADDRESSES',
            'TRON_NODE_URL'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.error(f"缺少必要的环境变量: {', '.join(missing_vars)}")
            logger.error("请在 .env 文件中配置这些变量")
            sys.exit(1)
        
        # 创建并运行应用
        app = TronMonitorApp()
        
        # 存储telegram_bot实例，供on_startup使用
        app.telegram_bot.application.bot_data["telegram_bot_instance"] = app.telegram_bot
        # 启动监控任务
        monitor_thread = threading.Thread(target=start_monitoring_task, args=(app,))
        monitor_thread.start()
        # 注册on_startup
        app.telegram_bot.application.post_init = on_startup
        # 只跑run_polling
        app.telegram_bot.application.run_polling()
        
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在退出...")
    except Exception as e:
        logger.error(f"应用启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 