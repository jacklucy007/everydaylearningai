/**
 * 飞书多维表格配置
 * 从主项目 config/sources.yaml 复制配置信息
 */
export const FEISHU_CONFIG = {
    // 飞书应用凭证 (从环境变量加载)
    APP_ID: import.meta.env.VITE_FEISHU_APP_ID,
    APP_SECRET: import.meta.env.VITE_FEISHU_APP_SECRET,

    // 多维表格配置
    APP_TOKEN: import.meta.env.VITE_FEISHU_APP_TOKEN,
    TABLE_ID: import.meta.env.VITE_FEISHU_TABLE_ID
}

/**
 * 网站配置
 */
export const SITE_CONFIG = {
    title: '每日内容策展',
    description: 'AI驱动的深度内容解读，精选优质创作者的核心观点与洞察',
    postsPerPage: 12
}
