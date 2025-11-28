# 程序主入口
import os
import math
from data.sqlite_handler import load_character, load_all_characters, init_db
from logic.character_manager import add_character, generate_random_character, batch_generate_characters, list_characters as list_all_characters, get_all_available_attributes, get_attribute_display_name, get_attribute_description
from logic.battle import battle_between_characters
from utils.attribute_calculator import generate_level_attributes
from utils.chart_generator import plot_attribute_growth
from ui.menu import menu, character_menu, battle_menu, analysis_menu, get_valid_input
from core.damage import calculate_damage, calculate_critical_rate

# 数据库文件路径
DB_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "game_data.db")

# 初始化数据库
init_db()

# 在文件顶部导入成长曲线相关模块
from utils.growth_curve import linear_growth, exponential_growth, logarithmic_growth, power_growth, sigmoid_growth, hybrid_growth

# 注意：不再在模块级别缓存属性，而是在需要时动态获取

# 修改 handle_character_menu 函数中的相关部分
def display_character_info(character):
    """
    显示角色信息
    """
    print(f"\n=== 角色信息 ===")
    print(f"ID: {character.id}")
    print(f"名称: {character.name}")
    print(f"等级: {character.level}")
    
    # 获取所有属性并显示
    all_attributes = character.get_all_attributes() if hasattr(character, 'get_all_attributes') else {}
    if all_attributes:
        print("\n属性:")
        for attr_name, attr_value in all_attributes.items():
            # 对于百分比类型的属性，添加%符号
            display_name = get_attribute_display_name(attr_name)
            if attr_name in ['crit', 'crit_resist']:
                print(f"  {display_name} ({attr_name}): {attr_value}%")
            else:
                print(f"  {display_name} ({attr_name}): {attr_value}")
    else:
        # 兼容旧格式
        print(f"攻击力: {character.attack}")
        print(f"防御力: {character.defense}")
        print(f"生命值: {character.health}")
        print(f"暴击值: {character.crit}")
        print(f"暴抗值: {character.crit_resist}")
    
    # 显示自定义属性（如果有）
    if hasattr(character, 'custom_attributes') and character.custom_attributes:
        print("\n自定义属性:")
        for attr_name, attr_value in character.custom_attributes.items():
            display_name = get_attribute_display_name(attr_name)
            print(f"  {display_name} ({attr_name}): {attr_value}")
    
    # 显示成长曲线信息（如果有）
    if hasattr(character, 'growth_curve_type'):
        print(f"\n成长曲线类型: {character.growth_curve_type}")
    
    print("================\n")

def handle_character_menu():
    """
    处理角色管理菜单选项
    """
    while True:
        character_menu()
        choice = get_valid_input("请选择操作 (1-5): ", int, 1, 1, 5)
        
        if choice == 5:
            break
        
        elif choice == 1:
            print("\n--- 添加单个角色 ---")
            name = input("请输入角色名称: ").strip()
            if not name:
                print("角色名称不能为空")
                continue
                
            level = get_valid_input("请输入角色等级: ", int, 1, 1, None)
            
            # 基础属性输入
            print("\n请输入基础属性值:")
            attack = get_valid_input("攻击力: ", int, 1, 1, None)
            defense = get_valid_input("防御力: ", int, 1, 1, None)
            health = get_valid_input("生命值: ", int, 10, 1, None)
            crit = get_valid_input("暴击值: ", int, 0, 0, None)
            crit_resist = get_valid_input("暴抗值: ", int, 0, 0, None)
            
            # 创建属性字典
            character_attributes = {
                'attack': attack, 
                'defense': defense, 
                'health': health, 
                'crit': crit, 
                'crit_resist': crit_resist
            }
            
            # 询问是否添加自定义属性
            add_custom = input("\n是否添加自定义属性? (y/n): ").lower()
            if add_custom == 'y':
                while True:
                    print("\n可用属性列表:")
                    # 获取所有可用属性（从XML配置）
                    available_attributes = get_all_available_attributes()
                    # 如果没有可用属性，使用默认属性列表
                    if not available_attributes:
                        available_attributes = ['attack', 'defense', 'health', 'crit', 'crit_resist']
                    # 只显示可用的属性列表
                    for i, attr_name in enumerate(available_attributes, 1):
                        display_name = get_attribute_display_name(attr_name)
                        desc = get_attribute_description(attr_name)
                        print(f"{i}. {display_name} ({attr_name}): {desc}")
                    
                    print("\n请选择操作:")
                    print("1. 从上面的列表中选择属性")
                    print("2. 添加新的自定义属性")
                    print("3. 返回")
                    
                    choice = get_valid_input("请选择: ", int, 3, 1, 3)
                    
                    if choice == 3:
                        break
                    elif choice == 1:
                        if available_attributes:
                            attr_idx = get_valid_input(f"请选择属性编号 (1-{len(available_attributes)}): ", int, 1, 1, len(available_attributes))
                            attr_name = available_attributes[attr_idx - 1]
                            display_name = get_attribute_display_name(attr_name)
                            
                            try:
                                current_value = character_attributes.get(attr_name, 0)
                                print(f"当前值: {current_value}")
                                attr_value_input = input(f"请输入{display_name}的值: ")
                                # 尝试转换为数字
                                try:
                                    if '.' in attr_value_input:
                                        character_attributes[attr_name] = float(attr_value_input)
                                    else:
                                        character_attributes[attr_name] = int(attr_value_input)
                                except ValueError:
                                    # 如果转换失败，保留字符串
                                    character_attributes[attr_name] = attr_value_input
                            except Exception as e:
                                print(f"添加属性时出错: {e}")
                        else:
                            print("没有可用的属性")
                    elif choice == 2:
                        attr_name = input("请输入新属性名称: ")
                        attr_value_input = input(f"请输入{attr_name}的值: ")
                        # 尝试转换为数字
                        try:
                            if '.' in attr_value_input:
                                character_attributes[attr_name] = float(attr_value_input)
                            else:
                                character_attributes[attr_name] = int(attr_value_input)
                        except ValueError:
                            # 如果转换失败，保留字符串
                            character_attributes[attr_name] = attr_value_input
            
            # 询问是否指定ID
            use_custom_id = input("\n是否指定角色ID? (y/n，默认n): ").lower().strip()
            char_id = None
            if use_custom_id == 'y':
                char_id = get_valid_input("请输入角色ID: ", int, None, 1, None)
            
            # 添加角色，使用关键字参数传递所有属性
            add_character(
                DB_FILE, 
                name, 
                level=level, 
                char_id=char_id,
                **character_attributes
            )
        
        elif choice == 2:
            print("\n--- 生成随机角色 ---\n")
            use_custom_name = input("是否指定角色名称? (y/n，默认n): ").lower().strip()
            name = None
            if use_custom_name == 'y':
                name = input("请输入角色名称: ").strip()
                if not name:
                    print("使用随机名称")
                    name = None
                    
            level = get_valid_input("请输入角色等级 (影响属性范围): ", int, 1, 1, None)
            
            # 添加选择成长曲线类型的选项
            print("\n请选择成长曲线类型:")
            print("1. 线性成长 (默认)")
            print("2. 指数成长")
            print("3. 对数成长")
            print("4. 幂函数成长")
            print("5. S形成长")
            print("6. 混合成长")
            curve_choice = get_valid_input("请选择 (1-6): ", int, 1, 1, 6)
            
            # 映射选择到曲线类型
            curve_types = {
                1: "linear",
                2: "exponential",
                3: "logarithmic",
                4: "power",
                5: "sigmoid",
                6: "hybrid"
            }
            curve_type = curve_types[curve_choice]
            
            # 获取曲线参数
            curve_params = get_curve_parameters(curve_type)
            
            # 询问是否为每个属性设置不同的成长曲线类型
            use_attr_specific_curves = input("\n是否为每个属性设置不同的成长曲线类型? (y/n，默认n): ").lower().strip()
            attr_growth_curves = {}
            
            if use_attr_specific_curves == 'y':
                attr_growth_curves = get_attribute_specific_curves()
            
            # 使用选定的成长曲线生成角色
            generate_random_character(DB_FILE, name, level, curve_type, curve_params, attr_growth_curves)
        
        elif choice == 3:
            print("\n--- 批量生成随机角色 ---\n")
            count = get_valid_input("请输入生成角色数量: ", int, 5, 1, 100)
            start_level = get_valid_input("请输入起始等级: ", int, 1, 1, None)
            name_prefix = input("请输入名称前缀 (默认为'随机角色'): ").strip() or "随机角色"
            
            # 添加选择成长曲线类型的选项
            print("\n请选择成长曲线类型:")
            print("1. 线性成长 (默认)")
            print("2. 指数成长")
            print("3. 对数成长")
            print("4. 幂函数成长")
            print("5. S形成长")
            print("6. 混合成长")
            curve_choice = get_valid_input("请选择 (1-6): ", int, 1, 1, 6)
            
            # 映射选择到曲线类型
            curve_types = {
                1: "linear",
                2: "exponential",
                3: "logarithmic",
                4: "power",
                5: "sigmoid",
                6: "hybrid"
            }
            curve_type = curve_types[curve_choice]
            
            # 获取曲线参数
            curve_params = get_curve_parameters(curve_type)
            
            # 询问是否为每个属性设置不同的成长曲线类型
            use_attr_specific_curves = input("\n是否为每个属性设置不同的成长曲线类型? (y/n，默认n): ").lower().strip()
            attr_growth_curves = {}
            
            if use_attr_specific_curves == 'y':
                attr_growth_curves = get_attribute_specific_curves()
            
            # 使用选定的成长曲线批量生成角色
            batch_generate_characters(DB_FILE, count, start_level, name_prefix, curve_type, curve_params, attr_growth_curves)
        
        elif choice == 4:
            list_all_characters(DB_FILE)
            
            # 询问是否查看特定角色详情
            show_detail = input("\n是否查看特定角色详情? (y/n): ").lower()
            if show_detail == 'y':
                char_id = get_valid_input("请输入角色ID: ", int, None, 1, None)
                character = load_character(character_id=char_id, db_path=DB_FILE)
                if character:
                    display_character_info(character)
                else:
                    print("找不到该角色")
        
        # 添加修改角色属性功能
        elif choice == 6:
            print("\n--- 修改角色属性 ---")
            char_id = get_valid_input("请输入角色ID: ", int, None, 1, None)
            
            # 先加载角色，查看当前属性
            character = load_character(character_id=char_id, db_path=DB_FILE)
            if not character:
                print("找不到该角色")
                continue
            
            display_character_info(character)
            
            # 获取所有可用属性（从XML配置）
            available_attributes = get_all_available_attributes()
            # 如果没有可用属性，使用默认属性列表
            if not available_attributes:
                available_attributes = ['attack', 'defense', 'health', 'crit', 'crit_resist']
            
            # 属性显示名称映射
            def get_attribute_display_name(attr_name):
                attr_display_names = {
                    'attack': '攻击力',
                    'defense': '防御力',
                    'health': '生命值',
                    'crit': '暴击值',
                    'crit_resist': '暴抗值'
                }
                return attr_display_names.get(attr_name, attr_name)
            
            while True:
                print("\n可用属性列表:")
                # 结合系统属性和角色已有的属性
                all_attr_names = sorted(list(set(available_attributes + list(character.get_all_attributes().keys()))))
                for i, attr_name in enumerate(all_attr_names, 1):
                    display_name = get_attribute_display_name(attr_name)
                    current_value = character.get_attribute(attr_name, 0) if hasattr(character, 'get_attribute') else character.get_all_attributes().get(attr_name, 0)
                    print(f"{i}. {display_name} ({attr_name}): 当前值 {current_value}")
                
                print("\n请选择操作:")
                print("1. 从上面的列表中选择属性修改")
                print("2. 添加/修改自定义属性")
                print("3. 返回")
                
                choice = get_valid_input("请选择: ", int, 3, 1, 3)
                
                if choice == 3:
                    break
                elif choice == 1:
                    if all_attr_names:
                        attr_idx = get_valid_input(f"请选择属性编号 (1-{len(all_attr_names)}): ", int, 1, 1, len(all_attr_names))
                        attr_name = all_attr_names[attr_idx - 1]
                        display_name = get_attribute_display_name(attr_name)
                        current_value = character.get_attribute(attr_name, 0) if hasattr(character, 'get_attribute') else character.get_all_attributes().get(attr_name, 0)
                        
                        print(f"当前{display_name}值: {current_value}")
                        try:
                            value_input = input(f"请输入新的{display_name}值: ")
                            
                            # 尝试转换为数字
                            try:
                                if '.' in value_input:
                                    new_value = float(value_input)
                                else:
                                    new_value = int(value_input)
                            except ValueError:
                                # 如果转换失败，保留字符串
                                new_value = value_input
                            
                            # 修改属性（这里需要假设character_manager有modify_character_attribute方法）
                            print(f"属性{attr_name}已修改为{new_value}（注意：需要在character_manager中实现modify_character_attribute方法）")
                        except ValueError:
                            print("无效的数值，请重新输入")
                elif choice == 2:
                    attr_name = input("请输入新属性名称 (输入'q'取消): ").strip()
                    if attr_name.lower() == 'q':
                        continue
                    
                    try:
                        current_value = character.get_attribute(attr_name, 0) if hasattr(character, 'get_attribute') else character.get_all_attributes().get(attr_name, 0)
                        if current_value > 0:
                            print(f"当前值: {current_value}")
                        value_input = input(f"请输入{attr_name}的值: ")
                        
                        # 尝试转换为数字
                        try:
                            if '.' in value_input:
                                new_value = float(value_input)
                            else:
                                new_value = int(value_input)
                        except ValueError:
                            # 如果转换失败，保留字符串
                            new_value = value_input
                        
                        print(f"属性{attr_name}已修改为{new_value}（注意：需要在character_manager中实现modify_character_attribute方法）")
                    except ValueError:
                        print("无效的数值，请重新输入")
        
        input("\n按回车键继续...")

# 在handle_battle_menu函数中添加死斗选项
def handle_battle_menu():
    """
    处理战斗模拟菜单选项
    """
    while True:
        battle_menu()
        choice = get_valid_input("请选择操作 (1-4): ", int, 1, 1, 4)  # 修改范围为1-4
        
        if choice == 4:  # 修改为4返回主菜单
            break
        
        # 先列出所有角色供用户选择
        list_all_characters(DB_FILE)
        
        if choice == 1:
            print("\n--- 单场战斗 ---\n")
            attacker_id = get_valid_input("请输入攻击方角色ID: ", int, None, 1, None)
            defender_id = get_valid_input("请输入防御方角色ID: ", int, None, 1, None)
            
            result = battle_between_characters(DB_FILE, attacker_id, defender_id)
            if result:
                print(f"\n{result['attacker']['name']} 攻击 {result['defender']['name']}")
                print(f"伤害: {result['battle_results'][0]['damage']}, 暴击: {result['battle_results'][0]['is_crit']}")
        
        elif choice == 2:
            print("\n--- 多次战斗统计 ---\n")
            attacker_id = get_valid_input("请输入攻击方角色ID: ", int, None, 1, None)
            defender_id = get_valid_input("请输入防御方角色ID: ", int, None, 1, None)
            simulate_count = get_valid_input("请输入模拟战斗次数: ", int, 1000, 1, 10000)
            
            result = battle_between_characters(DB_FILE, attacker_id, defender_id, simulate_count)
            if result:
                print(f"\n{result['attacker']['name']} 攻击 {result['defender']['name']} ({result['simulate_count']}次)")
                print(f"平均伤害: {result['average_damage']:.2f}")
                print(f"期望暴击率: {result['expected_crit_rate']:.2%}")
                print(f"实际暴击率: {result['actual_crit_rate']:.2%}")
        
        elif choice == 3:  # 新增死斗模式选项
            print("\n--- 死斗模式 ---")
            attacker_id = get_valid_input("请输入攻击方角色ID: ", int, None, 1, None)
            defender_id = get_valid_input("请输入防御方角色ID: ", int, None, 1, None)
            
            # 需要导入fight_to_the_death函数
            from logic.battle import fight_to_the_death
            result = fight_to_the_death(DB_FILE, attacker_id, defender_id)
            
            if result:
                print(f"\n死斗结果:")
                print(f"攻击者: {result['attacker']['name']}")
                print(f"防御者: {result['defender']['name']}")
                print(f"胜利者: {result['winner']}")
                print(f"战斗回合数: {result['rounds']}")
                print(f"攻击者总伤害: {result['total_attacker_damage']}")
                print(f"防御者总伤害: {result['total_defender_damage']}")
                print(f"攻击者暴击率: {result['attacker_actual_crit_rate']:.2%}")
                print(f"防御者暴击率: {result['defender_actual_crit_rate']:.2%}")
                
                # 询问是否查看详细战斗记录
                show_detail = input("是否查看详细战斗记录? (y/n): ").lower()
                if show_detail == 'y':
                    for round_data in result['round_history']:
                        print(f"\n回合 {round_data['round']}:")
                        print(f"  攻击方造成伤害: {round_data['attacker_damage']} {'[暴击]' if round_data['attacker_is_crit'] else ''}")
                        print(f"  防御方造成伤害: {round_data['defender_damage']} {'[暴击]' if round_data['defender_is_crit'] else ''}")
                        print(f"  攻击方生命: {round_data['attacker_health_after']}")
                        print(f"  防御方生命: {round_data['defender_health_after']}")
        
        input("\n按回车键继续...")

# 修改 handle_analysis_menu 函数
def handle_analysis_menu():
    """
    处理属性分析菜单选项
    """
    while True:
        analysis_menu()
        choice = get_valid_input("请选择操作 (1-2): ", int, 1, 1, 2)
        
        if choice == 2:
            break
        
        elif choice == 1:
            print("\n--- 生成角色属性成长曲线 ---")
            
            # 询问用户是否为现有角色生成曲线
            use_existing = input("是否为现有角色生成曲线? (y/n，默认y): ").lower().strip()
            
            if use_existing == 'y' or use_existing == '':
                # 先列出所有角色供用户选择
                list_all_characters(DB_FILE)
                
                # 询问用户是通过ID还是名称选择角色
                selection_method = input("请选择角色的方式 (1: 通过ID, 2: 通过名称，默认1): ").strip() or '1'
                
                if selection_method == '1':
                    char_id = get_valid_input("请输入角色ID: ", int, None, 1, None)
                    character = load_character(character_id=char_id, db_path=DB_FILE)
                else:
                    char_name = input("请输入角色名称: ").strip()
                    character = load_character(character_name=char_name, db_path=DB_FILE)
                
                if character:
                    print(f"为角色 '{character.name}' 生成1-100级属性曲线图... (使用{character.growth_curve_type}成长曲线)")
                    # 使用level_range参数而不是start_level/end_level
                    attributes = generate_level_attributes(character.name, level_range=range(1, 101), character=character)
                    plot_attribute_growth(attributes, character.name, character=character)
            else:
                # 为临时角色生成曲线（不保存到XML）
                name = input("请输入临时角色名称: ").strip() or "临时角色"
                
                # 添加选择成长曲线类型的选项
                print("\n请选择成长曲线类型:")
                print("1. 线性成长 (默认)")
                print("2. 指数成长")
                print("3. 对数成长")
                print("4. 幂函数成长")
                print("5. S形成长")
                print("6. 混合成长")
                curve_choice = get_valid_input("请选择 (1-6): ", int, 1, 1, 6)
                
                # 映射选择到曲线类型
                curve_types = {
                    1: "linear",
                    2: "exponential",
                    3: "logarithmic",
                    4: "power",
                    5: "sigmoid",
                    6: "hybrid"
                }
                curve_type = curve_types[curve_choice]
                
                # 获取曲线参数
                curve_params = get_curve_parameters(curve_type)
                
                # 询问是否为每个属性设置不同的成长曲线类型
                use_attr_specific_curves = input("\n是否为每个属性设置不同的成长曲线类型? (y/n，默认n): ").lower().strip()
                attr_growth_curves = {}
                
                if use_attr_specific_curves == 'y':
                    attr_growth_curves = get_attribute_specific_curves()
                    
                    # 为临时角色创建一个虚拟的Character对象用于测试
                    from core.character import Character
                    temp_character = Character(
                        character_id='temp',
                        name=name,
                        growth_curve_type=curve_type,
                        growth_curve_params=curve_params,
                        attr_growth_curves=attr_growth_curves
                    )
                    
                    # 生成属性数据，使用角色对象
                    attributes = generate_level_attributes(name, level_range=range(1, 101), character=temp_character)
                else:
                    # 生成属性数据，使用level_range参数
                    attributes = generate_level_attributes(name, level_range=range(1, 101), curve_type=curve_type, curve_params=curve_params)
                
                # 绘制曲线图
                plot_attribute_growth(attributes, name, curve_type)
        
        input("\n按回车键继续...")

# 添加一个新函数来获取曲线参数
def get_curve_parameters(curve_type):
    """
    获取选定曲线类型的参数
    """
    params = {}
    
    print(f"\n设置{curve_type}曲线参数（直接回车使用默认值）")
    
    if curve_type == "exponential":
        exponent = get_valid_input("指数系数 (默认1.2): ", float, 1.2, 1.0, None)
        params = {"exponent": exponent}
    elif curve_type == "logarithmic":
        base = get_valid_input("对数底数 (默认e): ", float, math.e, 2.0, None)
        params = {"base": base}
    elif curve_type == "power":
        exponent = get_valid_input("幂指数 (默认1.5): ", float, 1.5, 0.5, None)
        scaling = get_valid_input("缩放系数 (默认1.0): ", float, 1.0, 0.1, None)
        params = {"exponent": exponent, "scaling": scaling}
    elif curve_type == "sigmoid":
        midpoint = get_valid_input("中点等级 (默认50): ", int, 50, 1, 100)
        steepness = get_valid_input("陡峭度 (默认0.1): ", float, 0.1, 0.01, 1.0)
        params = {"midpoint": midpoint, "steepness": steepness}
    elif curve_type == "hybrid":
        early_coef = get_valid_input("前期系数 (默认1.5): ", float, 1.5, 1.0, None)
        late_coef = get_valid_input("后期系数 (默认1.0): ", float, 1.0, 0.1, None)
        transition_level = get_valid_input("过渡等级 (默认30): ", int, 30, 1, 100)
        params = {"early_coef": early_coef, "late_coef": late_coef, "transition_level": transition_level}
    
    # 为每个属性设置特定参数
    use_attr_specific = input("\n是否为每个属性设置不同的曲线参数? (y/n，默认n): ").lower().strip()
    if use_attr_specific == 'y':
        attr_params = {}
        # 从XML配置中获取所有可用属性
        attrs = get_all_available_attributes()
        # 如果没有可用属性，使用默认属性列表
        if not attrs:
            attrs = ['attack', 'defense', 'health', 'crit', 'crit_resist']
        
        for attr in attrs:
            print(f"\n设置{attr}属性的{curve_type}曲线参数:")
            attr_specific = {}
            
            if curve_type == "exponential":
                exponent = get_valid_input(f"{attr}的指数系数 (默认{params.get('exponent', 1.2)}): ", float, 
                                         params.get('exponent', 1.2), 1.0, None)
                attr_specific = {"exponent": exponent}
            elif curve_type == "logarithmic":
                base = get_valid_input(f"{attr}的对数底数 (默认{params.get('base', math.e):.2f}): ", float, 
                                     params.get('base', math.e), 2.0, None)
                attr_specific = {"base": base}
            elif curve_type == "power":
                exponent = get_valid_input(f"{attr}的幂指数 (默认{params.get('exponent', 1.5)}): ", float, 
                                         params.get('exponent', 1.5), 0.5, None)
                scaling = get_valid_input(f"{attr}的缩放系数 (默认{params.get('scaling', 1.0)}): ", float, 
                                         params.get('scaling', 1.0), 0.1, None)
                attr_specific = {"exponent": exponent, "scaling": scaling}
            elif curve_type == "sigmoid":
                midpoint = get_valid_input(f"{attr}的中点等级 (默认{params.get('midpoint', 50)}): ", int, 
                                          params.get('midpoint', 50), 1, 100)
                steepness = get_valid_input(f"{attr}的陡峭度 (默认{params.get('steepness', 0.1)}): ", float, 
                                           params.get('steepness', 0.1), 0.01, 1.0)
                attr_specific = {"midpoint": midpoint, "steepness": steepness}
            elif curve_type == "hybrid":
                early_coef = get_valid_input(f"{attr}的前期系数 (默认{params.get('early_coef', 1.5)}): ", float, 
                                           params.get('early_coef', 1.5), 1.0, None)
                late_coef = get_valid_input(f"{attr}的后期系数 (默认{params.get('late_coef', 1.0)}): ", float, 
                                          params.get('late_coef', 1.0), 0.1, None)
                transition_level = get_valid_input(f"{attr}的过渡等级 (默认{params.get('transition_level', 30)}): ", int, 
                                                 params.get('transition_level', 30), 1, 100)
                attr_specific = {"early_coef": early_coef, "late_coef": late_coef, "transition_level": transition_level}
            
            attr_params[attr] = attr_specific
        
        return attr_params
    
    return {attr: params.copy() for attr in ['attack', 'defense', 'health', 'crit', 'crit_resist']}

def run_damage_tests():
    """
    运行伤害计算的测试用例
    """
    print("\n=== 伤害计算测试用例 ===")
    
    # 测试用例1：基础伤害计算（无暴击）
    damage1, is_crit1 = calculate_damage(100, 50, attacker_crit=0, defender_crit_resist=0)
    print(f"攻击方攻击力100，受击方防御力50，无暴击属性，伤害: {damage1}，是否暴击: {is_crit1}")
    
    # 测试用例2：低暴击率情况（10%暴击率）
    print("\n测试低暴击率情况（10%）:")
    for i in range(5):
        damage, is_crit = calculate_damage(100, 50, attacker_crit=10, defender_crit_resist=0)
        print(f"  攻击方暴击10，受击方暴抗0，伤害: {damage}，是否暴击: {is_crit}")
    
    # 测试用例3：中等暴击率情况（50%暴击率）
    print("\n测试中等暴击率情况（50%）:")
    for i in range(5):
        damage, is_crit = calculate_damage(100, 50, attacker_crit=50, defender_crit_resist=0)
        print(f"  攻击方暴击50，受击方暴抗0，伤害: {damage}，是否暴击: {is_crit}")
    
    # 测试用例4：暴抗抵消暴击
    print("\n测试暴抗抵消暴击:")
    damage4, is_crit4 = calculate_damage(100, 50, attacker_crit=30, defender_crit_resist=15)
    critical_rate4 = calculate_critical_rate(30, 15)
    print(f"  攻击方暴击30，受击方暴抗15，计算暴击率: {critical_rate4:.2%}，伤害: {damage4}，是否暴击: {is_crit4}")
    
    # 测试用例5：防御过高情况下的暴击
    print("\n测试防御过高情况下的暴击:")
    damage5, is_crit5 = calculate_damage(50, 100, attacker_crit=100, defender_crit_resist=0, is_critical=True)
    print(f"  攻击方攻击力50，受击方防御力100，强制暴击，伤害: {damage5}，是否暴击: {is_crit5}")
    
    # 测试用例6：暴击率上限
    print("\n测试暴击率上限:")
    damage6, is_crit6 = calculate_damage(100, 50, attacker_crit=200, defender_crit_resist=0)
    critical_rate6 = calculate_critical_rate(200, 0)
    print(f"  攻击方暴击200，受击方暴抗0，计算暴击率: {critical_rate6:.2%}，伤害: {damage6}，是否暴击: {is_crit6}")
    
    input("\n按回车键继续...")

def get_attribute_specific_curves():
    """
    获取每个属性的特定成长曲线类型设置
    
    返回:
    attr_growth_curves: 包含每个属性成长曲线信息的字典
    """
    attr_growth_curves = {}
    attrs = ['attack', 'defense', 'health', 'crit', 'crit_resist']
    
    # 映射选择到曲线类型
    curve_types = {
        1: "linear",
        2: "exponential",
        3: "logarithmic",
        4: "power",
        5: "sigmoid",
        6: "hybrid"
    }
    
    curve_names = {
        "linear": "线性成长",
        "exponential": "指数成长",
        "logarithmic": "对数成长",
        "power": "幂函数成长",
        "sigmoid": "S形成长",
        "hybrid": "混合成长"
    }
    
    for attr in attrs:
        print(f"\n请选择{attr}属性的成长曲线类型:")
        print("1. 线性成长 (默认)")
        print("2. 指数成长")
        print("3. 对数成长")
        print("4. 幂函数成长")
        print("5. S形成长")
        print("6. 混合成长")
        curve_choice = get_valid_input(f"请选择 (1-6): ", int, 1, 1, 6)
        
        attr_curve_type = curve_types[curve_choice]
        print(f"已为{attr}属性选择{curve_names[attr_curve_type]}")
        
        # 获取该属性特定的曲线参数
        use_attr_params = input(f"是否为{attr}属性设置特定的曲线参数? (y/n，默认n): ").lower().strip()
        attr_curve_params = {}
        
        if use_attr_params == 'y':
            attr_curve_params = get_curve_parameters(attr_curve_type)
        
        attr_growth_curves[attr] = {
            'curve_type': attr_curve_type,
            'curve_params': attr_curve_params
        }
    
    return attr_growth_curves

def display_available_attributes():
    """
    显示所有可用的属性及其详细信息
    """
    print("\n=== 可用属性列表 ===")
    
    # 从character_manager获取所有可用属性
    all_attributes = get_all_available_attributes()
    
    if all_attributes:
        for i, attr_name in enumerate(all_attributes, 1):
            display_name = get_attribute_display_name(attr_name)
            description = get_attribute_description(attr_name)
            print(f"\n{i}. {display_name} ({attr_name})")
            print(f"   描述: {description}")
    else:
        print("当前没有可用的系统属性配置。")
    
    print("\n==================\n")
    input("按Enter键返回主菜单...")

def main():
    """
    主函数
    """
    print("欢迎使用数值系统测试工具！")
    
    while True:
        # 显示主菜单
        print("\n=== 主菜单 ===")
        print("1. 角色管理")
        print("2. 战斗系统")
        print("3. 数据分析")
        print("4. 查看可用属性")
        print("5. 退出")
        
        choice = get_valid_input("请选择操作 (1-5): ", int, 1, 1, 5)
        
        if choice == 1:
            handle_character_menu()
        elif choice == 2:
            handle_battle_menu()
        elif choice == 3:
            handle_analysis_menu()
        elif choice == 4:
            display_available_attributes()
            continue
        elif choice == 5:
            print("谢谢使用，再见！")
            break

if __name__ == "__main__":
    main()