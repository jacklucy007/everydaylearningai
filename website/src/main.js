/**
 * 首页主入口
 */
import { feishuAPI } from './api/feishu.js'
import { CHANNELS_DATA, DEFAULT_CHANNEL } from './data/channels.js'

class App {
    constructor() {
        this.posts = []
        this.filteredPosts = []
        this.channels = []
        this.currentChannel = '' // 当前选中的频道
        this.init()
    }

    async init() {
        this.bindEvents()
        await this.loadPosts()
    }

    bindEvents() {
        // 搜索框回车
        document.getElementById('searchInput')?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.search()
            }
        })

        // 搜索输入实时筛选 (可选)
        document.getElementById('searchInput')?.addEventListener('input', (e) => {
            // 简单的防抖处理可以加在这里，这里直接调用
            this.search()
        })
    }

    async loadPosts() {
        try {
            this.showLoading(true)

            const records = await feishuAPI.getAllRecords()
            this.posts = records.map(r => feishuAPI.constructor.parseRecord(r))
                .filter(p => p.title && p.title.trim()) // 过滤无标题数据

            // 按发布日期降序排序
            this.posts.sort((a, b) => (b.publish_date || '').localeCompare(a.publish_date || ''))

            // 提取频道列表（包含元数据）
            const channelMap = new Map()

            this.posts.forEach(post => {
                if (!post.channel) return

                // 优先从帖子中获取元数据
                const feishuDesc = post.channel_description
                const feishuIcon = post.channel_icon

                if (!channelMap.has(post.channel)) {
                    // 如果 Map 中没有，初始化（尝试使用 Feishu 数据，如果没有则回退到本地配置）
                    const localMeta = CHANNELS_DATA[post.channel] || DEFAULT_CHANNEL
                    channelMap.set(post.channel, {
                        name: post.channel,
                        description: feishuDesc || localMeta.description,
                        icon: feishuIcon || localMeta.icon,
                        fromFeishu: !!feishuDesc // 标记是否已经有了 Feishu 的数据
                    })
                } else {
                    // 如果 Map 中已有，且当前帖子有 Feishu 数据而 Map 中没有（或标记为非 Feishu），则更新
                    // 这样可以确保只要有一条帖子带了元数据，就能应用到频道上
                    const current = channelMap.get(post.channel)
                    if (feishuDesc && !current.fromFeishu) {
                        current.description = feishuDesc
                        current.icon = feishuIcon || current.icon
                        current.fromFeishu = true
                    }
                }
            })

            // 转换为数组并排序
            this.channels = Array.from(channelMap.values()).sort((a, b) => a.name.localeCompare(b.name))

            this.renderChannelGrid()
            this.filterPosts()

        } catch (error) {
            console.error('加载数据失败:', error)
            this.showEmpty()
        } finally {
            this.showLoading(false)
        }
    }

    renderChannelGrid() {
        const grid = document.getElementById('channelGrid')
        if (!grid) return

        // "全部" 按钮
        let html = `
            <button class="channel-btn ${this.currentChannel === '' ? 'active' : ''}" 
                    onclick="window.app.setChannel('')">
                <span class="channel-icon">✨</span>
                <span class="channel-name">全部推荐</span>
                <span class="channel-desc">汇聚所有优质创作者的精彩观点</span>
            </button>
        `

        // 各频道按钮
        this.channels.forEach(channel => {
            const isActive = this.currentChannel === channel.name

            html += `
                <button class="channel-btn ${isActive ? 'active' : ''}" 
                        onclick="window.app.setChannel('${channel.name}')">
                    <span class="channel-icon">${channel.icon}</span>
                    <span class="channel-name">${channel.name}</span>
                    <span class="channel-desc">${channel.description}</span>
                </button>
            `
        })

        grid.innerHTML = html
    }

    setChannel(channel) {
        this.currentChannel = channel
        this.renderChannelGrid() // 重新渲染以更新激活状态
        this.filterPosts()
    }

    filterPosts() {
        const channel = this.currentChannel
        const keyword = document.getElementById('searchInput')?.value?.toLowerCase() || ''

        this.filteredPosts = this.posts.filter(post => {
            const matchChannel = !channel || post.channel === channel
            const matchKeyword = !keyword ||
                post.title?.toLowerCase().includes(keyword) ||
                post.summary?.toLowerCase().includes(keyword) ||
                post.core_points?.some(p => p.toLowerCase().includes(keyword))

            return matchChannel && matchKeyword
        })

        this.renderPosts()
    }

    search() {
        this.filterPosts()
    }

    async refresh() {
        await this.loadPosts()
    }

    renderPosts() {
        const grid = document.getElementById('postsGrid')
        const empty = document.getElementById('emptyState')

        if (!grid) return

        if (this.filteredPosts.length === 0) {
            grid.style.display = 'none'
            if (empty) empty.style.display = 'flex'
            return
        }

        if (empty) empty.style.display = 'none'
        grid.style.display = 'grid'

        grid.innerHTML = this.filteredPosts.map(post => this.renderPostCard(post)).join('')

        // 绑定卡片点击事件
        grid.querySelectorAll('.post-card').forEach(card => {
            card.addEventListener('click', () => {
                const recordId = card.dataset.recordId
                window.open(`/detail.html?id=${recordId}`, '_blank')
            })
        })
    }

    renderPostCard(post) {
        const coverHtml = post.cover_url
            ? `<img src="${post.cover_url}" alt="${post.title}" loading="lazy">`
            : `<div class="post-cover-placeholder"><span>${(post.channel || '📄').slice(0, 2)}</span></div>`

        const pointsHtml = post.core_points?.slice(0, 2).map(point =>
            `<li>${this.truncate(point, 80)}</li>`
        ).join('') || ''

        const quoteHtml = post.golden_quotes?.[0]
            ? `<blockquote class="post-quote">"${this.truncate(post.golden_quotes[0], 100)}"</blockquote>`
            : ''

        return `
      <article class="post-card" data-record-id="${post.record_id}">
        <div class="post-cover">${coverHtml}</div>
        <div class="post-content">
          <div class="post-meta">
            <span class="post-channel">${post.channel || '未知频道'}</span>
            <span class="post-date">${post.publish_date || ''}</span>
          </div>
          <h2 class="post-title">${post.title || post.original_title || '无标题'}</h2>
          ${pointsHtml ? `<ul class="post-points">${pointsHtml}</ul>` : ''}
          ${quoteHtml}
        </div>
      </article>
    `
    }

    truncate(text, maxLength) {
        if (!text) return ''
        return text.length > maxLength ? text.slice(0, maxLength) + '...' : text
    }

    showLoading(show) {
        const loading = document.getElementById('loadingState')
        const grid = document.getElementById('postsGrid')

        if (loading) loading.style.display = show ? 'flex' : 'none'
        if (grid && !show) grid.style.display = 'grid'
    }

    showEmpty() {
        const grid = document.getElementById('postsGrid')
        const empty = document.getElementById('emptyState')

        if (grid) grid.style.display = 'none'
        if (empty) empty.style.display = 'flex'
    }
}

// 初始化应用
window.app = new App()
