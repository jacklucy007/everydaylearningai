"""
飞书多维表格 API 测试脚本 - Wiki 嵌入版本
"""

import requests
import json

# 用户提供的凭证
APP_ID = "cli_a9c5634f83b8dbc0"
APP_SECRET = "8W9t4DvjXgprdlKb76yIuftgX7NKvnHf"
APP_TOKEN = "WkTfbPXDpaXvnMstxO5cLahynXc"
TABLE_ID = "tblgSjcuaZSWa1OA"

def get_tenant_access_token():
    """获取 tenant_access_token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = {
        "app_id": APP_ID,
        "app_secret": APP_SECRET
    }
    response = requests.post(url, json=payload)
    data = response.json()
    if data.get("code") == 0:
        return data.get("tenant_access_token")
    else:
        print(f"获取 token 失败: {data}")
        return None

def get_table_fields(token):
    """获取表格字段列表"""
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/fields"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers)
    return response.json()

def list_tables(token):
    """列出多维表格中的所有数据表"""
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers)
    return response.json()

def create_record(token, fields_data):
    """创建一条记录"""
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "fields": fields_data
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

if __name__ == "__main__":
    print("=" * 60)
    print("飞书多维表格 API 调试 (Wiki 嵌入版)")
    print("=" * 60)
    print(f"App Token: {APP_TOKEN}")
    print(f"Table ID:  {TABLE_ID}")
    print(f"URL: https://ai.feishu.cn/wiki/{APP_TOKEN}?table={TABLE_ID}")
    
    print("\n[1] 获取 tenant_access_token...")
    token = get_tenant_access_token()
    if not token:
        print("    ✗ 获取 Token 失败")
        exit(1)
    print(f"    ✓ Token: {token[:30]}...")
    
    print("\n[2] 测试列出数据表...")
    tables = list_tables(token)
    code = tables.get('code')
    msg = tables.get('msg')
    print(f"    响应: code={code}, msg={msg}")
    
    if code == 0:
        items = tables.get('data', {}).get('items', [])
        print(f"    ✓ 成功！找到 {len(items)} 个数据表:")
        for t in items:
            print(f"      - {t.get('name')} (table_id: {t.get('table_id')})")
    elif code == 91402:
        print("\n    ✗ 错误 91402: 应用无权访问此多维表格")
        print("\n    【解决方案】")
        print("    由于您的多维表格在 Wiki 知识库中，需要额外授权：")
        print("")
        print("    方式一：开放平台配置权限")
        print("    1. 访问 https://open.feishu.cn/app")
        print("    2. 进入应用 → 权限管理 → 添加权限")
        print("    3. 搜索并启用以下权限：")
        print("       - bitable:app (查看、评论、编辑和管理多维表格)")
        print("       - wiki:wiki (获取知识空间信息)")
        print("    4. 发布应用版本")
        print("")
        print("    方式二：在知识库中授权")
        print("    1. 打开知识库设置")
        print("    2. 找到「成员设置」或「权限设置」")
        print("    3. 将应用添加为协作者")
    else:
        print(f"    其他错误: {tables}")
    
    print("\n[3] 测试获取字段...")
    fields = get_table_fields(token)
    code = fields.get('code')
    print(f"    响应: code={code}, msg={fields.get('msg')}")
    
    if code == 0:
        items = fields.get('data', {}).get('items', [])
        print(f"    ✓ 成功！找到 {len(items)} 个字段:")
        for f in items:
            print(f"      - {f.get('field_name')} (type: {f.get('type')}, id: {f.get('field_id')})")
