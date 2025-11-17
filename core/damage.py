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

def calculate_damage(attacker_attack, defender_defense, attacker_crit=0, defender_crit_resist=0, 
                    critical_multiplier=2.0, is_critical=None, attacker_level=1, defender_level=1):
    """
    计算最终伤害值，包含暴击率判定和等级差异调整
    
    参数:
    attacker_attack: 攻击方的攻击力
    defender_defense: 受击方的防御力
    attacker_crit: 攻击方的暴击值
    defender_crit_resist: 受击方的暴抗值
    critical_multiplier: 暴击系数，默认为2.0
    is_critical: 可选参数，如果指定则直接使用该值作为是否暴击，否则根据暴击率随机判定
    attacker_level: 攻击方的等级
    defender_level: 防御方的等级
    
    返回:
    (最终伤害, 是否暴击)
    """
    # 计算基础伤害 = max(攻击方·攻击 - 受击方·防御, 1)
    base_damage = max(attacker_attack - defender_defense, 1)
    
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
    final_damage = damage_after_level * final_multiplier
    
    return final_damage, is_critical