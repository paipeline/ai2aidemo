import json
def save_dict_to_json(data, file_path):
    """
    将字典保存为 JSON 文件。

    参数:
    data (dict): data path
    file_path (str): JSON path
    """
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)