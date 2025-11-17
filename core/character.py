# 角色核心类定义
class Character:
    """
    角色基础类，定义角色的基本属性和方法
    支持动态属性管理，无需修改代码即可添加新属性
    """
    # 基础属性列表（为了向后兼容保留）
    BASE_ATTRIBUTES = ['attack', 'defense', 'health', 'crit', 'crit_resist']
    
    def __init__(self, character_id, name, level=1, growth_curve_type="linear", 
                 growth_curve_params=None, attr_growth_curves=None, **kwargs):
        self.id = character_id
        self.name = name
        self.level = level
        # 全局成长曲线类型（作为默认值）
        self.growth_curve_type = growth_curve_type
        # 全局成长曲线参数（作为默认值）
        self.growth_curve_params = growth_curve_params or {}
        # 每个属性的成长曲线设置
        self.attr_growth_curves = attr_growth_curves or {}
        
        # 使用字典存储所有属性，支持动态添加
        self.attributes = {}
        
        # 尝试加载属性配置中的默认值
        try:
            from data.xml_handler import get_attribute_config
            config = get_attribute_config()
            
            # 设置基础属性的默认值
            for attr_name, attr_info in config.get('base_attributes', {}).items():
                self.attributes[attr_name] = attr_info.get('default_value', 0)
            
            # 设置自定义属性的默认值
            for attr_name, attr_info in config.get('custom_attributes', {}).items():
                self.attributes[attr_name] = attr_info.get('default_value', 0)
        except Exception:
            # 如果无法加载配置，使用硬编码的默认值
            for attr in self.BASE_ATTRIBUTES:
                self.attributes[attr] = 0 if attr != 'health' else 100
        
        # 覆盖用户提供的属性值
        for attr_name, attr_value in kwargs.items():
            if attr_name not in ['character_id', 'name', 'level', 'growth_curve_type', 
                                'growth_curve_params', 'attr_growth_curves']:
                self.attributes[attr_name] = attr_value
    
    # 使用属性访问器简化属性访问
    def __getattr__(self, name):
        # 直接访问__dict__来检查attributes是否存在，避免递归
        if 'attributes' in self.__dict__ and name in self.__dict__['attributes']:
            return self.__dict__['attributes'][name]
        # 如果属性不存在，抛出AttributeError
        raise AttributeError(f"'Character' object has no attribute '{name}'")
    
    # 使用属性设置器简化属性设置
    def __setattr__(self, name, value):
        # 处理常规属性
        if name in ['id', 'name', 'level', 'growth_curve_type', 'growth_curve_params', 
                   'attr_growth_curves', 'attributes']:
            super().__setattr__(name, value)
        # 处理动态属性
        else:
            if hasattr(self, 'attributes'):
                self.attributes[name] = value
            else:
                # 初始化前的处理
                super().__setattr__(name, value)
    
    def to_dict(self):
        """将角色对象转换为字典"""
        result = {
            'id': self.id,
            'name': self.name,
            'level': self.level,
            'growth_curve_type': self.growth_curve_type,
            'growth_curve_params': self.growth_curve_params,
            'attr_growth_curves': self.attr_growth_curves
        }
        # 添加所有属性
        result.update(self.attributes)
        return result
    
    def get_attribute_curve_info(self, attribute):
        """
        获取特定属性的成长曲线信息
        
        参数:
        attribute: 属性名称
        
        返回:
        包含曲线类型和参数的元组 (curve_type, curve_params)
        """
        if attribute in self.attr_growth_curves:
            attr_info = self.attr_growth_curves[attribute]
            return attr_info.get('curve_type', self.growth_curve_type), \
                   attr_info.get('curve_params', self.growth_curve_params.get(attribute, {}))
        return self.growth_curve_type, self.growth_curve_params.get(attribute, {})
    
    def add_attribute(self, name, value, curve_type=None, curve_params=None):
        """
        动态添加新属性
        
        参数:
        name: 属性名称
        value: 属性值
        curve_type: 可选，该属性的成长曲线类型
        curve_params: 可选，该属性的成长曲线参数
        """
        self.attributes[name] = value
        # 如果提供了成长曲线信息，保存它
        if curve_type is not None:
            if name not in self.attr_growth_curves:
                self.attr_growth_curves[name] = {}
            self.attr_growth_curves[name]['curve_type'] = curve_type
            if curve_params is not None:
                self.attr_growth_curves[name]['curve_params'] = curve_params
    
    def get_all_attributes(self):
        """
        获取所有属性的字典
        
        返回:
        包含所有属性的字典
        """
        return self.attributes.copy()
    
    def __str__(self):
        return f"角色: {self.name} (ID: {self.id}, 等级: {self.level})"