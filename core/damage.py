# 伤害计算核心逻辑
import random

def calculate_critical_rate(attacker_crit, defender_crit_resist, divisor=100):
    """
    计算暴击率
    
    参数:
    attacker_crit: 攻击方的暴击值
    defender_crit_resist: 受击方的暴抗值
    divisor: 除数，用于调整暴击数值的影响力，默认为100
    
    返回:
    计算后的暴击率（0到1之间的小数）
    """
    # 计算暴击率 = max(攻击方·暴击 - 受击方·暴抗, 0) / divisor
    critical_rate = max(attacker_crit - defender_crit_resist, 0) / divisor
    # 确保暴击率不超过100%
    return min(critical_rate, 1.0)

def calculate_hit_rate(attacker_accuracy, defender_evasion, divisor=100):
    """
    计算命中率
    
    参数:
    attacker_accuracy: 攻击方的命中值
    defender_evasion: 受击方的闪避值
    divisor: 除数，用于调整命中数值的影响力，默认为100
    
    返回:
    计算后的命中率（0到1之间的小数）
    """
    # 计算基础命中率 = max(攻击方·命中 - 受击方·闪避, 0) / divisor
    base_hit_rate = max(attacker_accuracy - defender_evasion, 0) / divisor
    # 确保命中率在5%到95%之间
    return max(min(base_hit_rate, 0.95), 0.05)

def calculate_damage(attacker_attack, defender_defense, attacker_crit=0, defender_crit_resist=0, 
                    critical_multiplier=2.0, is_critical=None, is_hit=None, attacker_level=1, defender_level=1, 
                    attacker_attributes=None, defender_attributes=None):
    """
    计算最终伤害值，包含命中/闪避、暴击率判定和等级差异调整
    
    参数:
    attacker_attack: 攻击方的攻击力
    defender_defense: 受击方的防御力
    attacker_crit: 攻击方的暴击值
    defender_crit_resist: 受击方的暴抗值
    critical_multiplier: 暴击系数，默认为2.0
    is_critical: 可选参数，如果指定则直接使用该值作为是否暴击，否则根据暴击率随机判定
    is_hit: 可选参数，如果指定则直接使用该值作为是否命中，否则根据命中率随机判定
    attacker_level: 攻击方的等级
    defender_level: 防御方的等级
    attacker_attributes: 攻击方的完整属性字典（可选）
    defender_attributes: 防御方的完整属性字典（可选）
    
    返回:
    包含详细伤害计算信息的字典
    """
    # 确保属性字典存在
    attacker_attributes = attacker_attributes or {}
    defender_attributes = defender_attributes or {}
    
    # 获取所有相关属性，使用保险机制处理缺失属性
    attacker_accuracy = attacker_attributes.get('accuracy', 0)
    defender_evasion = defender_attributes.get('evasion', 0)
    attacker_damage_boost = attacker_attributes.get('damage_boost', 0)
    defender_damage_reduction = defender_attributes.get('damage_reduction', 0)
    
    # 计算命中率
    hit_rate = calculate_hit_rate(attacker_accuracy, defender_evasion)
    
    # 判定是否命中
    if is_hit is None:
        # 根据命中率随机判定是否命中
        is_hit = random.random() < hit_rate
    
    # 计算基础伤害：使用更合理的公式，避免防御过高导致伤害过低
    if attacker_attack <= 0:
        base_damage = 1  # 攻击为0时，基础伤害为1
    else:
        base_damage = attacker_attack * (attacker_attack / (attacker_attack + defender_defense * 0.5))
        base_damage = max(base_damage, 1)  # 确保基础伤害至少为1
    
    # 计算等级差异系数：高等级角色对低等级角色有伤害加成，反之有减伤
    level_diff = attacker_level - defender_level
    # 每级等级差影响5%伤害，最高±50%（10级差异）
    level_factor = 1 + min(max(level_diff * 0.05, -0.5), 0.5)
    damage_after_level = base_damage * level_factor
    
    # 计算暴击率
    critical_rate = calculate_critical_rate(attacker_crit, defender_crit_resist)
    
    # 判定是否暴击
    if is_critical is None:
        # 根据暴击率随机判定是否暴击
        is_critical = random.random() < critical_rate
    
    # 根据是否暴击决定最终伤害
    final_multiplier = critical_multiplier if is_critical else 1.0
    damage_after_crit = damage_after_level * final_multiplier
    
    # 应用伤害加成和减益
    damage_boost_factor = 1 + attacker_damage_boost / 100
    damage_reduction_factor = 1 - defender_damage_reduction / 100
    damage_reduction_factor = max(damage_reduction_factor, 0.1)  # 减伤最高90%
    
    final_damage = damage_after_crit * damage_boost_factor * damage_reduction_factor
    
    # 保险机制：即使未命中，也确保有最低伤害
    if not is_hit:
        # 未命中时造成最低伤害
        final_damage = 1
    else:
        # 命中时确保伤害至少为1
        final_damage = max(final_damage, 1)
    
    # 收集所有参与计算的属性
    damage_info = {
        'final_damage': final_damage,
        'is_critical': is_critical,
        'is_hit': is_hit,
        'hit_rate': hit_rate,
        'base_damage': base_damage,
        'level_factor': level_factor,
        'damage_after_level': damage_after_level,
        'critical_rate': critical_rate,
        'critical_multiplier': final_multiplier,
        'damage_after_crit': damage_after_crit,
        'damage_boost_factor': damage_boost_factor,
        'damage_reduction_factor': damage_reduction_factor,
        'attacker_attributes': {
            'attack': attacker_attack,
            'crit': attacker_crit,
            'accuracy': attacker_accuracy,
            'damage_boost': attacker_damage_boost,
            'level': attacker_level
        },
        'defender_attributes': {
            'defense': defender_defense,
            'crit_resist': defender_crit_resist,
            'evasion': defender_evasion,
            'damage_reduction': defender_damage_reduction,
            'level': defender_level
        },
        'custom_attributes_applied': {
            'attacker': {k: v for k, v in attacker_attributes.items() if k not in ['attack', 'crit', 'accuracy', 'damage_boost', 'level']},
            'defender': {k: v for k, v in defender_attributes.items() if k not in ['defense', 'crit_resist', 'evasion', 'damage_reduction', 'level']}
        }
    }
    
    return damage_info