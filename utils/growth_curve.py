# 成长曲线算法模块
import math

def linear_growth(level, base_value, coefficient=1.0):
    """线性成长曲线"""
    return base_value * level * coefficient

def exponential_growth(level, base_value, exponent=1.2):
    """指数成长曲线"""
    return base_value * (level ** exponent)

def logarithmic_growth(level, base_value, base=math.e):
    """对数成长曲线"""
    return base_value * math.log(level + 1, base)

def power_growth(level, base_value, exponent=1.5, scaling=1.0):
    """幂函数成长曲线"""
    return base_value * (scaling * level) ** exponent

def sigmoid_growth(level, base_value, midpoint=50, steepness=0.1):
    """S形成长曲线"""
    return base_value / (1 + math.exp(-steepness * (level - midpoint)))

def hybrid_growth(level, base_value, early_coef=1.5, late_coef=1.0, transition_level=30):
    """混合成长曲线：前期快速，后期平缓"""
    if level < transition_level:
        return base_value * level * early_coef
    else:
        # 确保过渡平滑
        early_value = base_value * transition_level * early_coef
        additional_levels = level - transition_level
        return early_value + (base_value * additional_levels * late_coef)