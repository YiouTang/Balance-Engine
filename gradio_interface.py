import gradio as gr
import json
import os
import pandas as pd

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
                character.level,
                character.growth_curve_type
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
with gr.Blocks(title="数值系统操作界面") as demo:
    gr.Markdown("# 游戏数值系统管理")
    
    # 初始化数据库按钮
    with gr.Row():
        init_btn = gr.Button("初始化数据库")
        init_output = gr.Textbox(label="初始化结果")
    
    init_btn.click(
        fn=lambda: "数据库已初始化",
        inputs=[],
        outputs=init_output
    )
    
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
                    headers=["ID", "名称", "等级", "成长曲线类型"],
                    datatype=["number", "str", "number", "str"],
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
            
            # 右侧：角色详情和修改合并
            with gr.Column(scale=1):
                gr.Markdown("### 角色详情与修改")
                
                # 角色ID（只读）
                char_id_display = gr.Number(label="角色ID", minimum=1, interactive=False)
                
                # 角色基本信息编辑表单 - 默认布局
                char_name_edit = gr.Textbox(label="角色名称", placeholder="输入角色名称")
                char_level_edit = gr.Number(label="角色等级", value=1, minimum=1)
                char_growth_type_edit = gr.Dropdown(
                    choices=["linear", "exponential", "logarithmic"],
                    label="成长曲线类型",
                    value="linear"
                )
                char_growth_params_edit = gr.Textbox(
                    label="成长曲线参数 (JSON格式)",
                    placeholder='例如: {"base": 10, "factor": 2}',
                    value="{}"
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
                        str(row_data[3]),     # 成长曲线类型
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
        server_port=7873
    )
