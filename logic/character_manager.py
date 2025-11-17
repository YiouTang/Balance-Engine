# 角色管理模块
import random
from core.character import Character
from data.xml_handler import save_character_to_xml, get_next_available_id, load_character_from_xml, load_all_characters, get_all_attribute_names, get_attribute_info
from utils.growth_curve import (
    linear_growth, exponential_growth, logarithmic_growth,
    power_growth, sigmoid_growth, hybrid_growth
)

# 修改 add_character 函数，支持动态属性
def add_character(xml_file, name, level=1, char_id=None, 
                 growth_curve_type="linear", growth_curve_params=None, attr_growth_curves=None, **kwargs):
    """
    向XML文件添加一个新角色，支持动态属性
    """
    # 如果没有提供ID，需要先加载XML获取下一个可用ID
    if char_id is None:
        import xml.etree.ElementTree as ET
        import os
        if not os.path.exists(xml_file) or os.path.getsize(xml_file) == 0:
            char_id = 1
        else:
            try:
                tree = ET.parse(xml_file)
                root = tree.getroot()
                char_id = get_next_available_id(root)
            except Exception:
                char_id = 1
    
    # 创建角色对象，传递所有属性参数
    character = Character(
        character_id=char_id,
        name=name,
        level=level,
        growth_curve_type=growth_curve_type,
        growth_curve_params=growth_curve_params,
        attr_growth_curves=attr_growth_curves,
        **kwargs
    )
    
    # 保存到XML
    result = save_character_to_xml(xml_file, character)
    if result:
        # 打印所有设置的属性
        print(f"角色创建成功 - ID: {char_id}, 名称: {name}, 等级: {level}")
        print("属性详情:")
        all_attrs = character.get_all_attributes()
        for attr_name, attr_value in all_attrs.items():
            display_name = get_attribute_display_name(attr_name)
            print(f"  {display_name} ({attr_name}): {attr_value}")
    return result

# 获取所有可用的属性名称（包括基础属性和自定义属性）
def get_all_available_attributes():
    """
    获取所有系统中可用的属性名称
    
    返回:
    属性名称列表
    """
    try:
        # 优先从配置文件获取
        return get_all_attribute_names()
    except Exception:
        # 如果配置文件不可用，返回基本属性
        return Character.BASE_ATTRIBUTES

# 获取属性的显示名称
def get_attribute_display_name(attribute_name):
    """
    获取属性的显示名称
    
    参数:
    attribute_name: 属性名称
    
    返回:
    属性的显示名称
    """
    try:
        # 从配置文件获取
        attr_info = get_attribute_info(attribute_name)
        if attr_info:
            return attr_info.get('display_name', attribute_name)
    except Exception:
        pass
    
    # 默认返回原名称
    return attribute_name

# 获取属性的描述
def get_attribute_description(attribute_name):
    """
    获取属性的描述
    
    参数:
    attribute_name: 属性名称
    
    返回:
    属性的描述文本
    """
    try:
        # 从配置文件获取
        attr_info = get_attribute_info(attribute_name)
        if attr_info:
            return attr_info.get('description', '')
    except Exception:
        pass
    
    return ''

# 修改 generate_random_character 函数，支持动态属性和成长曲线信息
def generate_random_character(xml_file, name=None, level=1, curve_type="linear", curve_params=None, attr_growth_curves=None):
    """
    生成一个随机属性的角色，支持不同的成长曲线和动态属性
    """
    # 如果没有提供名称，生成随机名称
    if name is None:
        adjectives = ["勇猛的", "聪明的", "敏捷的", "强壮的", "狡猾的", "仁慈的", "邪恶的", "神秘的"]
        nouns = ["战士", "法师", "射手", "刺客", "骑士", "巫师", "猎人", "盗贼"]
        name = f"{random.choice(adjectives)}{random.choice(nouns)}"
    
    # 默认曲线参数
    if curve_params is None:
        curve_params = {}
    
    # 确保attr_growth_curves是字典
    if attr_growth_curves is None:
        attr_growth_curves = {}
    
    # 选择成长曲线函数
    curve_functions = {
        "linear": linear_growth,
        "exponential": exponential_growth,
        "logarithmic": logarithmic_growth,
        "power": power_growth,
        "sigmoid": sigmoid_growth,
        "hybrid": hybrid_growth
    }
    
    # 基础属性的基础值和系数
    base_values = {
        'attack': 1.2,
        'defense': 0.8,
        'health': 5.0,
        'crit': 0.3,
        'crit_resist': 0.2,
        # 为自定义属性添加默认系数
        'damage_boost': 0.5,
        'damage_reduction': 0.5,
        'agility': 1.0
    }
    
    # 获取所有可用属性
    available_attributes = get_all_available_attributes()
    if not available_attributes:
        available_attributes = Character.BASE_ATTRIBUTES
    
    # 生成属性值
    calculated_attributes = {}
    for attr in available_attributes:
        # 获取该属性的基础系数，如果没有定义则使用默认值
        base_coef = base_values.get(attr, 1.0)
        
        # 优先使用该属性特定的成长曲线设置
        if attr in attr_growth_curves:
            attr_curve_type = attr_growth_curves[attr]['curve_type']
            attr_curve_params = attr_growth_curves[attr]['curve_params'] or {}
            print(f"为{attr}属性使用特定成长曲线: {attr_curve_type}")
        else:
            # 否则使用全局设置
            attr_curve_type = curve_type
            attr_curve_params = curve_params.get(attr, {})
        
        # 获取对应的成长函数
        growth_function = curve_functions.get(attr_curve_type, linear_growth)
        
        base_value = 10  # 基础倍率
        # 计算期望值
        expected_value = growth_function(level, base_value, **attr_curve_params) * base_coef
        # 添加随机波动（30%）
        variance = expected_value * 0.3
        
        # 根据属性类型设置最小值
        min_value = 0
        if attr in ['health']:
            min_value = 10
        elif attr not in ['crit', 'crit_resist']:
            min_value = 1
            
        calculated_attributes[attr] = max(min_value, 
                                        int(random.normalvariate(expected_value, variance)))
    
    # 确保生命值至少为10
    if 'health' in calculated_attributes:
        calculated_attributes['health'] = max(10, calculated_attributes['health'])
    
    # 添加角色，使用关键字参数传递所有属性
    return add_character(
        xml_file, 
        name, 
        level=level,
        growth_curve_type=curve_type,
        growth_curve_params=curve_params,
        attr_growth_curves=attr_growth_curves,
        **calculated_attributes
    )

def batch_generate_characters(xml_file, count=5, start_level=1, name_prefix="随机角色", 
                             curve_type="linear", curve_params=None, attr_growth_curves=None):
    """
    批量生成随机角色
    
    参数:
    xml_file: XML文件路径
    count: 生成角色数量
    start_level: 起始等级
    name_prefix: 名称前缀
    curve_type: 成长曲线类型
    curve_params: 曲线参数字典
    
    返回:
    成功生成的角色数量
    """
    success_count = 0
    for i in range(count):
        level = start_level + i  # 每个角色等级递增
        name = f"{name_prefix}{i+1}"
        if generate_random_character(xml_file, name, level, curve_type, curve_params, attr_growth_curves):
            success_count += 1
    
    print(f"\n批量生成完成: 成功生成 {success_count}/{count} 个角色")
    return success_count

def list_characters(xml_file):
    """
    列出XML文件中的所有角色，支持显示动态属性
    """
    characters = load_all_characters(xml_file)
    
    if len(characters) == 0:
        print("没有找到角色")
        return
    
    print(f"\nXML文件中的角色列表 ({len(characters)} 个):")
    print("-" * 80)
    
    # 显示基本信息
    print(f"{'ID':<5}{'名称':<15}{'等级':<6}基础属性")
    print("-" * 80)
    
    for character in characters:
        print(f"{character.id:<5}{character.name:<15}{character.level:<6}")
        
        # 显示所有属性
        all_attributes = character.get_all_attributes() if hasattr(character, 'get_all_attributes') else {}
        if all_attributes:
            for attr_name, attr_value in all_attributes.items():
                display_name = get_attribute_display_name(attr_name)
                # 对于百分比类型的属性，添加%符号
                if attr_name in ['crit', 'crit_resist']:
                    print(f"      {display_name} ({attr_name}): {attr_value}%")
                else:
                    print(f"      {display_name} ({attr_name}): {attr_value}")
        else:
            # 兼容旧格式
            print(f"      攻击力: {getattr(character, 'attack', 'N/A')}")
            print(f"      防御力: {getattr(character, 'defense', 'N/A')}")
            print(f"      生命值: {getattr(character, 'health', 'N/A')}")
            print(f"      暴击值: {getattr(character, 'crit', 'N/A')}")
            print(f"      暴抗值: {getattr(character, 'crit_resist', 'N/A')}")
        
        # 显示成长曲线信息
        if hasattr(character, 'growth_curve_type'):
            print(f"      成长曲线类型: {character.growth_curve_type}")
        print()
    
    print("-" * 80)