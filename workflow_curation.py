"""
每日内容策展 Workflow Skill
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent


class CurationWorkflow:
    def __init__(self):
        self.main_script = PROJECT_ROOT / 'src' / 'python' / 'main.py'
        
    def run(self, min_duration: int = 15, days: int = 7, prompt_file: str = None, batch_mode: bool = True, url: str = None, cookies_file: str = None, cookies_browser: str = None, force: bool = False, auto_yes: bool = False, sync_feishu: bool = True):
        """运行内容策展工作流"""
        
        cmd = [sys.executable, str(self.main_script)]
        
        # 模式选择
        if url:
            cmd.extend(['--url', url])
        elif batch_mode:
            cmd.append('--batch')
            
        if force:
            cmd.append('--force')
            
        # 基础参数
        if min_duration > 0:
            cmd.extend(['--min-duration', str(min_duration)])
        
        if days > 0:
            cmd.extend(['--days', str(days)])
            
        if prompt_file:
            # 转换为绝对路径
            abs_prompt = os.path.abspath(prompt_file)
            cmd.extend(['--prompt-file', abs_prompt])
            
        # Cookies 支持
        if cookies_file:
            cmd.extend(['--cookies', os.path.abspath(cookies_file)])
        elif cookies_browser:
            cmd.extend(['--cookies-from-browser', cookies_browser])
        
        # 自动确认
        if auto_yes:
            cmd.append('--yes')
        
        # 飞书同步
        if sync_feishu:
            cmd.append('--sync-feishu')
            
        print(f"执行命令: {' '.join(cmd)}")
        
        try:
            # 交互式执行，保留用户输入能力
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"工作流执行失败: {e}")
        except KeyboardInterrupt:
            print("\n工作流已终止")


def main():
    parser = argparse.ArgumentParser(description="每日内容策展 Workflow Skill")
    
    # 核心参数
    parser.add_argument('--min-duration', type=int, default=15, help='最小视频时长（分钟），短于此时长的视频将被忽略 (默认: 15)')
    parser.add_argument('--days', type=int, default=7, help='仅处理最近 N 天内发布的视频 (默认: 7)')
    parser.add_argument('--prompt', dest='prompt_file', help='自定义 Prompt 文件路径')
    
    # 模式参数
    parser.add_argument('--url', help='直接处理指定的 YouTube URL')
    parser.add_argument('--batch', action='store_true', default=True, help='批量处理订阅源 (默认)')
    
    # Cookies 参数
    parser.add_argument('--cookies', help='cookies.txt 文件路径')
    parser.add_argument('--browser', dest='cookies_browser', help='从浏览器导出 cookies (如 chrome)')
    
    parser.add_argument('--force', action='store_true', help='强制重新处理')
    parser.add_argument('--yes', '-y', action='store_true', help='自动确认，跳过交互提示')
    parser.add_argument('--no-sync', dest='no_sync_feishu', action='store_true', help='禁用飞书同步 (默认开启)')
    
    args = parser.parse_args()
    
    # 处理逻辑：如果指定了 URL，则关闭 batch 模式
    batch_mode = args.batch
    if args.url:
        batch_mode = False
        
    workflow = CurationWorkflow()
    workflow.run(
        min_duration=args.min_duration,
        days=args.days,
        prompt_file=args.prompt_file,
        batch_mode=batch_mode,
        url=args.url,
        cookies_file=args.cookies,
        cookies_browser=args.cookies_browser,
        force=args.force,
        auto_yes=args.yes,
        sync_feishu=not args.no_sync_feishu
    )


if __name__ == '__main__':
    main()
