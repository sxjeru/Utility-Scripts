import json
import sys
import shutil
from pathlib import Path

def process_merges(data):
    """
    https://github.com/CheshireCC/faster-whisper-GUI/issues/292
    处理 tokenizer.json 中的 model.merges 项
    将形如 ["Ġpalab", "ra"] 的数组转换为 "Ġpalab ra"
    """
    processed_count = 0
    
    # 检查是否存在model.merges路径
    if not isinstance(data, dict) or 'model' not in data:
        print("警告: JSON文件中未找到'model'字段")
        return data, processed_count
    
    if not isinstance(data['model'], dict) or 'merges' not in data['model']:
        print("警告: JSON文件中未找到'model.merges'字段")
        return data, processed_count
    
    merges = data['model']['merges']
    if not isinstance(merges, list):
        print("警告: 'model.merges'不是列表格式")
        return data, processed_count
    
    # 处理merges中的每一项
    for i, item in enumerate(merges):
        # 检查是否为包含两个字符串元素的列表
        if (isinstance(item, list) and 
            len(item) == 2 and 
            all(isinstance(x, str) for x in item)):
            
            # 将两个元素合并为一个字符串，用空格分隔
            merged_string = " ".join(item)
            merges[i] = merged_string
            processed_count += 1
            print(f"处理项 {i+1}: {item} -> {merged_string}")
    
    return data, processed_count

def backup_file(file_path):
    """
    备份原文件，添加-bak后缀
    """
    file_path = Path(file_path)
    backup_path = file_path.with_stem(file_path.stem + '-bak')
    
    try:
        shutil.copy2(file_path, backup_path)
        print(f"原文件已备份为: {backup_path}")
        return True
    except Exception as e:
        print(f"备份文件失败: {e}")
        return False

def process_json_file(file_path):
    """
    处理JSON文件的主函数
    """
    file_path = Path(file_path)
    
    # 检查文件是否存在
    if not file_path.exists():
        print(f"错误: 文件不存在 - {file_path}")
        return False
    
    # 检查文件扩展名
    if file_path.suffix.lower() != '.json':
        print(f"错误: 不是JSON文件 - {file_path}")
        return False
    
    print(f"开始处理文件: {file_path}")
    
    try:
        # 读取JSON文件
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 处理数据
        processed_data, processed_count = process_merges(data)
        
        # 备份原文件
        if not backup_file(file_path):
            return False
        
        # 保存处理后的数据到原文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(processed_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n处理完成!")
        print(f"处理的条目数: {processed_count}")
        print(f"修改后的文件已保存到: {file_path}")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"错误: JSON文件格式无效 - {e}")
        return False
    except Exception as e:
        print(f"错误: 处理文件时发生异常 - {e}")
        return False

def get_file_path_interactive():
    """
    交互式获取文件路径
    """
    while True:
        file_path = input("\n请输入 tokenizer.json 文件路径 (或输入 'q' 退出): ").strip()
        
        if file_path.lower() == 'q':
            return None
        
        # 去除可能的引号
        file_path = file_path.strip('"\'')
        
        if file_path:
            return file_path
        else:
            print("请输入有效的文件路径")

def main():
    # 检查命令行参数（支持拖拽文件）
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        print(f"检测到拖拽文件: {file_path}")
        
        if process_json_file(file_path):
            print("\n文件处理成功!")
        else:
            print("\n文件处理失败!")
    else:
        # 交互式模式
        print("未检测到拖拽文件，进入交互模式")
        
        while True:
            file_path = get_file_path_interactive()
            
            if file_path is None:
                print("退出程序")
                break
            
            if process_json_file(file_path):
                print("\n文件处理成功!")
            else:
                print("\n文件处理失败!")
            
            # 询问是否继续处理其他文件
            while True:
                continue_choice = input("\n是否继续处理其他文件? (y/n): ").strip().lower()
                if continue_choice in ['y', 'yes', '是']:
                    break
                elif continue_choice in ['n', 'no', '否']:
                    print("退出程序")
                    return
                else:
                    print("请输入 y 或 n")
    
    # 程序结束前等待用户输入
    input("\n按Enter键退出...")

if __name__ == "__main__":
    main()
