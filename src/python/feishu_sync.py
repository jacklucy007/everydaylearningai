"""
飞书多维表格同步模块
将内容策展结果同步到飞书多维表格
"""

import json
import yaml
import requests
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# 默认配置
DEFAULT_CONFIG = {
    "app_id": "cli_a9c5634f83b8dbc0",
    "app_secret": "8W9t4DvjXgprdlKb76yIuftgX7NKvnHf",
    "app_token": "WkTfbPXDpaXvnMstxO5cLahynXc",
    "table_id": "tblgSjcuaZSWa1OA"
}


class FeishuSync:
    """飞书多维表格同步器"""
    
    def __init__(self, config: Dict[str, str] = None):
        self.config = config or DEFAULT_CONFIG.copy()
        
        # 尝试从根目录 .env 加载环境变量覆盖配置
        try:
            env_path = Path(__file__).parent.parent.parent / '.env'
            if env_path.exists():
                with open(env_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith('#') or '=' not in line:
                            continue
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip("'").strip('"')
                        
                        if key == 'FEISHU_APP_ID': self.config['app_id'] = value
                        elif key == 'FEISHU_APP_SECRET': self.config['app_secret'] = value
                        elif key == 'FEISHU_APP_TOKEN': self.config['app_token'] = value
                        elif key == 'FEISHU_TABLE_ID': self.config['table_id'] = value
        except Exception:
            pass
            
        self._token = None
        self._token_expires = 0
    
    def _get_token(self) -> Optional[str]:
        """获取或刷新 tenant_access_token"""
        now = datetime.now().timestamp()
        if self._token and now < self._token_expires:
            return self._token
        
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        payload = {
            "app_id": self.config["app_id"],
            "app_secret": self.config["app_secret"]
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            data = response.json()
            if data.get("code") == 0:
                self._token = data.get("tenant_access_token")
                self._token_expires = now + data.get("expire", 7200) - 60
                return self._token
        except Exception as e:
            print(f"[飞书] 获取 Token 失败: {e}")
        return None
    
    def _format_date(self, date_str: str) -> int:
        """将日期字符串转换为时间戳（毫秒）"""
        try:
            # 支持多种格式
            for fmt in ['%Y-%m-%d', '%Y%m%d', '%Y/%m/%d']:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return int(dt.timestamp() * 1000)
                except ValueError:
                    continue
        except:
            pass
        except:
            pass
        return int(datetime.now().timestamp() * 1000)

    def _get_channel_metadata(self, channel_name: str) -> Dict[str, str]:
        """获取频道的元数据（描述、图标）"""
        metadata = {"description": "", "icon": ""}
        
        try:
            # 假设 config 目录在当前文件的上两级
            config_path = Path(__file__).parent.parent.parent / 'config' / 'sources.yaml'
            if not config_path.exists():
                return metadata
                
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f) or {}
                
            youtube_sources = config.get('sources', {}).get('youtube', [])
            for source in youtube_sources:
                # 尝试匹配配置中的名称
                # 注意：这里简单的全等匹配，如果 yt-dlp 返回的频道名与配置文件不一致，可能匹配失败
                if source.get('name') == channel_name:
                    metadata['description'] = source.get('description', '')
                    metadata['icon'] = source.get('icon', '')
                    break
        except Exception as e:
            print(f"[飞书] 读取频道配置失败: {e}")
            
        return metadata
    
    def sync_record(self, archive_path: str) -> bool:
        """
        将单个归档同步到飞书多维表格
        
        Args:
            archive_path: 归档文件夹路径
            
        Returns:
            是否成功
        """
        archive = Path(archive_path)
        
        # 读取必要文件
        metadata_file = archive / "metadata.md"
        rewritten_file = archive / "rewritten.json"
        
        if not metadata_file.exists():
            print(f"[飞书] 跳过: 找不到 metadata.md")
            return False
        
        # 尝试读取 rewritten.json
        rewritten_data = {}
        if rewritten_file.exists():
            try:
                with open(rewritten_file, 'r', encoding='utf-8') as f:
                    rewritten_data = json.load(f)
            except:
                pass
        
        # 解析元数据
        metadata = self._parse_metadata(metadata_file)
        
        # 获取频道元数据
        channel_name = metadata.get("channel", "")
        channel_meta = self._get_channel_metadata(channel_name)
        
        # 构建字段数据
        fields = {
            "标题": rewritten_data.get("title", metadata.get("title", "")),
            "原标题": metadata.get("title", ""),
            "频道": channel_name,
            "频道描述": channel_meta["description"],
            "频道图标": channel_meta["icon"],
            "视频ID": metadata.get("video_id", ""),
            "时长": metadata.get("duration", ""),
            "核心观点": "\n".join(rewritten_data.get("core_points", [])),
            "关键洞察": "\n".join(rewritten_data.get("key_insights", [])),
            "金句": "\n".join(rewritten_data.get("golden_quotes", [])),
            "嘉宾": ", ".join(rewritten_data.get("guests", [])),
            "深度摘要": rewritten_data.get("summary", ""),
        }
        
        # 处理日期字段
        if metadata.get("upload_date"):
            fields["发布日期"] = self._format_date(metadata.get("upload_date"))
        
        fields["处理时间"] = int(datetime.now().timestamp() * 1000)
        
        # 处理超链接
        if metadata.get("url"):
            fields["视频链接"] = {
                "text": metadata.get("title", "观看视频"),
                "link": metadata.get("url")
            }
        
        # 创建记录
        return self._create_record(fields)
    
    def _parse_metadata(self, metadata_file: Path) -> Dict[str, str]:
        """从 metadata.md 解析基础信息"""
        result = {}
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 简单解析 Markdown
            for line in content.split('\n'):
                line = line.strip()
                if line.startswith('## '):
                    result['title'] = line[3:].strip()
                elif '**频道**:' in line or '**频道**：' in line:
                    result['channel'] = line.split(':')[-1].strip().split('：')[-1].strip()
                elif '**发布日期**:' in line or '**发布日期**：' in line:
                    result['upload_date'] = line.split(':')[-1].strip().split('：')[-1].strip()
                elif '**时长**:' in line or '**时长**：' in line:
                    result['duration'] = line.split(':')[-1].strip().split('：')[-1].strip()
                elif '**视频ID**:' in line or '**视频ID**：' in line:
                    vid = line.split('`')
                    if len(vid) >= 2:
                        result['video_id'] = vid[1]
                elif '**链接**:' in line or '**链接**：' in line:
                    # 提取 URL
                    import re
                    urls = re.findall(r'\((https?://[^)]+)\)', line)
                    if urls:
                        result['url'] = urls[0]
        except Exception as e:
            print(f"[飞书] 解析元数据失败: {e}")
        
        return result
    
    def _create_record(self, fields: Dict[str, Any]) -> bool:
        """创建一条记录"""
        token = self._get_token()
        if not token:
            return False
        
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{self.config['app_token']}/tables/{self.config['table_id']}/records"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        payload = {"fields": fields}
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            data = response.json()
            
            if data.get("code") == 0:
                record_id = data.get("data", {}).get("record", {}).get("record_id")
                print(f"[飞书] ✓ 同步成功 (record_id: {record_id})")
                return True
            else:
                print(f"[飞书] ✗ 同步失败: {data.get('msg')} (code: {data.get('code')})")
                return False
        except Exception as e:
            print(f"[飞书] ✗ 请求失败: {e}")
            return False


def sync_archive_to_feishu(archive_path: str, config: Dict[str, str] = None) -> bool:
    """便捷函数：同步单个归档到飞书"""
    syncer = FeishuSync(config)
    return syncer.sync_record(archive_path)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python feishu_sync.py <归档文件夹路径>")
        print("示例: python feishu_sync.py output/2025-12-21_0XI_Xt0ci2Y")
        exit(1)
    
    archive_path = sys.argv[1]
    success = sync_archive_to_feishu(archive_path)
    exit(0 if success else 1)
