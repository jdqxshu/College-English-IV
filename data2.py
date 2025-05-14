#这个代码想实现自动统计两公里内POIs的个数
import requests
import pandas as pd
from urllib.parse import urlencode

# 百度地图API配置
host = "https://api.map.baidu.com"
uri = "/place/v2/search"
ak = "FLDHZEgQh06z37MSyiMT65SS1YnFrsk0"  # 请替换为您的实际AK

# 定义请求参数
object = "美食"
object2 = "shangch"
radius = 5000  # 2公里范围
weidu=39.843393
jingdu=116.32388500000002


def get_poi_count(query, location, radius, ak):
    """获取指定范围内POI的总数量"""
    params = {
        "query": query,
        "location": location,
        "radius": radius,
        "output": "json",
        "ak": ak,
        "page_size": 1,  # 最小化数据返回
        "page_num": 0
    }
    
    try:
        response = requests.get(host + uri, params=params, timeout=10)
        data = response.json()
        if data.get('status') == 0:
            return data.get('total', 0)
        else:
            print(f"获取数量失败: {data.get('message')}")
            return 0
    except Exception as e:
        print(f"API请求异常: {str(e)}")
        return 0

def get_poi_details(query, location, radius, ak):
    """获取POI详细信息"""
    all_results = []
    total_count = get_poi_count(query, location, radius, ak)
    
    if total_count == 0:
        return pd.DataFrame()
    
    print(f"开始获取 {query} 数据，共发现 {total_count} 个POI...")
    
    # 分页获取所有数据
    page_size = 20  # 百度API每页最大值
    for page_num in range(0, (total_count // page_size) + 1):
        params = {
            "query": query,
            "location": location,
            "radius": radius,
            "output": "json",
            "ak": ak,
            "page_size": page_size,
            "page_num": page_num
        }
        
        try:
            response = requests.get(host + uri, params=params, timeout=10)
            data = response.json()
            
            if data.get('status') == 0:
                results = data.get('results', [])
                all_results.extend(results)
                print(f"已获取 {len(all_results)}/{total_count} 条数据", end='\r')
            else:
                print(f"第{page_num+1}页获取失败: {data.get('message')}")
                
        except Exception as e:
            print(f"第{page_num+1}页请求异常: {str(e)}")
    
    # 转换为DataFrame
    if all_results:
        df = pd.DataFrame([
            {
                'name': item.get('name'),
                'address': item.get('address'),
                'province': item.get('province'),
                'city': item.get('city'),
                'area': item.get('area'),
                'latitude': item.get('location', {}).get('lat'),
                'longitude': item.get('location', {}).get('lng'),
                'distance': item.get('distance'),
                'uid': item.get('uid')
            }
            for item in all_results
        ])
        return df
    else:
        return pd.DataFrame()

# 主程序
if __name__ == "__main__":
    location = f"{weidu},{jingdu}"  # 中心点坐标
    
    # 1. 先获取POI总数
    poi_count = get_poi_count(object, location, radius, ak)
    print(f"\n 在{radius/1000}公里范围内共有 {poi_count} 个{object}POI")
    
    # 2. 获取详细数据
    df = get_poi_details(object, location, radius, ak)
    
    if not df.empty:
        # 保存为CSV文件
        csv_filename = f'{object2}_locations.csv'
        df.to_csv(csv_filename, index=False, encoding='utf_8_sig')
        
        # 添加统计信息到文件开头
        with open(csv_filename, 'r+', encoding='utf-8') as f:
            content = f.read()
            f.seek(0)
            f.write(f"# 2公里范围内{object}POI总数: {poi_count}\n")
            f.write(f"# 实际获取数据量: {len(df)}\n")
            f.write(content)
        
        print(f"\n成功保存 {len(df)} 条{object}数据到 {csv_filename}")
        print("文件字段包括:", ', '.join(df.columns))
    else:
        print("未获取到有效数据")