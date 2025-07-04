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
from tronpy.keys import PrivateKey, is_base58check_address
from dotenv import load_dotenv
from address_manager import AddressManager

# 加载环境变量
load_dotenv()

class TronWallet:
    """Tron钱包操作类"""
    
    def __init__(self):
        # 设置日志
        self.logger = logging.getLogger(__name__)
        tron_api_key = os.getenv('TRON_API_KEY')
        self.tron = Tron(
            provider=HTTPProvider(
                os.getenv('TRON_NODE_URL', 'https://api.trongrid.io'),
                api_key=tron_api_key
            )
        )
        # 获取私钥
        self.private_key = self._get_private_key()
        if not self.private_key:
            self.logger.error("无法初始化私钥")
            raise ValueError("无法初始化私钥")
        # USDT合约地址
        self.usdt_contract_address = os.getenv('USDT_CONTRACT_ADDRESS', 'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t')
        self.usdt_contract = self.tron.get_contract(self.usdt_contract_address)
        # 安全设置
        self.max_trx_amount = float(os.getenv('MAX_TRX_AMOUNT', '100'))
        self.max_usdt_amount = float(os.getenv('MAX_USDT_AMOUNT', '1000'))
        # 自动同步白名单
        self.address_manager = AddressManager()
        self.allowed_addresses = [addr.strip() for addr in self.address_manager.get_whitelist_addresses()]
        self.logger.info(f"Tron钱包操作模块初始化完成，自动同步白名单: {self.allowed_addresses}")
    
    def _make_api_request(self, url: str, params: dict = None) -> Optional[dict]:
        """发送API请求"""
        try:
            import requests
            headers = {
                'Accept': 'application/json',
                'User-Agent': 'TronWallet/1.0'
            }
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"API请求失败: {e}")
            return None
    
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
                    gpg_passphrase = os.getenv('GPG_PASSPHRASE')
                    result = subprocess.run(
                        [
                            'gpg', '--batch', '--yes',
                            '--pinentry-mode', 'loopback',
                            f'--passphrase={gpg_passphrase}',
                            '--decrypt', encrypted_file
                        ],
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
            if not isinstance(to_address, str) or not to_address.strip() or not is_base58check_address(to_address.strip()):
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
            if self.allowed_addresses and to_address.strip() not in self.allowed_addresses:
                self.logger.error(f"地址不在白名单中: {to_address}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"验证转账参数失败: {e}")
            return False
    
    def get_balance(self, address: str) -> Dict[str, float]:
        """获取地址余额"""
        try:
            # 获取TRX余额（添加重试机制）
            trx_balance_float = 0.0
            for attempt in range(3):
                try:
                    trx_balance = self.tron.get_account_balance(address)
                    # 调试：显示原始余额值和不同精度转换
                    self.logger.info(f"TRX原始余额: {trx_balance}")
                    
                    # 测试不同的精度转换
                    balance_raw = float(trx_balance)
                    balance_6 = balance_raw / 1_000_000
                    balance_9 = balance_raw / 1_000_000_000
                    balance_12 = balance_raw / 1_000_000_000_000
                    
                    self.logger.info(f"不同精度转换结果:")
                    self.logger.info(f"  原始值: {balance_raw}")
                    self.logger.info(f"  除以1,000,000: {balance_6}")
                    self.logger.info(f"  除以1,000,000,000: {balance_9}")
                    self.logger.info(f"  除以1,000,000,000,000: {balance_12}")
                    
                    # 根据你的反馈，原始值已经是TRX单位，不需要转换
                    # 直接使用原始值作为TRX余额
                    trx_balance_float = balance_raw
                    self.logger.info(f"使用原始值作为TRX余额: {trx_balance_float}")
                    break
                except Exception as e:
                    self.logger.warning(f"TRX余额查询失败 (尝试 {attempt + 1}/3): {e}")
                    if attempt < 2:
                        import time
                        time.sleep(1)
                    else:
                        # 最后一次尝试失败，使用API直接查询
                        try:
                            api_url = f"https://api.trongrid.io/v1/accounts/{address}"
                            data = self._make_api_request(api_url)
                            if data and 'data' in data and data['data']:
                                raw_balance = data['data'][0].get('balance', 0)
                                self.logger.info(f"API TRX原始余额: {raw_balance}")
                                trx_balance_float = float(raw_balance)  # 直接使用原始值
                                self.logger.info(f"API获取TRX余额成功: {trx_balance_float}")
                        except Exception as api_e:
                            self.logger.error(f"API获取TRX余额也失败: {api_e}")
            
            # 获取USDT余额
            usdt_balance_float = 0.0
            try:
                usdt_balance = self.usdt_contract.functions.balanceOf(address)
                usdt_balance_float = float(usdt_balance) / 1_000_000  # USDT有6位小数
                self.logger.info(f"USDT余额查询成功: {usdt_balance_float}")
            except Exception as e:
                self.logger.error(f"USDT余额查询失败: {e}")
                # 备用API查询
                try:
                    api_url = f"https://api.trongrid.io/v1/accounts/{address}/tokens/trc20"
                    params = {'contract_address': self.usdt_contract_address}
                    data = self._make_api_request(api_url, params)
                    if data and 'data' in data and data['data']:
                        usdt_balance_float = float(data['data'][0].get('balance', 0)) / 1_000_000
                        self.logger.info(f"API获取USDT余额成功: {usdt_balance_float}")
                except Exception as api_e:
                    self.logger.error(f"API获取USDT余额也失败: {api_e}")
            
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
            self.logger.info(f"transfer_trx: to_address={repr(to_address)}, type={type(to_address)}, amount={amount}, type={type(amount)}")
            to_address = to_address.strip()
            if not isinstance(to_address, str) or not to_address or not is_base58check_address(to_address):
                self.logger.error(f"transfer_trx: 非法TRON主网地址: {repr(to_address)}")
                return {'success': False, 'error': f'非法TRON主网地址: {repr(to_address)}'}
            if not isinstance(amount, (int, float)) or amount <= 0:
                self.logger.error(f"transfer_trx: 非法金额: {amount}")
                return {'success': False, 'error': f'非法金额: {amount}'}
            if not self._validate_transfer(to_address, amount, 'TRX'):
                return {'success': False, 'error': '参数验证失败'}
            from_address = self.private_key.public_key.to_base58check_address()
            balance = self.get_balance(from_address)
            if balance['TRX'] < amount:
                return {'success': False, 'error': f'余额不足: {balance["TRX"]} < {amount}'}
            txn = self.tron.trx.transfer(
                from_address,
                to_address,
                int(amount * 1_000_000)
            )
            signed_txn = txn.build().sign(self.private_key)
            result = signed_txn.broadcast()
            txid = getattr(signed_txn, 'txid', None)
            self.logger.info(f"TRX转账txid: {txid}")
            self.logger.info(f"TRX转账raw_data: {getattr(signed_txn, 'raw_data', None)}")
            self.logger.info(f"TRX转账result: {result}")
            # 主动查询链上状态
            import time
            tx_info = None
            for _ in range(20):
                tx_info = self.tron.get_transaction_info(txid)
                if tx_info and 'receipt' in tx_info:
                    break
                time.sleep(1)
            self.logger.info(f"TRX转账链上tx_info: {tx_info}")
            if tx_info and tx_info.get('receipt', {}).get('result') == 'SUCCESS':
                self.logger.info(f"TRX转账成功: {amount} TRX -> {to_address}")
                return {
                    'success': True,
                    'txid': txid,
                    'amount': amount,
                    'to_address': to_address,
                    'from_address': from_address
                }
            elif tx_info and 'receipt' in tx_info:
                error_msg = tx_info.get('receipt', {}).get('result')
                self.logger.error(f"TRX转账链上失败: {error_msg}")
                return {'success': False, 'error': f'链上执行失败: {error_msg}'}
            else:
                self.logger.error(f"TRX转账链上确认超时或状态未知: {tx_info}")
                return {'success': False, 'error': '链上确认超时或状态未知，请稍后在区块浏览器查询'}
        except Exception as e:
            self.logger.error(f"TRX转账失败: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}
    
    def transfer_usdt(self, to_address: str, amount: float) -> Dict[str, Any]:
        """转账USDT"""
        try:
            self.logger.info(f"transfer_usdt: to_address={repr(to_address)}, type={type(to_address)}, amount={amount}, type={type(amount)}")
            to_address = to_address.strip()
            if not self._validate_transfer(to_address, amount, 'USDT'):
                return {'success': False, 'error': '参数验证失败'}
            from_address = self.private_key.public_key.to_base58check_address()
            balance = self.get_balance(from_address)
            if balance['USDT'] < amount:
                return {'success': False, 'error': f'余额不足: {balance["USDT"]} < {amount}'}
            resource = self.tron.get_account_resource(from_address)
            energy_limit = resource.get('EnergyLimit', 0)
            energy_used = resource.get('EnergyUsed', 0)
            available_energy = energy_limit - energy_used
            self.logger.info(f'USDT转账可用能量: {available_energy}')
            energy_needed = 50000
            if available_energy < energy_needed:
                self.logger.error(f"能源不足: {available_energy} < {energy_needed}")
                return {'success': False, 'error': f'能源不足: {available_energy} < {energy_needed}'}
            txn = self.usdt_contract.functions.transfer(
                to_address,
                int(amount * 1_000_000)
            ).with_owner(from_address).fee_limit(20_000_000).build().sign(self.private_key)
            result = txn.broadcast()
            txid = getattr(txn, 'txid', None)
            self.logger.info(f"USDT转账txid: {txid}")
            self.logger.info(f"USDT转账result: {result}")
            # 主动查询链上状态
            import time
            tx_info = None
            for _ in range(20):
                tx_info = self.tron.get_transaction_info(txid)
                if tx_info and 'receipt' in tx_info:
                    break
                time.sleep(1)
            self.logger.info(f"USDT转账链上tx_info: {tx_info}")
            if tx_info and tx_info.get('receipt', {}).get('result') == 'SUCCESS':
                self.logger.info(f"USDT转账成功: {amount} USDT -> {to_address}")
                explorer_url = f"https://tronscan.org/#/transaction/{txid}"
                return {
                    'success': True,
                    'txid': txid,
                    'amount': amount,
                    'to_address': to_address,
                    'from_address': from_address,
                    'explorer_url': explorer_url
                }
            elif tx_info and 'receipt' in tx_info:
                error_msg = tx_info.get('receipt', {}).get('result')
                self.logger.error(f"USDT转账链上失败: {error_msg}")
                return {'success': False, 'error': f'链上执行失败: {error_msg}'}
            else:
                self.logger.error(f"USDT转账链上确认超时或状态未知: {tx_info}")
                return {'success': False, 'error': '链上确认超时或状态未知，请稍后在区块浏览器查询'}
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
            if 'explorer_url' in result:
                message += f"🌐 <a href='{result['explorer_url']}'>在区块链浏览器查看</a>\n"
            message += f"⏰ 时间: {time.strftime('%Y-%m-%d %H:%M:%S')}"
        else:
            message = f"❌ {token_type}转账失败\n\n"
            message += f"错误信息: {result['error']}"
        
        return message 