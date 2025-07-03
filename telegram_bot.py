#!/usr/bin/env python3
"""
简化Telegram机器人
只提供选择功能，不提供编辑功能
"""

import os
import logging
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from telegram.error import Forbidden, NetworkError, TimedOut
from dotenv import load_dotenv

# 导入自定义模块
from tron_monitor import TronUSDTMonitor
from wallet_operations import WalletOperations
from address_manager import AddressManager

# 加载环境变量
load_dotenv()

class TelegramBot:
    """简化Telegram机器人"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # 获取配置
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.allowed_users = os.getenv('ALLOWED_USERS', '').split(',')
        self.allowed_users = [user.strip() for user in self.allowed_users if user.strip()]
        
        if not self.bot_token:
            raise ValueError("未设置TELEGRAM_BOT_TOKEN")
        
        # 初始化组件
        self.address_manager = AddressManager()
        self.tron_monitor = TronUSDTMonitor()
        self.wallet_operations = WalletOperations()
        
        # 初始化机器人
        self.application = Application.builder().token(self.bot_token).build()
        self._setup_handlers()
        
        self.logger.info("简化Telegram机器人初始化完成")
    
    def _setup_handlers(self):
        """设置命令处理器"""
        # 基础命令
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        
        # 监控相关命令
        self.application.add_handler(CommandHandler("balance", self.balance_command))
        self.application.add_handler(CommandHandler("latest", self.latest_transaction_command))
        self.application.add_handler(CommandHandler("whitelist", self.whitelist_command))
        
        # 钱包相关命令
        self.application.add_handler(CommandHandler("wallet_balance", self.wallet_balance_command))
        self.application.add_handler(CommandHandler("transfer", self.transfer_command))
        
        # 回调查询处理器
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # 错误处理器
        self.application.add_error_handler(self.error_handler)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """开始命令"""
        if not self._is_authorized(update.effective_user.id):
            await update.message.reply_text("❌ 您没有权限使用此机器人")
            return
        
        welcome_text = """
🤖 Tron地址监控机器人

📋 可用命令：
/start - 显示此帮助信息
/help - 显示详细帮助
/status - 显示监控状态
/balance - 查询监控地址余额
/latest - 显示最新交易
/whitelist - 显示白名单地址
/wallet_balance - 查询钱包余额
/transfer - 转账到白名单地址

💡 提示：白名单地址在 .env 文件中配置
        """
        
        await update.message.reply_text(welcome_text)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """帮助命令"""
        if not self._is_authorized(update.effective_user.id):
            await update.message.reply_text("❌ 您没有权限使用此机器人")
            return
        
        help_text = """
📖 详细帮助信息

🔍 监控命令：
/balance - 查询所有监控地址的USDT余额
/latest - 显示监控地址的最新交易记录
/status - 显示监控服务状态

💰 钱包命令：
/wallet_balance - 查询钱包TRX和USDT余额
/transfer - 转账到白名单地址（支持序号、别名、地址）

📋 管理命令：
/whitelist - 显示当前白名单地址列表

⚙️ 配置说明：
白名单地址在 .env 文件中配置，格式：
WHITELIST_ADDRESSES=地址1=别名1,描述1|地址2=别名2,描述2

🔒 安全提示：
- 只有授权用户可以使用机器人
- 转账前请仔细确认地址和金额
- 私钥已加密存储，确保安全
        """
        
        await update.message.reply_text(help_text)
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """状态命令"""
        if not self._is_authorized(update.effective_user.id):
            await update.message.reply_text("❌ 您没有权限使用此机器人")
            return
        
        try:
            # 获取监控地址数量
            monitor_addresses = os.getenv('MONITOR_ADDRESSES', '').split(',')
            monitor_addresses = [addr.strip() for addr in monitor_addresses if addr.strip()]
            
            # 获取白名单地址数量
            whitelist_addresses = self.address_manager.get_whitelist_addresses()
            
            status_text = f"""
📊 监控状态

📡 监控地址：{len(monitor_addresses)} 个
✅ 白名单地址：{len(whitelist_addresses)} 个
🕐 当前时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💡 提示：使用 /balance 查看余额，/latest 查看最新交易
            """
            
            await update.message.reply_text(status_text)
            
        except Exception as e:
            self.logger.error(f"获取状态失败: {e}")
            await update.message.reply_text("❌ 获取状态失败")
    
    async def balance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """余额查询命令"""
        if not self._is_authorized(update.effective_user.id):
            await update.message.reply_text("❌ 您没有权限使用此机器人")
            return
        
        try:
            await update.message.reply_text("🔄 正在查询余额，请稍候...")
            
            # 获取监控地址
            monitor_addresses = os.getenv('MONITOR_ADDRESSES', '').split(',')
            monitor_addresses = [addr.strip() for addr in monitor_addresses if addr.strip()]
            
            if not monitor_addresses:
                await update.message.reply_text("❌ 未配置监控地址")
                return
            
            balance_text = "💰 监控地址余额\n\n"
            
            for address in monitor_addresses:
                try:
                    balance = self.tron_monitor.get_address_balance(address)
                    balance_text += f"📍 {address[:10]}...{address[-10:]}\n"
                    balance_text += f"   💵 USDT: {balance:,.2f}\n\n"
                except Exception as e:
                    self.logger.error(f"查询地址 {address} 余额失败: {e}")
                    balance_text += f"📍 {address[:10]}...{address[-10:]}\n"
                    balance_text += f"   ❌ 查询失败\n\n"
            
            await update.message.reply_text(balance_text)
            
        except Exception as e:
            self.logger.error(f"余额查询失败: {e}")
            await update.message.reply_text("❌ 余额查询失败")
    
    async def latest_transaction_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """最新交易命令"""
        if not self._is_authorized(update.effective_user.id):
            await update.message.reply_text("❌ 您没有权限使用此机器人")
            return
        
        try:
            await update.message.reply_text("🔄 正在查询最新交易，请稍候...")
            
            # 获取监控地址
            monitor_addresses = os.getenv('MONITOR_ADDRESSES', '').split(',')
            monitor_addresses = [addr.strip() for addr in monitor_addresses if addr.strip()]
            
            if not monitor_addresses:
                await update.message.reply_text("❌ 未配置监控地址")
                return
            
            latest_text = "📊 最新交易记录\n\n"
            
            for address in monitor_addresses:
                try:
                    latest_tx = self.tron_monitor.get_latest_transfer(address)
                    if latest_tx:
                        latest_text += f"📍 {address[:10]}...{address[-10:]}\n"
                        latest_text += f"   🕐 时间: {latest_tx['timestamp']}\n"
                        latest_text += f"   💰 金额: {latest_tx['amount']} USDT\n"
                        latest_text += f"   📋 类型: {latest_tx['type']}\n"
                        latest_text += f"   🔗 交易ID: {latest_tx['txid'][:20]}...\n\n"
                    else:
                        latest_text += f"📍 {address[:10]}...{address[-10:]}\n"
                        latest_text += f"   📭 暂无交易记录\n\n"
                except Exception as e:
                    self.logger.error(f"查询地址 {address} 最新交易失败: {e}")
                    latest_text += f"📍 {address[:10]}...{address[-10:]}\n"
                    latest_text += f"   ❌ 查询失败\n\n"
            
            await update.message.reply_text(latest_text)
            
        except Exception as e:
            self.logger.error(f"最新交易查询失败: {e}")
            await update.message.reply_text("❌ 最新交易查询失败")
    
    async def whitelist_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """白名单命令"""
        if not self._is_authorized(update.effective_user.id):
            await update.message.reply_text("❌ 您没有权限使用此机器人")
            return
        
        try:
            whitelist_text = self.address_manager.format_whitelist()
            await update.message.reply_text(whitelist_text)
            
        except Exception as e:
            self.logger.error(f"显示白名单失败: {e}")
            await update.message.reply_text("❌ 显示白名单失败")
    
    async def wallet_balance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """钱包余额命令"""
        if not self._is_authorized(update.effective_user.id):
            await update.message.reply_text("❌ 您没有权限使用此机器人")
            return
        
        try:
            await update.message.reply_text("🔄 正在查询钱包余额，请稍候...")
            
            # 查询TRX余额
            trx_balance = self.wallet_operations.get_trx_balance()
            
            # 查询USDT余额
            usdt_balance = self.wallet_operations.get_usdt_balance()
            
            balance_text = f"""
💰 钱包余额

🪙 TRX: {trx_balance:,.6f}
💵 USDT: {usdt_balance:,.2f}

💡 提示：使用 /transfer 进行转账
            """
            
            await update.message.reply_text(balance_text)
            
        except Exception as e:
            self.logger.error(f"钱包余额查询失败: {e}")
            await update.message.reply_text("❌ 钱包余额查询失败")
    
    async def transfer_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """转账命令"""
        if not self._is_authorized(update.effective_user.id):
            await update.message.reply_text("❌ 您没有权限使用此机器人")
            return
        
        try:
            # 检查是否有参数
            if not context.args:
                # 显示地址选择界面
                address_list = self.address_manager.format_address_list()
                await update.message.reply_text(
                    f"{address_list}\n"
                    "💡 使用方法：\n"
                    "/transfer <序号/别名/地址> <金额> <备注(可选)>\n\n"
                    "示例：\n"
                    "/transfer 1 100 测试转账\n"
                    "/transfer 钱包1 50\n"
                    "/transfer TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t 25"
                )
                return
            
            # 解析参数
            if len(context.args) < 2:
                await update.message.reply_text("❌ 参数不足\n\n使用方法：/transfer <地址> <金额> [备注]")
                return
            
            address_input = context.args[0]
            amount_str = context.args[1]
            remark = " ".join(context.args[2:]) if len(context.args) > 2 else ""
            
            # 验证金额
            try:
                amount = float(amount_str)
                if amount <= 0:
                    await update.message.reply_text("❌ 金额必须大于0")
                    return
            except ValueError:
                await update.message.reply_text("❌ 无效的金额格式")
                return
            
            # 获取目标地址
            target_address = self.address_manager.get_address_for_transfer(address_input)
            if not target_address:
                await update.message.reply_text("❌ 未找到目标地址\n\n请检查序号、别名或地址是否正确")
                return
            
            # 获取地址信息
            addr_info = self.address_manager.get_address_info(target_address)
            alias = addr_info['alias'] if addr_info else "未知"
            
            # 确认转账
            confirm_text = f"""
⚠️ 转账确认

📤 目标地址: {alias}
📍 地址: {target_address}
💰 金额: {amount} USDT
📝 备注: {remark if remark else "无"}

🔒 请确认转账信息是否正确
            """
            
            # 创建确认按钮
            keyboard = [
                [
                    InlineKeyboardButton("✅ 确认转账", callback_data=f"confirm_transfer:{target_address}:{amount}:{remark}"),
                    InlineKeyboardButton("❌ 取消", callback_data="cancel_transfer")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(confirm_text, reply_markup=reply_markup)
            
        except Exception as e:
            self.logger.error(f"转账命令处理失败: {e}")
            await update.message.reply_text("❌ 转账命令处理失败")
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """按钮回调处理"""
        if not self._is_authorized(update.effective_user.id):
            await update.callback_query.answer("❌ 您没有权限使用此机器人")
            return
        
        query = update.callback_query
        await query.answer()
        
        try:
            if query.data == "cancel_transfer":
                await query.edit_message_text("❌ 转账已取消")
                return
            
            if query.data.startswith("confirm_transfer:"):
                # 解析转账参数
                parts = query.data.split(":")
                if len(parts) >= 3:
                    target_address = parts[1]
                    amount = float(parts[2])
                    remark = parts[3] if len(parts) > 3 else ""
                    
                    await query.edit_message_text("🔄 正在执行转账，请稍候...")
                    
                    try:
                        # 执行转账
                        txid = self.wallet_operations.transfer_usdt(target_address, amount, remark)
                        
                        # 获取地址信息
                        addr_info = self.address_manager.get_address_info(target_address)
                        alias = addr_info['alias'] if addr_info else "未知"
                        
                        success_text = f"""
✅ 转账成功

📤 目标地址: {alias}
📍 地址: {target_address}
💰 金额: {amount} USDT
📝 备注: {remark if remark else "无"}
🔗 交易ID: {txid}

💡 提示：交易可能需要几分钟确认
                        """
                        
                        await query.edit_message_text(success_text)
                        
                    except Exception as e:
                        self.logger.error(f"转账执行失败: {e}")
                        await query.edit_message_text(f"❌ 转账失败\n\n错误信息: {str(e)}")
            
        except Exception as e:
            self.logger.error(f"按钮回调处理失败: {e}")
            await query.edit_message_text("❌ 操作失败")
    
    def _is_authorized(self, user_id: int) -> bool:
        """检查用户是否授权"""
        if not self.allowed_users:
            return True  # 如果没有设置允许用户，则允许所有用户
        
        return str(user_id) in self.allowed_users
    
    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE):
        """错误处理器"""
        self.logger.error(f"机器人错误: {context.error}")
        
        if isinstance(context.error, Forbidden):
            self.logger.error("机器人token无效或已被删除")
        elif isinstance(context.error, NetworkError):
            self.logger.error("网络错误")
        elif isinstance(context.error, TimedOut):
            self.logger.error("请求超时")
    
    def run(self):
        """运行机器人"""
        try:
            self.logger.info("启动Telegram机器人...")
            self.application.run_polling()
        except Exception as e:
            self.logger.error(f"机器人运行失败: {e}")
            raise

if __name__ == "__main__":
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        bot = TelegramBot()
        bot.run()
    except Exception as e:
        logging.error(f"机器人启动失败: {e}") 