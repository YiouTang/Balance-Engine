import gradio as gr
import json
import os
import pandas as pd

# 设置Matplotlib非交互式后端，解决线程问题
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from data.sqlite_handler import (
    init_db,
    get_next_available_id,
    save_character,
    load_character,
    load_all_characters,
    get_attribute_config,
    delete_character
)
from core.character import Character
from utils.chart_generator import generate_gradio_chart_data, generate_single_attribute_chart_data

# 初始化数据库
init_db()

# 全局变量用于存储当前的角色数据和分页信息
current_characters = []
current_search = ""
current_page_size = 10
current_page_num = 1

def create_character(name, level, growth_curve_type, growth_curve_params_str):
    """创建新角色"""
    try:
        # 确保level是整数类型
        level_int = int(level) if level else 1
        
        # 解析成长曲线参数
        growth_curve_params = json.loads(growth_curve_params_str) if growth_curve_params_str else {}
        
        # 获取下一个可用ID
        char_id = get_next_available_id()
        
        # 创建角色对象
        character = Character(
            character_id=char_id,
            name=name,
            level=level_int,
            growth_curve_type=growth_curve_type,
            growth_curve_params=growth_curve_params
        )
        
        # 保存角色到数据库
        if save_character(character):
            return f"成功创建角色: {name} (ID: {char_id})"
        else:
            return f"创建角色失败: {name}"
    except Exception as e:
        return f"创建角色时出错: {str(e)}"

def view_character(character_id):
    """查看角色信息"""
    try:
        character = load_character(character_id=int(character_id))
        if character:
            char_dict = character.to_dict()
            result = f"角色信息:\n"
            result += f"ID: {char_dict['id']}\n"
            result += f"名称: {char_dict['name']}\n"
            result += f"等级: {char_dict['level']}\n"
            result += f"成长曲线类型: {char_dict['growth_curve_type']}\n"
            result += f"成长曲线参数: {json.dumps(char_dict['growth_curve_params'], ensure_ascii=False)}\n"
            result += f"属性成长曲线: {json.dumps(char_dict['attr_growth_curves'], ensure_ascii=False)}\n\n"
            result += "属性列表:\n"
            for attr_name, attr_value in char_dict.items():
                if attr_name not in ['id', 'name', 'level', 'growth_curve_type', 'growth_curve_params', 'attr_growth_curves']:
                    result += f"{attr_name}: {attr_value}\n"
            return result
        else:
            return f"未找到ID为 {character_id} 的角色"
    except Exception as e:
        return f"查看角色时出错: {str(e)}"

def update_character_attribute(character_id, attribute_name, attribute_value):
    """更新角色属性"""
    try:
        character = load_character(character_id=int(character_id))
        if character:
            # 更新属性值
            setattr(character, attribute_name, float(attribute_value))
            
            # 保存角色到数据库
            if save_character(character):
                return f"成功更新角色 {character.name} 的 {attribute_name} 属性为 {attribute_value}"
            else:
                return f"更新角色属性失败"
        else:
            return f"未找到ID为 {character_id} 的角色"
    except Exception as e:
        return f"更新角色属性时出错: {str(e)}"

def get_characters_dataframe(search="", page=1, page_size=10):
    """获取角色数据，支持搜索和分页"""
    global current_characters, current_search, current_page_size, current_page_num
    
    try:
        # 如果搜索条件变化，重置页码
        if search != current_search:
            current_search = search
            current_page_num = 1
        
        # 如果页面大小变化，重置页码
        if page_size != current_page_size:
            current_page_size = page_size
            current_page_num = 1
        
        # 更新当前页码
        current_page_num = page
        
        # 获取所有角色
        all_characters = load_all_characters()
        
        # 应用搜索过滤
        filtered_characters = []
        for character in all_characters:
            if not search or search.lower() in character.name.lower():
                filtered_characters.append(character)
        
        # 保存当前过滤后的角色数据
        current_characters = filtered_characters
        
        # 应用分页
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_characters = filtered_characters[start_idx:end_idx]
        
        # 转换为DataFrame格式：列表的列表
        data = []
        for character in paginated_characters:
            data.append([
                character.id,
                character.name,
                character.level
            ])
        
        return data
    except Exception as e:
        print(f"获取角色数据时出错: {str(e)}")
        return []

def get_total_pages(search="", page_size=10):
    """获取总页数"""
    try:
        all_characters = load_all_characters()
        
        # 应用搜索过滤
        filtered_count = 0
        for character in all_characters:
            if not search or search.lower() in character.name.lower():
                filtered_count += 1
        
        # 计算总页数
        total_pages = (filtered_count + page_size - 1) // page_size
        return max(1, total_pages)  # 至少1页
    except Exception as e:
        print(f"获取总页数时出错: {str(e)}")
        return 1

def list_all_characters():
    """列出所有角色"""
    try:
        characters = load_all_characters()
        if characters:
            result = "所有角色列表:\n\n"
            for character in characters:
                result += f"ID: {character.id}, 名称: {character.name}, 等级: {character.level}\n"
            return result
        else:
            return "数据库中没有角色"
    except Exception as e:
        return f"列出角色时出错: {str(e)}"

def delete_character_ui(character_id):
    """删除角色"""
    try:
        if delete_character(int(character_id)):
            return f"成功删除角色: ID={character_id}"
        else:
            return f"删除角色失败: ID={character_id}"
    except Exception as e:
        return f"删除角色时出错: {str(e)}"

def update_character_basic(character_id, name, level, growth_curve_type, growth_curve_params_str):
    """更新角色基本信息"""
    try:
        # 解析成长曲线参数
        growth_curve_params = json.loads(growth_curve_params_str) if growth_curve_params_str else {}
        
        # 加载角色
        character = load_character(character_id=int(character_id))
        if character:
            # 更新基本信息
            character.name = name
            character.level = level
            character.growth_curve_type = growth_curve_type
            character.growth_curve_params = growth_curve_params
            
            # 保存角色
            if save_character(character):
                return f"成功更新角色基本信息: {name} (ID: {character_id})"
            else:
                return f"更新角色基本信息失败: {name}"
        else:
            return f"未找到角色: ID={character_id}"
    except Exception as e:
        return f"更新角色基本信息时出错: {str(e)}"

def get_all_attributes():
    """获取所有属性名称"""
    config = get_attribute_config()
    all_attrs = list(config.get('base_attributes', {}).keys()) + list(config.get('custom_attributes', {}).keys())
    return all_attrs

def refresh_character_details(char_id):
    """刷新角色详情"""
    if char_id:
        character = load_character(character_id=int(char_id))
        if character:
            char_dict = character.to_dict()
            # 生成属性表格数据
            attributes_data = []
            for attr_name, attr_value in char_dict.items():
                if attr_name not in ['id', 'name', 'level', 'growth_curve_type', 'growth_curve_params', 'attr_growth_curves']:
                    # 获取属性的成长曲线类型和参数
                    curve_type, curve_params = character.get_attribute_curve_info(attr_name)
                    # 将参数转换为JSON字符串
                    params_str = json.dumps(curve_params) if curve_params else "{}"
                    attributes_data.append([attr_name, attr_value, curve_type, params_str])
            return attributes_data
    return []



def delete_character_and_refresh(char_id):
    """删除角色并刷新界面"""
    # 确保char_id是有效的正整数
    if not char_id or int(char_id) <= 0:
        return ["请先选择一个角色", "", "", 1, "linear", "{}", []]
    
    result = delete_character_ui(char_id)
    # 清空表单和表格，使用空字符串而不是None避免违反minimum=1约束
    return [result, "", "", 1, "linear", "{}", []]

def refresh_list():
    """刷新角色列表"""
    return get_characters_dataframe(search=current_search, page=current_page_num, page_size=current_page_size)

# 创建Gradio界面
with gr.Blocks(title="🎮 平衡引擎 Balance Engine") as demo:
    gr.Markdown("# 🎮 平衡引擎 Balance Engine")
    
    # 角色管理部分（查看、修改、删除）- 放在第一部分
    with gr.Tab("角色管理"):
        gr.Markdown("## 角色管理")
        
        # 角色列表和操作区域
        with gr.Row():
            # 左侧：角色列表和搜索
            with gr.Column(scale=1):
                # 角色列表搜索
                gr.Markdown("### 角色管理")
                search_input = gr.Textbox(label="搜索角色", placeholder="输入角色名称搜索")
                
                # 使用DataFrame展示角色列表
                characters_df = gr.DataFrame(
                    headers=["ID", "名称", "等级"],
                    datatype=["number", "str", "number"],
                    value=[],  # 初始为空，后续通过demo.load填充
                    interactive=False,
                    label="角色列表"
                )
                
                # 分页控件
                with gr.Row():
                    page_size = gr.Dropdown(
                        choices=[5, 10, 20],
                        label="每页显示数量",
                        value=10
                    )
                    current_page = gr.Number(label="当前页码", value=1, minimum=1, interactive=False)
                    with gr.Row():
                        prev_btn = gr.Button("上一页")
                        next_btn = gr.Button("下一页")
                
                # 刷新按钮
                refresh_btn = gr.Button("刷新列表")
                
                # 初始化数据库按钮
                gr.Markdown("⚠️ **提示：只有第一次启动项目时需要初始化数据库**")
                init_btn = gr.Button("初始化数据库")
                init_output = gr.Textbox(label="初始化结果")
                
                init_btn.click(
                    fn=lambda: "数据库已初始化",
                    inputs=[],
                    outputs=init_output
                )
            
            # 右侧：角色详情和修改合并
            with gr.Column(scale=1):
                gr.Markdown("### 角色详情与修改")
                
                # 角色ID（只读）
                char_id_display = gr.Number(label="角色ID", minimum=1, interactive=False)
                
                # 角色基本信息编辑表单 - 紧凑布局
                with gr.Row():
                    char_name_edit = gr.Textbox(label="角色名称", placeholder="输入角色名称", scale=2)
                    char_level_edit = gr.Number(label="角色等级", value=1, minimum=1, scale=1)
                
                with gr.Row():
                    char_growth_type_edit = gr.Dropdown(
                        choices=["linear", "exponential", "logarithmic"],
                        label="成长曲线类型",
                        value="linear",
                        scale=1
                    )
                    char_growth_params_edit = gr.Textbox(
                        label="成长曲线参数 (JSON格式)",
                        placeholder='例如: {"base": 10, "factor": 2}',
                        value="{}",
                        scale=2
                    )
                
                # 角色属性表格显示（可编辑）
                gr.Markdown("#### 角色属性（可编辑）")
                char_attributes_table = gr.DataFrame(
                    headers=["属性名称", "属性值", "成长曲线类型", "成长曲线参数"],
                    datatype=["str", "number", "str", "str"],
                    value=[],
                    interactive=True,  # 设置为可编辑
                    label="属性列表"
                )
                
                # 操作按钮 - 紧凑布局
                with gr.Row():
                    view_details_btn = gr.Button("刷新详情", scale=1)
                    save_btn = gr.Button("保存修改", scale=1)
                    delete_btn = gr.Button("删除角色", scale=1)
                
                # 操作结果
                operation_result = gr.Textbox(label="操作结果")
            
            # 角色成长曲线图表
            with gr.Column(scale=1):
                gr.Markdown("### 角色成长曲线")
                
                # 获取所有属性的函数
                def get_all_attribute_options():
                    """获取所有属性选项"""
                    from data.sqlite_handler import get_attribute_config
                    config = get_attribute_config()
                    # 获取所有基础属性和自定义属性
                    all_attrs = list(config.get('base_attributes', {}).keys()) + list(config.get('custom_attributes', {}).keys())
                    # 添加"所有属性"选项
                    return ["所有属性"] + all_attrs
                
                # 图表配置选项
                with gr.Row():
                    attribute_type = gr.Dropdown(
                        choices=get_all_attribute_options(),
                        label="属性类型",
                        value="所有属性"
                    )
                    max_level = gr.Number(label="最大等级", value=100, minimum=10, maximum=200, step=10)
                
                # 生成图表按钮
                generate_chart_btn = gr.Button("生成成长曲线")
                
                # 生成初始图表
                def get_initial_chart_data():
                    """生成初始图表"""
                    import matplotlib.pyplot as plt
                    import matplotlib as mpl
                    from utils.growth_curve import (linear_growth, exponential_growth, logarithmic_growth,
                                                  power_growth, sigmoid_growth, hybrid_growth)
                    
                    # 设置中文支持
                    mpl.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体显示中文
                    mpl.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
                    
                    # 创建示例数据
                    levels = range(1, 101)
                    
                    # 创建图表
                    fig, ax = plt.subplots(figsize=(10, 6))
                    
                    # 绘制不同成长曲线的示例
                    ax.plot(levels, [linear_growth(level, 10, 1.5) for level in levels], label='线性成长')
                    ax.plot(levels, [exponential_growth(level, 10, 1.1) for level in levels], label='指数成长')
                    ax.plot(levels, [logarithmic_growth(level, 50, 2) for level in levels], label='对数成长')
                    ax.plot(levels, [power_growth(level, 5, 1.5, 1) for level in levels], label='幂函数成长')
                    ax.plot(levels, [sigmoid_growth(level, 200, 50, 0.1) for level in levels], label='S形成长')
                    ax.plot(levels, [hybrid_growth(level, 10, 1.5, 1.0, 30) for level in levels], label='混合成长')
                    
                    # 设置图表标题和标签
                    ax.set_title('不同成长曲线示例')
                    ax.set_xlabel('等级')
                    ax.set_ylabel('属性值')
                    ax.legend()
                    ax.grid(True)
                    
                    return fig
                
                # 成长曲线图表，添加初始数据
                growth_chart = gr.Plot(
                    label="角色属性成长曲线",
                    value=get_initial_chart_data()  # 添加初始数据
                )
                
                # 生成图表数据的函数
                def generate_growth_chart(char_id, attribute_type, max_level_value):
                    try:
                        import matplotlib.pyplot as plt
                        import matplotlib as mpl
                        from utils.attribute_calculator import generate_level_attributes
                        from core.character import Character
                        from data.sqlite_handler import load_character
                        
                        # 设置中文支持
                        mpl.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体显示中文
                        mpl.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
                        
                        # 确保参数类型正确
                        char_id = int(char_id) if char_id is not None and str(char_id).strip().isdigit() else 1
                        max_level_value = int(max_level_value) if max_level_value is not None and str(max_level_value).isdigit() else 100
                        
                        # 加载角色对象
                        character = load_character(character_id=char_id)
                        
                        # 生成等级范围
                        levels = list(range(1, max_level_value + 1))
                        
                        # 生成属性数据
                        attributes_data = generate_level_attributes(
                            name=character.name if character else "角色",
                            level_range=levels,
                            character=character
                        )
                        
                        # 根据选择生成数据
                        attributes_to_plot = list(attributes_data.keys())[1:] if attribute_type == "所有属性" else [attribute_type]
                        
                        # 创建图表
                        fig, ax = plt.subplots(figsize=(10, 6))
                        
                        # 绘制不同属性的曲线
                        for attr in attributes_to_plot:
                            if attr in attributes_data:
                                ax.plot(levels, attributes_data[attr], label=attr)
                        
                        # 设置图表标题和标签
                        ax.set_title('角色属性成长曲线')
                        ax.set_xlabel('等级')
                        ax.set_ylabel('属性值')
                        ax.legend()
                        ax.grid(True)
                        
                        print(f"[图表生成] 生成数据: {len(levels)} 个等级, 属性: {attributes_to_plot}")
                        return fig
                    except Exception as e:
                        print(f"[图表生成] 错误: {str(e)}")
                        # 出错时返回简单的示例图表
                        import matplotlib.pyplot as plt
                        import matplotlib as mpl
                        from utils.growth_curve import (linear_growth, exponential_growth, logarithmic_growth,
                                                      power_growth, sigmoid_growth, hybrid_growth)
                        
                        # 设置中文支持
                        mpl.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体显示中文
                        mpl.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
                        
                        fig, ax = plt.subplots(figsize=(10, 6))
                        levels = range(1, 101)
                        
                        # 绘制不同成长曲线的示例
                        ax.plot(levels, [linear_growth(level, 10, 1.5) for level in levels], label='线性成长')
                        ax.plot(levels, [exponential_growth(level, 10, 1.1) for level in levels], label='指数成长')
                        ax.plot(levels, [logarithmic_growth(level, 50, 2) for level in levels], label='对数成长')
                        ax.plot(levels, [power_growth(level, 5, 1.5, 1) for level in levels], label='幂函数成长')
                        ax.plot(levels, [sigmoid_growth(level, 200, 50, 0.1) for level in levels], label='S形成长')
                        ax.plot(levels, [hybrid_growth(level, 10, 1.5, 1.0, 30) for level in levels], label='混合成长')
                        
                        ax.set_title('不同成长曲线示例')
                        ax.set_xlabel('等级')
                        ax.set_ylabel('属性值')
                        ax.legend()
                        ax.grid(True)
                        print(f"[图表生成] 返回示例数据")
                        return fig
                
                # 生成图表事件绑定
                generate_chart_btn.click(
                    fn=generate_growth_chart,
                    inputs=[char_id_display, attribute_type, max_level],
                    outputs=growth_chart
                )
                
                # 当选择角色时自动生成图表
                def on_character_select(evt: gr.SelectData):
                    # 获取当前页面的所有角色数据
                    current_data = get_characters_dataframe(search=current_search, page=current_page_num, page_size=current_page_size)
                    # evt.index是一个列表，第一个元素是行索引
                    if isinstance(evt.index, list):
                        row_idx = evt.index[0]
                    else:
                        row_idx = evt.index
                    
                    if 0 <= row_idx < len(current_data):
                        char_id = current_data[row_idx][0]  # 获取角色ID
                        return generate_growth_chart(char_id, "所有属性", 100)
                    return generate_growth_chart(1, "所有属性", 100)
                
                characters_df.select(
                    fn=on_character_select,
                    inputs=[],
                    outputs=growth_chart
                )
                
                # 当属性类型或最大等级变化时自动更新图表
                attribute_type.change(
                    fn=generate_growth_chart,
                    inputs=[char_id_display, attribute_type, max_level],
                    outputs=growth_chart
                )
                
                max_level.change(
                    fn=generate_growth_chart,
                    inputs=[char_id_display, attribute_type, max_level],
                    outputs=growth_chart
                )
        
        # 搜索功能实现
        def perform_search(search_text):
            return get_characters_dataframe(search=search_text, page=1, page_size=current_page_size)
        
        # 绑定搜索输入事件
        search_input.change(
            fn=perform_search,
            inputs=[search_input],
            outputs=[characters_df]
        )
        
        # 分页功能实现
        def go_to_previous_page():
            global current_page_num
            if current_page_num > 1:
                current_page_num -= 1
                return [
                    get_characters_dataframe(search=current_search, page=current_page_num, page_size=current_page_size),
                    current_page_num
                ]
            return [characters_df.value, current_page_num]
        
        def go_to_next_page():
            global current_page_num
            total_pages = get_total_pages(search=current_search, page_size=current_page_size)
            if current_page_num < total_pages:
                current_page_num += 1
                return [
                    get_characters_dataframe(search=current_search, page=current_page_num, page_size=current_page_size),
                    current_page_num
                ]
            return [characters_df.value, current_page_num]
        
        def change_page_size(new_page_size):
            global current_page_size, current_page_num
            current_page_size = new_page_size
            current_page_num = 1
            return [
                get_characters_dataframe(search=current_search, page=1, page_size=current_page_size),
                1
            ]
        
        # 绑定分页按钮事件
        prev_btn.click(
            fn=go_to_previous_page,
            inputs=[],
            outputs=[characters_df, current_page]
        )
        
        next_btn.click(
            fn=go_to_next_page,
            inputs=[],
            outputs=[characters_df, current_page]
        )
        
        page_size.change(
            fn=change_page_size,
            inputs=[page_size],
            outputs=[characters_df, current_page]
        )
        
        # 列表点击事件：当用户点击列表中的角色时，自动填充到表单
        def on_row_click(evt: gr.SelectData):
            # 获取行索引（evt.index是一个列表，第一个元素是行索引）
            if isinstance(evt.index, list) and len(evt.index) > 0:
                row_index = evt.index[0]
                
                # 获取完整的角色数据
                all_characters = get_characters_dataframe(search=current_search, page=current_page_num, page_size=current_page_size)
                
                # 检查行索引是否有效
                if 0 <= row_index < len(all_characters):
                    row_data = all_characters[row_index]
                    char_id = int(row_data[0])
                    
                    # 获取角色详情
                    character = load_character(character_id=char_id)
                    if character:
                        char_dict = character.to_dict()
                        # 生成属性表格数据
                        attributes_data = []
                        for attr_name, attr_value in char_dict.items():
                            if attr_name not in ['id', 'name', 'level', 'growth_curve_type', 'growth_curve_params', 'attr_growth_curves']:
                                # 获取属性的成长曲线类型和参数
                                curve_type, curve_params = character.get_attribute_curve_info(attr_name)
                                # 将参数转换为JSON字符串
                                params_str = json.dumps(curve_params) if curve_params else "{}"
                                attributes_data.append([attr_name, attr_value, curve_type, params_str])
                    else:
                        attributes_data = []
                    
                    # 返回填充数据
                    return [
                        char_id,              # 角色ID（只读）
                        str(row_data[1]),     # 角色名称
                        int(row_data[2]),     # 角色等级
                        "linear",            # 成长曲线类型（默认值）
                        "{}",                # 成长曲线参数（默认值）
                        attributes_data       # 角色属性表格数据
                    ]
            return [None, "", 1, "linear", "{}", []]  # 返回空列表作为默认值
        
        # 绑定列表点击事件
        characters_df.select(
            fn=on_row_click,
            inputs=[],
            outputs=[char_id_display, char_name_edit, char_level_edit, char_growth_type_edit, char_growth_params_edit, char_attributes_table]
        )
        
        # 刷新列表
        refresh_btn.click(
            fn=refresh_list,
            inputs=[],
            outputs=[characters_df]
        )
        
        # 刷新角色详情按钮
        view_details_btn.click(
            fn=refresh_character_details,
            inputs=[char_id_display],
            outputs=[char_attributes_table]
        )
        
        # 保存角色修改
        def save_character_changes(char_id, name, level, growth_type, growth_params_str, attributes_table):
            if not char_id:
                return "请先选择一个角色"
            
            try:
                # 解析成长曲线参数
                growth_params = json.loads(growth_params_str) if growth_params_str else {}
                
                # 加载角色
                character = load_character(character_id=int(char_id))
                if character:
                    # 更新角色基本信息
                    character.name = name
                    character.level = level
                    # 保留成长曲线类型和参数作为默认值
                    character.growth_curve_type = growth_type
                    character.growth_curve_params = growth_params
                    
                    # 更新属性的成长曲线类型和参数
                    if attributes_table is not None:
                        # 检查attributes_table是否为DataFrame，如果是则转换为列表
                        import pandas as pd
                        if isinstance(attributes_table, pd.DataFrame):
                            attributes_table = attributes_table.values.tolist()
                        
                        if isinstance(attributes_table, list):
                            for row in attributes_table:
                                if isinstance(row, list) and len(row) >= 4:
                                    attr_name, _, attr_curve_type, params_str = row
                                    # 确保attr_name是字符串类型
                                    attr_name = str(attr_name)
                                    # 确保成长曲线类型是有效的
                                    valid_curve_types = ["linear", "exponential", "logarithmic", "power", "sigmoid", "hybrid"]
                                    if attr_curve_type in valid_curve_types:
                                        if attr_name not in character.attr_growth_curves:
                                            character.attr_growth_curves[attr_name] = {}
                                        # 更新成长曲线类型
                                        character.attr_growth_curves[attr_name]['curve_type'] = attr_curve_type
                                        # 解析并更新成长曲线参数
                                        try:
                                            curve_params = json.loads(params_str) if params_str else {}
                                            character.attr_growth_curves[attr_name]['curve_params'] = curve_params
                                        except json.JSONDecodeError:
                                            # 如果JSON解析出错，使用空字典
                                            character.attr_growth_curves[attr_name]['curve_params'] = {}
                    
                    # 根据等级和成长曲线重新计算所有属性值
                    character.recalculate_attributes()
                    
                    # 保存角色
                    save_result = save_character(character)
                    if save_result:
                        # 刷新角色详情
                        return f"成功保存角色: {name} (ID: {char_id})"
                    else:
                        return f"保存角色失败: {name}"
                else:
                    return f"未找到角色: ID={char_id}"
            except Exception as e:
                import traceback
                error_msg = f"保存角色时出错: {str(e)}\n{traceback.format_exc()}"
                print(error_msg)
                return error_msg
        
        # 保存修改按钮
        save_btn.click(
            fn=save_character_changes,
            inputs=[char_id_display, char_name_edit, char_level_edit, char_growth_type_edit, char_growth_params_edit, char_attributes_table],
            outputs=[operation_result]
        )
        
        # 保存修改后刷新列表和详情
        save_btn.click(
            fn=refresh_list,
            inputs=[],
            outputs=[characters_df]
        )
        
        save_btn.click(
            fn=refresh_character_details,
            inputs=[char_id_display],
            outputs=[char_attributes_table]
        )
        
        # 删除角色按钮事件绑定
        delete_btn.click(
            fn=delete_character_and_refresh,
            inputs=[char_id_display],
            outputs=[operation_result, char_id_display, char_name_edit, char_level_edit, char_growth_type_edit, char_growth_params_edit, char_attributes_table]
        )
        
        # 删除角色后刷新列表
        delete_btn.click(
            fn=refresh_list,
            inputs=[],
            outputs=[characters_df]
        )
    
    # 创建新角色部分 - 放在第二部分
    with gr.Tab("创建角色"):
        gr.Markdown("## 创建新角色")
        with gr.Row():
            with gr.Column(scale=1):
                char_name = gr.Textbox(label="角色名称", placeholder="输入角色名称")
                char_level = gr.Number(label="角色等级", value=1, minimum=1)
                growth_curve_type = gr.Dropdown(
                    choices=["linear", "exponential", "logarithmic"],
                    label="成长曲线类型",
                    value="linear"
                )
                growth_curve_params = gr.Textbox(
                    label="成长曲线参数 (JSON格式)",
                    placeholder='例如: {"base": 10, "factor": 2}',
                    value="{}"
                )
                create_btn = gr.Button("创建角色")
        create_output = gr.Textbox(label="创建结果")
        
        create_btn.click(
            fn=create_character,
            inputs=[char_name, char_level, growth_curve_type, growth_curve_params],
            outputs=create_output
        )
        
        # 创建角色后刷新角色列表
        create_btn.click(
            fn=get_characters_dataframe,
            inputs=[],
            outputs=characters_df
        )
    
    # 成长曲线参数计算器
    with gr.Tab("成长曲线参数计算器"):
        gr.Markdown("## 成长曲线参数计算器")
        gr.Markdown("通过输入两个等级和对应的属性值，自动计算成长曲线参数")
        
        # 曲线类型选择
        curve_type = gr.Dropdown(
            choices=["linear", "exponential", "logarithmic", "power", "sigmoid", "hybrid"],
            label="成长曲线类型",
            value="linear"
        )
        
        # 输入两个点
        with gr.Row():
            with gr.Column():
                gr.Markdown("### 点1")
                level1 = gr.Number(label="等级1", value=1, minimum=1)
                value1 = gr.Number(label="属性值1", value=10, minimum=0)
            
            with gr.Column():
                gr.Markdown("### 点2")
                level2 = gr.Number(label="等级2", value=100, minimum=1)
                value2 = gr.Number(label="属性值2", value=1000, minimum=0)
        
        # 计算按钮
        calculate_btn = gr.Button("计算参数")
        
        # 结果显示
        result_params = gr.Textbox(
            label="计算结果 (JSON格式)",
            placeholder="计算出的参数将显示在这里",
            interactive=False
        )
        
        # 计算结果的说明
        result_explanation = gr.Markdown("### 参数说明")
        
        # 计算参数的函数
        def calculate_curve_params(curve_type, l1, v1, l2, v2):
            import math
            
            # 确保输入值有效
            if l1 <= 0 or l2 <= 0 or l1 == l2:
                return "{} (错误：等级必须为正整数且不相等)", "### 参数说明\n输入无效：等级必须为正整数且不相等"
            
            # 确保level1 < level2
            if l1 > l2:
                l1, l2 = l2, l1
                v1, v2 = v2, v1
            
            try:
                params = {}
                explanation = f"### 参数说明\n曲线类型：{curve_type}\n"
                
                if curve_type == "linear":
                    # 线性：y = base_value * level * coefficient
                    # 假设base_value=10（与系统默认一致）
                    base_value = 10
                    coefficient = (v2 - v1) / (base_value * (l2 - l1))
                    params = {"coefficient": round(coefficient, 4)}
                    explanation += f"- coefficient: {round(coefficient, 4)}（成长系数）\n"
                    explanation += f"公式：y = {base_value} * level * {round(coefficient, 4)}"
                
                elif curve_type == "exponential":
                    # 指数：y = base_value * (level ** exponent)
                    base_value = 10
                    # 解方程组：
                    # v1 = base_value * (l1 ** exponent)
                    # v2 = base_value * (l2 ** exponent)
                    # 相除得：v2/v1 = (l2/l1) ** exponent
                    # 取对数得：ln(v2/v1) = exponent * ln(l2/l1)
                    exponent = math.log(v2/v1) / math.log(l2/l1)
                    params = {"exponent": round(exponent, 4)}
                    explanation += f"- exponent: {round(exponent, 4)}（指数）\n"
                    explanation += f"公式：y = {base_value} * (level ** {round(exponent, 4)})"
                
                elif curve_type == "logarithmic":
                    # 对数：y = base_value * math.log(level + 1, base)
                    base_value = 10
                    # 解方程组：
                    # v1 = base_value * log(1+l1, base)
                    # v2 = base_value * log(1+l2, base)
                    # 相除得：v2/v1 = log(1+l2, base) / log(1+l1, base)
                    # 换底公式：log(a,b) = ln(a)/ln(b)
                    # 所以：v2/v1 = ln(1+l2)/ln(base) / (ln(1+l1)/ln(base)) = ln(1+l2)/ln(1+l1)
                    # 这说明对数曲线无法通过两个点唯一确定base参数
                    # 我们使用默认base=e，并调整base_value来拟合
                    log_ratio = math.log(1+l2) / math.log(1+l1)
                    if log_ratio != 0:
                        adjusted_base_value = v1 / math.log(1+l1)
                        params = {"base": round(math.e, 4)}
                        explanation += f"- base: {round(math.e, 4)}（对数底数）\n"
                        explanation += f"公式：y = {round(adjusted_base_value, 4)} * log(level + 1, e)\n"
                        explanation += f"注意：对数曲线通过调整base_value来拟合，base参数固定为e"
                    else:
                        params = {"base": 2.0}
                        explanation += f"- base: 2.0（对数底数）\n"
                        explanation += f"公式：y = {base_value} * log(level + 1, 2)\n"
                        explanation += f"注意：无法精确拟合，使用默认参数"
                
                elif curve_type == "power":
                    # 幂函数：y = base_value * (scaling * level) ** exponent
                    base_value = 10
                    # 假设scaling=1，解exponent
                    exponent = math.log(v2/v1) / math.log(l2/l1)
                    # 然后计算scaling
                    scaling = (v1 / base_value) ** (1/exponent) / l1
                    params = {"exponent": round(exponent, 4), "scaling": round(scaling, 4)}
                    explanation += f"- exponent: {round(exponent, 4)}（指数）\n"
                    explanation += f"- scaling: {round(scaling, 4)}（缩放系数）\n"
                    explanation += f"公式：y = {base_value} * ({round(scaling, 4)} * level) ** {round(exponent, 4)}"
                
                elif curve_type == "sigmoid":
                    # S形：y = base_value / (1 + math.exp(-steepness * (level - midpoint)))
                    # 假设base_value=1000（根据v2的大小调整）
                    base_value = max(v2 * 1.1, 1000)  # 确保最大值接近v2
                    # 解方程组：
                    # v1 = base_value / (1 + e^(-s*(l1 - m)))
                    # v2 = base_value / (1 + e^(-s*(l2 - m)))
                    # 简化：
                    # 1 + e^(-s*(l1 - m)) = base_value / v1
                    # 1 + e^(-s*(l2 - m)) = base_value / v2
                    # 令：
                    # a = base_value / v1 - 1
                    # b = base_value / v2 - 1
                    # 则：
                    # e^(-s*(l1 - m)) = a
                    # e^(-s*(l2 - m)) = b
                    # 取对数：
                    # -s*(l1 - m) = ln(a)
                    # -s*(l2 - m) = ln(b)
                    # 解方程组得：
                    # s = (ln(b) - ln(a)) / (l1 - l2)
                    # m = l1 + ln(a) / s
                    a = base_value / v1 - 1
                    b = base_value / v2 - 1
                    
                    if a > 0 and b > 0:
                        steepness = (math.log(b) - math.log(a)) / (l1 - l2)
                        midpoint = l1 + math.log(a) / steepness
                        params = {"midpoint": round(midpoint, 2), "steepness": round(steepness, 4)}
                        explanation += f"- midpoint: {round(midpoint, 2)}（曲线中点等级）\n"
                        explanation += f"- steepness: {round(steepness, 4)}（曲线陡峭程度）\n"
                        explanation += f"公式：y = {base_value} / (1 + e^(-{round(steepness, 4)} * (level - {round(midpoint, 2)})))\n"
                    else:
                        params = {"midpoint": round((l1 + l2)/2, 2), "steepness": 0.1}
                        explanation += f"- midpoint: {round((l1 + l2)/2, 2)}（曲线中点等级，默认）\n"
                        explanation += f"- steepness: 0.1（曲线陡峭程度，默认）\n"
                        explanation += f"公式：y = {base_value} / (1 + e^(-0.1 * (level - {round((l1 + l2)/2, 2)})))\n"
                        explanation += f"注意：无法精确拟合，使用默认参数"
                
                elif curve_type == "hybrid":
                    # 混合：前期快速，后期平缓
                    # y = base_value * level * early_coef (level < transition_level)
                    # y = early_value + (base_value * additional_levels * late_coef) (level >= transition_level)
                    base_value = 10
                    transition_level = l1 + (l2 - l1) * 0.3  # 过渡点设为总区间的30%
                    transition_level = round(transition_level)
                    
                    # 前期：从l1到transition_level
                    early_coef = (v1 * 0.8) / (base_value * l1)  # 前期系数
                    # 后期：从transition_level到l2
                    early_value = base_value * transition_level * early_coef
                    additional_levels = l2 - transition_level
                    if additional_levels > 0:
                        late_coef = (v2 - early_value) / (base_value * additional_levels)
                    else:
                        late_coef = early_coef * 0.5
                    
                    params = {
                        "early_coef": round(early_coef, 4),
                        "late_coef": round(late_coef, 4),
                        "transition_level": transition_level
                    }
                    explanation += f"- early_coef: {round(early_coef, 4)}（前期成长系数）\n"
                    explanation += f"- late_coef: {round(late_coef, 4)}（后期成长系数）\n"
                    explanation += f"- transition_level: {transition_level}（过渡等级）\n"
                    explanation += f"公式：\n"
                    explanation += f"- 当 level < {transition_level}: y = {base_value} * level * {round(early_coef, 4)}\n"
                    explanation += f"- 当 level >= {transition_level}: y = {round(early_value, 2)} + ({base_value} * (level - {transition_level}) * {round(late_coef, 4)})"
                
                # 转换为JSON字符串
                import json
                params_str = json.dumps(params, ensure_ascii=False, indent=2)
                
                return params_str, explanation
            
            except Exception as e:
                return f"{{}} (计算错误：{str(e)})", f"### 参数说明\n计算错误：{str(e)}"
        
        # 绑定计算按钮
        calculate_btn.click(
            fn=calculate_curve_params,
            inputs=[curve_type, level1, value1, level2, value2],
            outputs=[result_params, result_explanation]
        )
    
    # 战斗模拟模块
    with gr.Tab("战斗模拟"):
        gr.Markdown("## 战斗模拟")
        gr.Markdown("模拟两个角色之间的战斗，支持单次战斗统计和死斗模拟")
        
        # 获取所有角色的函数
        def get_all_character_options():
            from data.sqlite_handler import load_all_characters
            characters = load_all_characters()
            return [(char.name, str(char.id)) for char in characters]
        
        # 角色选择
        with gr.Row():
            attacker_selector = gr.Dropdown(
                choices=get_all_character_options(),
                label="攻击方角色",
                value=None
            )
            defender_selector = gr.Dropdown(
                choices=get_all_character_options(),
                label="防御方角色",
                value=None
            )
        
        # 刷新角色列表按钮
        refresh_characters_btn = gr.Button("刷新角色列表")
        
        # 战斗模式选择
        battle_mode = gr.Radio(
            choices=["单次战斗统计", "死斗模拟"],
            label="战斗模式",
            value="单次战斗统计"
        )
        
        # 战斗参数设置
        with gr.Row():
            simulate_count = gr.Number(
                label="模拟次数",
                value=100,
                minimum=1,
                maximum=10000,
                step=1
            )
            max_rounds = gr.Number(
                label="最大回合数",
                value=1000,
                minimum=10,
                maximum=10000,
                step=10
            )
        
        # 执行战斗模拟按钮
        battle_btn = gr.Button("开始战斗模拟")
        
        # 战斗结果展示
        battle_result = gr.Markdown("### 战斗结果")
        
        # 战斗历史记录 - 使用固定列
        battle_history = gr.DataFrame(
            headers=["回合", "攻击方伤害", "攻击方暴击", "防御方伤害", "防御方暴击", "攻击方生命值", "防御方生命值"],
            datatype=["number", "number", "bool", "number", "bool", "number", "number"],
            value=[],
            interactive=False,
            label="战斗历史记录"
        )
        
        # 战斗模拟函数
        def run_battle_simulation(attacker_id, defender_id, mode, count, rounds):
            import json
            from logic.battle import battle_between_characters, fight_to_the_death
            from data.sqlite_handler import load_character
            
            # 确保角色ID有效
            if not attacker_id or not defender_id:
                return "请选择攻击方和防御方角色", []
            
            try:
                attacker = load_character(character_id=int(attacker_id))
                defender = load_character(character_id=int(defender_id))
                
                if not attacker or not defender:
                    return "无法加载选择的角色", []
                
                if mode == "单次战斗统计":
                    # 执行单次战斗统计
                    result = battle_between_characters(
                        db_path="./data/character.db",
                        attacker_id=int(attacker_id),
                        defender_id=int(defender_id),
                        simulate_count=int(count)
                    )
                    
                    if result:
                        # 获取攻击方和防御方的详细属性
                        attacker = result['attacker']
                        defender = result['defender']
                        
                        # 生成战斗结果报告
                        report = f"## 🎮 战斗模拟结果\n\n"
                        
                        # 角色信息卡片
                        report += f"### 📋 角色信息\n"
                        report += f"<div style='display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 10px 0;'>\n"
                        report += f"<div style='background-color: #f0f8ff; padding: 15px; border-radius: 8px; border-left: 4px solid #1e90ff;'>\n"
                        report += f"<strong>⚔️ 攻击方</strong>: {attacker['name']} (等级 {attacker['level']})\n\n"
                        report += f"<strong>基础属性</strong>:\n"
                        report += f"- 攻击力: {attacker.get('attack', 0)}\n"
                        report += f"- 防御力: {attacker.get('defense', 0)}\n"
                        report += f"- 暴击: {attacker.get('crit', 0)}\n"
                        report += f"- 暴抗: {attacker.get('crit_resist', 0)}\n\n"
                        report += f"<strong>高级属性</strong>:\n"
                        report += f"- 命中: {attacker.get('accuracy', 0)}\n"
                        report += f"- 闪避: {attacker.get('evasion', 0)}\n"
                        report += f"- 伤害加成: {attacker.get('damage_boost', 0)}%\n"
                        report += f"- 伤害减免: {attacker.get('damage_reduction', 0)}%\n"
                        report += f"- 敏捷: {attacker.get('agility', 0)}\n"
                        report += f"- 生命回复: {attacker.get('health_regen', 0)}\n"
                        report += f"</div>\n"
                        
                        report += f"<div style='background-color: #fff0f5; padding: 15px; border-radius: 8px; border-left: 4px solid #ff69b4;'>\n"
                        report += f"<strong>🛡️ 防御方</strong>: {defender['name']} (等级 {defender['level']})\n\n"
                        report += f"<strong>基础属性</strong>:\n"
                        report += f"- 攻击力: {defender.get('attack', 0)}\n"
                        report += f"- 防御力: {defender.get('defense', 0)}\n"
                        report += f"- 暴击: {defender.get('crit', 0)}\n"
                        report += f"- 暴抗: {defender.get('crit_resist', 0)}\n\n"
                        report += f"<strong>高级属性</strong>:\n"
                        report += f"- 命中: {defender.get('accuracy', 0)}\n"
                        report += f"- 闪避: {defender.get('evasion', 0)}\n"
                        report += f"- 伤害加成: {defender.get('damage_boost', 0)}%\n"
                        report += f"- 伤害减免: {defender.get('damage_reduction', 0)}%\n"
                        report += f"- 敏捷: {defender.get('agility', 0)}\n"
                        report += f"- 生命回复: {defender.get('health_regen', 0)}\n"
                        report += f"</div>\n"
                        report += f"</div>\n\n"
                        
                        # 模拟结果统计
                        report += f"### 📊 模拟结果统计\n"
                        report += f"<div style='background-color: #f5f5f5; padding: 15px; border-radius: 8px; margin: 10px 0;'>\n"
                        report += f"- **模拟次数**: {result['simulate_count']}\n"
                        report += f"- **平均伤害**: {result['average_damage']:.2f}\n"
                        report += f"- **实际暴击率**: {result['actual_crit_rate']:.2%}\n"
                        report += f"- **预期暴击率**: {result['expected_crit_rate']:.2%}\n"
                        if 'actual_hit_rate' in result:
                            report += f"- **实际命中率**: {result['actual_hit_rate']:.2%}\n"
                        report += f"</div>\n\n"
                        
                        # 属性计算过程说明
                        report += f"### 🔢 属性计算过程\n"
                        report += f"<div style='background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0;'>\n"
                        report += f"<strong>1. 基础伤害计算</strong>:\n"
                        report += f"   公式: 攻击 * (攻击 / (攻击 + 防御 * 0.5))\n"
                        report += f"   示例: {attacker.get('attack', 0)} * ({attacker.get('attack', 0)} / ({attacker.get('attack', 0)} + {defender.get('defense', 0)} * 0.5))\n\n"
                        
                        report += f"<strong>2. 等级差异系数</strong>:\n"
                        report += f"   公式: 1 + min(max(等级差 * 0.05, -0.5), 0.5)\n"
                        level_diff = attacker.get('level', 1) - defender.get('level', 1)
                        report += f"   示例: 1 + min(max({level_diff} * 0.05, -0.5), 0.5) = {1 + min(max(level_diff * 0.05, -0.5), 0.5):.2f}\n\n"
                        
                        report += f"<strong>3. 暴击率计算</strong>:\n"
                        report += f"   公式: max(攻击方暴击 - 受击方暴抗, 0) / 100\n"
                        report += f"   示例: max({attacker.get('crit', 0)} - {defender.get('crit_resist', 0)}, 0) / 100 = {result['expected_crit_rate']:.2%}\n\n"
                        
                        report += f"<strong>4. 命中率计算</strong>:\n"
                        report += f"   公式: max(min((攻击方命中 - 受击方闪避) / 100, 0.95), 0.05)\n"
                        accuracy = attacker.get('accuracy', 0)
                        evasion = defender.get('evasion', 0)
                        hit_rate = max(min((accuracy - evasion) / 100, 0.95), 0.05)
                        report += f"   示例: max(min(({accuracy} - {evasion}) / 100, 0.95), 0.05) = {hit_rate:.2%}\n\n"
                        
                        report += f"<strong>5. 伤害加成与减免</strong>:\n"
                        report += f"   公式: 最终伤害 = 伤害 * (1 + 伤害加成%) * (1 - 伤害减免%)\n"
                        report += f"   示例: 伤害 * (1 + {attacker.get('damage_boost', 0)}%) * (1 - {defender.get('damage_reduction', 0)}%)\n\n"
                        
                        report += f"<strong>6. 最终伤害</strong>:\n"
                        report += f"   公式: max(最终伤害, 1) (确保至少造成1点伤害)\n"
                        report += f"</div>\n\n"
                        
                        # 生成单次战斗统计的表格数据
                        history_data = []
                        # 只显示前100条记录，避免表格过大
                        for i, battle_info in enumerate(result['battle_results'][:100]):
                            # 构建适合固定列的数据
                            row = [
                                i + 1,  # 回合/序号
                                battle_info['damage'],  # 攻击方伤害
                                battle_info['is_crit'],  # 攻击方暴击
                                0,  # 防御方伤害（单次模拟没有防御方反击）
                                False,  # 防御方暴击（单次模拟没有防御方反击）
                                100,  # 攻击方生命值（单次模拟不涉及生命值变化）
                                100 - battle_info['damage']  # 防御方生命值（模拟值）
                            ]
                            history_data.append(row)
                        
                        return report, history_data
                    else:
                        return "战斗模拟失败", []
                
                else:  # 死斗模拟
                    # 执行死斗模拟
                    result = fight_to_the_death(
                        db_path="./data/character.db",
                        attacker_id=int(attacker_id),
                        defender_id=int(defender_id),
                        max_rounds=int(rounds)
                    )
                    
                    if result:
                        # 获取攻击方和防御方的详细信息
                        attacker = result['attacker']
                        defender = result['defender']
                        
                        # 生成战斗结果报告
                        report = f"## ⚔️ 死斗模拟结果\n\n"
                        
                        # 战斗结果概览
                        report += f"### 🏆 战斗结果\n"
                        report += f"<div style='background-color: #{'#d4edda' if result['winner'] == attacker['name'] else '#f8d7da' if result['winner'] == defender['name'] else '#fff3cd'}; padding: 15px; border-radius: 8px; margin: 10px 0; border: 1px solid {'#c3e6cb' if result['winner'] == attacker['name'] else '#f5c6cb' if result['winner'] == defender['name'] else '#ffeeba'};'>\n"
                        report += f"<strong>胜利者</strong>: {result['winner']}\n\n"
                        report += f"<strong>战斗回合数</strong>: {result['rounds']}\n"
                        if result['max_rounds_reached']:
                            report += f"<strong>注意</strong>: 已达到最大回合数限制\n\n"
                        
                        report += f"<strong>攻击方</strong>: {attacker['name']}\n"
                        report += f"   - 初始生命值: {attacker['initial_health']}\n"
                        report += f"   - 最终生命值: {attacker['final_health']}\n"
                        report += f"   - 总伤害: {result['total_attacker_damage']}\n"
                        report += f"   - 暴击率: {result['attacker_actual_crit_rate']:.2%}\n\n"
                        
                        report += f"<strong>防御方</strong>: {defender['name']}\n"
                        report += f"   - 初始生命值: {defender['initial_health']}\n"
                        report += f"   - 最终生命值: {defender['final_health']}\n"
                        report += f"   - 总伤害: {result['total_defender_damage']}\n"
                        report += f"   - 暴击率: {result['defender_actual_crit_rate']:.2%}\n"
                        report += f"</div>\n\n"
                        
                        # 角色属性信息
                        report += f"### 📋 角色属性\n"
                        report += f"<div style='display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 10px 0;'>\n"
                        report += f"<div style='background-color: #f0f8ff; padding: 15px; border-radius: 8px; border-left: 4px solid #1e90ff;'>\n"
                        report += f"<strong>⚔️ {attacker['name']}</strong> (等级 {attacker.get('level', 1)})\n\n"
                        report += f"<strong>基础属性</strong>:\n"
                        report += f"- 攻击力: {attacker.get('attack', 0)}\n"
                        report += f"- 防御力: {attacker.get('defense', 0)}\n"
                        report += f"- 暴击: {attacker.get('crit', 0)}\n"
                        report += f"- 暴抗: {attacker.get('crit_resist', 0)}\n\n"
                        report += f"<strong>高级属性</strong>:\n"
                        report += f"- 命中: {attacker['custom_attributes'].get('accuracy', 0)}\n"
                        report += f"- 闪避: {attacker['custom_attributes'].get('evasion', 0)}\n"
                        report += f"- 伤害加成: {attacker['custom_attributes'].get('damage_boost', 0)}%\n"
                        report += f"- 伤害减免: {attacker['custom_attributes'].get('damage_reduction', 0)}%\n"
                        report += f"- 敏捷: {attacker['custom_attributes'].get('agility', 0)}\n"
                        report += f"- 生命回复: {attacker['custom_attributes'].get('health_regen', 0)}\n"
                        report += f"</div>\n"
                        
                        report += f"<div style='background-color: #fff0f5; padding: 15px; border-radius: 8px; border-left: 4px solid #ff69b4;'>\n"
                        report += f"<strong>🛡️ {defender['name']}</strong> (等级 {defender.get('level', 1)})\n\n"
                        report += f"<strong>基础属性</strong>:\n"
                        report += f"- 攻击力: {defender.get('attack', 0)}\n"
                        report += f"- 防御力: {defender.get('defense', 0)}\n"
                        report += f"- 暴击: {defender.get('crit', 0)}\n"
                        report += f"- 暴抗: {defender.get('crit_resist', 0)}\n\n"
                        report += f"<strong>高级属性</strong>:\n"
                        report += f"- 命中: {defender['custom_attributes'].get('accuracy', 0)}\n"
                        report += f"- 闪避: {defender['custom_attributes'].get('evasion', 0)}\n"
                        report += f"- 伤害加成: {defender['custom_attributes'].get('damage_boost', 0)}%\n"
                        report += f"- 伤害减免: {defender['custom_attributes'].get('damage_reduction', 0)}%\n"
                        report += f"- 敏捷: {defender['custom_attributes'].get('agility', 0)}\n"
                        report += f"- 生命回复: {defender['custom_attributes'].get('health_regen', 0)}\n"
                        report += f"</div>\n"
                        report += f"</div>\n\n"
                        
                        # 战斗统计信息
                        report += f"### 📊 战斗统计\n"
                        report += f"<div style='background-color: #f5f5f5; padding: 15px; border-radius: 8px; margin: 10px 0;'>\n"
                        report += f"<strong>总伤害统计</strong>:\n"
                        report += f"- 攻击方总伤害: {result['total_attacker_damage']}\n"
                        report += f"- 防御方总伤害: {result['total_defender_damage']}\n\n"
                        report += f"<strong>暴击率统计</strong>:\n"
                        report += f"- 攻击方暴击率: {result['attacker_actual_crit_rate']:.2%}\n"
                        report += f"- 防御方暴击率: {result['defender_actual_crit_rate']:.2%}\n\n"
                        
                        if 'attacker_actual_hit_rate' in result:
                            report += f"<strong>命中率统计</strong>:\n"
                            report += f"- 攻击方命中率: {result['attacker_actual_hit_rate']:.2%}\n"
                            report += f"- 防御方命中率: {result['defender_actual_hit_rate']:.2%}\n\n"
                        report += f"</div>\n\n"
                        
                        # 战斗流程说明
                        report += f"### 🔄 战斗流程\n"
                        report += f"<div style='background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0;'>\n"
                        report += f"1. **回合开始**: 双方根据生命回复属性回复生命值\n"
                        report += f"2. **先手判定**: 基于敏捷属性决定攻击顺序\n"
                        report += f"3. **攻击阶段**: 双方依次攻击，包含命中/闪避判定\n"
                        report += f"4. **伤害计算**: 基于攻击力、防御力、等级差异等属性\n"
                        report += f"5. **暴击判定**: 根据暴击率决定是否造成暴击伤害\n"
                        report += f"6. **生命值更新**: 扣除伤害，检查战斗结束条件\n"
                        report += f"</div>\n\n"
                        
                        # 生成战斗历史记录 - 只包含固定列
                        history_data = []
                        for round_info in result['round_history']:
                            # 只构建固定列的数据，避免嵌套对象
                            row = [
                                round_info['round'],
                                round_info['attacker_damage'],
                                round_info['attacker_is_crit'],
                                round_info.get('defender_damage', 0),
                                round_info.get('defender_is_crit', False),
                                round_info['attacker_health_after'],
                                round_info['defender_health_after']
                            ]
                            history_data.append(row)
                        
                        return report, history_data
                    else:
                        return "死斗模拟失败", []
            
            except Exception as e:
                import traceback
                error_msg = f"战斗模拟出错: {str(e)}\n{traceback.format_exc()}"
                return error_msg, []
        
        # 绑定按钮事件
        battle_btn.click(
            fn=run_battle_simulation,
            inputs=[attacker_selector, defender_selector, battle_mode, simulate_count, max_rounds],
            outputs=[battle_result, battle_history]
        )
        
        # 刷新角色列表
        refresh_characters_btn.click(
            fn=lambda: [gr.Dropdown(choices=get_all_character_options()), gr.Dropdown(choices=get_all_character_options())],
            inputs=[],
            outputs=[attacker_selector, defender_selector]
        )
    
    # 页面加载时刷新角色列表
    demo.load(
        fn=get_characters_dataframe,
        inputs=[],
        outputs=characters_df
    )

# 使用标准Gradio启动方法
if __name__ == "__main__":
    # 启动Gradio应用，使用新端口
    demo.launch(
        share=False,
        server_name="localhost",
        server_port=7861
    )
