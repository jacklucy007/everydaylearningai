"""
YouTube 内容抓取模块
使用 yt-dlp 获取 YouTube 视频信息和频道最新视频列表
"""

import re
import json
import subprocess
from typing import Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class VideoInfo:
    """视频信息数据类"""
    video_id: str
    title: str
    description: str
    channel_name: str
    channel_id: str
    upload_date: str  # YYYYMMDD 格式
    duration: int  # 秒
    thumbnail_url: str
    url: str
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @property
    def formatted_date(self) -> str:
        """返回格式化的日期 YYYY-MM-DD"""
        if self.upload_date and len(self.upload_date) == 8:
            return f"{self.upload_date[:4]}-{self.upload_date[4:6]}-{self.upload_date[6:8]}"
        return self.upload_date

    @property
    def duration_minutes(self) -> float:
        """返回时长（分钟）"""
        return self.duration / 60.0


def extract_video_id(url: str) -> Optional[str]:
    """从 YouTube URL 中提取视频 ID"""
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com/embed/([a-zA-Z0-9_-]{11})',
        r'youtube\.com/v/([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def fetch_video_info(url: str, cookies_from_browser: Optional[str] = None, cookies_file: Optional[str] = None) -> Optional[VideoInfo]:
    """
    获取单个 YouTube 视频的详细信息
    
    Args:
        url: YouTube 视频 URL
        cookies_from_browser: 浏览器名称 (如 'chrome', 'firefox')
        cookies_file: cookies.txt 文件路径
        
    Returns:
        VideoInfo 对象，失败返回 None
    """
    video_id = extract_video_id(url)
    if not video_id:
        print(f"[错误] 无法从 URL 提取视频 ID: {url}")
        return None
    
    try:
        # 使用 yt-dlp 获取视频信息
        cmd = [
            'python', '-m', 'yt_dlp',
            '--dump-json',
            '--no-download',
            '--no-playlist',
            '--js-runtime', 'node',
            '--no-warnings',
            '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            '--add-header', 'Accept-Language:zh-CN,zh;q=0.9,en;q=0.8',
            url
        ]
        
        if cookies_from_browser:
            cmd.extend(['--cookies-from-browser', cookies_from_browser])
        
        if cookies_file:
            cmd.extend(['--cookies', cookies_file])
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            print(f"[错误] yt-dlp 执行失败: {result.stderr}")
            return None
        
        data = json.loads(result.stdout)
        
        return VideoInfo(
            video_id=data.get('id', video_id),
            title=data.get('title', ''),
            description=data.get('description', ''),
            channel_name=data.get('channel', data.get('uploader', '')),
            channel_id=data.get('channel_id', ''),
            upload_date=data.get('upload_date', ''),
            duration=data.get('duration', 0),
            thumbnail_url=data.get('thumbnail', ''),
            url=f"https://www.youtube.com/watch?v={video_id}"
        )
        
    except subprocess.TimeoutExpired:
        print(f"[错误] 获取视频信息超时: {url}")
        return None
    except json.JSONDecodeError as e:
        print(f"[错误] 解析视频信息失败: {e}")
        return None
    except Exception as e:
        print(f"[错误] 获取视频信息时发生异常: {e}")
        return None


def fetch_channel_videos(channel_id: str, max_count: int = 10, cookies_from_browser: Optional[str] = None, cookies_file: Optional[str] = None) -> list[VideoInfo]:
    """
    获取 YouTube 频道的最新视频列表
    
    Args:
        channel_id: YouTube 频道 ID
        max_count: 最大获取数量
        cookies_from_browser: 浏览器名称
        cookies_file: cookies.txt 文件路径
        
    Returns:
        VideoInfo 列表
    """
    # 智能构造 URL
    if channel_id.startswith('UC') and len(channel_id) > 10:
        # 标准频道 ID
        channel_url = f"https://www.youtube.com/channel/{channel_id}/videos"
    elif channel_id.startswith('@'):
        # 已经是 Handle 格式
        channel_url = f"https://www.youtube.com/{channel_id}/videos"
    else:
        # 假设是 Handle 但没加 @，或者是旧式用户名
        channel_url = f"https://www.youtube.com/@{channel_id}/videos"
    
    try:
        cmd = [
            'python', '-m', 'yt_dlp',
            '--dump-json',
            '--no-download',
            '--flat-playlist',
            '--playlist-end', str(max_count),
            '--js-runtime', 'node',
            '--no-warnings',
            '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            '--add-header', 'Accept-Language:zh-CN,zh;q=0.9,en;q=0.8',
            channel_url
        ]
        
        if cookies_from_browser:
            cmd.extend(['--cookies-from-browser', cookies_from_browser])
        
        if cookies_file:
            cmd.extend(['--cookies', cookies_file])
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode != 0:
            print(f"[错误] 获取频道视频列表失败: {result.stderr}")
            return []
        
        videos = []
        for line in result.stdout.strip().split('\n'):
            if line:
                try:
                    data = json.loads(line)
                    video_url = data.get('url', '')
                    if video_url:
                        # 获取完整视频信息
                        video_info = fetch_video_info(
                            f"https://www.youtube.com/watch?v={data.get('id', '')}",
                            cookies_from_browser=cookies_from_browser,
                            cookies_file=cookies_file
                        )
                        if video_info:
                            videos.append(video_info)
                except json.JSONDecodeError:
                    continue
        
        return videos
        
    except subprocess.TimeoutExpired:
        print(f"[错误] 获取频道视频列表超时")
        return []
    except Exception as e:
        print(f"[错误] 获取频道视频列表时发生异常: {e}")
        return []


def parse_url(url: str) -> tuple[str, str]:
    """
    解析 URL，判断类型并返回平台和 ID
    
    Args:
        url: 视频或频道 URL
        
    Returns:
        (platform, id) 元组
        - platform: 'youtube_video', 'youtube_channel', 'unknown'
        - id: 视频 ID 或频道 ID
    """
    # YouTube 视频
    video_id = extract_video_id(url)
    if video_id:
        return ('youtube_video', video_id)
    
    # YouTube 频道
    channel_patterns = [
        r'youtube\.com/channel/([a-zA-Z0-9_-]+)',
        r'youtube\.com/@([a-zA-Z0-9_-]+)',
        r'youtube\.com/c/([a-zA-Z0-9_-]+)',
    ]
    
    for pattern in channel_patterns:
        match = re.search(pattern, url)
        if match:
            return ('youtube_channel', match.group(1))
    
    return ('unknown', '')


if __name__ == '__main__':
    # 测试代码
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    print(f"测试 URL: {test_url}")
    
    video_id = extract_video_id(test_url)
    print(f"提取的视频 ID: {video_id}")
    
    info = fetch_video_info(test_url)
    if info:
        print(f"视频标题: {info.title}")
        print(f"频道名称: {info.channel_name}")
        print(f"发布日期: {info.formatted_date}")
        print(f"时长: {info.duration} 秒")
