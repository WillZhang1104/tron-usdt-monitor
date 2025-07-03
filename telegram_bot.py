import os
import logging
import asyncio
from typing import Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import TelegramError, BadRequest
from telegram.constants import ParseMode
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class TelegramBot:
    """Telegram机器人管理器"""
    
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN 未设置")
        
        if not self.chat_id:
            raise ValueError("TELEGRAM_CHAT_ID 未设置")
        
        # 初始化机器人应用
        self.application = Application.builder().token(self.bot_token).build()
        
        # 设置日志
        self.logger = logging.getLogger(__name__)
        
        # 注册命令处理器
        self._register_handlers()
        
        self.logger.info("Telegram机器人初始化完成")
    
    def _register_handlers(self):
        """注册命令处理器"""
        # 基本命令
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("balance", self.balance_command))
        self.application.add_handler(CommandHandler("settings", self.settings_command))
        
        # 新增命令
        self.application.add_handler(CommandHandler("latest", self.latest_command))
        self.application.add_handler(CommandHandler("add", self.add_address_command))
        self.application.add_handler(CommandHandler("remove", self.remove_address_command))
        self.application.add_handler(CommandHandler("list", self.list_addresses_command))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /start 命令"""
        welcome_message = (
            "🤖 欢迎使用Tron链USDT监控机器人！\n\n"
            "📋 可用命令：\n"
            "/start - 显示欢迎信息\n"
            "/help - 显示帮助信息\n"
            "/status - 查看监控状态\n"
            "/balance - 查看地址余额\n"
            "/latest - 查看最新交易\n"
            "/list - 查看监控地址列表\n"
            "/add <地址> - 添加监控地址\n"
            "/remove <地址> - 删除监控地址\n"
            "/settings - 查看设置\n\n"
            "🔔 机器人会自动监控指定地址的USDT入账情况，"
            "一旦有新交易就会发送通知。"
        )
        
        await update.message.reply_text(welcome_message)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /help 命令"""
        help_message = (
            "📖 使用帮助\n\n"
            "🔧 配置说明：\n"
            "1. 在 .env 文件中设置 TELEGRAM_BOT_TOKEN\n"
            "2. 设置 TELEGRAM_CHAT_ID 为你的聊天ID\n"
            "3. 在 MONITOR_ADDRESSES 中配置要监控的地址\n\n"
            "📊 监控功能：\n"
            "- 自动监控Tron链上指定地址的USDT入账\n"
            "- 实时发送通知消息\n"
            "- 显示交易详情和区块信息\n\n"
            "⚙️ 命令说明：\n"
            "/status - 查看当前监控状态\n"
            "/balance - 查看监控地址的USDT余额\n"
            "/latest - 查看每个地址的最新转入交易\n"
            "/list - 显示当前监控的地址列表\n"
            "/add <Tron地址> - 添加新的监控地址\n"
            "/remove <Tron地址> - 删除监控地址\n"
            "/settings - 查看当前配置\n\n"
            "💡 示例：\n"
            "/add TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t\n"
            "/remove TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
        )
        
        await update.message.reply_text(help_message)
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /status 命令"""
        from tron_monitor import TronUSDTMonitor
        
        try:
            monitor = TronUSDTMonitor()
            status_message = "📊 监控状态\n\n"
            
            if monitor.monitor_addresses:
                status_message += f"✅ 监控地址数量: {len(monitor.monitor_addresses)}\n"
                status_message += f"📝 已处理交易数: {len(monitor.processed_transactions)}\n\n"
                
                status_message += "📍 监控地址列表：\n"
                for i, addr in enumerate(monitor.monitor_addresses, 1):
                    balance = monitor.get_address_balance(addr)
                    status_message += f"{i}. {addr[:10]}...{addr[-10:]} - {balance:,.2f} USDT\n"
            else:
                status_message += "❌ 未配置监控地址\n"
                status_message += "使用 /add <地址> 添加监控地址"
            
            await update.message.reply_text(status_message)
            
        except Exception as e:
            await update.message.reply_text(f"❌ 获取状态失败: {str(e)}")
    
    async def balance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /balance 命令"""
        from tron_monitor import TronUSDTMonitor
        
        try:
            monitor = TronUSDTMonitor()
            balance_message = "💰 地址余额\n\n"
            
            if monitor.monitor_addresses:
                for i, addr in enumerate(monitor.monitor_addresses, 1):
                    balance = monitor.get_address_balance(addr)
                    balance_message += f"📍 地址 {i}: {addr[:10]}...{addr[-10:]}\n"
                    balance_message += f"💵 余额: {balance:,.2f} USDT\n\n"
            else:
                balance_message += "❌ 未配置监控地址\n"
                balance_message += "使用 /add <地址> 添加监控地址"
            
            await update.message.reply_text(balance_message)
            
        except Exception as e:
            await update.message.reply_text(f"❌ 获取余额失败: {str(e)}")
    
    async def latest_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /latest 命令 - 显示每个地址的最新交易"""
        from tron_monitor import TronUSDTMonitor
        
        try:
            monitor = TronUSDTMonitor()
            latest_message = "🕐 最新交易记录\n\n"
            
            if monitor.monitor_addresses:
                for i, addr in enumerate(monitor.monitor_addresses, 1):
                    latest_transfer = monitor.get_latest_transfer(addr)
                    latest_message += f"📍 地址 {i}: {addr[:10]}...{addr[-10:]}\n"
                    
                    if latest_transfer:
                        import time
                        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', 
                                                time.localtime(latest_transfer['timestamp'] / 1000))
                        latest_message += f"💰 金额: {latest_transfer['amount']:,.2f} USDT\n"
                        latest_message += f"📤 发送方: {latest_transfer['from'][:10]}...{latest_transfer['from'][-10:]}\n"
                        latest_message += f"🕐 时间: {timestamp}\n"
                        latest_message += f"🔗 交易: {latest_transfer['txid'][:10]}...{latest_transfer['txid'][-10:]}\n\n"
                    else:
                        latest_message += "❌ 暂无交易记录\n\n"
            else:
                latest_message += "❌ 未配置监控地址\n"
                latest_message += "使用 /add <地址> 添加监控地址"
            
            await update.message.reply_text(latest_message)
            
        except Exception as e:
            await update.message.reply_text(f"❌ 获取最新交易失败: {str(e)}")
    
    async def add_address_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /add 命令 - 添加监控地址"""
        from tron_monitor import TronUSDTMonitor
        
        try:
            if not context.args:
                await update.message.reply_text(
                    "❌ 请提供要添加的地址\n"
                    "用法: /add <Tron地址>\n"
                    "示例: /add TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
                )
                return
            
            address = context.args[0].strip()
            monitor = TronUSDTMonitor()
            
            if monitor.add_monitor_address(address):
                await update.message.reply_text(f"✅ 成功添加监控地址: {address}")
            else:
                await update.message.reply_text(
                    f"❌ 添加失败\n"
                    f"可能原因：\n"
                    f"1. 地址格式不正确\n"
                    f"2. 地址已存在\n"
                    f"3. 地址无效"
                )
                
        except Exception as e:
            await update.message.reply_text(f"❌ 添加地址失败: {str(e)}")
    
    async def remove_address_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /remove 命令 - 删除监控地址"""
        from tron_monitor import TronUSDTMonitor
        
        try:
            if not context.args:
                await update.message.reply_text(
                    "❌ 请提供要删除的地址\n"
                    "用法: /remove <Tron地址>\n"
                    "示例: /remove TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
                )
                return
            
            address = context.args[0].strip()
            monitor = TronUSDTMonitor()
            
            if monitor.remove_monitor_address(address):
                await update.message.reply_text(f"✅ 成功删除监控地址: {address}")
            else:
                await update.message.reply_text(
                    f"❌ 删除失败\n"
                    f"可能原因：\n"
                    f"1. 地址不存在于监控列表中\n"
                    f"2. 地址格式不正确"
                )
                
        except Exception as e:
            await update.message.reply_text(f"❌ 删除地址失败: {str(e)}")
    
    async def list_addresses_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /list 命令 - 显示监控地址列表"""
        from tron_monitor import TronUSDTMonitor
        
        try:
            monitor = TronUSDTMonitor()
            addresses = monitor.get_monitor_addresses()
            
            if addresses:
                list_message = "📋 监控地址列表\n\n"
                for i, addr in enumerate(addresses, 1):
                    balance = monitor.get_address_balance(addr)
                    list_message += f"{i}. {addr}\n"
                    list_message += f"   余额: {balance:,.2f} USDT\n\n"
            else:
                list_message = "❌ 当前没有监控地址\n"
                list_message += "使用 /add <地址> 添加监控地址"
            
            await update.message.reply_text(list_message)
            
        except Exception as e:
            await update.message.reply_text(f"❌ 获取地址列表失败: {str(e)}")
    
    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /settings 命令"""
        settings_message = "⚙️ 当前设置\n\n"
        
        # 显示配置信息（隐藏敏感信息）
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '未设置')
        if bot_token != '未设置':
            bot_token = f"{bot_token[:10]}...{bot_token[-10:]}"
        
        chat_id = os.getenv('TELEGRAM_CHAT_ID', '未设置')
        node_url = os.getenv('TRON_NODE_URL', 'https://api.trongrid.io')
        usdt_contract = os.getenv('USDT_CONTRACT_ADDRESS', 'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t')
        monitor_interval = os.getenv('MONITOR_INTERVAL', '30')
        
        settings_message += f"🤖 Bot Token: {bot_token}\n"
        settings_message += f"💬 Chat ID: {chat_id}\n"
        settings_message += f"🌐 Tron节点: {node_url}\n"
        settings_message += f"📄 USDT合约: {usdt_contract[:10]}...{usdt_contract[-10:]}\n"
        settings_message += f"⏱️ 监控间隔: {monitor_interval}秒\n"
        
        await update.message.reply_text(settings_message)
    
    async def send_notification(self, message: str) -> bool:
        """发送通知消息"""
        try:
            await self.application.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML'
            )
            self.logger.info("通知消息发送成功")
            return True
            
        except BadRequest as e:
            self.logger.error(f"Telegram请求错误: {e}")
            return False
        except TelegramError as e:
            self.logger.error(f"Telegram错误: {e}")
            return False
        except Exception as e:
            self.logger.error(f"发送通知失败: {e}")
            return False
    
    async def send_transfer_notification(self, transfer_info: dict) -> bool:
        """发送转账通知"""
        from tron_monitor import TronUSDTMonitor
        
        monitor = TronUSDTMonitor()
        message = monitor.format_transfer_message(transfer_info)
        
        return await self.send_notification(message)
    
    def run(self):
        """启动机器人"""
        self.logger.info("启动Telegram机器人...")
        self.application.run_polling()
    
    async def stop(self):
        """停止机器人"""
        await self.application.stop()
        await self.application.shutdown() 