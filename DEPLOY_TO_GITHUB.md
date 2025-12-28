# 如何上传代码到 GitHub

本项目已配置好所有安全保护措施，你可以放心地将整个项目上传到 GitHub。

## 1. 检查准备工作
以下敏感文件已被 `.gitignore` 自动排除，**不会**被上传：
- [x] `.env` (包含所有 API Key)
- [x] `output/` (本地产生的视频归档)
- [x] `node_modules/` (依赖包)
- [x] `__pycache__` (Python 缓存)

以下文件**会**被上传（供他人参考）：
- [x] `.env.example` (配置模板，无密钥)
- [x] `config/sources.yaml` (其中的 Key 已被替换为占位符)
- [x] `website/` (前端源代码)
- [x] `src/` (脚本源代码)

## 2. 执行上传 (命令行)

在项目根目录 (`c:\Users\tianx\Desktop\pic\jiangzao`) 打开终端，运行：

```bash
# 1. 初始化 Git 仓库 (如果没有)
git init

# 2. 添加所有文件
git add .

# 3. 提交代码
git commit -m "feat: initial release of content curation workflow and website"

# 4. 关联远程仓库 (请替换为你的真实 GitHub 地址)
# git remote add origin https://github.com/你的用户名/你的仓库名.git

# 5. 推送
# git branch -M main
# git push -u origin main
```

## 3. 下一步
上传成功后，去 Vercel 导入这个 GitHub 仓库。
记得在 Vercel 的 **Environment Variables** 设置中，把本地 `.env` 文件里的 `VITE_FEISHU_...` 变量填进去（不需要填后端的 OPENAI KEY，除非你在 Vercel 上跑后端 Function）。
