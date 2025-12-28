/**
 * 详情页逻辑
 */
import { feishuAPI } from './api/feishu.js'
import { marked } from 'marked'

class DetailPage {
    constructor() {
        this.init()
    }

    async init() {
        const recordId = this.getRecordId()

        if (!recordId) {
            this.showError()
            return
        }

        await this.loadPost(recordId)
    }

    getRecordId() {
        const params = new URLSearchParams(window.location.search)
        return params.get('id')
    }

    async loadPost(recordId) {
        try {
            this.showLoading(true)

            const record = await feishuAPI.getRecordById(recordId)

            if (!record) {
                this.showError()
                return
            }

            const post = feishuAPI.constructor.parseRecord(record)
            this.renderPost(post)

            // 更新页面标题
            document.title = `${post.title || '文章详情'} - 每日策展`

        } catch (error) {
            console.error('加载文章失败:', error)
            this.showError()
        } finally {
            this.showLoading(false)
        }
    }

    renderPost(post) {
        const container = document.getElementById('detailContent')
        if (!container) return

        container.style.display = 'block'

        // 封面
        const coverHtml = post.cover_url
            ? `<div class="detail-cover"><img src="${post.cover_url}" alt="${post.title}"></div>`
            : ''

        // 嘉宾
        const guestsHtml = post.guests?.length
            ? `<div class="detail-guests">
           <span class="guests-label">嘉宾：</span>
           ${post.guests.map(g => `<span class="guest-tag">${g}</span>`).join('')}
         </div>`
            : ''

        // 核心观点
        const corePointsHtml = post.core_points?.length
            ? `<section class="detail-section">
           <h2 class="section-title"><span class="section-icon">🎯</span>核心观点</h2>
           <ul class="core-points-list">
             ${post.core_points.map(p => `<li class="core-point-item">${p}</li>`).join('')}
           </ul>
         </section>`
            : ''

        // 关键洞察
        const insightsHtml = post.key_insights?.length
            ? `<section class="detail-section">
           <h2 class="section-title"><span class="section-icon">💡</span>关键洞察</h2>
           <div class="insights-grid">
             ${post.key_insights.map(i => `<div class="insight-card"><p>${i}</p></div>`).join('')}
           </div>
         </section>`
            : ''

        // 金句
        const quotesHtml = post.golden_quotes?.length
            ? `<section class="detail-section">
           <h2 class="section-title"><span class="section-icon">✨</span>金句精选</h2>
           <div class="quotes-container">
             ${post.golden_quotes.map(q => `<blockquote class="golden-quote"><p>"${q}"</p></blockquote>`).join('')}
           </div>
         </section>`
            : ''

        // 深度摘要
        const summaryHtml = post.summary
            ? `<section class="detail-section">
           <h2 class="section-title"><span class="section-icon">📝</span>深度摘要</h2>
           <div class="summary-content markdown-body">${marked.parse(post.summary)}</div>
         </section>`
            : ''

        container.innerHTML = `
      <!-- Back Navigation -->
      <div class="container">
        <a href="/" class="back-link">← 返回首页</a>
      </div>

      <!-- Hero Header -->
      <header class="detail-hero">
        <div class="container">
          ${coverHtml}
          <div class="detail-header-content">
            <div class="detail-meta">
              <span class="detail-channel">${post.channel || ''}</span>
              <span class="detail-date">${post.publish_date || ''}</span>
              ${post.duration ? `<span class="detail-duration">⏱️ ${post.duration}</span>` : ''}
            </div>
            <h1 class="detail-title">${post.title || '无标题'}</h1>
            ${post.original_title && post.original_title !== post.title
                ? `<p class="detail-original-title">原标题: ${post.original_title}</p>`
                : ''}
            ${guestsHtml}
            ${post.video_url
                ? `<a href="${post.video_url}" target="_blank" class="btn-watch">▶️ 观看原视频</a>`
                : ''}
          </div>
        </div>
      </header>

      <!-- Content Sections -->
      <div class="container detail-body">
        ${corePointsHtml}
        ${insightsHtml}
        ${quotesHtml}
        ${summaryHtml}
      </div>

      <!-- Footer Actions -->
      <div class="container detail-footer">
        <div class="detail-actions">
          ${post.video_url
                ? `<a href="${post.video_url}" target="_blank" class="action-btn primary">▶️ 观看原视频</a>`
                : ''}
          <button onclick="navigator.clipboard.writeText(window.location.href).then(() => alert('链接已复制'))" class="action-btn secondary">
            📋 复制链接
          </button>
          <a href="/" class="action-btn secondary">← 返回首页</a>
        </div>
      </div>
    `
    }

    showLoading(show) {
        const loading = document.getElementById('loadingState')
        if (loading) loading.style.display = show ? 'flex' : 'none'
    }

    showError() {
        this.showLoading(false)
        const content = document.getElementById('detailContent')
        const error = document.getElementById('errorState')

        if (content) content.style.display = 'none'
        if (error) error.style.display = 'flex'
    }
}

// 初始化
new DetailPage()
