# 每日内容策展展示平台（飞书多维表格驱动）

这是一个基于 Flask 的内容策展展示网站，数据来源于飞书多维表格。采用现代苹果设计风格，融合深色模式与渐变主题，提供沉浸式的阅读体验。

## 功能特点

### 1. 首页展示

- **内容卡片列表**
  - 视频封面图片（支持悬浮放大效果）
  - AI 生成的中文标题（加粗醒目）
  - 频道名称与发布日期标签
  - 核心观点预览（展示前3条）
  - 点击卡片新标签页打开详情

- **筛选与搜索**
  - 按频道筛选
  - 按日期范围筛选
  - 关键词搜索

### 2. 文章详情页

- **头部信息**
  - 大尺寸封面图
  - AI 生成标题 + 原标题
  - 频道、发布日期、视频时长
  - 嘉宾信息（如有）

- **核心内容区**
  - 🎯 核心观点（列表展示）
  - 💡 关键洞察（卡片式布局）
  - ✨ 金句精选（特殊引用样式）
  - 📝 深度摘要（Markdown 渲染）

- **互动元素**
  - 一键跳转原视频链接
  - 复制分享功能
  - 返回首页导航

## 技术栈

- **后端**：Python Flask 3.0.0
- **前端**：原生 HTML/CSS/JS，采用苹果设计风格
- **数据源**：飞书多维表格 Bitable API
- **样式**：CSS 变量 + Flexbox/Grid 布局

## 飞书多维表格字段说明

本项目需要以下字段结构（由 `setup_feishu_fields.py` 自动创建）：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| 标题 | 文本 | AI 生成的中文标题 |
| 原标题 | 文本 | 原始视频标题 |
| 频道 | 文本 | 内容来源频道名 |
| 发布日期 | 日期 | 原视频发布时间 |
| 视频链接 | 超链接 | 原视频 URL |
| 视频ID | 文本 | YouTube 视频 ID |
| 时长 | 文本 | 视频时长 |
| 核心观点 | 文本 | JSON 数组格式的核心观点列表 |
| 关键洞察 | 文本 | JSON 数组格式的关键洞察列表 |
| 金句 | 文本 | JSON 数组格式的精选金句 |
| 嘉宾 | 文本 | 视频嘉宾信息 |
| 深度摘要 | 文本 | Markdown 格式的详细摘要 |
| 封面 | 附件 | 视频封面图片 |
| 处理时间 | 日期 | 内容处理入库时间 |

## 快速开始

### 1. 项目结构

```
jiangzao/
├── README.md
├── readme01.md              # 本网站项目说明
├── requirements.txt
├── config/
│   └── sources.yaml         # 包含飞书配置
├── webapp/                  # 网站应用目录（待创建）
│   ├── app.py              # Flask 主应用
│   ├── config.py           # 配置文件
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css   # 主样式表
│   │   └── js/
│   │       └── main.js     # 前端交互
│   └── templates/
│       ├── base.html       # 基础模板
│       ├── index.html      # 首页
│       └── detail.html     # 详情页
└── output/                  # 本地归档数据
```

### 2. 安装依赖

```bash
pip install flask requests python-dotenv markdown
```

### 3. 配置飞书应用

从 `config/sources.yaml` 读取配置或新建 `webapp/config.py`：

```python
class Config:
    # 飞书应用配置（从 sources.yaml 复制）
    FEISHU_APP_ID = "cli_a9c5634f83b8dbc0"
    FEISHU_APP_SECRET = "your_app_secret"
    
    # 多维表格配置
    APP_TOKEN = "WkTfbPXDpaXvnMstxO5cLahynXc"
    TABLE_ID = "tblgSjcuaZSWa1OA"
```

### 4. 运行应用

```bash
cd webapp
python app.py
```

### 5. 访问网站

打开浏览器访问 http://localhost:5000

## 页面设计规范

### 颜色系统

```css
:root {
  /* 主色调 - 渐变紫蓝 */
  --primary: #7C3AED;
  --primary-light: #A78BFA;
  --primary-dark: #5B21B6;
  
  /* 强调色 */
  --accent: #F97316;
  --accent-light: #FDBA74;
  
  /* 中性色 */
  --bg-dark: #0F172A;
  --bg-card: #1E293B;
  --text-primary: #F1F5F9;
  --text-secondary: #94A3B8;
  
  /* 功能色 */
  --success: #10B981;
  --warning: #FBBF24;
  --error: #EF4444;
}
```

### 排版规范

- 标题字体：`'SF Pro Display', system-ui, sans-serif`
- 正文字体：`'SF Pro Text', 'PingFang SC', sans-serif`
- 代码字体：`'SF Mono', 'Fira Code', monospace`
- 行高：1.6（正文），1.3（标题）

### 动效指南

- 过渡时间：200ms（快速）、300ms（标准）、500ms（缓慢）
- 缓动函数：`cubic-bezier(0.4, 0, 0.2, 1)`
- 悬浮效果：轻微上移 + 阴影增强
- 加载动画：骨架屏 + 渐入效果

## API 接口设计

### 获取内容列表

```
GET /api/posts
Query: page, limit, channel, date_from, date_to, keyword
Response: { posts: [...], total: number, page: number }
```

### 获取单条内容

```
GET /api/posts/<record_id>
Response: { post: {...} }
```

### 数据格式

```json
{
  "record_id": "recXXXXXX",
  "title": "AI时代生存法则：掌握自主性，成为不可替代的通用型人才",
  "original_title": "Agency: The Most Important Skill of the Future",
  "channel": "Dan Koe",
  "publish_date": "2025-12-21",
  "video_url": "https://youtube.com/watch?v=XXXXX",
  "video_id": "0XI_Xt0ci2Y",
  "duration": "25:32",
  "core_points": [
    "自主性（Agency）是未来最重要的能力...",
    "AI不是高自主性人群的威胁..."
  ],
  "key_insights": [
    "自主性的本质不是简单的'无需许可的行动'...",
    "社会教育系统本质上是一种'大规模顺从武器'..."
  ],
  "golden_quotes": [
    "未来属于那些明白AI需要方向的人...",
    "自主性不是机械的顺从..."
  ],
  "guests": [],
  "summary": "## 自主性：AI时代的终极生存技能\n\n...",
  "cover_url": "https://...",
  "processed_at": "2025-12-27T20:00:00"
}
```

## 常见问题

### 1. 数据显示异常

- 检查飞书应用权限是否正确开启（需要 `bitable:record:read`）
- 验证多维表格的字段名称是否与配置完全一致
- 确认表格中已有数据记录

### 2. 封面图片不显示

- 飞书附件需要通过 Token 访问
- 可考虑将图片代理到本地服务器
- 或使用本地 `output/` 目录的封面备份

### 3. JSON 字段解析错误

- 核心观点、关键洞察、金句字段存储的是 JSON 数组字符串
- 前端需要 `JSON.parse()` 处理
- 后端可预处理为原生数组

## 后续优化方向

### Phase 1 - 基础功能

- [x] 首页内容列表展示
- [x] 详情页完整展示
- [ ] 分页与加载更多
- [ ] 响应式移动端适配

### Phase 2 - 增强体验

- [ ] 频道分类筛选
- [ ] 日期范围筛选
- [ ] 全文搜索功能
- [ ] 暗色/亮色主题切换

### Phase 3 - 高级功能

- [ ] 用户收藏功能
- [ ] 阅读历史记录
- [ ] RSS 订阅输出
- [ ] PWA 支持

## 项目维护

如需帮助或报告问题，请提供以下信息：

1. 完整的错误信息截图
2. 飞书应用配置截图（隐藏敏感信息）
3. 多维表格的字段结构截图
4. 浏览器控制台错误日志
