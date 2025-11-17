# 用户界面模块

def menu():
    """
    显示主菜单
    """
    print("\n=== 数值系统测试工具 ===")
    print("1. 角色管理")
    print("2. 战斗模拟")
    print("3. 属性分析")
    print("4. 退出")  # 修复这里的语法错误
    print("=" * 25)

def character_menu():
    """
    显示角色管理菜单
    """
    print("\n--- 角色管理 ---\n")
    print("1. 添加单个角色")
    print("2. 生成随机角色")
    print("3. 批量生成随机角色")
    print("4. 列出所有角色")
    print("5. 返回主菜单")
    print("-" * 25)

def battle_menu():
    """
    显示战斗模拟菜单
    """
    print("\n--- 战斗模拟 ---")
    print("1. 单场战斗")
    print("2. 多次战斗统计")
    print("3. 死斗模式")  # 新增死斗模式选项
    print("4. 返回主菜单")  # 修改为4返回
    print("-" * 25)

def analysis_menu():
    """
    显示属性分析菜单
    """
    print("\n--- 属性分析 ---\n")
    print("1. 生成角色属性成长曲线")
    print("2. 返回主菜单")
    print("-" * 25)

def get_valid_input(prompt, input_type=int, default=None, min_value=None, max_value=None):
    """
    获取有效的用户输入
    """
    while True:
        try:
            user_input = input(prompt)
            if not user_input and default is not None:
                return default
                
            value = input_type(user_input)
            
            if min_value is not None and value < min_value:
                print(f"值必须大于或等于 {min_value}")
                continue
                
            if max_value is not None and value > max_value:
                print(f"值必须小于或等于 {max_value}")
                continue
                
            return value
        except ValueError:
            print(f"无效的输入，请输入{input_type.__name__}类型的值")