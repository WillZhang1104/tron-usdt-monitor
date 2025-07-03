#!/usr/bin/env python3
"""
Tron钱包操作模块
支持TRX和USDT转账功能
"""

import os
import time
import logging
from typing import Optional, Dict, Any
from tronpy import Tron
from tronpy.providers import HTTPProvider
from tronpy.contract import Contract
from tronpy.keys import PrivateKey
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class TronWallet:
    """Tron钱包操作类"""
    
    def __init__(self):
        self.tron = Tron(
            provider=HTTPProvider(os.getenv('TRON_NODE_URL', 'https://api.trongrid.io'))
        )
        
        # USDT合约地址
        self.usdt_contract_address = os.getenv('USDT_CONTRACT_ADDRESS', 'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t')
        self.usdt_contract = self.tron.get_contract(self.usdt_contract_address)
        
        # 设置日志
        self.logger = logging.getLogger(__name__)
        
        # 安全设置
        self.max_trx_amount = float(os.getenv('MAX_TRX_AMOUNT', '100'))  # 最大TRX转账金额
        self.max_usdt_amount = float(os.getenv('MAX_USDT_AMOUNT', '1000'))  # 最大USDT转账金额
        self.allowed_addresses = os.getenv('ALLOWED_ADDRESSES', '').split(',')  # 允许转账的地址白名单
        
        self.logger.info("Tron钱包操作模块初始化完成")
    
    def _get_private_key(self) -> Optional[PrivateKey]:
        """获取私钥（支持加密存储）"""
        try:
            # 方法1：从环境变量获取私钥
            private_key_hex = os.getenv('TRON_PRIVATE_KEY')
            if private_key_hex:
                return PrivateKey(bytes.fromhex(private_key_hex))
            
            # 方法2：从加密文件获取私钥
            encrypted_file = os.getenv('TRON_PRIVATE_KEY_FILE', 'private_key.txt.gpg')
            if os.path.exists(encrypted_file):
                import subprocess
                try:
                    # 解密私钥文件
                    result = subprocess.run(
                        ['gpg', '--decrypt', encrypted_file],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    private_key_hex = result.stdout.strip()
                    return PrivateKey(bytes.fromhex(private_key_hex))
                except subprocess.CalledProcessError as e:
                    self.logger.error(f"解密私钥文件失败: {e}")
                    return None
            
            self.logger.error("未找到私钥配置")
            return None
            
        except Exception as e:
            self.logger.error(f"获取私钥失败: {e}")
            return None
    
    def _validate_transfer(self, to_address: str, amount: float, token_type: str) -> bool:
        """验证转账参数"""
        try:
            # 验证地址格式
            if not to_address.startswith('T') or len(to_address) != 34:
                self.logger.error(f"无效的地址格式: {to_address}")
                return False
            
            # 验证金额
            if amount <= 0:
                self.logger.error(f"转账金额必须大于0: {amount}")
                return False
            
            # 检查金额限制
            if token_type == 'TRX' and amount > self.max_trx_amount:
                self.logger.error(f"TRX转账金额超过限制: {amount} > {self.max_trx_amount}")
                return False
            
            if token_type == 'USDT' and amount > self.max_usdt_amount:
                self.logger.error(f"USDT转账金额超过限制: {amount} > {self.max_usdt_amount}")
                return False
            
            # 检查白名单（如果设置了）
            if self.allowed_addresses and to_address not in self.allowed_addresses:
                self.logger.error(f"地址不在白名单中: {to_address}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"验证转账参数失败: {e}")
            return False
    
    def get_balance(self, address: str) -> Dict[str, float]:
        """获取地址余额"""
        try:
            # 获取TRX余额
            trx_balance = self.tron.get_account_balance(address)
            trx_balance_float = float(trx_balance) / 1_000_000  # TRX有6位小数
            
            # 获取USDT余额
            usdt_balance = self.usdt_contract.functions.balanceOf(address)
            usdt_balance_float = float(usdt_balance) / 1_000_000  # USDT有6位小数
            
            return {
                'TRX': trx_balance_float,
                'USDT': usdt_balance_float
            }
            
        except Exception as e:
            self.logger.error(f"获取余额失败: {e}")
            return {'TRX': 0.0, 'USDT': 0.0}
    
    def transfer_trx(self, to_address: str, amount: float) -> Dict[str, Any]:
        """转账TRX"""
        try:
            # 验证参数
            if not self._validate_transfer(to_address, amount, 'TRX'):
                return {'success': False, 'error': '参数验证失败'}
            
            # 获取私钥
            private_key = self._get_private_key()
            if not private_key:
                return {'success': False, 'error': '无法获取私钥'}
            
            # 获取发送方地址
            from_address = private_key.public_key.to_base58check_address()
            
            # 检查余额
            balance = self.get_balance(from_address)
            if balance['TRX'] < amount:
                return {'success': False, 'error': f'余额不足: {balance["TRX"]} < {amount}'}
            
            # 创建交易
            txn = self.tron.trx.transfer(
                to_address,
                int(amount * 1_000_000),  # 转换为最小单位
                private_key
            )
            
            # 等待交易确认
            result = txn.wait()
            
            if result.get('receipt', {}).get('result') == 'SUCCESS':
                self.logger.info(f"TRX转账成功: {amount} TRX -> {to_address}")
                return {
                    'success': True,
                    'txid': txn.txid,
                    'amount': amount,
                    'to_address': to_address,
                    'from_address': from_address
                }
            else:
                return {'success': False, 'error': '交易失败'}
                
        except Exception as e:
            self.logger.error(f"TRX转账失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def transfer_usdt(self, to_address: str, amount: float) -> Dict[str, Any]:
        """转账USDT"""
        try:
            # 验证参数
            if not self._validate_transfer(to_address, amount, 'USDT'):
                return {'success': False, 'error': '参数验证失败'}
            
            # 获取私钥
            private_key = self._get_private_key()
            if not private_key:
                return {'success': False, 'error': '无法获取私钥'}
            
            # 获取发送方地址
            from_address = private_key.public_key.to_base58check_address()
            
            # 检查余额
            balance = self.get_balance(from_address)
            if balance['USDT'] < amount:
                return {'success': False, 'error': f'余额不足: {balance["USDT"]} < {amount}'}
            
            # 创建USDT转账交易
            txn = self.usdt_contract.functions.transfer(
                to_address,
                int(amount * 1_000_000)  # 转换为最小单位
            ).with_owner(from_address).fee_limit(10_000_000).build().sign(private_key)
            
            # 发送交易
            result = txn.broadcast().wait()
            
            if result.get('receipt', {}).get('result') == 'SUCCESS':
                self.logger.info(f"USDT转账成功: {amount} USDT -> {to_address}")
                return {
                    'success': True,
                    'txid': txn.txid,
                    'amount': amount,
                    'to_address': to_address,
                    'from_address': from_address
                }
            else:
                return {'success': False, 'error': '交易失败'}
                
        except Exception as e:
            self.logger.error(f"USDT转账失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_transaction_info(self, txid: str) -> Dict[str, Any]:
        """获取交易信息"""
        try:
            tx_info = self.tron.get_transaction_info(txid)
            return {
                'success': True,
                'txid': txid,
                'status': tx_info.get('receipt', {}).get('result'),
                'block': tx_info.get('blockNumber'),
                'timestamp': tx_info.get('blockTimeStamp'),
                'fee': tx_info.get('fee', 0) / 1_000_000
            }
        except Exception as e:
            self.logger.error(f"获取交易信息失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def format_transfer_message(self, result: Dict[str, Any], token_type: str) -> str:
        """格式化转账结果消息"""
        if result['success']:
            message = f"✅ {token_type}转账成功\n\n"
            message += f"💰 金额: {result['amount']:,.2f} {token_type}\n"
            message += f"📤 发送方: {result['from_address'][:10]}...{result['from_address'][-10:]}\n"
            message += f"📥 接收方: {result['to_address'][:10]}...{result['to_address'][-10:]}\n"
            message += f"🔗 交易哈希: {result['txid']}\n"
            message += f"⏰ 时间: {time.strftime('%Y-%m-%d %H:%M:%S')}"
        else:
            message = f"❌ {token_type}转账失败\n\n"
            message += f"错误信息: {result['error']}"
        
        return message 