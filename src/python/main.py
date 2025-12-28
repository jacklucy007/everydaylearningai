"""
每日内容策展工作流 - 主入口
支持批量模式和 URL 模式
"""

import os
import sys
import click
import yaml
from pathlib import Path
from typing import List, Optional
from rich.console import Console
from rich.table import Table
from rich.prompt import Confirm
from datetime import datetime, timedelta

# 添加 src 到路径以便导入
sys.path.append(str(Path(__file__).parent))

from fetcher import fetch_video_info, fetch_channel_videos, parse_url
from transcriber import get_transcript_with_text
from state_manager import get_state_manager
from archiver import Archiver

console = Console()

# 默认配置文件路径
CONFIG_DIR = Path(__file__).parent.parent.parent / 'config'
SOURCES_FILE = CONFIG_DIR / 'sources.yaml'


def load_config() -> dict:
    """加载配置文件"""
    if not SOURCES_FILE.exists():
        console.print(f"[bold red]错误:[/bold red] 找不到配置文件 {SOURCES_FILE}")
        return {}
    
    try:
        with open(SOURCES_FILE, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        console.print(f"[bold red]错误:[/bold red] 加载配置文件失败: {e}")
        return {}


def process_single_video(url: str, archiver: Archiver, state_manager, skip_ai: bool = False, force: bool = False, cookies_from_browser: Optional[str] = None, cookies_file: Optional[str] = None, prompt_file: Optional[str] = None, sync_feishu: bool = False):
    """处理单个视频"""
    platform, content_id = parse_url(url)
    
    if platform != 'youtube_video':
        console.print(f"[yellow]跳过:[/yellow] 目前仅支持 YouTube 视频 URL: {url}")
        return False
    
    # 检查是否已处理
    if not force and state_manager.is_processed(content_id, 'youtube'):
        console.print(f"[blue]信息:[/blue] 视频 {content_id} 已处理，跳过。使用 --force 强制重新处理。")
        return True

    console.print(f"[bold blue]正在处理:[/bold blue] {url}")
    
    # 1. 获取视频信息
    with console.status("[bold green]正在获取视频信息..."):
        video_info = fetch_video_info(url, cookies_from_browser=cookies_from_browser, cookies_file=cookies_file)
    
    if not video_info:
        console.print(f"[red]错误:[/red] 无法获取视频信息: {url}")
        return False
    
    console.print(f"  [cyan]标题:[/cyan] {video_info.title}")
    console.print(f"  [cyan]频道:[/cyan] {video_info.channel_name}")
    
    # 2. 获取转录
    with console.status("[bold green]正在获取转录..."):
        raw, formatted, plain = get_transcript_with_text(video_info.video_id)
    
    if not raw:
        console.print(f"[yellow]警告:[/yellow] 该视频没有转录内容，将跳过。")
        return False
    
    console.print(f"  [cyan]转录:[/cyan] 已获取 ({len(plain)} 字符)")
    
    # 3. 创建归档
    folder = archiver.create_full_archive(
        video_info,
        formatted,
        plain,
        config_path=str(SOURCES_FILE),
        skip_ai=skip_ai,
        prompt_path=prompt_file,
        sync_feishu=sync_feishu
    )
    
    if folder:
        # 4. 标记为已处理
        state_manager.mark_processed(content_id, 'youtube')
        console.print(f"[bold green]成功:[/bold green] 已归档至 {folder}")
        return True
    else:
        console.print(f"[red]错误:[/red] 归档创建失败。")
        return False


@click.command()
@click.option('--batch', is_flag=True, help='运行批量扫描订阅源模式')
@click.option('--url', help='直接处理指定的单个或多个 URL (用逗号分隔)')
@click.option('--skip-ai', is_flag=True, help='跳过 AI 改写步骤')
@click.option('--force', is_flag=True, help='强制重新处理已存在的内容')
@click.option('--max-count', default=5, help='批量模式下每个频道获取的最大视频数')
@click.option('--cookies-from-browser', help='从指定的浏览器导出 cookies (如 chrome, firefox, edge)')
@click.option('--cookies', 'cookies_file', help='cookies.txt 文件路径')
@click.option('--min-duration', default=0, help='最小视频时长（分钟），短于此时长的视频将被忽略')
@click.option('--prompt-file', help='自定义 AI 改写提示词文件路径')
@click.option('--yes', '-y', is_flag=True, help='自动确认，跳过批量模式的交互提示')
@click.option('--days', default=0, help='仅处理最近 N 天内发布的视频，0 表示不限制')
@click.option('--sync-feishu', is_flag=True, help='同步到飞书多维表格')
def main(batch: bool, url: Optional[str], skip_ai: bool, force: bool, max_count: int, cookies_from_browser: Optional[str], cookies_file: Optional[str], min_duration: int, prompt_file: Optional[str], yes: bool, days: int, sync_feishu: bool):
    """
    每日内容策展工作流 - 自动化处理 YouTube 内容
    """
    console.print("[bold magenta]=== 每日内容策展自动化工作流 ===[/bold magenta]")
    
    config = load_config()
    if not config:
        return

    state_manager = get_state_manager()
    archiver = Archiver()
    
    if url:
        # URL 模式：自动处理无需确认
        urls = [u.strip() for u in url.split(',')]
        console.print(f"[bold]模式:[/bold] URL 模式 ({len(urls)} 个链接)")
        
        for u in urls:
            process_single_video(u, archiver, state_manager, skip_ai, force, cookies_from_browser=cookies_from_browser, cookies_file=cookies_file, prompt_file=prompt_file, sync_feishu=sync_feishu)
            
    elif batch:
        # 批量模式：扫描订阅源并供用户选择
        console.print("[bold]模式:[/bold] 订阅源批量模式")
        
        youtube_sources = config.get('sources', {}).get('youtube', [])
        enabled_sources = [s for s in youtube_sources if s.get('enabled')]
        
        if not enabled_sources:
            console.print("[yellow]警告:[/yellow] 没有启用的 YouTube 订阅源。请在 config/sources.yaml 中配置。")
            return
        
        all_new_videos = []
        
        for source in enabled_sources:
            name = source.get('name')
            channel_id = source.get('channel_id')
            console.print(f"正在扫描频道: [cyan]{name}[/cyan] ({channel_id})...")
            
            videos = fetch_channel_videos(channel_id, max_count=max_count, cookies_from_browser=cookies_from_browser, cookies_file=cookies_file)
            
            new_videos = []
            # 计算日期截止线
            cutoff_date = None
            if days > 0:
                cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
            
            for v in videos:
                # 过滤时长
                if min_duration > 0 and v.duration_minutes < min_duration:
                    continue
                
                # 过滤日期
                if cutoff_date and v.upload_date < cutoff_date:
                    continue
                
                if force or not state_manager.is_processed(v.video_id, 'youtube'):
                    new_videos.append(v)
            
            if new_videos:
                all_new_videos.extend(new_videos)
                console.print(f"  找到 [green]{len(new_videos)}[/green] 个新视频")
            else:
                console.print(f"  没有新视频")
        
        if not all_new_videos:
            console.print("[bold green]订阅源已是最新，无新内容需处理。[/bold green]")
            return
        
        # 显示列表供用户选择
        table = Table(title="待处理的新视频")
        table.add_column("序号", style="dim")
        table.add_column("发布日期")
        table.add_column("时长", style="cyan")
        table.add_column("频道")
        table.add_column("标题")
        
        for i, v in enumerate(all_new_videos, 1):
            table.add_row(str(i), v.formatted_date, f"{v.duration_minutes:.1f}m", v.channel_name, v.title)
        
        console.print(table)
        
        # 自动确认或用户确认
        should_process = yes or Confirm.ask(f"是否处理以上 {len(all_new_videos)} 个视频?")
        if should_process:
            for v in all_new_videos:
                process_single_video(v.url, archiver, state_manager, skip_ai, force, cookies_from_browser=cookies_from_browser, cookies_file=cookies_file, prompt_file=prompt_file, sync_feishu=sync_feishu)
        else:
            console.print("[yellow]已取消批量处理。[/yellow]")
            
    else:
        # 默认显示帮助
        with click.Context(main) as ctx:
            click.echo(ctx.get_help())


if __name__ == '__main__':
    main()
