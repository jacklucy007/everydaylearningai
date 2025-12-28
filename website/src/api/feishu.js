/**
 * 飞书 Bitable API 客户端
 */
import { FEISHU_CONFIG } from '../config.js'

// 使用代理路径避免 CORS 问题（开发环境）
const API_BASE = '/feishu-api/open-apis'

class FeishuAPI {
    constructor() {
        this.token = null
        this.tokenExpires = null
    }

    /**
     * 获取 tenant_access_token
     */
    async getToken() {
        // 检查缓存的 token 是否有效
        if (this.token && this.tokenExpires && Date.now() < this.tokenExpires) {
            return this.token
        }

        const response = await fetch(`${API_BASE}/auth/v3/tenant_access_token/internal`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                app_id: FEISHU_CONFIG.APP_ID,
                app_secret: FEISHU_CONFIG.APP_SECRET
            })
        })

        const data = await response.json()

        if (data.code === 0) {
            this.token = data.tenant_access_token
            // Token 有效期 2 小时，提前 5 分钟刷新
            this.tokenExpires = Date.now() + (115 * 60 * 1000)
            return this.token
        }

        throw new Error(`获取 Token 失败: ${data.msg}`)
    }

    /**
     * 获取请求头
     */
    async getHeaders() {
        const token = await this.getToken()
        return {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    }

    /**
     * 获取表格记录
     */
    async getRecords(pageSize = 100, pageToken = null) {
        const headers = await this.getHeaders()
        const params = new URLSearchParams({ page_size: pageSize })
        if (pageToken) params.append('page_token', pageToken)

        const url = `${API_BASE}/bitable/v1/apps/${FEISHU_CONFIG.APP_TOKEN}/tables/${FEISHU_CONFIG.TABLE_ID}/records?${params}`

        const response = await fetch(url, { headers })
        return response.json()
    }

    /**
     * 获取所有记录
     */
    async getAllRecords() {
        const allRecords = []
        let pageToken = null

        while (true) {
            const result = await this.getRecords(100, pageToken)

            if (result.code !== 0) {
                console.error('Error fetching records:', result.msg)
                break
            }

            const items = result.data?.items || []
            allRecords.push(...items)

            pageToken = result.data?.page_token
            if (!pageToken) break
        }

        return allRecords
    }

    /**
     * 获取单条记录
     */
    async getRecordById(recordId) {
        const headers = await this.getHeaders()
        const url = `${API_BASE}/bitable/v1/apps/${FEISHU_CONFIG.APP_TOKEN}/tables/${FEISHU_CONFIG.TABLE_ID}/records/${recordId}`

        const response = await fetch(url, { headers })
        const result = await response.json()

        if (result.code === 0) {
            return result.data?.record
        }
        return null
    }

    /**
     * 解析记录为标准格式
     */
    static parseRecord(record) {
        const fields = record.fields || {}
        const recordId = record.record_id || ''

        // 提取文本值
        const getText = (fieldValue) => {
            if (Array.isArray(fieldValue)) {
                return fieldValue.map(item => item?.text || '').join('')
            }
            if (typeof fieldValue === 'object' && fieldValue !== null) {
                return fieldValue.text || String(fieldValue)
            }
            return fieldValue ? String(fieldValue) : ''
        }

        // 提取链接
        const getLink = (fieldValue) => {
            if (typeof fieldValue === 'object' && fieldValue !== null) {
                return fieldValue.link || fieldValue.text || ''
            }
            return fieldValue ? String(fieldValue) : ''
        }

        // 解析 JSON 数组
        const parseJsonArray = (fieldValue) => {
            const text = getText(fieldValue)
            if (!text) return []
            try {
                const result = JSON.parse(text)
                return Array.isArray(result) ? result : [result]
            } catch {
                // 如果不是 JSON，按换行分割
                return text.split('\n').filter(line => line.trim())
            }
        }

        // 提取日期
        const getDate = (fieldValue) => {
            if (typeof fieldValue === 'number') {
                return new Date(fieldValue).toISOString().split('T')[0]
            }
            return fieldValue ? String(fieldValue) : ''
        }

        // 提取视频ID
        const videoId = getText(fields['视频ID'])

        // 提取封面图 URL (支持 YouTube 封面回退)
        const getCoverUrl = (fieldValue) => {
            if (Array.isArray(fieldValue) && fieldValue.length > 0) {
                return fieldValue[0]?.url || ''
            }
            // 如果没有飞书封面但有视频ID，使用 YouTube 封面
            if (videoId) {
                return `https://img.youtube.com/vi/${videoId}/maxresdefault.jpg`
            }
            return ''
        }

        return {
            record_id: recordId,
            title: getText(fields['标题']),
            original_title: getText(fields['原标题']),
            channel: getText(fields['频道']),
            publish_date: getDate(fields['发布日期']),
            video_url: getLink(fields['视频链接']),
            video_id: videoId,
            duration: getText(fields['时长']),
            core_points: parseJsonArray(fields['核心观点']),
            key_insights: parseJsonArray(fields['关键洞察']),
            golden_quotes: parseJsonArray(fields['金句']),
            guests: parseJsonArray(fields['嘉宾']),
            summary: getText(fields['深度摘要']),
            cover_url: getCoverUrl(fields['封面']),
            processed_at: getDate(fields['处理时间']),
            channel_description: getText(fields['频道描述']),
            channel_icon: getText(fields['频道图标'])
        }
    }
}

// 导出单例
export const feishuAPI = new FeishuAPI()
export default feishuAPI
