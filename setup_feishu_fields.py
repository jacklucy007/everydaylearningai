"""
飞书多维表格字段创建脚本
为内容策展工作流创建必要的字段
"""

import requests
import json

# 凭证配置
APP_ID = "cli_a9c5634f83b8dbc0"
APP_SECRET = "8W9t4DvjXgprdlKb76yIuftgX7NKvnHf"
APP_TOKEN = "WkTfbPXDpaXvnMstxO5cLahynXc"
TABLE_ID = "tblgSjcuaZSWa1OA"

def get_tenant_access_token():
    """获取 tenant_access_token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = {"app_id": APP_ID, "app_secret": APP_SECRET}
    response = requests.post(url, json=payload)
    data = response.json()
    return data.get("tenant_access_token") if data.get("code") == 0 else None

def create_field(token, field_name, field_type):
    """
    创建字段
    field_type: 1=文本, 2=数字, 3=单选, 4=多选, 5=日期, 7=复选框, 11=人员, 13=电话, 15=超链接, 17=附件, 18=关联, 19=单向关联, 20=公式, 21=创建时间, 22=修改时间, 23=创建人, 24=修改人
    """
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/fields"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "field_name": field_name,
        "type": field_type
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

# 需要创建的字段
FIELDS_TO_CREATE = [
    ("标题", 1),           # 文本
    ("原标题", 1),         # 文本
    ("频道", 1),           # 文本
    ("发布日期", 5),       # 日期
    ("视频链接", 15),      # 超链接
    ("视频ID", 1),         # 文本
    ("时长", 1),           # 文本
    ("核心观点", 1),       # 文本 (多行)
    ("关键洞察", 1),       # 文本 (多行)
    ("金句", 1),           # 文本 (多行)
    ("嘉宾", 1),           # 文本
    ("深度摘要", 1),       # 文本 (多行)
    ("封面", 17),          # 附件
    ("处理时间", 5),       # 日期
    ("频道描述", 1),       # 文本
    ("频道图标", 1),       # 文本
]

if __name__ == "__main__":
    print("正在获取 Token...")
    token = get_tenant_access_token()
    if not token:
        print("获取 Token 失败")
        exit(1)
    print(f"✓ Token 获取成功")
    
    print("\n正在创建字段...")
    for field_name, field_type in FIELDS_TO_CREATE:
        result = create_field(token, field_name, field_type)
        code = result.get('code')
        if code == 0:
            field_id = result.get('data', {}).get('field', {}).get('field_id')
            print(f"  ✓ {field_name} (field_id: {field_id})")
        elif code == 1254043:
            print(f"  - {field_name} (已存在)")
        else:
            print(f"  ✗ {field_name} 创建失败: {result.get('msg')}")
    
    print("\n完成！")
