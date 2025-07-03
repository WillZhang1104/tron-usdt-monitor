#!/usr/bin/env python3
"""
Tron链USDT监控Telegram机器人主程序
"""

import os
import time
import asyncio
import signal
import sys
import logging
from typing import Optional
from dotenv import load_dotenv

# 导入自定义模块
from tron_monitor import TronUSDTMonitor
from telegram_bot import TelegramBot

# 加载环境变量
load_dotenv()

class USDTMonitorBot:
    """USDT监控机器人主类"""
    
    def __init__(self):
        # 设置日志
        logging.basicConfig(
            level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('monitor.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # 初始化组件
        self.monitor = TronUSDTMonitor()
        self.telegram_bot = TelegramBot()
        
        # 监控间隔（秒）
        self.monitor_interval = int(os.getenv('MONITOR_INTERVAL', '30'))
        
        # 运行标志
        self.running = False
        
        self.logger.info("USDT监控机器人初始化完成")
    
    async def check_and_notify(self):
        """检查新交易并发送通知"""
        try:
            # 检查新交易
            new_transfers = self.monitor.check_new_transfers()
            
            if new_transfers:
                self.logger.info(f"发现 {len(new_transfers)} 笔新交易")
                
                # 发送通知
                for transfer in new_transfers:
                    success = await self.telegram_bot.send_transfer_notification(transfer)
                    if success:
                        self.logger.info(f"成功发送交易通知: {transfer['txid']}")
                    else:
                        self.logger.error(f"发送交易通知失败: {transfer['txid']}")
                    
                    # 避免消息发送过快
                    await asyncio.sleep(1)
            else:
                self.logger.debug("未发现新交易")
                
        except Exception as e:
            self.logger.error(f"检查交易时发生错误: {e}")
    
    async def monitor_loop(self):
        """监控循环"""
        self.logger.info(f"开始监控循环，间隔: {self.monitor_interval}秒")
        
        while self.running:
            try:
                await self.check_and_notify()
                await asyncio.sleep(self.monitor_interval)
                
            except asyncio.CancelledError:
                self.logger.info("监控循环被取消")
                break
            except Exception as e:
                self.logger.error(f"监控循环发生错误: {e}")
                await asyncio.sleep(10)  # 错误后等待10秒再继续
    
    async def start(self):
        """启动机器人"""
        self.running = True
        self.logger.info("启动USDT监控机器人...")
        
        # 发送启动通知
        start_message = (
            "🚀 USDT监控机器人已启动\n\n"
            f"📍 监控地址数量: {len(self.monitor.monitor_addresses)}\n"
            f"⏱️ 监控间隔: {self.monitor_interval}秒\n"
            f"🌐 Tron节点: {os.getenv('TRON_NODE_URL', 'https://api.trongrid.io')}\n\n"
            "🔔 机器人将自动监控USDT入账并发送通知"
        )
        
        await self.telegram_bot.send_notification(start_message)
        
        # 启动监控循环
        monitor_task = asyncio.create_task(self.monitor_loop())
        
        try:
            # 启动Telegram机器人
            await self.telegram_bot.application.initialize()
            await self.telegram_bot.application.start()
            await self.telegram_bot.application.updater.start_polling()
            
            self.logger.info("Telegram机器人启动成功")
            
            # 等待监控任务
            await monitor_task
            
        except Exception as e:
            self.logger.error(f"启动失败: {e}")
            raise
        finally:
            await self.stop()
    
    async def stop(self):
        """停止机器人"""
        self.running = False
        self.logger.info("正在停止USDT监控机器人...")
        
        # 发送停止通知
        stop_message = "🛑 USDT监控机器人已停止"
        try:
            await self.telegram_bot.send_notification(stop_message)
        except:
            pass
        
        # 停止Telegram机器人
        try:
            await self.telegram_bot.stop()
        except:
            pass
        
        self.logger.info("USDT监控机器人已停止")

def signal_handler(signum, frame):
    """信号处理器"""
    print(f"\n收到信号 {signum}，正在停止...")
    sys.exit(0)

async def main():
    """主函数"""
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 检查环境变量
    required_vars = ['TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHAT_ID', 'MONITOR_ADDRESSES']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ 缺少必要的环境变量: {', '.join(missing_vars)}")
        print("请检查 .env 文件配置")
        return
    
    try:
        # 创建并启动机器人
        bot = USDTMonitorBot()
        await bot.start()
        
    except KeyboardInterrupt:
        print("\n用户中断，正在停止...")
    except Exception as e:
        print(f"程序运行出错: {e}")
        logging.error(f"程序运行出错: {e}")

if __name__ == "__main__":
    # 运行主程序
    asyncio.run(main()) 