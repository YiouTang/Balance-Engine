# 属性计算工具
import math
from utils.growth_curve import (
    linear_growth, exponential_growth, logarithmic_growth,
    power_growth, sigmoid_growth, hybrid_growth
)

def get_default_curve_params():
    """
    获取默认的成长曲线参数
    
    返回:
    默认参数字典，包含基础属性的默认成长参数
    """
    default_params = {
        # 基础属性的默认参数
        "attack": {
            "factor": 2.0,  # 线性因子
            "exponent": 1.1,  # 指数基数
            "log_base": 2.0,  # 对数底数
            "power": 1.2,  # 幂函数指数
            "midpoint": 20.0,  # S型曲线中点
            "steepness": 0.1,  # S型曲线陡度
            "switch_level": 30  # 混合曲线切换等级
        },
        "defense": {
            "factor": 1.5,  # 线性因子
            "exponent": 1.08,  # 指数基数
            "log_base": 2.0,  # 对数底数
            "power": 1.1,  # 幂函数指数
            "midpoint": 25.0,  # S型曲线中点
            "steepness": 0.08,  # S型曲线陡度
            "switch_level": 30  # 混合曲线切换等级
        },
        "health": {
            "factor": 10.0,  # 线性因子
            "exponent": 1.1,  # 指数基数
            "log_base": 2.0,  # 对数底数
            "power": 1.2,  # 幂函数指数
            "midpoint": 20.0,  # S型曲线中点
            "steepness": 0.1,  # S型曲线陡度
            "switch_level": 30  # 混合曲线切换等级
        },
        "crit": {
            "factor": 0.5,  # 线性因子
            "exponent": 1.05,  # 指数基数
            "log_base": 2.0,  # 对数底数
            "power": 1.05,  # 幂函数指数
            "midpoint": 25.0,  # S型曲线中点
            "steepness": 0.05,  # S型曲线陡度
            "switch_level": 30  # 混合曲线切换等级
        },
        "crit_resist": {
            "factor": 0.5,  # 线性因子
            "exponent": 1.05,  # 指数基数
            "log_base": 2.0,  # 对数底数
            "power": 1.05,  # 幂函数指数
            "midpoint": 25.0,  # S型曲线中点
            "steepness": 0.05,  # S型曲线陡度
            "switch_level": 30  # 混合曲线切换等级
        }
    }
    
    # 添加通用默认参数，用于处理自定义属性
    default_params["_default"] = {
        "factor": 1.0,  # 线性因子
        "exponent": 1.05,  # 指数基数
        "log_base": 2.0,  # 对数底数
        "power": 1.05,  # 幂函数指数
        "midpoint": 20.0,  # S型曲线中点
        "steepness": 0.05,  # S型曲线陡度
        "switch_level": 30  # 混合曲线切换等级
    }
    
    return default_params


def get_attribute_curve_params(attr_name, curve_params_dict=None):
    """
    获取指定属性的成长曲线参数，支持自定义属性
    
    参数:
    attr_name: 属性名称
    curve_params_dict: 已有的曲线参数字典（可选）
    
    返回:
    属性的曲线参数字典
    """
    # 如果没有提供参数字典，使用默认参数
    if curve_params_dict is None:
        curve_params_dict = get_default_curve_params()
    
    # 如果属性有特定参数，返回它
    if attr_name in curve_params_dict:
        return curve_params_dict[attr_name]
    
    # 否则返回默认参数
    return curve_params_dict.get("_default", {
        "factor": 1.0,
        "exponent": 1.05,
        "log_base": 2.0,
        "power": 1.05,
        "midpoint": 20.0,
        "steepness": 0.05,
        "switch_level": 30
    })

def generate_level_attributes(name, level_range=range(1, 101), curve_type="linear", curve_params=None, character=None):
    """
    生成角色从指定等级范围的预测属性值，支持不同的成长曲线，包括每个属性独立的曲线设置
    
    参数:
    name: 角色名称
    level_range: 要预测的等级范围，默认1-100级
    curve_type: 成长曲线类型（全局默认值）
    curve_params: 曲线参数字典（全局默认值）
    character: 可选的角色对象，如果提供则使用角色中保存的成长曲线信息
    """
    # 如果提供了角色对象，使用角色中保存的全局成长曲线信息
    if character is not None:
        curve_type = character.growth_curve_type
        curve_params = character.growth_curve_params
    
    # 默认曲线参数
    if curve_params is None:
        curve_params = {}
        # 为每个属性设置默认参数
        for attr in ['attack', 'defense', 'health', 'crit', 'crit_resist']:
            curve_params[attr] = get_default_curve_params(curve_type)
    
    # 选择成长曲线函数
    curve_functions = {
        "linear": linear_growth,
        "exponential": exponential_growth,
        "logarithmic": logarithmic_growth,
        "power": power_growth,
        "sigmoid": sigmoid_growth,
        "hybrid": hybrid_growth
    }
    
    # 创建属性字典
    attributes = {
        'level': list(level_range),
        'attack': [],
        'defense': [],
        'health': [],
        'crit': [],
        'crit_resist': []
    }
    
    # 各属性的基础值和系数
    base_values = {
        'attack': 1.2,
        'defense': 0.8,
        'health': 5.0,
        'crit': 0.3,
        'crit_resist': 0.2
    }
    
    # 为每个等级计算属性值
    for level in level_range:
        # 根据不同属性应用不同的成长曲线
        for attr, base_coef in base_values.items():
            # 如果有角色对象，获取该属性特定的曲线类型和参数
            attr_curve_type = curve_type
            attr_params = curve_params.get(attr, {})
            
            if character is not None:
                attr_curve_type, attr_params = character.get_attribute_curve_info(attr)
            
            # 为该属性选择对应的成长曲线函数
            growth_function = curve_functions.get(attr_curve_type, linear_growth)
            
            # 计算基础值
            base_value = 10  # 基础倍率
            # 应用成长曲线
            value = growth_function(level, base_value, **attr_params) * base_coef
            # 保存结果
            attributes[attr].append(int(value))
    
    return attributes