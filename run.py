# 快速运行脚本
import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 初始化数据库和属性配置
from data.sqlite_handler import init_db, get_attribute_config
print("正在初始化数据库...")
init_db()  # 初始化数据库和表结构
print("数据库初始化完成")
print("正在加载属性配置...")
get_attribute_config()  # 加载属性配置
print("属性配置加载完成")

# 导入并运行主程序
from main.app import main

if __name__ == "__main__":
    main()