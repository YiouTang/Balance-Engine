# 战斗模拟模块
from core.damage import calculate_damage, calculate_critical_rate
from data.xml_handler import load_character_from_xml
import copy

def battle_between_characters(xml_file, attacker_id, defender_id, simulate_count=1):
    """
    模拟两个角色之间的战斗
    
    参数:
    xml_file: XML文件路径
    attacker_id: 攻击方角色ID
    defender_id: 防御方角色ID
    simulate_count: 模拟战斗次数
    
    返回:
    战斗结果统计字典
    """
    # 加载角色
    attacker = load_character_from_xml(xml_file, character_id=attacker_id)
    defender = load_character_from_xml(xml_file, character_id=defender_id)
    
    if not attacker or not defender:
        print("无法加载角色信息，战斗取消")
        return None
    
    # 获取角色属性，支持动态属性
    attacker_attrs = attacker.to_dict() if hasattr(attacker, 'to_dict') else vars(attacker)
    defender_attrs = defender.to_dict() if hasattr(defender, 'to_dict') else vars(defender)
    
    # 模拟战斗
    total_damage = 0
    crit_count = 0
    battle_results = []
    
    for i in range(simulate_count):
        # 获取基础属性，使用字典get方法支持动态属性结构
        attack = attacker_attrs.get('attack', 0)
        defense = defender_attrs.get('defense', 0)
        crit = attacker_attrs.get('crit', 0)
        crit_resist = defender_attrs.get('crit_resist', 0)
        attacker_level = attacker_attrs.get('level', 1)
        defender_level = defender_attrs.get('level', 1)
        
        # 计算伤害
        damage, is_crit = calculate_damage(
            attack,
            defense,
            crit,
            crit_resist,
            attacker_level=attacker_level,
            defender_level=defender_level
        )
        
        # 应用自定义属性效果
        if 'damage_boost' in attacker_attrs:
            damage = int(damage * (1 + attacker_attrs['damage_boost'] / 100))
        
        if 'damage_reduction' in defender_attrs:
            damage = int(damage * (1 - defender_attrs['damage_reduction'] / 100))
        
        total_damage += damage
        if is_crit:
            crit_count += 1
        
        battle_results.append({
            'damage': damage,
            'is_crit': is_crit,
            'custom_effects_applied': {
                'damage_boost': attacker_attrs.get('damage_boost', 0),
                'damage_reduction': defender_attrs.get('damage_reduction', 0)
            }
        })
    
    # 计算统计信息
    avg_damage = total_damage / simulate_count
    actual_crit_rate = crit_count / simulate_count
    
    return {
        'attacker': attacker_attrs,
        'defender': defender_attrs,
        'simulate_count': simulate_count,
        'average_damage': avg_damage,
        'actual_crit_rate': actual_crit_rate,
        'expected_crit_rate': calculate_critical_rate(attacker_attrs.get('crit', 0), attacker_attrs.get('crit_resist', 0)),
        'battle_results': battle_results
    }

def fight_to_the_death(xml_file, attacker_id, defender_id, max_rounds=1000):
    """
    模拟两个角色之间的死斗，直到一方生命值降为0或以下
    
    参数:
    xml_file: XML文件路径
    attacker_id: 攻击方角色ID
    defender_id: 防御方角色ID
    max_rounds: 最大回合数，防止无限循环
    
    返回:
    战斗结果字典
    """
    # 加载角色，不使用深拷贝，而是直接获取字典数据
    attacker = load_character_from_xml(xml_file, character_id=attacker_id)
    defender = load_character_from_xml(xml_file, character_id=defender_id)
    
    if not attacker or not defender:
        print("无法加载角色信息，战斗取消")
        return None
    
    # 直接获取角色的字典表示，避免深拷贝
    attacker_props = attacker.to_dict()
    defender_props = defender.to_dict()
    
    # 确保必要的属性存在
    attacker_props.setdefault('health', 100)
    defender_props.setdefault('health', 100)
    attacker_props.setdefault('attack', 10)
    defender_props.setdefault('attack', 10)
    attacker_props.setdefault('defense', 5)
    defender_props.setdefault('defense', 5)
    attacker_props.setdefault('crit', 0)
    defender_props.setdefault('crit', 0)
    attacker_props.setdefault('crit_resist', 0)
    defender_props.setdefault('crit_resist', 0)
    attacker_props.setdefault('level', 1)
    defender_props.setdefault('level', 1)
    
    # 创建角色战斗副本，使用字典存储属性
    attacker_battle = attacker_props.copy()
    defender_battle = defender_props.copy()
    
    # 初始化统计数据
    rounds = 0
    total_attacker_damage = 0
    total_defender_damage = 0
    attacker_crit_count = 0
    defender_crit_count = 0
    round_history = []
    
    # 初始化生命值（如果不存在，则使用默认值）
    if 'health' not in attacker_battle:
        attacker_battle['health'] = attacker_battle.get('max_health', 100)
    if 'health' not in defender_battle:
        defender_battle['health'] = defender_battle.get('max_health', 100)
    
    # 战斗循环
    while attacker_battle['health'] > 0 and defender_battle['health'] > 0 and rounds < max_rounds:
        rounds += 1
        
        # 记录当前回合信息
        round_data = {
            'round': rounds,
            'attacker_damage': 0,
            'defender_damage': 0,
            'attacker_is_crit': False,
            'defender_is_crit': False
        }
        
        # 攻击者攻击防御者
        attacker_attack = attacker_battle.get('attack', 0)
        attacker_crit = attacker_battle.get('crit', 0)
        defender_defense = defender_battle.get('defense', 0)
        defender_crit_resist = defender_battle.get('crit_resist', 0)
        attacker_level = attacker_battle.get('level', 1)
        defender_level = defender_battle.get('level', 1)
        
        # 应用自定义属性加成
        damage_boost = attacker_battle.get('damage_boost', 0)
        damage_reduction = defender_battle.get('damage_reduction', 0)
        
        # 计算伤害
        damage, is_crit = calculate_damage(
            attacker_attack, defender_defense, 
            attacker_crit, defender_crit_resist,
            attacker_level=attacker_level, defender_level=defender_level
        )
        
        # 应用伤害加成和减益
        damage = max(1, damage + damage_boost - damage_reduction)
        
        # 记录伤害和暴击信息
        total_attacker_damage += damage
        if is_crit:
            attacker_crit_count += 1
        round_data['attacker_damage'] = damage
        round_data['attacker_is_crit'] = is_crit
        
        # 扣除防御者生命值
        defender_battle['health'] -= damage
        
        # 如果防御者已经死亡，结束战斗
        if defender_battle['health'] <= 0:
            round_data['attacker_health_after'] = attacker_battle['health']
            round_data['defender_health_after'] = 0
            round_history.append(round_data)
            break
        
        # 防御者反击攻击者
        defender_attack = defender_battle.get('attack', 0)
        defender_crit = defender_battle.get('crit', 0)
        attacker_defense = attacker_battle.get('defense', 0)
        attacker_crit_resist = attacker_battle.get('crit_resist', 0)
        
        # 应用自定义属性加成
        damage_boost = defender_battle.get('damage_boost', 0)
        damage_reduction = attacker_battle.get('damage_reduction', 0)
        
        # 计算伤害
        damage, is_crit = calculate_damage(
            defender_attack, attacker_defense, 
            defender_crit, attacker_crit_resist,
            attacker_level=defender_level, defender_level=attacker_level
        )
        
        # 应用伤害加成和减益
        damage = max(1, damage + damage_boost - damage_reduction)
        
        # 记录伤害和暴击信息
        total_defender_damage += damage
        if is_crit:
            defender_crit_count += 1
        round_data['defender_damage'] = damage
        round_data['defender_is_crit'] = is_crit
        
        # 扣除攻击者生命值
        attacker_battle['health'] -= damage
        
        # 记录回合结束后的生命值
        round_data['attacker_health_after'] = max(0, attacker_battle['health'])
        round_data['defender_health_after'] = max(0, defender_battle['health'])
        
        # 添加到战斗历史
        round_history.append(round_data)
    
    # 确定胜利者
    if attacker_battle['health'] > 0 and defender_battle['health'] <= 0:
        winner = attacker_props.get('name', '攻击方')
    elif defender_battle['health'] > 0 and attacker_battle['health'] <= 0:
        winner = defender_props.get('name', '防御方')
    else:
        winner = '平局'
    
    # 计算实际暴击率
    attacker_actual_crit_rate = attacker_crit_count / rounds if rounds > 0 else 0
    defender_actual_crit_rate = defender_crit_count / rounds if rounds > 0 else 0
    
    return {
        'attacker': {
            'name': attacker_props.get('name', '未知攻击者'),
            'id': attacker_props.get('id', 'unknown'),
            'initial_health': attacker_props['health'] + total_defender_damage,  # 还原初始生命值
            'final_health': max(0, attacker_props['health']),
            'custom_attributes': {k: v for k, v in attacker_props.items() if k not in ['name', 'id', 'health', 'attack', 'defense', 'crit', 'crit_resist', 'level']}
        },
        'defender': {
            'name': defender_props.get('name', '未知防御者'),
            'id': defender_props.get('id', 'unknown'),
            'initial_health': defender_props['health'] + total_attacker_damage,  # 还原初始生命值
            'final_health': max(0, defender_props['health']),
            'custom_attributes': {k: v for k, v in defender_props.items() if k not in ['name', 'id', 'health', 'attack', 'defense', 'crit', 'crit_resist', 'level']}
        },
        'winner': winner,
        'rounds': rounds,
        'max_rounds_reached': rounds >= max_rounds,
        'total_attacker_damage': total_attacker_damage,
        'total_defender_damage': total_defender_damage,
        'attacker_actual_crit_rate': attacker_actual_crit_rate,
        'defender_actual_crit_rate': defender_actual_crit_rate,
        'round_history': round_history
    }