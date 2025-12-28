"""
YouTube 转录模块
使用 youtube-transcript-api 获取视频字幕/转录
"""

from typing import Optional
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable
)


def get_transcript(video_id: str, languages: list[str] = None) -> Optional[list[dict]]:
    """
    获取 YouTube 视频的转录文本
    
    Args:
        video_id: YouTube 视频 ID
        languages: 优先语言列表，默认 ['zh-Hans', 'zh-Hant', 'zh', 'en']
        
    Returns:
        转录列表，每项包含 {'text': str, 'start': float, 'duration': float}
        失败返回 None
    """
    if languages is None:
        languages = ['zh-Hans', 'zh-Hant', 'zh', 'en', 'ja', 'ko']
    
    try:
        # 获取可用的转录列表
        transcript_list = YouTubeTranscriptApi().list(video_id)
        
        # 尝试按优先级获取转录
        transcript = None
        
        # 首先尝试手动创建的字幕
        try:
            transcript = transcript_list.find_manually_created_transcript(languages)
        except NoTranscriptFound:
            pass
        
        # 如果没有手动字幕，尝试自动生成的
        if transcript is None:
            try:
                transcript = transcript_list.find_generated_transcript(languages)
            except NoTranscriptFound:
                pass
        
        # 如果还是没有，尝试获取任何可用的并翻译
        if transcript is None:
            try:
                # 获取第一个可用的转录
                for t in transcript_list:
                    transcript = t
                    break
            except Exception:
                pass
        
        if transcript is None:
            print(f"[警告] 视频 {video_id} 没有可用的转录")
            return None
        
        # 获取转录内容
        return transcript.fetch()
        
    except TranscriptsDisabled:
        print(f"[警告] 视频 {video_id} 已禁用转录")
        return None
    except VideoUnavailable:
        print(f"[警告] 视频 {video_id} 不可用")
        return None
    except Exception as e:
        print(f"[错误] 获取转录失败: {e}")
        return None


def format_transcript(transcript, include_timestamps: bool = True) -> str:
    """
    将转录列表格式化为文本
    
    Args:
        transcript: 转录列表 (FetchedTranscript or list of dicts)
        include_timestamps: 是否包含时间戳
        
    Returns:
        格式化后的转录文本
    """
    if not transcript:
        return ""
    
    lines = []
    
    for item in transcript:
        # 支持新版 FetchedTranscriptSnippet 对象和旧版 dict
        if hasattr(item, 'text'):
            text = item.text.strip() if item.text else ''
            start = getattr(item, 'start', 0)
        else:
            text = item.get('text', '').strip()
            start = item.get('start', 0)
        
        if not text:
            continue
            
        if include_timestamps:
            # 格式化时间为 HH:MM:SS 或 MM:SS
            hours = int(start // 3600)
            minutes = int((start % 3600) // 60)
            seconds = int(start % 60)
            
            if hours > 0:
                timestamp = f"[{hours:02d}:{minutes:02d}:{seconds:02d}]"
            else:
                timestamp = f"[{minutes:02d}:{seconds:02d}]"
            
            lines.append(f"{timestamp} {text}")
        else:
            lines.append(text)
    
    return '\n'.join(lines)


def get_plain_text(transcript) -> str:
    """
    获取纯文本转录（不含时间戳，用于 AI 处理）
    
    Args:
        transcript: 转录列表 (FetchedTranscript or list of dicts)
        
    Returns:
        纯文本转录
    """
    if not transcript:
        return ""
    
    texts = []
    for item in transcript:
        # 支持新版 FetchedTranscriptSnippet 对象和旧版 dict
        if hasattr(item, 'text'):
            text = item.text.strip() if item.text else ''
        else:
            text = item.get('text', '').strip()
        
        if text:
            texts.append(text)
    
    # 合并连续的文本，处理分句
    full_text = ' '.join(texts)
    
    # 简单的清理
    full_text = full_text.replace('  ', ' ')
    
    return full_text


def get_transcript_with_text(video_id: str) -> tuple[Optional[list[dict]], str, str]:
    """
    获取转录并返回原始数据和格式化文本
    
    Args:
        video_id: YouTube 视频 ID
        
    Returns:
        (raw_transcript, formatted_text, plain_text) 元组
    """
    transcript = get_transcript(video_id)
    
    if transcript is None:
        return None, "", ""
    
    formatted = format_transcript(transcript, include_timestamps=True)
    plain = get_plain_text(transcript)
    
    return transcript, formatted, plain


if __name__ == '__main__':
    # 测试代码
    test_video_id = "dQw4w9WgXcQ"
    print(f"测试视频 ID: {test_video_id}")
    
    raw, formatted, plain = get_transcript_with_text(test_video_id)
    
    if raw:
        print(f"\n转录条目数: {len(raw)}")
        print(f"\n格式化文本（前500字符）:\n{formatted[:500]}...")
        print(f"\n纯文本长度: {len(plain)} 字符")
    else:
        print("获取转录失败")
