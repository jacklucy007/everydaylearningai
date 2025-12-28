"""
状态管理模块
管理已处理内容的记录，实现去重功能
"""

import os
import yaml
from datetime import datetime
from typing import Optional
from pathlib import Path


# 默认状态文件路径
DEFAULT_STATE_FILE = Path(__file__).parent.parent.parent / 'config' / 'state.yaml'


class StateManager:
    """状态管理器"""
    
    def __init__(self, state_file: Optional[str] = None):
        """
        初始化状态管理器
        
        Args:
            state_file: 状态文件路径，默认为 config/state.yaml
        """
        self.state_file = Path(state_file) if state_file else DEFAULT_STATE_FILE
        self.state = self._load_state()
    
    def _load_state(self) -> dict:
        """加载状态文件"""
        if not self.state_file.exists():
            return self._get_default_state()
        
        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                state = yaml.safe_load(f) or {}
                # 确保必要的键存在
                if 'processed' not in state:
                    state['processed'] = {}
                if 'youtube' not in state['processed']:
                    state['processed']['youtube'] = []
                if 'last_check' not in state:
                    state['last_check'] = {}
                return state
        except Exception as e:
            print(f"[警告] 加载状态文件失败: {e}")
            return self._get_default_state()
    
    def _get_default_state(self) -> dict:
        """获取默认状态"""
        return {
            'processed': {
                'youtube': [],
            },
            'last_check': {
                'youtube': None,
            }
        }
    
    def _save_state(self) -> bool:
        """保存状态到文件"""
        try:
            # 确保目录存在
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.state_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.state, f, allow_unicode=True, default_flow_style=False)
            return True
        except Exception as e:
            print(f"[错误] 保存状态文件失败: {e}")
            return False
    
    def is_processed(self, content_id: str, platform: str = 'youtube') -> bool:
        """
        检查内容是否已处理
        
        Args:
            content_id: 内容 ID (如视频 ID)
            platform: 平台名称
            
        Returns:
            是否已处理
        """
        processed_list = self.state.get('processed', {}).get(platform, [])
        return content_id in processed_list
    
    def mark_processed(self, content_id: str, platform: str = 'youtube') -> bool:
        """
        标记内容为已处理
        
        Args:
            content_id: 内容 ID
            platform: 平台名称
            
        Returns:
            是否成功
        """
        if platform not in self.state['processed']:
            self.state['processed'][platform] = []
        
        if content_id not in self.state['processed'][platform]:
            self.state['processed'][platform].append(content_id)
            return self._save_state()
        
        return True
    
    def unmark_processed(self, content_id: str, platform: str = 'youtube') -> bool:
        """
        取消标记（重新处理时使用）
        
        Args:
            content_id: 内容 ID
            platform: 平台名称
            
        Returns:
            是否成功
        """
        if platform in self.state['processed']:
            if content_id in self.state['processed'][platform]:
                self.state['processed'][platform].remove(content_id)
                return self._save_state()
        return True
    
    def update_last_check(self, platform: str = 'youtube') -> bool:
        """
        更新最后检查时间
        
        Args:
            platform: 平台名称
            
        Returns:
            是否成功
        """
        self.state['last_check'][platform] = datetime.now().isoformat()
        return self._save_state()
    
    def get_last_check(self, platform: str = 'youtube') -> Optional[str]:
        """
        获取最后检查时间
        
        Args:
            platform: 平台名称
            
        Returns:
            ISO 格式的时间字符串，或 None
        """
        return self.state.get('last_check', {}).get(platform)
    
    def get_processed_count(self, platform: str = 'youtube') -> int:
        """
        获取已处理的内容数量
        
        Args:
            platform: 平台名称
            
        Returns:
            已处理数量
        """
        return len(self.state.get('processed', {}).get(platform, []))
    
    def clear_processed(self, platform: str = 'youtube') -> bool:
        """
        清除指定平台的所有处理记录
        
        Args:
            platform: 平台名称
            
        Returns:
            是否成功
        """
        if platform in self.state['processed']:
            self.state['processed'][platform] = []
            return self._save_state()
        return True


# 全局状态管理器实例
_state_manager: Optional[StateManager] = None


def get_state_manager(state_file: Optional[str] = None) -> StateManager:
    """获取状态管理器单例"""
    global _state_manager
    if _state_manager is None:
        _state_manager = StateManager(state_file)
    return _state_manager


if __name__ == '__main__':
    # 测试代码
    sm = StateManager()
    
    test_id = "test_video_123"
    
    print(f"已处理数量: {sm.get_processed_count()}")
    print(f"'{test_id}' 是否已处理: {sm.is_processed(test_id)}")
    
    print(f"\n标记 '{test_id}' 为已处理...")
    sm.mark_processed(test_id)
    
    print(f"'{test_id}' 是否已处理: {sm.is_processed(test_id)}")
    print(f"已处理数量: {sm.get_processed_count()}")
    
    print(f"\n取消标记 '{test_id}'...")
    sm.unmark_processed(test_id)
    
    print(f"'{test_id}' 是否已处理: {sm.is_processed(test_id)}")
