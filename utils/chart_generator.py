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