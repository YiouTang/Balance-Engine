# 快速运行脚本
import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 初始化属性配置
from data.xml_handler import get_attribute_config
print("正在初始化属性配置...")
get_attribute_config()  # 这将自动创建配置文件（如果不存在）
print("属性配置初始化完成")

# 导入并运行主程序
from main.app import main

if __name__ == "__main__":
    main()