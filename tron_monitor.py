import os
import time
import logging
import json
import requests
from typing import List, Dict, Optional
from tronpy import Tron
from tronpy.providers import HTTPProvider
from tronpy.contract import Contract
from dotenv import load_dotenv
from address_manager import AddressManager

# 加载环境变量
load_dotenv()

class TronUSDTMonitor:
    """Tron链USDT监控器"""
    
    def __init__(self):
        tron_api_key = os.getenv('TRON_API_KEY')
        self.tron = Tron(
            provider=HTTPProvider(
                os.getenv('TRON_NODE_URL', 'https://api.trongrid.io'),
                api_key=tron_api_key
            )
        )
        
        # USDT合约地址 (Tron主网)
        self.usdt_contract_address = os.getenv('USDT_CONTRACT_ADDRESS', 'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t')
        self.usdt_contract = self.tron.get_contract(self.usdt_contract_address)
        
        # 初始化地址管理器
        self.address_manager = AddressManager()
        
        # 获取白名单地址作为监控地址
        self.monitor_addresses = self.address_manager.get_whitelist_addresses()
        
        # 记录已处理的交易
        self.processed_transactions = set()
        
        # 余额缓存
        self.balance_cache = {}
        self.cache_timeout = 30  # 30秒缓存
        
        # 设置日志
        logging.basicConfig(
            level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        self.logger.info(f"初始化Tron监控器，监控地址: {self.monitor_addresses}")
    
    def _make_api_request(self, url: str, params: dict = None, max_retries: int = 3) -> Optional[dict]:
        """发送API请求，带重试机制"""
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'TronUSDTMonitor/1.0'
        }
        
        for attempt in range(max_retries):
            try:
                response = requests.get(url, params=params, headers=headers, timeout=10)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"API请求失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # 指数退避
                else:
                    self.logger.error(f"API请求最终失败: {e}")
                    return None
    
    def get_usdt_transfers(self, address: str, limit: int = 50) -> List[Dict]:
        """获取指定地址的USDT转账记录"""
        try:
            transfers = []
            
            # 使用TronGrid API获取TRC20转账记录
            api_url = "https://api.trongrid.io/v1/accounts/{}/transactions/trc20".format(address)
            params = {
                'limit': limit,
                'contract_address': self.usdt_contract_address,
                'only_to': 'true'  # 只获取转入交易
            }
            
            data = self._make_api_request(api_url, params)
            if not data or 'data' not in data:
                self.logger.warning(f"无法获取地址 {address} 的交易数据")
                return []
            
            for tx in data['data']:
                if tx.get('to') == address:
                    transfer_info = {
                        'txid': tx['transaction_id'],
                        'from': tx.get('from'),
                        'to': tx.get('to'),
                        'amount': float(tx.get('value', 0)) / 1_000_000,  # USDT有6位小数
                        'timestamp': tx.get('block_timestamp', 0),
                        'block': tx.get('block', 0)
                    }
                    transfers.append(transfer_info)
            
            return transfers
            
        except Exception as e:
            self.logger.error(f"获取USDT转账记录失败: {e}")
            return []
    
    def get_latest_transfer(self, address: str) -> Optional[Dict]:
        """获取指定地址的最新一笔转入交易"""
        try:
            transfers = self.get_usdt_transfers(address, limit=1)
            if transfers:
                return transfers[0]
            return None
        except Exception as e:
            self.logger.error(f"获取最新交易失败: {e}")
            return None
    
    def check_new_transfers(self) -> List[Dict]:
        """检查新的USDT转入交易"""
        new_transfers = []
        
        for address in self.monitor_addresses:
            try:
                transfers = self.get_usdt_transfers(address, limit=20)
                
                for transfer in transfers:
                    tx_id = transfer['txid']
                    
                    if tx_id not in self.processed_transactions:
                        self.processed_transactions.add(tx_id)
                        new_transfers.append(transfer)
                        self.logger.info(f"发现新交易: {tx_id}, 金额: {transfer['amount']} USDT")
                
            except Exception as e:
                self.logger.error(f"检查地址 {address} 失败: {e}")
        
        return new_transfers
    
    def format_transfer_message(self, transfer: Dict) -> str:
        """格式化转账消息"""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(transfer['timestamp'] / 1000))
        
        message = f"🔔 新的USDT入账通知\n\n"
        message += f"💰 金额: {transfer['amount']:,.2f} USDT\n"
        message += f"📤 发送方: {transfer['from']}\n"
        message += f"📥 接收方: {transfer['to']}\n"
        message += f"🕐 时间: {timestamp}\n"
        message += f"🔗 交易哈希: {transfer['txid']}\n"
        message += f"📊 区块: {transfer['block']}"
        
        return message
    
    def get_address_balance(self, address: str) -> float:
        """获取地址的USDT余额"""
        try:
            # 检查缓存
            current_time = time.time()
            if address in self.balance_cache:
                cached_balance, cache_time = self.balance_cache[address]
                if current_time - cache_time < self.cache_timeout:
                    return cached_balance
            
            # 使用合约方法获取余额
            balance = self.usdt_contract.functions.balanceOf(address)
            balance_float = float(balance) / 1_000_000  # USDT有6位小数
            
            # 更新缓存
            self.balance_cache[address] = (balance_float, current_time)
            
            return balance_float
            
        except Exception as e:
            self.logger.error(f"获取余额失败: {e}")
            # 如果合约调用失败，尝试使用API
            try:
                api_url = f"https://api.trongrid.io/v1/accounts/{address}/tokens/trc20"
                params = {'contract_address': self.usdt_contract_address}
                
                data = self._make_api_request(api_url, params)
                if data and 'data' in data and data['data']:
                    balance = float(data['data'][0].get('balance', 0)) / 1_000_000
                    self.balance_cache[address] = (balance, current_time)
                    return balance
            except Exception as api_e:
                self.logger.error(f"API获取余额也失败: {api_e}")
            
            return 0.0
    
    def refresh_monitor_addresses(self):
        """刷新监控地址列表（从地址管理器重新获取）"""
        self.monitor_addresses = self.address_manager.get_whitelist_addresses()
        self.logger.info(f"监控地址已刷新: {self.monitor_addresses}")
    
    def get_monitor_addresses(self) -> List[str]:
        """获取监控地址列表"""
        return self.monitor_addresses.copy() 