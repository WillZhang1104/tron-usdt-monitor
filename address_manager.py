#!/usr/bin/env python3
"""
简化地址管理器
只读取.env文件中的白名单，不提供编辑功能
"""

import os
import logging
from typing import Dict, List, Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class AddressManager:
    """简化地址管理器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.whitelist_addresses = self._load_whitelist_addresses()
        self.logger.info(f"简化地址管理器初始化完成，共加载 {len(self.whitelist_addresses)} 个白名单地址")
    
    def _load_whitelist_addresses(self) -> Dict[str, Dict]:
        """从.env文件加载白名单地址"""
        try:
            whitelist_config = os.getenv('WHITELIST_ADDRESSES', '')
            if not whitelist_config:
                self.logger.warning("未找到WHITELIST_ADDRESSES配置")
                return {}
            
            addresses = {}
            
            # 解析配置格式：地址=别名,描述|地址=别名,描述
            for item in whitelist_config.split('|'):
                if '=' in item:
                    address_part, info_part = item.split('=', 1)
                    address = address_part.strip()
                    
                    if ',' in info_part:
                        alias, description = info_part.split(',', 1)
                        alias = alias.strip()
                        description = description.strip()
                    else:
                        alias = info_part.strip()
                        description = ""
                    
                    if self._validate_address(address):
                        addresses[address] = {
                            "address": address,
                            "alias": alias,
                            "description": description,
                            "whitelist": True
                        }
                        self.logger.info(f"加载白名单地址: {alias} ({address})")
                    else:
                        self.logger.warning(f"跳过无效地址: {address}")
            
            return addresses
            
        except Exception as e:
            self.logger.error(f"加载白名单地址失败: {e}")
            return {}
    
    def _validate_address(self, address: str) -> bool:
        """验证地址格式"""
        return address.startswith('T') and len(address) == 34
    
    def get_whitelist_addresses(self) -> List[str]:
        """获取白名单地址列表"""
        return list(self.whitelist_addresses.keys())
    
    def get_address_info(self, address: str) -> Optional[Dict]:
        """获取地址信息"""
        return self.whitelist_addresses.get(address)
    
    def get_address_by_alias(self, alias: str) -> Optional[Dict]:
        """通过别名获取地址信息"""
        for addr_data in self.whitelist_addresses.values():
            if addr_data['alias'] == alias:
                return addr_data
        return None
    
    def search_addresses(self, keyword: str) -> List[Dict]:
        """搜索地址"""
        results = []
        keyword_lower = keyword.lower()
        
        for addr_data in self.whitelist_addresses.values():
            if (keyword_lower in addr_data['address'].lower() or
                keyword_lower in addr_data['alias'].lower() or
                keyword_lower in addr_data['description'].lower()):
                results.append(addr_data)
        
        return results
    
    def format_whitelist(self) -> str:
        """格式化白名单显示"""
        if not self.whitelist_addresses:
            return "❌ 白名单为空\n\n请在 .env 文件中配置 WHITELIST_ADDRESSES"
        
        result = "✅ 白名单地址\n\n"
        
        for i, (address, addr_data) in enumerate(self.whitelist_addresses.items(), 1):
            result += f"{i}. {addr_data['alias']}\n"
            result += f"   📍 {address}\n"
            if addr_data['description']:
                result += f"   📝 {addr_data['description']}\n"
            result += "\n"
        
        return result
    
    def format_address_list(self) -> str:
        """格式化地址列表（用于选择）"""
        if not self.whitelist_addresses:
            return "❌ 白名单为空\n\n请在 .env 文件中配置 WHITELIST_ADDRESSES"
        
        result = "📋 可用地址列表\n\n"
        
        for i, (address, addr_data) in enumerate(self.whitelist_addresses.items(), 1):
            result += f"{i}. {addr_data['alias']}\n"
            result += f"   📍 {address[:10]}...{address[-10:]}\n"
            if addr_data['description']:
                result += f"   📝 {addr_data['description']}\n"
            result += "\n"
        
        return result
    
    def get_address_for_transfer(self, input_text: str) -> Optional[str]:
        """根据输入获取转账地址（支持序号、别名、地址）"""
        try:
            # 尝试按序号查找
            if input_text.isdigit():
                index = int(input_text) - 1
                addresses = list(self.whitelist_addresses.keys())
                if 0 <= index < len(addresses):
                    return addresses[index]
            
            # 尝试按别名查找
            addr_data = self.get_address_by_alias(input_text)
            if addr_data:
                return addr_data['address']
            
            # 尝试按地址查找
            if self._validate_address(input_text) and input_text in self.whitelist_addresses:
                return input_text
            
            return None
            
        except Exception as e:
            self.logger.error(f"获取转账地址失败: {e}")
            return None 