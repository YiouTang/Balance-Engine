# 图表生成工具
import matplotlib.pyplot as plt
import numpy as np
import csv

# 在文件顶部添加必要的导入
import math

# 修改 plot_attribute_growth 函数
def plot_attribute_growth(attributes, character_name, curve_type="linear", character=None):
    """
    绘制角色属性成长曲线图
    
    参数:
    attributes: 包含各等级属性值的字典
    character_name: 角色名称
    curve_type: 成长曲线类型，用于显示在图表标题中
    character: 角色对象，如果提供则从中获取成长曲线信息
    """
    import matplotlib.pyplot as plt
    import os
    
    # 确保中文显示正常
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    
    # 确定图表标题
    if character:
        # 检查是否存在不同的曲线类型
        has_different_curves = False
        attr_curve_types = {}
        
        # 获取所有属性的曲线类型
        for attr in ['attack', 'defense', 'health', 'crit', 'crit_resist']:
            curve_type, _ = character.get_attribute_curve_info(attr)
            attr_curve_types[attr] = curve_type
            
        # 检查是否有不同的曲线类型
        unique_types = set(attr_curve_types.values())
        has_different_curves = len(unique_types) > 1
        
        # 决定图表标题
        if has_different_curves:
            title = f'{character_name} 的属性成长曲线 (混合成长曲线)'  
        else:
            display_curve_type = character.growth_curve_type
            title = f'{character_name} 的属性成长曲线 ({get_curve_type_name(display_curve_type)})'
    else:
        title = f'{character_name} 的属性成长曲线 ({get_curve_type_name(curve_type)})'
    
    # 创建图表
    fig, axs = plt.subplots(3, 2, figsize=(15, 12))
    fig.suptitle(title, fontsize=16)
    
    # 定义属性和对应的子图位置
    attr_config = {
        'attack': {'ax': axs[0, 0], 'title': '攻击力成长', 'color': 'red'},
        'defense': {'ax': axs[0, 1], 'title': '防御力成长', 'color': 'blue'},
        'health': {'ax': axs[1, 0], 'title': '生命值成长', 'color': 'green'},
        'crit': {'ax': axs[1, 1], 'title': '暴击值成长', 'color': 'purple'},
        'crit_resist': {'ax': axs[2, 0], 'title': '暴抗值成长', 'color': 'orange'}
    }
    
    # 为每个属性绘制曲线
    for attr, config in attr_config.items():
        config['ax'].plot(attributes['level'], attributes[attr], color=config['color'], marker='o', markersize=2)
        
        # 如果提供了角色对象，在子图标题中显示该属性的曲线类型
        if character:
            attr_curve_type, _ = character.get_attribute_curve_info(attr)
            curve_type_name = get_curve_type_name(attr_curve_type)
            config['ax'].set_title(f'{config["title"]} ({curve_type_name})')
        else:
            config['ax'].set_title(config['title'])
        
        config['ax'].set_xlabel('等级')
        config['ax'].set_ylabel(attr)
        config['ax'].grid(True, linestyle='--', alpha=0.7)
    
    # 删除多余的子图
    fig.delaxes(axs[2, 1])
    
    # 调整布局
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    
    # 定义输出文件夹路径
    output_dir = "output_charts"
    # 如果文件夹不存在则创建
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 先生成并保存CSV表格
    csv_filename = f"{character_name}_属性数据.csv"
    csv_file_path = os.path.join(output_dir, csv_filename)
    
    # 定义CSV的列名
    headers = ['等级', 'attack', 'defense', 'health', 'crit', 'crit_resist']
    
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        # 写入表头
        writer.writerow(headers)
        
        # 写入数据行
        for i in range(len(attributes['level'])):
            row = [attributes['level'][i]]
            for attr in headers[1:]:  # 跳过'等级'列
                if attr in attributes:
                    row.append(attributes[attr][i])
                else:
                    row.append('')  # 如果某个属性不存在，则留空
            writer.writerow(row)
    
    print(f"属性数据已保存为CSV: {csv_file_path}")
    
    # 再保存图片到输出文件夹
    filename = f"{character_name}_属性曲线.png"
    file_path = os.path.join(output_dir, filename)
    plt.savefig(file_path)
    print(f"属性成长曲线已保存为: {file_path}")
    
    # 显示图表
    plt.show()

# 添加获取曲线类型中文名称的函数
def get_curve_type_name(curve_type):
    """
    获取曲线类型的中文名称
    """
    names = {
        "linear": "线性成长",
        "exponential": "指数成长",
        "logarithmic": "对数成长",
        "power": "幂函数成长",
        "sigmoid": "S形成长",
        "hybrid": "混合成长"
    }
    return names.get(curve_type, curve_type)

# 添加生成Gradio line_plot图表数据的函数
def generate_gradio_chart_data(character, max_level=100):
    """
    为Gradio的line_plot组件生成角色属性成长曲线数据
    
    参数:
    character: 角色对象
    max_level: 最大显示等级
    
    返回:
    x_data: 等级数据列表
    y_data_dict: 各属性的成长值字典，格式为 {"属性名": [值列表]}
    """
    print(f"[图表生成] 开始生成角色图表数据 - 角色: {character.name}, 最大等级: {max_level}")
    
    # 生成等级数据
    x_data = list(range(1, max_level + 1))
    print(f"[图表生成] 生成的等级数据: {x_data[:10]}...")
    
    # 定义需要显示的属性
    attributes = ['attack', 'defense', 'health', 'crit', 'crit_resist']
    
    # 检查角色基本属性
    for attr in attributes:
        base_value = character.__dict__.get(attr, 0)
        growth_factor = character.__dict__.get(f"{attr}_growth", 1)
        print(f"[图表生成] {character.name}的{attr}基础值: {base_value}, 成长因子: {growth_factor}")
    
    # 生成各属性的成长值数据
    y_data_dict = {}
    for attr in attributes:
        y_data = []
        print(f"[图表生成] 开始计算{attr}的成长数据")
        
        for level in x_data:
            # 计算该等级下的属性值
            # 创建临时字典存储属性值，模拟不同等级的角色
            temp_attrs = {}
            for temp_attr in attributes:
                curve_type, params = character.get_attribute_curve_info(temp_attr)
                # 根据曲线类型和参数计算属性值
                base_value = character.__dict__.get(temp_attr, 0)
                growth_factor = character.__dict__.get(f"{temp_attr}_growth", 1)
                
                # 简化的成长计算逻辑，实际应根据角色类中的计算方法
                if curve_type == "linear":
                    value = base_value + growth_factor * (level - 1)
                elif curve_type == "exponential":
                    factor = params.get("factor", 1.05)
                    value = base_value * (factor ** (level - 1))
                elif curve_type == "logarithmic":
                    value = base_value + growth_factor * math.log(level)
                else:  # 默认为线性
                    value = base_value + growth_factor * (level - 1)
                
                # 根据属性类型进行适当的数值处理
                if temp_attr in ['crit', 'crit_resist']:
                    value = min(value, 100)  # 暴击和暴抗上限设为100
                
                temp_attrs[temp_attr] = round(value, 2)
            
            # 记录第1、10、50、100等级的数据用于调试
            if level in [1, 10, 50, 100] and level <= max_level:
                print(f"[图表生成] 等级{level}的{attr}值: {temp_attrs[attr]}")
            
            y_data.append(temp_attrs[attr])
        
        y_data_dict[attr] = y_data
        print(f"[图表生成] {attr}数据生成完成，长度: {len(y_data)}")
    
    print(f"[图表生成] 所有属性数据生成完成，准备返回")
    return x_data, y_data_dict

# 添加生成单个属性Gradio图表数据的函数（用于单独显示某个属性的详细曲线）
def generate_single_attribute_chart_data(character, attribute, max_level=100):
    """
    为单个属性生成Gradio line_plot图表数据
    
    参数:
    character: 角色对象
    attribute: 属性名称
    max_level: 最大显示等级
    
    返回:
    x_data: 等级数据列表
    y_data: 属性值列表
    title: 图表标题
    """
    # 生成等级数据
    x_data = list(range(1, max_level + 1))
    
    # 生成属性成长值数据
    y_data = []
    curve_type, params = character.get_attribute_curve_info(attribute)
    base_value = character.__dict__.get(attribute, 0)
    growth_factor = character.__dict__.get(f"{attribute}_growth", 1)
    
    for level in x_data:
        # 根据曲线类型和参数计算属性值
        if curve_type == "linear":
            value = base_value + growth_factor * (level - 1)
        elif curve_type == "exponential":
            factor = params.get("factor", 1.05)
            value = base_value * (factor ** (level - 1))
        elif curve_type == "logarithmic":
            value = base_value + growth_factor * math.log(level)
        else:  # 默认为线性
            value = base_value + growth_factor * (level - 1)
        
        # 根据属性类型进行适当的数值处理
        if attribute in ['crit', 'crit_resist']:
            value = min(value, 100)  # 暴击和暴抗上限设为100
        
        y_data.append(round(value, 2))
    
    # 生成图表标题
    attribute_names = {
        'attack': '攻击力',
        'defense': '防御力',
        'health': '生命值',
        'crit': '暴击值',
        'crit_resist': '暴抗值'
    }
    attr_name = attribute_names.get(attribute, attribute)
    curve_name = get_curve_type_name(curve_type)
    title = f"{character.name} - {attr_name}成长曲线 ({curve_name})"
    
    return x_data, y_data, title