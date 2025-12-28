---
description: Daily Content Curation (Fetch YouTube, Transcribe, AI Rewrite, Sync to Feishu)
---

自动化内容策展：抓取新视频 → 字幕 → AI 改写 → 飞书同步

**默认**：近 7 天、15 分钟以上、自动同步飞书

# 处理单个视频

// turbo
1. 处理并同步
```bash
python workflow_curation.py --url "{URL}" --yes
```

# 批量处理

// turbo
1. 处理所有订阅源新视频
```bash
python workflow_curation.py --yes
```

# 禁用飞书同步

```bash
python workflow_curation.py --yes --no-sync
```
