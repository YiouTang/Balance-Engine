# SQLite数据库处理模块
import os
import sqlite3
import json
from core.character import Character

# 默认数据库文件路径
DEFAULT_DB_PATH = 'game_data.db'

# 使用线程本地存储来保存数据库连接，确保线程安全
import threading
local_storage = threading.local()


def get_db_connection(db_path=DEFAULT_DB_PATH):
    """
    获取数据库连接，使用线程本地存储确保线程安全
    
    参数:
    db_path: 数据库文件路径
    
    返回:
    sqlite3.Connection: 数据库连接对象
    """
    # 检查当前线程是否已有连接
    if not hasattr(local_storage, 'db_connection'):
        # 确保数据库目录存在
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
        
        # 创建新连接
        local_storage.db_connection = sqlite3.connect(db_path)
        local_storage.db_connection.row_factory = sqlite3.Row
        # 启用外键约束
        local_storage.db_connection.execute('PRAGMA foreign_keys = ON')
    else:
        # 检查连接是否仍然有效
        try:
            local_storage.db_connection.execute('SELECT 1')
        except sqlite3.ProgrammingError:
            # 连接已关闭，创建新连接
            local_storage.db_connection = sqlite3.connect(db_path)
            local_storage.db_connection.row_factory = sqlite3.Row
            local_storage.db_connection.execute('PRAGMA foreign_keys = ON')
    return local_storage.db_connection


def init_database(db_path=DEFAULT_DB_PATH):
    """
    初始化数据库，创建所需的表
    
    参数:
    db_path: 数据库文件路径
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    # 创建属性配置表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS attributes_config (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        display_name TEXT NOT NULL,
        default_value INTEGER NOT NULL,
        min_value INTEGER NOT NULL,
        max_value INTEGER NOT NULL,
        description TEXT,
        attr_type TEXT NOT NULL CHECK(attr_type IN ('base', 'custom')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 创建角色表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS characters (
        id INTEGER PRIMARY KEY,
        name TEXT UNIQUE NOT NULL,
        level INTEGER NOT NULL DEFAULT 1,
        growth_curve_type TEXT NOT NULL DEFAULT 'linear',
        growth_curve_params TEXT NOT NULL DEFAULT '{}',
        attr_growth_curves TEXT NOT NULL DEFAULT '{}',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 创建角色属性表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS character_attributes (
        character_id INTEGER NOT NULL,
        attribute_name TEXT NOT NULL,
        attribute_value REAL NOT NULL,
        FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE,
        PRIMARY KEY (character_id, attribute_name)
    )
    ''')
    
    conn.commit()
    
    # 检查是否需要初始化默认属性配置
    cursor.execute('SELECT COUNT(*) FROM attributes_config')
    if cursor.fetchone()[0] == 0:
        create_default_attribute_config(db_path)
    
    conn.close()
    global _db_connection
    _db_connection = None


def create_default_attribute_config(db_path=DEFAULT_DB_PATH):
    """
    创建默认的属性配置
    
    参数:
    db_path: 数据库文件路径
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    # 基础属性
    basic_attributes = [
        {
            'name': 'attack',
            'display_name': '攻击力',
            'default_value': 10,
            'min_value': 1,
            'max_value': 9999,
            'description': '角色的基本攻击能力，影响造成的伤害',
            'attr_type': 'base'
        },
        {
            'name': 'defense',
            'display_name': '防御力',
            'default_value': 5,
            'min_value': 0,
            'max_value': 9999,
            'description': '角色的基本防御能力，减少受到的伤害',
            'attr_type': 'base'
        },
        {
            'name': 'health',
            'display_name': '生命值',
            'default_value': 100,
            'min_value': 1,
            'max_value': 99999,
            'description': '角色的生命值，降至0时角色死亡',
            'attr_type': 'base'
        },
        {
            'name': 'crit',
            'display_name': '暴击值',
            'default_value': 5,
            'min_value': 0,
            'max_value': 100,
            'description': '增加暴击概率的属性',
            'attr_type': 'base'
        },
        {
            'name': 'crit_resist',
            'display_name': '暴抗值',
            'default_value': 5,
            'min_value': 0,
            'max_value': 100,
            'description': '减少被暴击概率的属性',
            'attr_type': 'base'
        }
    ]
    
    # 自定义属性
    custom_attributes = [
        {
            'name': 'damage_boost',
            'display_name': '伤害加成',
            'default_value': 0,
            'min_value': 0,
            'max_value': 100,
            'description': '增加造成的最终伤害百分比',
            'attr_type': 'custom'
        },
        {
            'name': 'damage_reduction',
            'display_name': '伤害减免',
            'default_value': 0,
            'min_value': 0,
            'max_value': 100,
            'description': '减少受到的最终伤害百分比',
            'attr_type': 'custom'
        },
        {
            'name': 'agility',
            'display_name': '敏捷',
            'default_value': 10,
            'min_value': 0,
            'max_value': 9999,
            'description': '影响攻击顺序和闪避概率',
            'attr_type': 'custom'
        },
        {
            'name': 'accuracy',
            'display_name': '命中',
            'default_value': 95,
            'min_value': 0,
            'max_value': 100,
            'description': '影响攻击命中目标的概率',
            'attr_type': 'custom'
        },
        {
            'name': 'evasion',
            'display_name': '闪避',
            'default_value': 5,
            'min_value': 0,
            'max_value': 100,
            'description': '影响闪避敌人攻击的概率',
            'attr_type': 'custom'
        },
        {
            'name': 'health_regen',
            'display_name': '生命值恢复',
            'default_value': 2,
            'min_value': 0,
            'max_value': 100,
            'description': '每个回合自动恢复的生命值',
            'attr_type': 'custom'
        }
    ]
    
    # 插入所有属性
    all_attributes = basic_attributes + custom_attributes
    cursor.executemany('''
    INSERT INTO attributes_config (name, display_name, default_value, min_value, max_value, description, attr_type)
    VALUES (:name, :display_name, :default_value, :min_value, :max_value, :description, :attr_type)
    ''', all_attributes)
    
    conn.commit()
    print(f"已创建默认属性配置")


def load_attribute_config(db_path=DEFAULT_DB_PATH):
    """
    加载属性配置
    
    参数:
    db_path: 数据库文件路径
    
    返回:
    属性配置字典
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    config = {
        'base_attributes': {},
        'custom_attributes': {}
    }
    
    # 查询所有属性配置
    cursor.execute('SELECT * FROM attributes_config')
    rows = cursor.fetchall()
    
    for row in rows:
        attr_data = {
            'display_name': row['display_name'],
            'default_value': row['default_value'],
            'min_value': row['min_value'],
            'max_value': row['max_value'],
            'description': row['description']
        }
        
        if row['attr_type'] == 'base':
            config['base_attributes'][row['name']] = attr_data
        else:
            config['custom_attributes'][row['name']] = attr_data
    
    return config


def get_attribute_config():
    """
    获取属性配置（带缓存）
    
    返回:
    属性配置字典
    """
    # 每次重新加载配置，确保即时反映数据库的更改
    return load_attribute_config()


def get_all_attribute_names():
    """
    获取所有已配置的属性名称
    
    返回:
    属性名称列表
    """
    config = get_attribute_config()
    return list(config.get('base_attributes', {}).keys()) + list(config.get('custom_attributes', {}).keys())


def get_attribute_info(attribute_name):
    """
    获取指定属性的配置信息
    
    参数:
    attribute_name: 属性名称
    
    返回:
    属性配置信息字典或None
    """
    config = get_attribute_config()
    
    # 先在基础属性中查找
    if attribute_name in config.get('base_attributes', {}):
        return config['base_attributes'][attribute_name]
    
    # 再在自定义属性中查找
    if attribute_name in config.get('custom_attributes', {}):
        return config['custom_attributes'][attribute_name]
    
    return None


def get_next_available_id(db_path=DEFAULT_DB_PATH):
    """
    获取下一个可用的角色ID
    
    参数:
    db_path: 数据库文件路径
    
    返回:
    下一个可用的角色ID
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    cursor.execute('SELECT MAX(id) FROM characters')
    max_id = cursor.fetchone()[0]
    
    return (max_id or 0) + 1


def load_character(character_id=None, character_name=None, db_path=DEFAULT_DB_PATH):
    """
    从数据库加载角色
    
    参数:
    character_id: 角色ID（可选）
    character_name: 角色名称（可选）
    db_path: 数据库文件路径
    
    返回:
    Character对象，如果未找到则返回None
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    query = 'SELECT * FROM characters WHERE '
    params = []
    
    if character_id is not None:
        query += 'id = ?'
        params.append(character_id)
    elif character_name is not None:
        query += 'name = ?'
        params.append(character_name)
    else:
        return None
    
    cursor.execute(query, params)
    row = cursor.fetchone()
    
    if not row:
        print(f"未找到角色：ID={character_id}, 名称={character_name}")
        return None
    
    # 查询角色属性
    cursor.execute('SELECT attribute_name, attribute_value FROM character_attributes WHERE character_id = ?', (row['id'],))
    attributes_rows = cursor.fetchall()
    
    attributes = {}
    for attr_row in attributes_rows:
        attributes[attr_row['attribute_name']] = attr_row['attribute_value']
    
    # 解析JSON字段
    growth_curve_params = json.loads(row['growth_curve_params'])
    attr_growth_curves = json.loads(row['attr_growth_curves'])
    
    # 创建角色对象
    return Character(
        character_id=row['id'],
        name=row['name'],
        level=row['level'],
        growth_curve_type=row['growth_curve_type'],
        growth_curve_params=growth_curve_params,
        attr_growth_curves=attr_growth_curves,
        **attributes
    )


def save_character(character, db_path=DEFAULT_DB_PATH):
    """
    保存角色到数据库
    
    参数:
    character: Character对象
    db_path: 数据库文件路径
    
    返回:
    成功返回True，失败返回False
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    try:
        # 检查角色名称是否已存在（排除当前角色）
        cursor.execute('SELECT id FROM characters WHERE name = ? AND id != ?', (character.name, character.id))
        if cursor.fetchone():
            print(f"错误: 角色名称 '{character.name}' 已存在")
            return False
        
        # 准备角色数据
        character_data = {
            'id': character.id,
            'name': character.name,
            'level': character.level,
            'growth_curve_type': character.growth_curve_type,
            'growth_curve_params': json.dumps(character.growth_curve_params),
            'attr_growth_curves': json.dumps(character.attr_growth_curves)
        }
        
        # 插入或更新角色
        cursor.execute('''
        INSERT OR REPLACE INTO characters (id, name, level, growth_curve_type, growth_curve_params, attr_growth_curves)
        VALUES (:id, :name, :level, :growth_curve_type, :growth_curve_params, :attr_growth_curves)
        ''', character_data)
        
        # 删除旧属性
        cursor.execute('DELETE FROM character_attributes WHERE character_id = ?', (character.id,))
        
        # 插入新属性
        attributes = character.get_all_attributes()
        if attributes:
            attr_values = [(character.id, attr_name, attr_value) for attr_name, attr_value in attributes.items()]
            cursor.executemany('''
            INSERT INTO character_attributes (character_id, attribute_name, attribute_value)
            VALUES (?, ?, ?)
            ''', attr_values)
        
        conn.commit()
        print(f"成功保存角色: {character.name} (ID: {character.id})")
        return True
        
    except Exception as e:
        print(f"保存角色时出错: {e}")
        conn.rollback()
        return False


def load_all_characters(db_path=DEFAULT_DB_PATH):
    """
    加载数据库中的所有角色
    
    参数:
    db_path: 数据库文件路径
    
    返回:
    Character对象列表
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    characters = []
    
    try:
        # 查询所有角色
        cursor.execute('SELECT * FROM characters ORDER BY id')
        character_rows = cursor.fetchall()
        
        for row in character_rows:
            # 查询角色属性
            cursor.execute('SELECT attribute_name, attribute_value FROM character_attributes WHERE character_id = ?', (row['id'],))
            attributes_rows = cursor.fetchall()
            
            attributes = {}
            for attr_row in attributes_rows:
                attributes[attr_row['attribute_name']] = attr_row['attribute_value']
            
            # 解析JSON字段
            growth_curve_params = json.loads(row['growth_curve_params'])
            attr_growth_curves = json.loads(row['attr_growth_curves'])
            
            # 创建角色对象
            character = Character(
                character_id=row['id'],
                name=row['name'],
                level=row['level'],
                growth_curve_type=row['growth_curve_type'],
                growth_curve_params=growth_curve_params,
                attr_growth_curves=attr_growth_curves,
                **attributes
            )
            characters.append(character)
        
    except Exception as e:
        print(f"加载所有角色时出错: {e}")
    
    conn.close()
    return characters


def delete_character(character_id, db_path=DEFAULT_DB_PATH):
    """
    从数据库删除角色
    
    参数:
    character_id: 角色ID
    db_path: 数据库文件路径
    
    返回:
    成功返回True，失败返回False
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    try:
        # 删除角色（由于外键约束，角色属性会自动删除）
        cursor.execute('DELETE FROM characters WHERE id = ?', (character_id,))
        
        if cursor.rowcount > 0:
            conn.commit()
            print(f"成功删除角色: ID={character_id}")
            return True
        else:
            print(f"未找到角色: ID={character_id}")
            return False
    except Exception as e:
        print(f"删除角色时出错: {e}")
        conn.rollback()
        return False


def init_db():
    """
    初始化数据库（对外接口）
    """
    init_database()
