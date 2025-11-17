# XML文件处理模块
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
from core.character import Character

# 默认属性配置缓存
_attribute_config = None

def create_default_attribute_config(config_file):
    """
    创建默认的属性配置文件
    
    参数:
    config_file: 属性配置文件路径
    """
    root = ET.Element('attributes')
    
    # 创建基础属性节点
    base_attributes_elem = ET.SubElement(root, 'base_attributes')
    
    # 基础属性
    basic_attributes = [
        {
            'name': 'attack',
            'display_name': '攻击力',
            'default_value': 10,
            'min_value': 1,
            'max_value': 9999,
            'description': '角色的基本攻击能力，影响造成的伤害'
        },
        {
            'name': 'defense',
            'display_name': '防御力',
            'default_value': 5,
            'min_value': 0,
            'max_value': 9999,
            'description': '角色的基本防御能力，减少受到的伤害'
        },
        {
            'name': 'health',
            'display_name': '生命值',
            'default_value': 100,
            'min_value': 1,
            'max_value': 99999,
            'description': '角色的生命值，降至0时角色死亡'
        },
        {
            'name': 'crit',
            'display_name': '暴击值',
            'default_value': 5,
            'min_value': 0,
            'max_value': 100,
            'description': '增加暴击概率的属性'
        },
        {
            'name': 'crit_resist',
            'display_name': '暴抗值',
            'default_value': 5,
            'min_value': 0,
            'max_value': 100,
            'description': '减少被暴击概率的属性'
        }
    ]
    
    # 创建自定义属性节点
    custom_attributes_elem = ET.SubElement(root, 'custom_attributes')
    
    # 自定义属性
    custom_attributes = [
        {
            'name': 'damage_boost',
            'display_name': '伤害加成',
            'default_value': 0,
            'min_value': 0,
            'max_value': 100,
            'description': '增加造成的最终伤害百分比'
        },
        {
            'name': 'damage_reduction',
            'display_name': '伤害减免',
            'default_value': 0,
            'min_value': 0,
            'max_value': 100,
            'description': '减少受到的最终伤害百分比'
        },
        {
            'name': 'agility',
            'display_name': '敏捷',
            'default_value': 10,
            'min_value': 0,
            'max_value': 9999,
            'description': '影响攻击顺序和闪避概率'
        },
        {
            'name': 'accuracy',
            'display_name': '命中',
            'default_value': 95,
            'min_value': 0,
            'max_value': 100,
            'description': '影响攻击命中目标的概率'
        },
        {
            'name': 'evasion',
            'display_name': '闪避',
            'default_value': 5,
            'min_value': 0,
            'max_value': 100,
            'description': '影响闪避敌人攻击的概率'
        },
        {
            'name': 'health_regen',
            'display_name': '生命值恢复',
            'default_value': 2,
            'min_value': 0,
            'max_value': 100,
            'description': '每个回合自动恢复的生命值'
        }
    ]
    
    # 添加基础属性
    for attr_data in basic_attributes:
        attr_elem = ET.SubElement(base_attributes_elem, 'attribute')
        for key, value in attr_data.items():
            attr_elem.set(key, str(value))
    
    # 添加自定义属性
    for attr_data in custom_attributes:
        attr_elem = ET.SubElement(custom_attributes_elem, 'attribute')
        for key, value in attr_data.items():
            attr_elem.set(key, str(value))
    
    # 创建XML树并写入文件
    tree = ET.ElementTree(root)
    tree.write(config_file, encoding='UTF-8', xml_declaration=True)
    print(f"已创建默认属性配置文件: {config_file}")

def load_attribute_config(config_file="attributes_config.xml"):
    """
    加载属性配置文件，如果文件不存在则自动创建默认配置
    
    参数:
    config_file: 属性配置XML文件路径
    
    返回:
    属性配置字典
    """
    # 如果配置文件不存在于当前目录，尝试在项目根目录查找
    if not os.path.exists(config_file):
        config_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), config_file)
    
    # 如果文件不存在，创建默认配置文件
    if not os.path.exists(config_file):
        create_default_attribute_config(config_file)
    
    try:
        tree = ET.parse(config_file)
        root = tree.getroot()
        
        config = {
            'base_attributes': {},
            'custom_attributes': {}
        }
        
        # 解析基础属性
        for attr_elem in root.findall('./base_attributes/attribute'):
            attr_name = attr_elem.get('name')
            config['base_attributes'][attr_name] = {
                'display_name': attr_elem.get('display_name', attr_name),
                'default_value': int(attr_elem.get('default_value', '0')),
                'min_value': int(attr_elem.get('min_value', '0')),
                'max_value': int(attr_elem.get('max_value', '9999')),
                'description': attr_elem.get('description', '')
            }
        
        # 解析自定义属性
        for attr_elem in root.findall('./custom_attributes/attribute'):
            attr_name = attr_elem.get('name')
            config['custom_attributes'][attr_name] = {
                'display_name': attr_elem.get('display_name', attr_name),
                'default_value': int(attr_elem.get('default_value', '0')),
                'min_value': int(attr_elem.get('min_value', '0')),
                'max_value': int(attr_elem.get('max_value', '9999')),
                'description': attr_elem.get('description', '')
            }
        
        return config
    except Exception as e:
        print(f"加载属性配置文件时出错: {e}")
        return {}

def get_attribute_config():
    """
    获取属性配置（带缓存）
    
    返回:
    属性配置字典
    """
    global _attribute_config
    # 每次重新加载配置，确保即时反映XML文件的更改
    _attribute_config = load_attribute_config()
    return _attribute_config

def get_all_attribute_names():
    """
    获取所有已配置的属性名称
    
    返回:
    属性名称列表
    """
    config = get_attribute_config()
    return list(config.get('base_attributes', {}).keys()) + list(config.get('custom_attributes', {}).keys())

def get_attribute_info(attribute_name):
    """
    获取指定属性的配置信息
    
    参数:
    attribute_name: 属性名称
    
    返回:
    属性配置信息字典或None
    """
    config = get_attribute_config()
    
    # 先在基础属性中查找
    if attribute_name in config.get('base_attributes', {}):
        return config['base_attributes'][attribute_name]
    
    # 再在自定义属性中查找
    if attribute_name in config.get('custom_attributes', {}):
        return config['custom_attributes'][attribute_name]
    
    return None

def get_next_available_id(root):
    """
    获取下一个可用的角色ID
    """
    max_id = 0
    for character in root.findall('character'):
        try:
            char_id = int(character.get('id'))
            if char_id > max_id:
                max_id = char_id
        except ValueError:
            continue
    return max_id + 1

def prettify_xml(element):
    """
    美化XML格式，使其具有良好的缩进和换行
    """
    rough_string = ET.tostring(element, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="    ", encoding='utf-8').decode('utf-8')

def load_character_from_xml(xml_file, character_id=None, character_name=None):
    """
    从XML文件加载角色属性
    
    参数:
    xml_file: XML文件路径
    character_id: 角色ID（可选）
    character_name: 角色名称（可选）
    
    返回:
    Character对象，如果未找到则返回None
    """
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # 根据ID或名称查找角色
        for character in root.findall('character'):
            if (character_id is not None and character.get('id') == str(character_id)) or \
               (character_name is not None and character.get('name') == character_name):
                # 提取角色基本信息
                # 添加对level属性的支持，如果没有则默认为1
                level_elem = character.find('level')
                level = int(level_elem.text) if level_elem is not None else 1
                
                # 提取成长曲线信息
                growth_curve_type_elem = character.find('growth_curve_type')
                growth_curve_type = growth_curve_type_elem.text if growth_curve_type_elem is not None else "linear"
                
                # 提取成长曲线参数
                growth_curve_params = {}
                growth_curve_params_elem = character.find('growth_curve_params')
                if growth_curve_params_elem is not None:
                    for attr_elem in growth_curve_params_elem.findall('*'):
                        attr_name = attr_elem.tag
                        attr_params = {}
                        for param_elem in attr_elem.findall('*'):
                            param_name = param_elem.tag
                            param_value = param_elem.text
                            # 尝试转换为数字类型
                            try:
                                if '.' in param_value:
                                    param_value = float(param_value)
                                else:
                                    param_value = int(param_value)
                            except ValueError:
                                pass
                            attr_params[param_name] = param_value
                        growth_curve_params[attr_name] = attr_params
                
                # 加载每个属性的成长曲线信息
                attr_growth_curves = {}
                attr_growth_curves_elem = character.find('attr_growth_curves')
                if attr_growth_curves_elem is not None:
                    for attr_elem in attr_growth_curves_elem.findall('*'):
                        attr_name = attr_elem.tag
                        curve_type_elem = attr_elem.find('curve_type')
                        curve_params_elem = attr_elem.find('curve_params')
                        
                        attr_info = {}
                        if curve_type_elem is not None:
                            attr_info['curve_type'] = curve_type_elem.text
                        
                        if curve_params_elem is not None:
                            params = {}
                            for param_elem in curve_params_elem.findall('*'):
                                param_name = param_elem.tag
                                param_value = param_elem.text
                                # 尝试转换为数字类型
                                try:
                                    if '.' in param_value:
                                        param_value = float(param_value)
                                    else:
                                        param_value = int(param_value)
                                except ValueError:
                                    pass
                                params[param_name] = param_value
                            attr_info['curve_params'] = params
                        
                        if attr_info:
                            attr_growth_curves[attr_name] = attr_info
                
                # 收集所有属性，包括基础属性和自定义属性
                attributes = {}
                # 遍历所有子元素，找出所有不是特殊标签的元素作为属性
                for elem in character:
                    # 跳过特殊标签
                    if elem.tag not in ['level', 'growth_curve_type', 'growth_curve_params', 'attr_growth_curves']:
                        # 尝试将值转换为数字
                        try:
                            if '.' in elem.text:
                                attributes[elem.tag] = float(elem.text)
                            else:
                                attributes[elem.tag] = int(elem.text)
                        except (ValueError, TypeError):
                            # 如果转换失败，保留原始字符串
                            attributes[elem.tag] = elem.text
                
                # 创建角色对象，使用关键字参数传递所有属性
                return Character(
                    character_id=character.get('id'),
                    name=character.get('name'),
                    level=level,
                    growth_curve_type=growth_curve_type,
                    growth_curve_params=growth_curve_params,
                    attr_growth_curves=attr_growth_curves,
                    **attributes
                )
        
        print(f"未找到角色：ID={character_id}, 名称={character_name}")
        return None
    
    except Exception as e:
        print(f"加载XML文件时出错: {e}")
        return None

def save_character_to_xml(xml_file, character):
    """
    保存角色到XML文件
    
    参数:
    xml_file: XML文件路径
    character: Character对象
    
    返回:
    成功返回True，失败返回False
    """
    try:
        # 检查文件是否存在或为空
        if not os.path.exists(xml_file) or os.path.getsize(xml_file) == 0:
            # 创建新的XML文件
            root = ET.Element('characters')
            tree = ET.ElementTree(root)
        else:
            try:
                # 尝试加载现有XML文件
                tree = ET.parse(xml_file)
                root = tree.getroot()
                
                # 检查角色名称是否已存在
                for existing_char in root.findall('character'):
                    if existing_char.get('name') == character.name and existing_char.get('id') != character.id:
                        print(f"错误: 角色名称 '{character.name}' 已存在")
                        return False
                
                # 检查提供的ID是否已存在
                for existing_char in root.findall('character'):
                    if existing_char.get('id') == str(character.id):
                        # 更新现有角色
                        root.remove(existing_char)
                        break
            except ET.ParseError:
                # 如果XML解析失败，创建新的XML文件
                print("警告: XML文件格式无效，将创建新的XML结构")
                root = ET.Element('characters')
                tree = ET.ElementTree(root)
        
        # 创建新角色元素
        new_character = ET.SubElement(root, 'character')
        new_character.set('id', str(character.id))
        new_character.set('name', character.name)
        
        # 添加等级属性
        level_elem = ET.SubElement(new_character, 'level')
        level_elem.text = str(character.level)
        
        # 保存所有属性，包括基础属性和自定义属性
        for attr_name, attr_value in character.get_all_attributes().items():
            attr_elem = ET.SubElement(new_character, attr_name)
            attr_elem.text = str(attr_value)
        
        # 添加成长曲线信息
        growth_curve_type_elem = ET.SubElement(new_character, 'growth_curve_type')
        growth_curve_type_elem.text = character.growth_curve_type
        
        # 保存曲线参数
        growth_curve_params_elem = ET.SubElement(new_character, 'growth_curve_params')
        for attr, params in character.growth_curve_params.items():
            attr_elem = ET.SubElement(growth_curve_params_elem, attr)
            for param_name, param_value in params.items():
                param_elem = ET.SubElement(attr_elem, param_name)
                param_elem.text = str(param_value)
        
        # 保存每个属性的成长曲线信息
        attr_growth_curves_elem = ET.SubElement(new_character, 'attr_growth_curves')
        for attr_name, attr_info in character.attr_growth_curves.items():
            attr_elem = ET.SubElement(attr_growth_curves_elem, attr_name)
            
            # 保存曲线类型
            if 'curve_type' in attr_info:
                curve_type_elem = ET.SubElement(attr_elem, 'curve_type')
                curve_type_elem.text = attr_info['curve_type']
            
            # 保存曲线参数
            if 'curve_params' in attr_info:
                curve_params_elem = ET.SubElement(attr_elem, 'curve_params')
                for param_name, param_value in attr_info['curve_params'].items():
                    param_elem = ET.SubElement(curve_params_elem, param_name)
                    param_elem.text = str(param_value)
        
        # 美化XML并保存
        pretty_xml = prettify_xml(root)
        with open(xml_file, 'w', encoding='utf-8') as f:
            f.write(pretty_xml)
        
        print(f"成功保存角色: {character.name} (ID: {character.id})")
        return True
    
    except Exception as e:
        print(f"保存角色时出错: {e}")
        return False

def load_all_characters(xml_file):
    """
    加载XML文件中的所有角色
    
    参数:
    xml_file: XML文件路径
    
    返回:
    Character对象列表
    """
    characters = []
    try:
        if not os.path.exists(xml_file):
            print("角色文件不存在")
            return characters
        
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        for character_elem in root.findall('character'):
            # 提取角色基本信息
            level_elem = character_elem.find('level')
            level = int(level_elem.text) if level_elem is not None else 1
            
            # 提取成长曲线信息
            growth_curve_type_elem = character_elem.find('growth_curve_type')
            growth_curve_type = growth_curve_type_elem.text if growth_curve_type_elem is not None else "linear"
            
            # 提取成长曲线参数
            growth_curve_params = {}
            growth_curve_params_elem = character_elem.find('growth_curve_params')
            if growth_curve_params_elem is not None:
                for attr_elem in growth_curve_params_elem.findall('*'):
                    attr_name = attr_elem.tag
                    attr_params = {}
                    for param_elem in attr_elem.findall('*'):
                        param_name = param_elem.tag
                        param_value = param_elem.text
                        # 尝试转换为数字类型
                        try:
                            if '.' in param_value:
                                param_value = float(param_value)
                            else:
                                param_value = int(param_value)
                        except ValueError:
                            pass
                        attr_params[param_name] = param_value
                    growth_curve_params[attr_name] = attr_params
            
            # 加载每个属性的成长曲线信息
            attr_growth_curves = {}
            attr_growth_curves_elem = character_elem.find('attr_growth_curves')
            if attr_growth_curves_elem is not None:
                for attr_elem in attr_growth_curves_elem.findall('*'):
                    attr_name = attr_elem.tag
                    curve_type_elem = attr_elem.find('curve_type')
                    curve_params_elem = attr_elem.find('curve_params')
                    
                    attr_info = {}
                    if curve_type_elem is not None:
                        attr_info['curve_type'] = curve_type_elem.text
                    
                    if curve_params_elem is not None:
                        params = {}
                        for param_elem in curve_params_elem.findall('*'):
                            param_name = param_elem.tag
                            param_value = param_elem.text
                            # 尝试转换为数字类型
                            try:
                                if '.' in param_value:
                                    param_value = float(param_value)
                                else:
                                    param_value = int(param_value)
                            except ValueError:
                                pass
                            params[param_name] = param_value
                        attr_info['curve_params'] = params
                    
                    if attr_info:
                        attr_growth_curves[attr_name] = attr_info
            
            # 收集所有属性
            attributes = {}
            for elem in character_elem:
                # 跳过特殊标签
                if elem.tag not in ['level', 'growth_curve_type', 'growth_curve_params', 'attr_growth_curves']:
                    # 尝试将值转换为数字
                    try:
                        if '.' in elem.text:
                            attributes[elem.tag] = float(elem.text)
                        else:
                            attributes[elem.tag] = int(elem.text)
                    except (ValueError, TypeError):
                        attributes[elem.tag] = elem.text
            
            # 创建角色对象
            character = Character(
                character_id=character_elem.get('id'),
                name=character_elem.get('name'),
                level=level,
                growth_curve_type=growth_curve_type,
                growth_curve_params=growth_curve_params,
                attr_growth_curves=attr_growth_curves,
                **attributes
            )
            characters.append(character)
        
        return sorted(characters, key=lambda c: int(c.id))
    
    except Exception as e:
        print(f"加载所有角色时出错: {e}")
        return characters