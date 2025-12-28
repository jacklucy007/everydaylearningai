"""
归档管理模块
创建归档文件夹结构，生成 metadata.md, transcript.md, rewritten.md
"""

import os
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional

from fetcher import VideoInfo
from metadata import download_cover, get_best_thumbnail_url, extract_metadata_for_archive
from feishu_sync import sync_archive_to_feishu


# 默认输出目录
DEFAULT_OUTPUT_DIR = Path(__file__).parent.parent.parent / 'output'
NODE_REWRITER_PATH = Path(__file__).parent.parent / 'node' / 'rewriter.js'


class Archiver:
    """归档管理器"""
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        初始化归档管理器
        
        Args:
            output_dir: 输出目录路径
        """
        self.output_dir = Path(output_dir) if output_dir else DEFAULT_OUTPUT_DIR
    
    def create_archive_folder(self, video_info: VideoInfo) -> Path:
        """
        创建归档文件夹
        
        Args:
            video_info: 视频信息
            
        Returns:
            归档文件夹路径
        """
        # 文件夹命名: YYYY-MM-DD_video_id
        folder_name = f"{video_info.formatted_date}_{video_info.video_id}"
        folder_path = self.output_dir / folder_name
        
        folder_path.mkdir(parents=True, exist_ok=True)
        
        return folder_path
    
    def generate_metadata_md(self, metadata: dict, rewritten_data: Optional[dict] = None) -> str:
        """
        生成 metadata.md 内容
        
        Args:
            metadata: 基础元数据
            rewritten_data: AI 改写后的数据（包含标题、嘉宾、金句等）
            
        Returns:
            Markdown 格式的元数据
        """
        lines = [
            "# 内容元数据",
            "",
        ]
        
        # 如果有 AI 生成的标题，使用它
        if rewritten_data and rewritten_data.get('title'):
            lines.extend([
                f"## {rewritten_data['title']}",
                "",
                f"> 原标题：{metadata.get('title', '')}",
                "",
            ])
        else:
            lines.extend([
                f"## {metadata.get('title', '未知标题')}",
                "",
            ])
        
        # 基本信息
        lines.extend([
            "### 基本信息",
            "",
            f"- **平台**: {metadata.get('platform', 'youtube').upper()}",
            f"- **频道**: {metadata.get('channel_name', '')}",
            f"- **发布日期**: {metadata.get('upload_date', '')}",
            f"- **时长**: {metadata.get('duration', '')}",
            f"- **链接**: [{metadata.get('video_id', '')}]({metadata.get('url', '')})",
            "",
        ])
        
        # 嘉宾信息
        if rewritten_data and rewritten_data.get('guests'):
            guests = rewritten_data['guests']
            if guests:
                lines.extend([
                    "### 嘉宾",
                    "",
                ])
                for guest in guests:
                    lines.append(f"- {guest}")
                lines.append("")
        
        # 金句
        if rewritten_data and rewritten_data.get('golden_quotes'):
            quotes = rewritten_data['golden_quotes']
            if quotes:
                lines.extend([
                    "### 金句",
                    "",
                ])
                for i, quote in enumerate(quotes, 1):
                    lines.append(f"{i}. {quote}")
                lines.append("")
        
        # 核心观点
        if rewritten_data and rewritten_data.get('core_points'):
            points = rewritten_data['core_points']
            if points:
                lines.extend([
                    "### 核心观点",
                    "",
                ])
                for point in points:
                    lines.append(f"- {point}")
                lines.append("")
        
        # 处理信息
        lines.extend([
            "---",
            "",
            "### 处理信息",
            "",
            f"- **处理时间**: {metadata.get('processed_at', datetime.now().isoformat())}",
            f"- **视频ID**: `{metadata.get('video_id', '')}`",
            "",
        ])
        
        return '\n'.join(lines)
    
    def generate_transcript_md(self, formatted_transcript: str, video_info: VideoInfo) -> str:
        """
        生成 transcript.md 内容
        
        Args:
            formatted_transcript: 格式化的转录文本（带时间戳）
            video_info: 视频信息
            
        Returns:
            Markdown 格式的转录
        """
        lines = [
            f"# 转录: {video_info.title}",
            "",
            f"> 来源: [{video_info.channel_name}]({video_info.url})",
            f"> 发布日期: {video_info.formatted_date}",
            "",
            "---",
            "",
            formatted_transcript,
        ]
        
        return '\n'.join(lines)
    
    def generate_rewritten_md(self, rewritten_data: dict, video_info: VideoInfo) -> str:
        """
        生成 rewritten.md 内容
        
        Args:
            rewritten_data: AI 改写后的数据
            video_info: 视频信息
            
        Returns:
            Markdown 格式的改写内容
        """
        title = rewritten_data.get('title', video_info.title)
        summary = rewritten_data.get('summary', '')
        key_insights = rewritten_data.get('key_insights', [])
        
        lines = [
            f"# {title}",
            "",
            f"> 原视频: [{video_info.title}]({video_info.url})",
            f"> 频道: {video_info.channel_name}",
            f"> 发布日期: {video_info.formatted_date}",
            "",
        ]
        
        # 关键洞察
        if key_insights:
            lines.extend([
                "## 关键洞察",
                "",
            ])
            for insight in key_insights:
                lines.append(f"- {insight}")
            lines.extend(["", "---", ""])
        
        # 深度摘要
        lines.extend([
            "## 深度摘要",
            "",
            summary,
        ])
        
        return '\n'.join(lines)
    
    def call_ai_rewriter(self, plain_transcript: str, config_path: Optional[str] = None, prompt_path: Optional[str] = None) -> Optional[dict]:
        """
        调用 Node.js AI 改写模块
        
        Args:
            plain_transcript: 纯文本转录
            config_path: 配置文件路径
            prompt_path: 自定义 Promt 文件路径
            
        Returns:
            改写后的 JSON 数据，失败返回 None
        """
        if not NODE_REWRITER_PATH.exists():
            print(f"[错误] Node.js 改写模块不存在: {NODE_REWRITER_PATH}")
            return None
        
        try:
            # 将转录文本通过 stdin 传递给 Node.js
            cmd = ['node', str(NODE_REWRITER_PATH)]
            
            if config_path:
                cmd.extend(['--config', config_path])
            
            if prompt_path:
                cmd.extend(['--prompt', prompt_path])
            
            result = subprocess.run(
                cmd,
                input=plain_transcript,
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=180,  # 3 分钟超时
                cwd=NODE_REWRITER_PATH.parent
            )
            
            if result.returncode != 0:
                print(f"[错误] AI 改写失败: {result.stderr}")
                return None
            
            # 解析输出的 JSON
            return json.loads(result.stdout)
            
        except subprocess.TimeoutExpired:
            print("[错误] AI 改写超时")
            return None
        except json.JSONDecodeError as e:
            print(f"[错误] 解析 AI 输出失败: {e}")
            return None
        except Exception as e:
            print(f"[错误] 调用 AI 改写时发生异常: {e}")
            return None
    
    def create_full_archive(
        self,
        video_info: VideoInfo,
        formatted_transcript: str,
        plain_transcript: str,
        config_path: Optional[str] = None,
        skip_ai: bool = False,
        prompt_path: Optional[str] = None,
        sync_feishu: bool = False
    ) -> Optional[Path]:
        """
        创建完整的归档
        
        Args:
            video_info: 视频信息
            formatted_transcript: 格式化转录（带时间戳）
            plain_transcript: 纯文本转录
            config_path: 配置文件路径
            skip_ai: 是否跳过 AI 改写
            prompt_path: 自定义 Prompt 文件路径
            sync_feishu: 是否同步到飞书多维表格
            
        Returns:
            归档文件夹路径，失败返回 None
        """
        try:
            # 创建文件夹
            folder = self.create_archive_folder(video_info)
            print(f"[信息] 创建归档文件夹: {folder}")
            
            # 提取元数据
            metadata = extract_metadata_for_archive(video_info)
            
            # AI 改写
            rewritten_data = None
            if not skip_ai and plain_transcript:
                print("[信息] 正在调用 AI 改写...")
                rewritten_data = self.call_ai_rewriter(plain_transcript, config_path, prompt_path)
                if rewritten_data:
                    print("[成功] AI 改写完成")
                else:
                    print("[警告] AI 改写失败，将只保存原始转录")
            
            # 生成并保存 metadata.md
            metadata_content = self.generate_metadata_md(metadata, rewritten_data)
            with open(folder / 'metadata.md', 'w', encoding='utf-8') as f:
                f.write(metadata_content)
            print(f"[成功] 已保存 metadata.md")
            
            # 保存 transcript.md
            transcript_content = self.generate_transcript_md(formatted_transcript, video_info)
            with open(folder / 'transcript.md', 'w', encoding='utf-8') as f:
                f.write(transcript_content)
            print(f"[成功] 已保存 transcript.md")
            
            # 保存 rewritten.md
            if rewritten_data:
                rewritten_content = self.generate_rewritten_md(rewritten_data, video_info)
                with open(folder / 'rewritten.md', 'w', encoding='utf-8') as f:
                    f.write(rewritten_content)
                print(f"[成功] 已保存 rewritten.md")
                
                # 同时保存原始 JSON
                with open(folder / 'rewritten.json', 'w', encoding='utf-8') as f:
                    json.dump(rewritten_data, f, ensure_ascii=False, indent=2)
            
            # 下载封面
            thumbnail_url = get_best_thumbnail_url(video_info)
            cover_path = folder / 'cover.jpg'
            if download_cover(thumbnail_url, str(cover_path)):
                print(f"[成功] 已保存封面图片")
            
            # 同步到飞书
            if sync_feishu:
                print("[信息] 正在同步到飞书多维表格...")
                sync_archive_to_feishu(str(folder))
            
            return folder
            
        except Exception as e:
            print(f"[错误] 创建归档失败: {e}")
            return None


if __name__ == '__main__':
    # 测试代码
    from fetcher import fetch_video_info
    from transcriber import get_transcript_with_text
    
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    print(f"测试 URL: {test_url}")
    
    # 获取视频信息
    video_info = fetch_video_info(test_url)
    if not video_info:
        print("获取视频信息失败")
        exit(1)
    
    # 获取转录
    raw, formatted, plain = get_transcript_with_text(video_info.video_id)
    if not raw:
        print("获取转录失败")
        exit(1)
    
    # 创建归档
    archiver = Archiver()
    folder = archiver.create_full_archive(
        video_info,
        formatted,
        plain,
        skip_ai=True  # 测试时跳过 AI
    )
    
    if folder:
        print(f"\n归档完成: {folder}")
