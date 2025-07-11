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
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from telegram.error import Forbidden, NetworkError, TimedOut
from dotenv import load_dotenv

# 导入自定义模块
from tron_monitor import TronUSDTMonitor
from wallet_operations import TronWallet
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
        self.wallet_operations = TronWallet()
        
        # 初始化机器人
        self.application = Application.builder().token(self.bot_token).build()
        self._setup_handlers()
        
        self.logger.info("简化Telegram机器人初始化完成")
    
    def _setup_handlers(self):
        """
        设置命令处理器（BotCommand注册交由on_startup处理）
        """
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
            monitor_addresses = os.getenv('MONITOR_ADDRESSES', '').split(',')
            monitor_addresses = [addr.strip() for addr in monitor_addresses if addr.strip()]
            if not monitor_addresses:
                await update.message.reply_text("❌ 未配置监控地址")
                return
            found = False
            for address in monitor_addresses:
                try:
                    latest_tx = self.tron_monitor.get_latest_transfer(address)
                    if latest_tx:
                        found = True
                        # 格式化时间戳
                        ts = latest_tx.get('timestamp', 0)
                        if isinstance(ts, (int, float)) and ts > 1e10:
                            ts = int(ts / 1000)
                        time_str = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S') if ts else '未知'
                        msg = f"📍 {address[:10]}...{address[-10:]}\n"
                        msg += f"🕐 时间: {time_str}\n"
                        msg += f"💰 金额: {latest_tx['amount']} USDT\n"
                        msg += f"🔗 交易哈希: {latest_tx['txid'][:20]}..."
                        # 构造按钮
                        keyboard = [[InlineKeyboardButton("在区块链浏览器查看", url=f"https://tronscan.org/#/transaction/{latest_tx['txid']}")]]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        await update.message.reply_text(msg, reply_markup=reply_markup)
                except Exception as e:
                    self.logger.error(f"查询地址 {address} 最新交易失败: {e}")
            if not found:
                await update.message.reply_text("📭 所有监控地址暂无交易记录")
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
            
            # 获取私钥
            private_key = self.wallet_operations._get_private_key()
            if not private_key:
                await update.message.reply_text("❌ 未配置钱包私钥")
                return
            
            # 获取钱包地址
            wallet_address = private_key.public_key.to_base58check_address()
            
            # 查询余额
            balance = self.wallet_operations.get_balance(wallet_address)
            trx_balance = balance['TRX']
            usdt_balance = balance['USDT']
            
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
        """转账命令，支持TRX和USDT，按钮只传递transfer_confirm，参数存user_data"""
        if not self._is_authorized(update.effective_user.id):
            await update.message.reply_text("❌ 您没有权限使用此机器人")
            return
        try:
            # 没有参数时，弹出币种选择按钮
            if not context.args:
                keyboard = [
                    [InlineKeyboardButton("USDT", callback_data="choose_token:USDT"),
                     InlineKeyboardButton("TRX", callback_data="choose_token:TRX")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(
                    "请选择转账币种：",
                    reply_markup=reply_markup
                )
                return
            # 参数 >=2，支持/transfer <目标> <金额> <币种> <备注>
            address_input = context.args[0]
            amount_str = context.args[1]
            token_type = None
            remark = ""
            if len(context.args) >= 3 and context.args[2].upper() in ("TRX", "USDT"):
                token_type = context.args[2].upper()
                remark = " ".join(context.args[3:]) if len(context.args) > 3 else ""
            else:
                remark = " ".join(context.args[2:]) if len(context.args) > 2 else ""
                token_type = context.user_data.get("transfer_token")
            if token_type not in ("TRX", "USDT"):
                await update.message.reply_text("❌ 未指定币种，请输入/transfer后选择币种或在命令中加上TRX/USDT")
                return
            try:
                amount = float(amount_str)
                if amount <= 0:
                    await update.message.reply_text("❌ 金额必须大于0")
                    return
            except ValueError:
                await update.message.reply_text("❌ 无效的金额格式")
                return
            target_address = self.address_manager.get_address_for_transfer(address_input)
            if not target_address:
                await update.message.reply_text("❌ 未找到目标地址\n\n请检查序号、别名或地址是否正确")
                return
            addr_info = self.address_manager.get_address_info(target_address)
            alias = addr_info['alias'] if addr_info else "未知"
            # 存储转账参数到user_data
            context.user_data["transfer_params"] = {
                "target_address": target_address,
                "amount": amount,
                "token_type": token_type,
                "remark": remark
            }
            confirm_text = f"""
⚠️ 转账确认

📤 目标地址: {alias}
📍 地址: {target_address}
💰 金额: {amount} {token_type}
📝 备注: {remark if remark else "无"}

🔒 请确认转账信息是否正确
            """
            keyboard = [
                [InlineKeyboardButton("✅ 确认转账", callback_data="transfer_confirm"),
                 InlineKeyboardButton("❌ 取消", callback_data="cancel_transfer")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(confirm_text, reply_markup=reply_markup)
        except Exception as e:
            self.logger.error(f"转账命令处理失败: {e}")
            await update.message.reply_text("❌ 转账命令处理失败")
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """按钮回调处理，支持币种选择和转账确认，参数用user_data"""
        if not self._is_authorized(update.effective_user.id):
            await update.callback_query.answer("❌ 您没有权限使用此机器人")
            return
        query = update.callback_query
        await query.answer()
        try:
            if query.data == "cancel_transfer":
                await query.edit_message_text("❌ 转账已取消")
                return
            if query.data.startswith("choose_token:"):
                token_type = query.data.split(":")[1]
                context.user_data["transfer_token"] = token_type
                address_list = self.address_manager.format_address_list()
                await query.edit_message_text(
                    f"已选择币种：{token_type}\n\n{address_list}\n\n"
                    "请输入转账命令：\n/transfer <序号/别名/地址> <金额> <备注(可选)>\n"
                    "如：/transfer 1 10 测试"
                )
                return
            if query.data == "transfer_confirm":
                params = context.user_data.get("transfer_params")
                if not params:
                    await query.edit_message_text("❌ 转账参数丢失，请重新发起转账")
                    return
                target_address = params["target_address"]
                amount = params["amount"]
                token_type = params["token_type"]
                remark = params["remark"]
                await query.edit_message_text("🔄 正在执行转账，请稍候...")
                try:
                    if token_type == "TRX":
                        result = self.wallet_operations.transfer_trx(target_address, amount)
                    else:
                        result = self.wallet_operations.transfer_usdt(target_address, amount)
                    
                    # 获取交易哈希，无论成功与否
                    txid = result.get('txid')
                    if not txid:
                        raise Exception("未获取到交易哈希")
                    
                    addr_info = self.address_manager.get_address_info(target_address)
                    alias = addr_info['alias'] if addr_info else "未知"
                    
                    # 生成区块链浏览器链接
                    explorer_url = f"https://tronscan.org/#/transaction/{txid}"
                    
                    success_text = f"""
📤 转账已提交

📤 目标地址: {alias}
📍 地址: {target_address}
💰 金额: {amount} {token_type}
📝 备注: {remark if remark else "无"}
🔗 交易哈希: {txid}

💡 点击下方按钮查看交易状态
                    """
                    
                    # 创建查看按钮
                    keyboard = [
                        [InlineKeyboardButton("🌐 在区块链浏览器查看", url=explorer_url)]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    await query.edit_message_text(success_text, reply_markup=reply_markup)
                    
                except Exception as e:
                    self.logger.error(f"转账执行失败: {e}")
                    await query.edit_message_text(f"❌ 转账提交失败\n\n错误信息: {str(e)}")
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
    
    async def send_startup_info(self):
        msg = """
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
        try:
            await self.application.bot.send_message(chat_id=8171033557, text=msg)
        except Exception as e:
            self.logger.error(f"推送启动信息失败: {e}")

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