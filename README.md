# 每日内容策展自动化工作流 (V1)

这是一个自动化的内容策展工具，旨在从 YouTube 提取有价值的内容，通过 AI 生成深度摘要，并归档到本地。

## 核心功能

- **内容抓取**：自动提取 YouTube 视频详细信息、发布时间和封面图片。
- **转录生成**：自动获取视频字幕/转录（支持多语言）。
- **AI 改写**：调用 OpenAI 兼容接口，将原始转录改写为包含核心观点、关键洞察和金句的结构化中文摘要。
- **状态管理**：自动记录已处理的内容 ID，避免重复处理。
- **本地归档**：每个视频生成独立文件夹，包含元数据、转录、AI 改写结果及封面图片。

## 安装指南

### 1. 环境要求
- Python 3.8+
- Node.js 18+

### 2. 安装依赖
```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 安装 Node.js 依赖
cd src/node
npm install
cd ../..
```

## 配置说明

编辑 `config/sources.yaml` 文件：

1. **API 配置**：填写你的 OpenAI 兼容接口 API Key。
2. **订阅源**：在 `sources.youtube` 下添加你感兴趣的频道 ID。

```yaml
api:
  openai:
    api_key: "sk-xxxxxx"
    base_url: "https://api.openai.com/v1"
    model: "gpt-4o"

sources:
  youtube:
    - name: "示例频道"
      channel_id: "UCxxxxx"
      enabled: true
```

## 使用方法

### 1. URL 模式 (处理特定链接)
可以直接处理一个或多个 YouTube 视频：
```bash
python src/python/main.py --url "https://www.youtube.com/watch?v=xxx"
```

处理多个链接（逗号分隔）：
```bash
python src/python/main.py --url "url1,url2"
```

### 2. 批量模式 (扫描订阅源)
扫描 `sources.yaml` 中所有已启用的频道：
```bash
python src/python/main.py --batch
```
系统会列出未处理的新内容，待用户确认后开始处理。

### 3. 跳过 AI 改写 (仅获取转录)
如果你只想获取转录而不想消耗 API 额度：
```bash
python src/python/main.py --url "url" --skip-ai
```

### 4. 解决 Bot 检测问题
如果遇到 YouTube Bot 检测错误，可以使用你的本地浏览器 Cookies：
```bash
python src/python/main.py --url "url" --cookies-from-browser chrome
```
支持的浏览器：`chrome`, `firefox`, `edge`, `safari` 等。

## 归档结构

处理后的内容保存在 `output/` 目录下：
```
output/[日期]_[视频ID]/
├── metadata.md     # 元数据（标题、日期、嘉宾、金句等）
├── transcript.md   # 原始转录（带时间戳）
├── rewritten.md    # AI 改写后的深度摘要
├── rewritten.json  # AI 改写的原始数据
└── cover.jpg       # 视频封面图
```

## 后续计划 (V2)
- [ ] Bilibili 内容抓取与转录支持。
- [ ] 小宇宙播客抓取与转录支持。
- [ ] 飞书多维表格同步功能。
- [ ] 本地 Whisper 模型支持，解决无字幕视频。
