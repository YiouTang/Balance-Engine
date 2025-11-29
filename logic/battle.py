# 战斗模拟模块
from core.damage import calculate_damage, calculate_critical_rate
from data.sqlite_handler import load_character
import copy
import random

def battle_between_characters(db_path, attacker_id, defender_id, simulate_count=1):
    """
    模拟两个角色之间的战斗
    
    参数:
    db_path: 数据库文件路径
    attacker_id: 攻击方角色ID
    defender_id: 防御方角色ID
    simulate_count: 模拟战斗次数
    
    返回:
    战斗结果统计字典
    """
    # 加载角色
    attacker = load_character(character_id=attacker_id, db_path=db_path)
    defender = load_character(character_id=defender_id, db_path=db_path)
    
    if not attacker or not defender:
        print("无法加载角色信息，战斗取消")
        return None
    
    # 获取角色属性，支持动态属性
    attacker_attrs = attacker.to_dict() if hasattr(attacker, 'to_dict') else vars(attacker)
    defender_attrs = defender.to_dict() if hasattr(defender, 'to_dict') else vars(defender)
    
    # 模拟战斗
    total_damage = 0
    crit_count = 0
    hit_count = 0
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
        damage_info = calculate_damage(
            attack,
            defense,
            crit,
            crit_resist,
            attacker_level=attacker_level,
            defender_level=defender_level,
            attacker_attributes=attacker_attrs,
            defender_attributes=defender_attrs
        )
        
        # 获取最终伤害和暴击信息
        damage = damage_info['final_damage']
        is_crit = damage_info['is_critical']
        is_hit = damage_info['is_hit']
        
        # 转换为整数伤害
        damage = int(damage)
        
        total_damage += damage
        if is_crit:
            crit_count += 1
        if is_hit:
            hit_count += 1
        
        # 构建战斗结果，包含所有伤害计算信息
        battle_result = {
            'damage': damage,
            'is_crit': is_crit,
            'is_hit': is_hit,
            'custom_effects_applied': {
                'damage_boost': attacker_attrs.get('damage_boost', 0),
                'damage_reduction': defender_attrs.get('damage_reduction', 0),
                'accuracy': attacker_attrs.get('accuracy', 0),
                'evasion': defender_attrs.get('evasion', 0)
            }
        }
        
        # 添加详细的伤害计算信息
        battle_result.update(damage_info)
        
        battle_results.append(battle_result)
    
    # 计算统计信息
    avg_damage = total_damage / simulate_count
    actual_crit_rate = crit_count / simulate_count
    actual_hit_rate = hit_count / simulate_count
    
    return {
        'attacker': attacker_attrs,
        'defender': defender_attrs,
        'simulate_count': simulate_count,
        'average_damage': avg_damage,
        'actual_crit_rate': actual_crit_rate,
        'actual_hit_rate': actual_hit_rate,
        'expected_crit_rate': calculate_critical_rate(attacker_attrs.get('crit', 0), attacker_attrs.get('crit_resist', 0)),
        'battle_results': battle_results
    }

def fight_to_the_death(db_path, attacker_id, defender_id, max_rounds=1000):
    """
    模拟两个角色之间的死斗，直到一方生命值降为0或以下
    
    参数:
    db_path: 数据库文件路径
    attacker_id: 攻击方角色ID
    defender_id: 防御方角色ID
    max_rounds: 最大回合数，防止无限循环
    
    返回:
    战斗结果字典
    """
    # 加载角色，不使用深拷贝，而是直接获取字典数据
    attacker = load_character(character_id=attacker_id, db_path=db_path)
    defender = load_character(character_id=defender_id, db_path=db_path)
    
    if not attacker or not defender:
        print("无法加载角色信息，战斗取消")
        return None
    
    # 直接获取角色的字典表示，避免深拷贝
    attacker_props = attacker.to_dict()
    defender_props = defender.to_dict()
    
    # 确保必要的属性存在
    attacker_props.setdefault('health', 100)
    defender_props.setdefault('health', 100)
    attacker_props.setdefault('max_health', attacker_props['health'])
    defender_props.setdefault('max_health', defender_props['health'])
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
    attacker_props.setdefault('agility', 10)
    defender_props.setdefault('agility', 10)
    attacker_props.setdefault('accuracy', 0)
    defender_props.setdefault('accuracy', 0)
    attacker_props.setdefault('evasion', 0)
    defender_props.setdefault('evasion', 0)
    attacker_props.setdefault('damage_boost', 0)
    defender_props.setdefault('damage_boost', 0)
    attacker_props.setdefault('damage_reduction', 0)
    defender_props.setdefault('damage_reduction', 0)
    attacker_props.setdefault('health_regen', 0)
    defender_props.setdefault('health_regen', 0)
    
    # 创建角色战斗副本，使用字典存储属性
    attacker_battle = attacker_props.copy()
    defender_battle = defender_props.copy()
    
    # 初始化统计数据
    rounds = 0
    total_attacker_damage = 0
    total_defender_damage = 0
    attacker_crit_count = 0
    defender_crit_count = 0
    attacker_hit_count = 0
    defender_hit_count = 0
    round_history = []
    
    # 战斗循环
    while attacker_battle['health'] > 0 and defender_battle['health'] > 0 and rounds < max_rounds:
        rounds += 1
        
        # 记录当前回合信息
        round_data = {
            'round': rounds,
            'first_attacker': '',
            'attacker_damage': 0,
            'defender_damage': 0,
            'attacker_is_crit': False,
            'defender_is_crit': False,
            'attacker_is_hit': False,
            'defender_is_hit': False,
            'attacker_health_regen': 0,
            'defender_health_regen': 0
        }
        
        # 1. 回合开始：生命回复
        attacker_health_regen = attacker_battle.get('health_regen', 0)
        defender_health_regen = defender_battle.get('health_regen', 0)
        
        if attacker_health_regen > 0:
            attacker_battle['health'] = min(attacker_battle['max_health'], attacker_battle['health'] + attacker_health_regen)
            round_data['attacker_health_regen'] = attacker_health_regen
        
        if defender_health_regen > 0:
            defender_battle['health'] = min(defender_battle['max_health'], defender_battle['health'] + defender_health_regen)
            round_data['defender_health_regen'] = defender_health_regen
        
        # 2. 先手判定：基于agility属性
        attacker_agility = attacker_battle.get('agility', 10)
        defender_agility = defender_battle.get('agility', 10)
        
        # 先手判定逻辑：敏捷高的一方先攻击，相同则随机
        if attacker_agility > defender_agility:
            first_attacker = 'attacker'
            second_attacker = 'defender'
        elif defender_agility > attacker_agility:
            first_attacker = 'defender'
            second_attacker = 'attacker'
        else:
            # 敏捷相同，随机决定先手
            first_attacker = random.choice(['attacker', 'defender'])
            second_attacker = 'defender' if first_attacker == 'attacker' else 'attacker'
        
        round_data['first_attacker'] = first_attacker
        
        # 3. 攻击顺序处理
        for attacker_role in [first_attacker, second_attacker]:
            if attacker_role == 'attacker':
                # 攻击者攻击防御者
                attacker = attacker_battle
                defender = defender_battle
                attacker_prefix = 'attacker'
                defender_prefix = 'defender'
            else:
                # 防御者攻击攻击者
                attacker = defender_battle
                defender = attacker_battle
                attacker_prefix = 'defender'
                defender_prefix = 'attacker'
            
            # 获取攻击方和防御方属性
            attacker_attack = attacker.get('attack', 0)
            attacker_crit = attacker.get('crit', 0)
            defender_defense = defender.get('defense', 0)
            defender_crit_resist = defender.get('crit_resist', 0)
            attacker_level = attacker.get('level', 1)
            defender_level = defender.get('level', 1)
            
            # 计算伤害
            damage_info = calculate_damage(
                attacker_attack, defender_defense, 
                attacker_crit, defender_crit_resist,
                attacker_level=attacker_level, defender_level=defender_level,
                attacker_attributes=attacker,
                defender_attributes=defender
            )
            
            # 获取最终伤害和暴击信息
            damage = int(damage_info['final_damage'])
            is_crit = damage_info['is_critical']
            is_hit = damage_info['is_hit']
            
            # 记录伤害和暴击信息
            if attacker_role == 'attacker':
                total_attacker_damage += damage
                if is_crit:
                    attacker_crit_count += 1
                if is_hit:
                    attacker_hit_count += 1
                round_data['attacker_damage'] = damage
                round_data['attacker_is_crit'] = is_crit
                round_data['attacker_is_hit'] = is_hit
                round_data['attacker_damage_info'] = damage_info
                
                # 扣除防御者生命值
                defender_battle['health'] -= damage
            else:
                total_defender_damage += damage
                if is_crit:
                    defender_crit_count += 1
                if is_hit:
                    defender_hit_count += 1
                round_data['defender_damage'] = damage
                round_data['defender_is_crit'] = is_crit
                round_data['defender_is_hit'] = is_hit
                round_data['defender_damage_info'] = damage_info
                
                # 扣除攻击者生命值
                attacker_battle['health'] -= damage
            
            # 检查是否有角色死亡
            if attacker_battle['health'] <= 0 or defender_battle['health'] <= 0:
                break
        
        # 记录回合结束后的生命值
        round_data['attacker_health_after'] = max(0, attacker_battle['health'])
        round_data['defender_health_after'] = max(0, defender_battle['health'])
        
        # 添加到战斗历史
        round_history.append(round_data)
        
        # 检查战斗是否结束
        if attacker_battle['health'] <= 0 or defender_battle['health'] <= 0:
            break
    
    # 确定胜利者
    if attacker_battle['health'] > 0 and defender_battle['health'] <= 0:
        winner = attacker_props.get('name', '攻击方')
    elif defender_battle['health'] > 0 and attacker_battle['health'] <= 0:
        winner = defender_props.get('name', '防御方')
    else:
        winner = '平局'
    
    # 计算实际暴击率和命中率
    attacker_actual_crit_rate = attacker_crit_count / rounds if rounds > 0 else 0
    defender_actual_crit_rate = defender_crit_count / rounds if rounds > 0 else 0
    attacker_actual_hit_rate = attacker_hit_count / rounds if rounds > 0 else 0
    defender_actual_hit_rate = defender_hit_count / rounds if rounds > 0 else 0
    
    return {
        'attacker': {
            'name': attacker_props.get('name', '未知攻击者'),
            'id': attacker_props.get('id', 'unknown'),
            'level': attacker_props.get('level', 1),
            'initial_health': attacker_props['health'],
            'final_health': max(0, attacker_battle['health']),
            'attack': attacker_props.get('attack', 0),
            'defense': attacker_props.get('defense', 0),
            'crit': attacker_props.get('crit', 0),
            'crit_resist': attacker_props.get('crit_resist', 0),
            'custom_attributes': {k: v for k, v in attacker_props.items() if k not in ['name', 'id', 'health', 'max_health', 'attack', 'defense', 'crit', 'crit_resist', 'level']}
        },
        'defender': {
            'name': defender_props.get('name', '未知防御者'),
            'id': defender_props.get('id', 'unknown'),
            'level': defender_props.get('level', 1),
            'initial_health': defender_props['health'],
            'final_health': max(0, defender_battle['health']),
            'attack': defender_props.get('attack', 0),
            'defense': defender_props.get('defense', 0),
            'crit': defender_props.get('crit', 0),
            'crit_resist': defender_props.get('crit_resist', 0),
            'custom_attributes': {k: v for k, v in defender_props.items() if k not in ['name', 'id', 'health', 'max_health', 'attack', 'defense', 'crit', 'crit_resist', 'level']}
        },
        'winner': winner,
        'rounds': rounds,
        'max_rounds_reached': rounds >= max_rounds,
        'total_attacker_damage': total_attacker_damage,
        'total_defender_damage': total_defender_damage,
        'attacker_actual_crit_rate': attacker_actual_crit_rate,
        'defender_actual_crit_rate': defender_actual_crit_rate,
        'attacker_actual_hit_rate': attacker_actual_hit_rate,
        'defender_actual_hit_rate': defender_actual_hit_rate,
        'round_history': round_history
    }