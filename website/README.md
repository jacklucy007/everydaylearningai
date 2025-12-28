# 每日内容策展 - 前端网站

这是一个独立的前端项目，用于展示飞书多维表格中的策展内容。

## 项目结构

```
website/
├── index.html          # 首页入口
├── detail.html         # 详情页
├── package.json        # 依赖配置
├── vite.config.js      # Vite 构建配置
└── src/
    ├── main.js         # 首页逻辑
    ├── detail.js       # 详情页逻辑
    ├── config.js       # 配置文件
    ├── api/
    │   └── feishu.js   # 飞书 API 客户端
    └── styles/
        └── main.css    # 主样式表
```

## 快速开始

### 1. 安装依赖

```bash
cd website
npm install
```

### 2. 开发模式

```bash
npm run dev
```

浏览器访问 http://localhost:3000

### 🚀 部署指南 (Deploy with Vercel)

本项目已经配置了 `vercel.json`，支持一键部署到 Vercel，并自动处理飞书 API 的跨域代理。

### 1. 推送到 GitHub
将本项目提交并推送到你的 GitHub 仓库：

```bash
git add .
git commit -m "feat: init website"
git push
```

### 2. 在 Vercel 上导入
1.  登录 [Vercel Dashboard](https://vercel.com/dashboard)
2.  点击 **"Add New..."** -> **"Project"**
3.  导入你刚刚推送的 GitHub 仓库
5.  **配置环境变量 (Environment Variables)**:
    *   在部署前的 Configure Project 页面，展开 **Environment Variables**
    *   根据 `.env.example` 填入以下变量：
        *   `VITE_FEISHU_APP_ID`
        *   `VITE_FEISHU_APP_SECRET`
        *   `VITE_FEISHU_APP_TOKEN`
        *   `VITE_FEISHU_TABLE_ID`
6.  点击 **Deploy**

### 3. API 代理说明
由于浏览器安全策略 (CORS)，前端无法直接访问飞书 API。
*   **开发环境**: `vite.config.js` 中的 `server.proxy` 负责代理。
*   **生产环境 (Vercel)**: `vercel.json` 中的 `rewrites` 规则会将 `/feishu-api/*` 的请求转发到 `https://open.feishu.cn/*`，从而完美解决跨域问题。

---

## 🛠 开发 (Development)

### 3. 生产构建

```bash
npm run build
```

构建产物在 `dist/` 目录，可直接部署到任何静态托管服务。

## 配置说明

编辑 `src/config.js` 更新飞书应用配置：

```javascript
export const FEISHU_CONFIG = {
  APP_ID: 'your_app_id',
  APP_SECRET: 'your_app_secret',
  APP_TOKEN: 'your_bitable_app_token',
  TABLE_ID: 'your_table_id'
}
```

## 部署选项

### Vercel

```bash
npm i -g vercel
vercel
```

### Netlify

1. 推送代码到 GitHub
2. 连接 Netlify
3. 设置构建命令: `npm run build`
4. 设置发布目录: `dist`

### 静态服务器

```bash
npm run build
npx serve dist
```

## 功能特点

- ✨ 现代深色主题设计
- 📱 响应式布局，支持移动端
- 🔍 频道筛选和关键词搜索
- 📝 Markdown 摘要渲染
- ⚡ Vite 构建，快速热更新
- 🚀 可独立部署，与后端完全解耦
