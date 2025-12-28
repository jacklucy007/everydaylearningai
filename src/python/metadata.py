"""
元数据提取与封面下载模块
"""

import os
import requests
from typing import Optional
from dataclasses import dataclass
from datetime import datetime

from fetcher import VideoInfo, fetch_video_info


def download_cover(url: str, output_path: str, timeout: int = 30) -> bool:
    """
    下载视频封面图片
    
    Args:
        url: 封面图片 URL
        output_path: 保存路径
        timeout: 超时时间（秒）
        
    Returns:
        是否成功
    """
    if not url:
        print("[警告] 封面 URL 为空")
        return False
    
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        response = requests.get(url, timeout=timeout, stream=True)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"[成功] 封面已保存: {output_path}")
        return True
        
    except requests.exceptions.Timeout:
        print(f"[错误] 下载封面超时: {url}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"[错误] 下载封面失败: {e}")
        return False
    except IOError as e:
        print(f"[错误] 保存封面失败: {e}")
        return False


def get_best_thumbnail_url(video_info: VideoInfo) -> str:
    """
    获取最佳质量的缩略图 URL
    
    Args:
        video_info: 视频信息对象
        
    Returns:
        最佳缩略图 URL
    """
    video_id = video_info.video_id
    
    # YouTube 缩略图质量顺序（从高到低）
    thumbnail_options = [
        f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
        f"https://img.youtube.com/vi/{video_id}/sddefault.jpg",
        f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
        f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg",
        f"https://img.youtube.com/vi/{video_id}/default.jpg",
    ]
    
    # 检查哪个可用
    for url in thumbnail_options:
        try:
            response = requests.head(url, timeout=5)
            if response.status_code == 200:
                return url
        except:
            continue
    
    # 回退到 yt-dlp 提供的 URL
    return video_info.thumbnail_url or thumbnail_options[-1]


def format_duration(seconds: int) -> str:
    """
    格式化时长
    
    Args:
        seconds: 秒数
        
    Returns:
        格式化的时长字符串 (如 "1:23:45" 或 "23:45")
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes}:{secs:02d}"


def extract_metadata_for_archive(video_info: VideoInfo) -> dict:
    """
    提取用于归档的元数据
    
    Args:
        video_info: 视频信息对象
        
    Returns:
        归档用的元数据字典
    """
    return {
        'video_id': video_info.video_id,
        'title': video_info.title,
        'description': video_info.description,
        'channel_name': video_info.channel_name,
        'channel_id': video_info.channel_id,
        'upload_date': video_info.formatted_date,
        'duration': format_duration(video_info.duration),
        'duration_seconds': video_info.duration,
        'url': video_info.url,
        'thumbnail_url': video_info.thumbnail_url,
        'platform': 'youtube',
        'processed_at': datetime.now().isoformat(),
    }


if __name__ == '__main__':
    # 测试代码
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    print(f"测试 URL: {test_url}")
    
    info = fetch_video_info(test_url)
    if info:
        print(f"\n视频信息:")
        print(f"  标题: {info.title}")
        print(f"  频道: {info.channel_name}")
        print(f"  日期: {info.formatted_date}")
        print(f"  时长: {format_duration(info.duration)}")
        
        best_thumb = get_best_thumbnail_url(info)
        print(f"  最佳缩略图: {best_thumb}")
        
        # 测试下载
        # download_cover(best_thumb, "test_cover.jpg")
