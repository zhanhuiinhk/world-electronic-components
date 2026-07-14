import json
import os

def search_components(keyword):
    data_dir = 'data'
    keyword = keyword.lower()
    found = False
    
    for filename in os.listdir(data_dir):
        if filename.endswith('.json'):
            with open(os.path.join(data_dir, filename), 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    for item in data:
                        if (keyword in item['part_number'].lower() or 
                            keyword in item['manufacturer'].lower() or
                            keyword in item['category'].lower()):
                            print(f"\n✅ 匹配到: {item['part_number']}")
                            print(f"   厂家: {item['manufacturer']} | 产地: {item.get('origin', '未知')}")
                            print(f"   分类: {item['category']} > {item['sub_category']}")
                            print(f"   手册: {item['datasheet_url']}")
                            found = True
                except json.JSONDecodeError:
                    print(f"文件 {filename} 格式有误，请检查。")
    
    if not found:
        print("未找到匹配元器件。")

if __name__ == "__main__":
    q = input("请输入要搜索的型号/厂家/分类: ")
    search_components(q)
