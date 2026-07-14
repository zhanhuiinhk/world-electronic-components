import json
import os

def search_components(keyword):
    # 自动遍历 data 目录下的所有 json 文件
    data_dir = 'data'
    keyword = keyword.lower()
    
    for filename in os.listdir(data_dir):
        if filename.endswith('.json'):
            with open(os.path.join(data_dir, filename), 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    if (keyword in item['part_number'].lower() or 
                        keyword in item['manufacturer'].lower()):
                        print(f"找到匹配: {item['part_number']} | 厂家: {item['manufacturer']} | 资料: {item['datasheet_url']}")

if __name__ == "__main__":
    q = input("请输入要搜索的元器件型号或厂家: ")
    search_components(q)
