import json
import re
import os, shutil
import pandas as pd
from loguru import logger as 日志
from 翻译工具 import 通义千问模型
from 内置变量 import *
from 代码工具 import *
from 通用处理 import *

关联文件_列表 = []
已保存变量_路径 = "已保存变量.json"

# 原始代码
代码文本 = '''
import 张三
import 张三, 李四
import pandas as 数据处理
import re as 正则表达式, os as 文件管理包
from numpy import array
from numpy import ndarray as 数组
from datetime import datetime as 时间, date as 日期

import re
import re, os
import pandas as 数据处理
import re as 正则表达式, os as 文件管理包
from numpy import 数组
from numpy import ndarray as 数组
from datetime import datetime as 时间, date as 日期

# 获取当前代码文件的绝对路径
当前_文件_路径 = os.path.abspath(__file__)
# 获取该路径的目录部分
当前_文件 = os.path.dirname(当前_文件_路径)

# 将工作目录切换到代码所在目录
os.chdir(当前_文件)

# 打印当前工作目录（确认更改）
print("当前工作目录：", os.getcwd())
# 思路, 设置几个类呢?
# 第一个 小说处理类
# 第二个 邮件发送类

class 小说处理器_类:
    def __init__(self, 小说名称, 输入文件_路径, 输出文件_路径):
        self.小说内容 = None
        self.章节正则匹配模式 = None
        self.小说名称 = 小说名称
        if not os.path.exists(输出文件_路径):
            os.mkdir(输出文件_路径)
        self.输入文件_路径 = 输入文件_路径
        self.输出文件_路径 = 输出文件_路径
        正则表达式.

    def 读取小说内容(self):
        # 第一次的时候执行, 后面不执行
        self.章节正则匹配模式 = r'(第\s*(\d+|[零一二两三四五六七八九十百千万]+)\s*章\s*.*)'
        with open(self.输入文件_路径, "r", encoding="utf8") as 文件:
            # 按行模式读取整本小说内容
            self.小说内容_按行切分 = 文件.readlines()
'''


def 匹配代码定义变量(代码文本):
    匹配到变量_列表 = []
    for 一行 in 代码文本.split("\n"):
        一行 = 一行.strip()
        # 首先判断不是注释内容, 注释不匹配
        if not 一行.startswith("#"):  # 注释不处理
            # 正则表达式匹配使用等号定义的变量 a = b
            # var_pattern = re.compile(r'([0-9a-zA-Z_\u4e00-\u9fa5]+)\s*=\s*')
            var_pattern = re.compile(r'\s*([0-9a-zA-Z_\u4e00-\u9fa5, ]+?)\s*=\s*[^\s=]+')
            # 返回有可能是一个变量, 也可能是逗号分割的多个变量组成的字符串
            # 提取所有变量名
            匹配结果_列表 = var_pattern.findall(一行)

            # 对变量列表进行循环, 如果包含逗号, 说明需要进一步处理
            # ['c, d_d ']
            for 元素 in 匹配结果_列表:
                if "," in 元素:  # ['c, d_d ']
                    for 变量 in 元素.split(","):
                        匹配到变量_列表.append(变量.strip())
                else:
                    匹配到变量_列表.append(元素.strip())

    return 匹配到变量_列表


def 提取导入变量(代码文本):
    """提取所有import 变量和 from xxx import xxx"""

    变量列表 = []
    for 一行 in 代码文本.split("\n"):
        # 判断这行是不是以import 开头的
        if 一行.startswith("import "):
            # 如果是以import 开头的, 分成四种情况,
            """import 张三
                import 宋六, 李四
                import 王五, sunqi as 孙七
                import pandas as 数据处理
                import re as 正则表达式, os as 文件管理包"""
            # 凡是有from的一定是有import 的, 需要的是import后面的内容, 前边from ... import 去掉
            import_后面文本 = 一行.split("import ")[-1]
            import_后面文本_切分 = import_后面文本.split(",")
            for 一个 in import_后面文本_切分:
                if 一个.find("as") < 0:  # 没有as, 这个需要单独添加到一个队列当中去, 后续判断是否中文
                    变量列表.append(一个.strip())
                    关联文件_列表.append(一个.strip())
                else:  # 有as, 提取后面部分
                    # 这里我假设有这种 import 通义千问大模型 as 通义, 两个都是中文, 完全有可能
                    变量列表.append(一个.split("as")[0].strip())
                    变量列表.append(一个.split("as")[-1].strip())
                    关联文件_列表.append(一个.split("as")[0].strip())

        """from numpy import 测试1
            from numpy import ndarray as 测试1
            from datetime import 测试3, date as 测试4
            from datetime import datetime as 测试5, date as 测试6"""
        if 一行.startswith("from "):
            # 提取from后面的变量
            import_前面变量 = 一行.split("import ")[0].strip("from").strip()
            变量列表.append(import_前面变量)
            关联文件_列表.append(import_前面变量)

            # 凡是有from的一定是有import 的, 需要的是import后面的内容, 前边from ... import 去掉
            import_后面文本 = 一行.split("import ")[-1]
            import_后面文本_切分 = import_后面文本.split(",")
            for 一个 in import_后面文本_切分:
                if 一个.find("as") < 0:  # 没有as, 直接保存
                    变量列表.append(一个.strip())
                    关联文件_列表.append(一个.strip())
                else:  # 有as, 提取后面部分
                    变量列表.append(一个.split("as")[0].strip())
                    变量列表.append(一个.split("as")[-1].strip())
                    关联文件_列表.append(一个.split("as")[0].strip())

    return 变量列表


def 固定语法匹配(代码文本):
    变量列表 = []
    # def 传入大模型返回JSON(messages: List[Dict[str, str]]) -> Dict[str, str]:
    def_pattern = r"def ([0-9a-zA-Z_\u4e00-\u9fa5]+?)\((.*?)\).*:"
    class_pattern = r"class ([0-9a-zA-Z_\u4e00-\u9fa5]+?).*\:"
    # for_pattern = r"for\s+([0-9a-zA-Z_\u4e00-\u9fa5]+)\s+in"
    for_pattern = r"for\s+([0-9a-zA-Z_\u4e00-\u9fa5\s,]+?)\s+in"
    with_pattern = r"with.*?as\s(.+?):"
    for 一行 in 代码文本.split("\n"):
        一行 = 一行.strip()
        # 去掉注释内容
        if not 一行.startswith("#"):
            搜索结果 = re.match(def_pattern, 一行)
            if 搜索结果:
                函数名称 = 搜索结果.group(1)
                函数参数名称 = 搜索结果.group(2)
                变量列表.append(函数名称)
                # def f():
                # def 函数(a):  def 函数(a, b):  def 函数(a, b=1):  def 函数(a="ok", b=1):
                # def 函数(a: str, b=1):
                # def 函数(a="ok", b=1):   def 函数(a : str="ok", b=1):  def 函数(a : str="ok", b :int=1):
                # 规律: 不管怎么样, 多个参数之间一定是用逗号分隔的. 一个参数中有可能有 = , 可能有: , 只要等号和冒号前边的内容
                if 函数参数名称:
                    for 一个 in 函数参数名称.split(","):
                        提取变量 = 一个.split("=")[0].split(":")[0].strip()
                        变量列表.append(提取变量)
                continue

            搜索结果 = re.match(class_pattern, 一行)
            if 搜索结果:
                类名称 = 搜索结果.group(1)
                变量列表.append(类名称)
                continue

            搜索结果 = re.match(with_pattern, 一行)
            if 搜索结果:
                with匹配结果 = 搜索结果.group(1)
                变量列表.append(with匹配结果)
                continue

            # for 目录路径, 目录列表, 文件列表 in os.walk(start_directory):
            # 这种没匹配上
            搜索结果 = re.search(for_pattern, 一行)
            if 搜索结果:
                for匹配结果 = 搜索结果.group(1)
                # for后面可能有1个临时变量, 或者多个临时变量 for 目录路径, 目录列表, 文件列表 in os.walk(start_directory):
                if for匹配结果.find(","):
                    提取变量 = [i.strip() for i in for匹配结果.split(",")]
                    变量列表.extend(提取变量)
                else:
                    变量列表.append(for匹配结果)

    return 变量列表





def 遍历目录和文件列表(开始目录='.', 忽略目录=None):
    """
    列出指定路径下的所有目录和文件，忽略指定的目录。

    :param 开始目录: 起始目录，默认为当前目录。
    :param 忽略目录: 要忽略的目录列表。
    """
    收集_目录列表 = []
    收集_文件列表 = []
    if 忽略目录 is None:
        忽略目录 = ['__pycache__', '.git', '.idea']
    # 遍历目录
    for 目录路径, 目录列表, 文件列表 in os.walk(开始目录):
        # 修改 目录列表，移除忽略的目录，影响 os.walk 的遍历行为
        目录列表[:] = [d for d in 目录列表 if d not in 忽略目录]

        收集_目录列表.append(目录路径)

        # 输出当前目录下的所有文件
        for 文件 in 文件列表:
            收集_文件列表.append(os.path.join(目录路径, 文件))
    return 收集_目录列表, 收集_文件列表


def 关联文件判断(项目绝对路径):
    """函数功能:
    公共列表, 关联文件_列表 中保存着import的其他文件,

    from 示例代码 import 案例1
    from 通义千问大模型 import 翻译中文变量
    import 示例代码.nover_send
    import 示例代码
    import 通义千问大模型

    分别会获取变量 示例代码, 案例1, 通义千问大模型, 翻译中文变量
    然后我需要判断这几个变量, 到底代表一个包, 还是一个py文件.

    可以把整个项目, 遍历所有文件名, 这样就知道了, 是否在当前项目当中.如果在肯定优先当前项目文件.
    1. 判断改文件名中是否包含中国字
    2. 如果包含中国字, 再判断该文件是否在当前项目当中, 如果在当前项目当中, 再判断是目录还是py文件.
    如果是目录, 则批量替换"""
    关联中文文件_列表 = 过滤中文变量(关联文件_列表)
    日志.debug("关联中文文件_列表: {}", 关联中文文件_列表)
    收集_目录列表, 收集_文件列表 = 遍历目录和文件列表(项目绝对路径)  # 收集_目录列表 收集_文件列表
    # 对 关联中文文件_列表 中的进行判断
    日志.debug("收集_目录列表: {}", 收集_目录列表)
    日志.debug("收集_文件列表: {}", 收集_文件列表)
    目录名称映射字典 = {}
    for 完整目录 in 收集_目录列表:
        目录名称 = 完整目录.split("/")[-1]
        目录名称映射字典[目录名称] = 完整目录

    文件名称映射字典 = {}
    for 完整文件 in 收集_文件列表:
        文件名称 = 完整文件.split("/")[-1]
        文件名称映射字典[文件名称] = 完整文件

    for 中文变量 in 关联中文文件_列表:
        # /Users/yangxinyi/Library/CloudStorage/OneDrive-个人/100_code/Code_Chinese_to_Enghlish/示例代码/__init__.py
        # 注意这里面提取出的中文变量, 很可能并没有运行.
        if 中文变量 in 目录名称映射字典.keys():  # 目录
            # 在同一层级, 创建一个文件夹
            目录映射字典 = 通义千问模型.翻译文件名(中文变量)
            翻译英文名称 = 目录映射字典[中文变量]
            完整目录 = 目录名称映射字典[中文变量]
            上层目录 = 完整目录[:-len(中文变量)]
            日志.debug(上层目录 + 翻译英文名称)
            os.mkdir(上层目录 + 翻译英文名称)


        elif 中文变量 in 收集_文件列表:
            # 传到递归函数里面再次进行处理
            # todo
            pass


def 读取已保存变量():
    # 检查文件是否存在

    # # 获取当前文件的绝对路径
    # current_file_path = os.path.abspath(__file__)
    # # 获取当前文件所在的目录
    # current_directory = os.path.dirname(current_file_path)
    # # 改变工作目录到当前文件所在的目录
    # os.chdir(current_directory)
    # 日志.info("工作目录已改变为: {}", os.getcwd())
    if not os.path.exists(已保存变量_路径):
        with open(已保存变量_路径, 'w', encoding='utf-8') as f:
            json.dump({"测试": "test"}, f, ensure_ascii=False, indent=4)

    with open(已保存变量_路径, 'r', encoding='utf-8') as f:
        已保存变量 = json.load(f)
    return 已保存变量


def 保存合并后变量(合并后变量):
    """传入的应该是一个完整的字典, 然后将字典的值保存进来? """
    with open(已保存变量_路径, 'w', encoding='utf-8') as f:
        json.dump(合并后变量, f, ensure_ascii=False, indent=4)


def 翻转字典_变成列表(输入字典):
    """创建一个反转的字典，键是原来的值，值是原来的键的列表
    注意的是, 会将原来的key变成一个列表, 因此格式不是key和value调转的关系
    """
    翻转字典 = {}
    for 键, 值 in 输入字典.items():
        if 值 in 翻转字典:
            翻转字典[值].append(键)
        else:
            翻转字典[值] = [键]
    return 翻转字典


def 字典重复值检测(输入字典):
    # 找出所有值的列表长度大于1的条目
    重复项 = {}
    for 键, 值 in 输入字典.items():
        if len(值) > 1:
            for i in 值:
                重复项[i] = 键

    return 重复项


def 查询并合并变量(中文变量列表):
    # 读取已保存变量, 对其中已经保存的变量进行替换
    # 现在是获取到了一个集合, 我需要获取已保存变量, 这是一个字典, 然后
    已保存变量 = 读取已保存变量()
    # 我想要进行代码文件的替换, 需要一个字典, 不需要过滤, 只要保存的是所有的变量就可以了
    # 有一个集合和一个字典, 现在需要从集合中提取出所有不在字典的key当中的数据
    未保存变量 = [元素 for 元素 in 中文变量列表 if not 已保存变量.get(元素)]
    # 几个函数下来, 应该会获取到一个完整的变量列表, 然后将这个变量列表传入到
    # 考虑未保存变量为空的情况, 不需要连接大模型
    if 未保存变量:
        新变量_字典 = 通义千问模型.翻译中文变量(未保存变量)

        # 发现这里大模型返回的字典有可能存在确实, 部分传入的变量没有翻译回来, 这里添加一个缺失检测功能
        # 如何检测呢? 未保存变量是我要查询的变量, 新变量_字典 查询这个key里面不存在的 未保存变量 元素
        缺失变量 = [元素 for 元素 in 未保存变量 if not 新变量_字典.get(元素)]

        if 缺失变量:
            日志.debug("查询到缺失变量: {}", 缺失变量)
            缺失变量翻译_字典 = 通义千问模型.翻译中文变量(缺失变量)
            新变量_字典.update(缺失变量翻译_字典)
        新变量_字典.update(已保存变量)  # 放在后面的是保留的, 历史变量优先级更高

        # 这里遇到 `传入大模型返回JSON`被大模型变成了 `传入大模型返回_json`, 导致翻译缺失key.
        # 如何处理呢? 再次检测是否存在缺失, 如果存在缺失则换成单独翻译添加进去.

        缺失变量 = [元素 for 元素 in 未保存变量 if not 新变量_字典.get(元素)]
        if 缺失变量:
            日志.debug("第二次查询到缺失变量: {}", 缺失变量)
            缺失变量翻译_字典 = 通义千问模型.翻译文件名(缺失变量)
            新变量_字典.update(缺失变量翻译_字典)

        合并后变量 = 新变量_字典
    else:
        合并后变量 = 已保存变量
    # 防止出现两个中文变量被翻译成同样的中文, 这里要进行重复数据检查.
    翻转字典 = 翻转字典_变成列表(合并后变量)
    重复项 = 字典重复值检测(翻转字典)
    if 重复项:
        日志.debug("检测到重复项: {}", 重复项)
        去重字典 = 通义千问模型.处理重复变量(重复项)
        日志.debug("大模型去重后: {}", 去重字典)
        # 去重后的字典应该, 把这些值覆盖原来的key和value
        合并后变量.update(去重字典)
    else:
        日志.debug("未检测到重复项")
    保存合并后变量(合并后变量)
    return 合并后变量


def 函数_替换代码变量(代码文本, 变量映射, 引号=0):
    """引号:
    1: 开启引号中的中文匹配

    0: 去掉引号中的中文提取
    """
    # 匹配注释部分
    注释匹配模式 = r'(#.*?)\n'
    # 识别所有的字符串部分 (包括单引号和双引号, 以及单行和多行字符串)
    字符串匹配模式 = r'(\"\"\".*?\"\"\"|\'\'\'.*?\'\'\'|\".*?\"|\'.*?\')'
    # 修改为跨行匹配模式
    多行字符串匹配模式 = r'(\"\"\".*?\"\"\"|\'\'\'.*?\'\'\')'

    # 用于替换的回调函数
    def 替换函数(匹配结果):
        匹配文本 = 匹配结果.group(0)
        if 匹配文本.startswith(('"', "'", "#")):
            # 如果是字符串（包括多行字符串），直接返回不做替换
            return 匹配文本
        else:
            # 如果是变量名，根据映射进行替换
            return 变量映射.get(匹配文本, 匹配文本)

    # 构造变量名的正则表达式 (注意这里使用了 \b 进行词边界匹配)
    变量匹配模式 = r'\b(' + '|'.join(re.escape(中文变量) for 中文变量 in 变量映射.keys()) + r')\b'

    if not 引号:
        # 合并字符串匹配模式和变量匹配模式
        综合匹配模式 = 注释匹配模式 + r'|' + 多行字符串匹配模式 + r'|' + 字符串匹配模式 + r'|' + 变量匹配模式
    else:
        综合匹配模式 = 注释匹配模式 + r'|' + 多行字符串匹配模式 + r'|' + 变量匹配模式

    # 使用 sub 函数进行替换，结合字符串的保护
    代码文本 = re.sub(综合匹配模式, 替换函数, 代码文本, flags=re.DOTALL)

    return 代码文本


def ipynb转换成py(notebook):
    py_代码 = ""
    md_文本 = ""
    for cell in notebook['cells']:
        if cell['cell_type'] == 'code':
            code = ''.join(cell['source'])
            py_代码 += code + '\n'

        elif cell['cell_type'] == 'markdown':
            # 将 Markdown 内容转换为注释
            comments = ''.join(cell['source'])
            # 转换每一行为注释形式
            comment_lines = comments.splitlines()
            for line in comment_lines:
                py_代码 += '# ' + line + '\n'
    return py_代码


def 代码文件翻译_V1(代码_绝对路径):
    with open(代码_绝对路径, "r") as 文件:
        代码文本 = 文件.read()
    变量列表 = []
    变量列表1 = 匹配代码定义变量(代码文本)
    变量列表2 = 提取导入变量(代码文本)
    变量列表3 = 固定语法匹配(代码文本)
    变量列表.extend(变量列表1)
    变量列表.extend(变量列表2)
    变量列表.extend(变量列表3)
    变量列表_集合 = set(变量列表)

    中文变量列表 = 过滤中文变量(变量列表_集合)
    日志.debug(中文变量列表)
    合并后变量_字典 = 查询并合并变量(中文变量列表)
    中文变量映射 = {变量: 合并后变量_字典[变量] for 变量 in 中文变量列表}
    # 替换只需要替换 `中文变量列表` 中的就可以了, 需要一个映射关系
    代码文本 = 函数_替换代码变量(代码文本, 中文变量映射)

    # 保存修改后英文代码, 保存在同一个路径, 文件名称, 原来的中文文件名称翻译成一个英文的文件名称
    代码所在目录 = os.path.dirname(代码_绝对路径)
    # 提取文件名部分
    文件名 = os.path.basename(代码_绝对路径)
    文件名前缀, 文件名后缀 = 文件名.split(".")
    # 这里有可能文件名早就在已保存变量里面已经有了, 就不再需要翻译了.
    已保存变量 = 读取已保存变量()
    if 文件名前缀 not in 已保存变量:
        文件名前缀_翻译字典 = 通义千问模型.翻译文件名(文件名前缀)
        文件名前缀_翻译结果 = 文件名前缀_翻译字典[文件名前缀]
        # 将翻译的结果也保存到变量中
        已保存变量.setdefault(文件名前缀, 文件名前缀_翻译字典[文件名前缀])
        保存合并后变量(已保存变量)
    else:
        文件名前缀_翻译结果 = 已保存变量[文件名前缀]

    英文代码_保存路径 = 代码所在目录 + "/" + 文件名前缀_翻译结果 + "." + 文件名后缀
    with open(英文代码_保存路径, "w") as f:
        f.write(代码文本)


def 代码文件翻译_V2(代码_绝对路径):
    """升级成直接匹配中文变量
    可以自动根据传入的是py还是ipynb来分别进行处理"""
    if 代码_绝对路径.endswith(".py"):
        代码类型 = "py"
    elif 代码_绝对路径.endswith(".ipynb"):
        代码类型 = "ipynb"


    if 代码类型 == "py":
        with open(代码_绝对路径, "r") as 文件:
            代码文本 = 文件.read()
    elif 代码类型 == "ipynb":
        with open(代码_绝对路径, 'r', encoding='utf-8') as file:
            notebook = json.load(file)
            代码文本 = ipynb转换成py(notebook)

    中文变量_集合 = 提取中文变量(代码文本)
    # 变量列表1 = 匹配代码定义变量(代码文本)
    # 变量列表2 = 提取导入变量(代码文本)
    # 变量列表3 = 固定语法匹配(代码文本)

    日志.debug(中文变量_集合)
    合并后变量_字典 = 查询并合并变量(中文变量_集合)
    中文变量映射 = {变量: 合并后变量_字典[变量] for 变量 in 中文变量_集合}
    # 替换只需要替换 `中文变量列表` 中的就可以了, 需要一个映射关系
    if 代码类型 == "py":
        代码文本 = 函数_替换代码变量(代码文本, 中文变量映射)
    elif 代码类型 == "ipynb":
        for cell in notebook['cells']:
            if cell['cell_type'] == 'code':
                source = ''.join(cell['source'])
                翻译代码 = 函数_替换代码变量(source, 中文变量映射)
                if isinstance(source, list):
                    cell['source'] = 翻译代码.splitlines(keepends=True)
                elif isinstance(source, str):
                    cell['source'] = 翻译代码

        # 保存修改后英文代码, 保存在同一个路径, 文件名称, 原来的中文文件名称翻译成一个英文的文件名称
    代码所在目录 = os.path.dirname(代码_绝对路径)
    # 提取文件名部分
    文件名 = os.path.basename(代码_绝对路径)
    文件名前缀, 文件名后缀 = 文件名.split(".")
    # 这里有可能文件名早就在已保存变量里面已经有了, 就不再需要翻译了.
    已保存变量 = 读取已保存变量()
    if 文件名前缀 not in 已保存变量:
        文件名前缀_翻译字典 = 通义千问模型.翻译文件名(文件名前缀)
        文件名前缀_翻译结果 = 文件名前缀_翻译字典[文件名前缀]
        # 将翻译的结果也保存到变量中
        已保存变量.setdefault(文件名前缀, 文件名前缀_翻译字典[文件名前缀])
        保存合并后变量(已保存变量)
    else:
        文件名前缀_翻译结果 = 已保存变量[文件名前缀]

    英文代码_保存路径 = 代码所在目录 + "/" + 文件名前缀_翻译结果 + "." + 文件名后缀
    with open(英文代码_保存路径, "w") as f:
        if 代码类型 == "py":
            f.write(代码文本)
        elif 代码类型 == "ipynb":
            json.dump(notebook, f, ensure_ascii=False, indent=4)
    return 英文代码_保存路径


def 代码文件翻译_特殊(代码_绝对路径):
    """__init__文件替换"""
    with open(代码_绝对路径, "r") as 文件:
        代码文本 = 文件.read()
    中文变量_集合 = 提取中文变量(代码文本, 引号=1)

    日志.debug(中文变量_集合)
    合并后变量_字典 = 查询并合并变量(中文变量_集合)
    中文变量映射 = {变量: 合并后变量_字典[变量] for 变量 in 中文变量_集合}
    # 替换只需要替换 `中文变量列表` 中的就可以了, 需要一个映射关系
    代码文本 = 函数_替换代码变量(代码文本, 中文变量映射, 引号=1)

    with open(代码_绝对路径, "w") as f:
        f.write(代码文本)


def 创建英文文件夹(项目_根路径):
    """函数功能:
    当传输一个项目路径, 则对项目中的中文路径, 创建一个对应的英文路径
    对于英文路径不变.
    对于英文路径当中的中文路径, 创建一个对应的英文目录
    对于中文路径中的英文路径, 复制到对应的英文父路径
    对于中文路径中的中文路径, 会在对应的英文父路径中生成对应的英文路径"""
    收集_目录列表, 收集_文件列表 = 遍历目录和文件列表(项目_根路径)
    收集_相对目录列表 = [元素.replace(项目_根路径, "") for 元素 in 收集_目录列表]
    项目_目录表单 = pd.DataFrame(columns=["文件夹名称", "英文变量", "相对路径",
                                          "英文相对路径", "上层路径", "英文上层路径", "修改标识"])
    id = 0

    for 相对路径 in 收集_相对目录列表:
        if 相对路径:  # 排除根路径
            上层路径, 文件夹名称 = 相对路径.rsplit("/", maxsplit=1)
            项目_目录表单.loc[id] = {
                "文件夹名称": 文件夹名称,
                "英文变量": "",
                "相对路径": 相对路径,
                "英文相对路径": 相对路径,
                "上层路径": 上层路径,
                "英文上层路径": 上层路径,
                "修改标识": 0,
                "包含中文": 0
            }

            if 判断中文变量(文件夹名称):  # 过滤带有中文的目录
                项目_目录表单.loc[id, "包含中文"] = 1
            elif 判断中文变量(项目_目录表单.loc[id, "相对路径"]):  # 上层包含中文
                项目_目录表单.loc[id, "包含中文"] = 2  # 包含中文为2
            id += 1

    项目_中文目录表单 = 项目_目录表单[项目_目录表单["包含中文"] == 1]
    项目_父目录中文表单 = 项目_目录表单[项目_目录表单["包含中文"] == 2]
    项目_纯英文目录表单 = 项目_目录表单[项目_目录表单["包含中文"] == 0]

    合并后变量 = 查询并合并变量(项目_中文目录表单["文件夹名称"].to_list())

    for 索引 in 项目_中文目录表单.index:
        项目_中文目录表单.loc[索引, "英文变量"] = 合并后变量[项目_中文目录表单.loc[索引, "文件夹名称"]]

    for 索引 in 项目_中文目录表单.index:
        if not 项目_中文目录表单.loc[索引, "修改标识"]:
            # 直接创建该文件夹, 如果没有修改标识, 代表这个目录的上层都是英文的, 或者是第一层文件夹
            文件夹名称 = 项目_中文目录表单.loc[索引, "文件夹名称"]
            英文上层路径 = 项目_中文目录表单.loc[索引, "英文上层路径"]
            创建目录 = 项目_根路径 + "/" + 英文上层路径 + "/" + 项目_中文目录表单.loc[索引, "英文变量"]
            原目录 = 项目_根路径 + "/" + 英文上层路径 + "/" + 文件夹名称
            项目_中文目录表单.loc[索引, "英文相对路径"] = 项目_中文目录表单.loc[索引, "英文相对路径"].replace(
                文件夹名称,
                合并后变量[文件夹名称])

            复制文件夹_删除已存在(原目录, 创建目录)

            # 这里要对所有该目录的子目录的 "英文相对路径", "英文上层路径" 进行修改
            for 索引_内层 in 项目_中文目录表单.index:
                if 索引 != 索引_内层:  # 如果不是当前处理目录
                    if 项目_中文目录表单.loc[索引_内层, "英文相对路径"].find(
                            项目_中文目录表单.loc[索引, "相对路径"]) > -1:
                        # 上层目录修改过, 标记一下
                        项目_中文目录表单.loc[索引_内层, "修改标识"] = 1
                        项目_中文目录表单.loc[索引_内层, "英文相对路径"] = 项目_中文目录表单.loc[
                            索引_内层, "英文相对路径"].replace(
                            项目_中文目录表单.loc[索引, "相对路径"], 项目_中文目录表单.loc[索引, "英文相对路径"])

                        项目_中文目录表单.loc[索引_内层, "英文上层路径"] = 项目_中文目录表单.loc[
                            索引_内层, "英文上层路径"].replace(
                            项目_中文目录表单.loc[索引, "相对路径"], 项目_中文目录表单.loc[索引, "英文相对路径"])

            # 将原文件夹中的所有内容复制过来
        else:  # 说明不是第一层文件夹
            # 走到这里说明父路径已经被替换过了, 这不是原生文件夹, 可以直接改名
            文件夹名称 = 项目_中文目录表单.loc[索引, "文件夹名称"]
            英文上层路径 = 项目_中文目录表单.loc[索引, "英文上层路径"]
            创建目录 = 项目_根路径 + 英文上层路径 + "/" + 项目_中文目录表单.loc[索引, "英文变量"]
            原目录 = 项目_根路径 + 英文上层路径 + "/" + 文件夹名称

            项目_中文目录表单.loc[索引, "英文相对路径"] = 项目_中文目录表单.loc[索引, "英文相对路径"].replace(
                文件夹名称,
                合并后变量[文件夹名称])

            if not os.path.exists(创建目录):
                os.rename(原目录, 创建目录)
            # 如果这个文件夹翻译成英文了, 那么它的子文件夹也都应该将上级目录英文数据翻译一下
            for 索引_内层 in 项目_中文目录表单.index:
                if 索引 != 索引_内层:  # 如果不是当前处理目录
                    if 项目_中文目录表单.loc[索引_内层, "相对路径"].find(项目_中文目录表单.loc[索引, "相对路径"]) > -1:
                        # 上层目录修改过, 标记一下
                        项目_中文目录表单.loc[索引_内层, "修改标识"] += 1
                        项目_中文目录表单.loc[索引_内层, "英文相对路径"] = 项目_中文目录表单.loc[
                            索引_内层, "英文相对路径"].replace(
                            项目_中文目录表单.loc[索引, "相对路径"], 项目_中文目录表单.loc[索引, "英文相对路径"])
                        项目_中文目录表单.loc[索引_内层, "英文上层路径"] = 项目_中文目录表单.loc[
                            索引_内层, "上层路径"].replace(
                            项目_中文目录表单.loc[索引, "相对路径"], 项目_中文目录表单.loc[索引, "英文相对路径"])
    项目_目录表单.update(项目_中文目录表单)

    # 项目_父目录中文表单.index  # 这个是英文目录, 但是父目录中包含中文, 那么对于这种一定已经有复制体了, 不需要再处理, 但是这里并没有记录

    return 项目_中文目录表单, 项目_目录表单


def 复制文件_覆盖(原目录, 目标目录):
    """将一个文件夹内容复制到另外一个文件夹中, 如果原来文件已经存在, 则覆盖掉同名文件"""
    if not os.path.exists(目标目录):
        os.makedirs(目标目录)

    for 文件 in os.listdir(原目录):
        源路径 = os.path.join(原目录, 文件)
        目标路径 = os.path.join(目标目录, 文件)

        if os.path.isdir(源路径):
            # 递归复制文件夹
            复制文件_覆盖(源路径, 目标路径)
        else:
            # 复制文件并覆盖
            shutil.copy2(源路径, 目标路径)


def 复制文件夹_删除已存在(原目录, 创建目录):
    """复制一个目录内容到新的目录, 如果原来"""
    if not os.path.exists(创建目录):
        shutil.copytree(原目录, 创建目录)
    else:  # 如果原来这个文件夹已经存在了? 那应该是希望重新翻译整个项目, 覆盖原来的翻译结果, 考虑到配置文件也可能会发生变化, 整个重新翻译吧
        shutil.rmtree(创建目录)
        shutil.copytree(原目录, 创建目录)


def 转换中文文件夹_到英文(项目_根路径):
    """函数功能: 将复制后的文件夹当中, 所有的中文文件夹, 重命名成英文.
    遍历所有文件夹,
    过滤中文文件夹
    重命名文件夹变成英文"""

    收集_目录列表, 收集_文件列表 = 遍历目录和文件列表(项目_根路径)
    收集_相对目录列表 = [元素.replace(项目_根路径, "") for 元素 in 收集_目录列表]
    项目_目录表单 = pd.DataFrame(columns=["文件夹名称", "英文变量", "相对路径",
                                          "英文相对路径", "上层路径", "英文上层路径", "修改标识"])
    id = 0

    for 相对路径 in 收集_相对目录列表:
        if 相对路径:  # 排除根路径
            上层路径, 文件夹名称 = 相对路径.rsplit("/", maxsplit=1)
            项目_目录表单.loc[id] = {
                "文件夹名称": 文件夹名称,
                "英文变量": "",
                "相对路径": 相对路径,
                "英文相对路径": 相对路径,
                "上层路径": 上层路径,
                "英文上层路径": 上层路径,
                "修改标识": 0,
                "包含中文": 0
            }

            if 判断中文变量(文件夹名称):  # 过滤带有中文的目录
                项目_目录表单.loc[id, "包含中文"] = 1
            elif 判断中文变量(项目_目录表单.loc[id, "相对路径"]):  # 上层包含中文
                项目_目录表单.loc[id, "包含中文"] = 2  # 包含中文为2
            id += 1

    项目_中文目录表单 = 项目_目录表单[项目_目录表单["包含中文"] == 1]
    项目_父目录中文表单 = 项目_目录表单[项目_目录表单["包含中文"] == 2]
    项目_纯英文目录表单 = 项目_目录表单[项目_目录表单["包含中文"] == 0]

    合并后变量 = 查询并合并变量(项目_中文目录表单["文件夹名称"].to_list())

    for 索引 in 项目_中文目录表单.index:
        项目_中文目录表单.loc[索引, "英文变量"] = 合并后变量[项目_中文目录表单.loc[索引, "文件夹名称"]]

    for 索引 in 项目_中文目录表单.index:
        # 直接创建该文件夹, 如果没有修改标识, 代表这个目录的上层都是英文的, 或者是第一层文件夹
        文件夹名称 = 项目_中文目录表单.loc[索引, "文件夹名称"]
        英文上层路径 = 项目_中文目录表单.loc[索引, "英文上层路径"]
        创建目录 = 项目_根路径 + "/" + 英文上层路径 + "/" + 项目_中文目录表单.loc[索引, "英文变量"]
        原目录 = 项目_根路径 + "/" + 英文上层路径 + "/" + 文件夹名称
        项目_中文目录表单.loc[索引, "英文相对路径"] = 项目_中文目录表单.loc[索引, "英文相对路径"].replace(
            文件夹名称,
            合并后变量[文件夹名称])
        if not os.path.exists(创建目录):
            os.rename(原目录, 创建目录)  # 将中文文件夹重命名成英文文件夹
        else:
            复制文件_覆盖(原目录, 创建目录)
            shutil.rmtree(原目录)

        # 这里要对所有该目录的子目录的 "英文相对路径", "英文上层路径" 进行修改
        for 索引_内层 in 项目_中文目录表单.index:
            if 索引 != 索引_内层:  # 如果不是当前处理目录
                if 判断子目录(项目_中文目录表单.loc[索引, "相对路径"],
                              项目_中文目录表单.loc[索引_内层, "英文相对路径"]):
                    # 上层目录修改过, 标记一下
                    项目_中文目录表单.loc[索引_内层, "修改标识"] = 1  # 没用了
                    项目_中文目录表单.loc[索引_内层, "英文相对路径"] = 项目_中文目录表单.loc[
                        索引_内层, "英文相对路径"].replace(
                        项目_中文目录表单.loc[索引, "相对路径"], 项目_中文目录表单.loc[索引, "英文相对路径"])

                    项目_中文目录表单.loc[索引_内层, "英文上层路径"] = 项目_中文目录表单.loc[
                        索引_内层, "英文上层路径"].replace(
                        项目_中文目录表单.loc[索引, "相对路径"], 项目_中文目录表单.loc[索引, "英文相对路径"])

    项目_目录表单.update(项目_中文目录表单)


def 全项目代码翻译(项目_根路径):
    收集_目录列表, 收集_文件列表 = 遍历目录和文件列表(项目_根路径)
    收集_相对目录列表 = [元素.replace(项目_根路径, "") for 元素 in 收集_目录列表]  # 有了创建文件夹之后的, 目录列表, 如何判断呢?
    收集_相对文件列表 = [元素.replace(项目_根路径, "") for 元素 in 收集_文件列表]

    日志.info(收集_相对目录列表)
    日志.info(收集_相对文件列表)

    # 分析目录之间的中英文映射关系
    中文路径映射关系 = {}
    已保存变量 = 读取已保存变量()
    for 目录 in 收集_相对目录列表:
        目录组成_列表 = 目录.split("/")
        if 过滤中文变量(目录组成_列表):
            翻译英文路径 = "/".join([已保存变量[i] if 判断中文变量(i) else i for i in 目录组成_列表])
            中文路径映射关系[目录] = 翻译英文路径

    项目_文件表单 = pd.DataFrame(columns=["文件名称", "英文变量", "相对路径",
                                          "英文相对路径", "上层路径", "英文上层路径", "修改标识"])

    id = 0

    for 相对路径 in 收集_相对文件列表:
        上层路径, 文件名称 = 相对路径.rsplit("/", maxsplit=1)
        项目_文件表单.loc[id] = {
            "文件名称": 文件名称,
            "英文变量": "",
            "相对路径": 相对路径,
            "英文相对路径": 相对路径,
            "上层路径": 上层路径,
            "英文上层路径": 上层路径,
            "修改标识": 0,
            "包含中文": 0
        }
        if 判断中文变量(文件名称) and (文件名称.find(".py") > -1 or 文件名称.find(".ipynb") > -1):  # 过滤带有中文的目录
            项目_文件表单.loc[id, "包含中文"] = 1
        id += 1

    项目_中文文件表单 = 项目_文件表单.loc[项目_文件表单["包含中文"] == 1]  # 切片视图
    日志.debug(项目_中文文件表单)

    for 索引 in 项目_中文文件表单.index:
        # 索引全部是中文py文件,
        上层路径 = 项目_中文文件表单.loc[索引, "上层路径"]
        if 上层路径 == "":  # 项目根路径中, 直接翻译
            英文代码_保存路径 = 代码文件翻译_V2(项目_根路径 + "/" + 项目_中文文件表单.loc[索引, "相对路径"])  # 翻译成英文
        elif 判断中文变量(上层路径):  # 判断所在路径如果存在中文, 则应该有对应的英文路径, 不用处理
            pass
        else:  # 全部是英文的路径, 看看有没有对应映射
            if 上层路径 in 中文路径映射关系.values():  # 有映射关系, 说明是衍生文件, 应该翻译后删除
                英文代码_保存路径 = 代码文件翻译_V2(
                    项目_根路径 + "/" + 项目_中文文件表单.loc[索引, "相对路径"])  # 翻译成英文
                # 删除对应中文
                os.remove(项目_根路径 + "/" + 项目_中文文件表单.loc[索引, "相对路径"])
            else:  # 原生英文文件夹, 里面的内容应该翻译, 原来的保留.
                英文代码_保存路径 = 代码文件翻译_V2(
                    项目_根路径 + "/" + 项目_中文文件表单.loc[索引, "相对路径"])  # 翻译成英文

    # 应该有很多目录, 我要判断一个目录当中, 中英文的映射关系, 如果是有映射的, 那么就应该对其中的中文进行翻译, 然后删除.
    # 如果是没有映射的, 那么就应该翻译然后保留, 反正只要是在有映射对象的中文, 一定要翻译.

    # 反之, 如果是在中文目录当中, 如果有英文映射目录, 那么不需要翻译.
    # 如果没有英文映射, 那是不可能的说明文件夹出错了.

    # 如果在根目录, 翻译并且保留.

    # 不对啊,
    # '/Users/yangxinyi/Downloads/Test_Translate_Project/example/novel_send/小说_发送_脚本.py',
    # '/Users/yangxinyi/Downloads/Test_Translate_Project/示例代码/novel_send/小说_发送_脚本.py',
    # 现在对于某些代码, 已经有过复制了, 对于有复制记录的, 应该翻译复制之后的,
    # 对于没有复制记录的, 应该翻译原来的, 所以需要判断是否有过翻译记录
    # 1. 提取出 "相对路径" 序列, 如果在这里, 就不处理
    # 2. 提取出 "'英文相对路径'" 序列, 如果在这里, 就替换
    # 3. 如果不在这两个当中, 就是原生的, 创建一个新的英文版本, 原来的保留.

    项目_文件表单.update(项目_中文文件表单)

    for 索引 in 项目_文件表单.index:
        if 项目_文件表单.loc[索引, "文件名称"] == "__init__.py":
            # 判断上层是中文还是英文
            上层文件夹 = 项目_文件表单.loc[索引, "上层路径"].rsplit("/", maxsplit=1)[-1]
            if not 判断中文变量(上层文件夹):  # 上层是英文文件夹, 对这个文件中的内容进行翻译.
                代码文件翻译_特殊(项目_根路径 + "/" + 项目_文件表单.loc[索引, "相对路径"])

    return 项目_文件表单


def 复制项目代码翻译(项目_根路径):
    收集_目录列表, 收集_文件列表 = 遍历目录和文件列表(项目_根路径)
    收集_相对目录列表 = [元素.replace(项目_根路径, "") for 元素 in 收集_目录列表]  # 有了创建文件夹之后的, 目录列表, 如何判断呢?
    收集_相对文件列表 = [元素.replace(项目_根路径, "") for 元素 in 收集_文件列表]

    日志.info(收集_相对目录列表)
    日志.info(收集_相对文件列表)

    # 应该不用这么麻烦, 直接遍历文件, 如果当前文件名称包含中文, 则进行翻译
    for 相对路径 in 收集_相对文件列表:
        上层路径, 文件名称 = 相对路径.rsplit("/", maxsplit=1)
        if 判断中文变量(文件名称) and (文件名称.find(".py") > -1 or 文件名称.find(".ipynb") > -1):  # 过滤带有中文的文件
            # 将文件完整路径传入到函数中翻译就可以了.
            代码文件翻译_V2(项目_根路径 + "/" + 相对路径)
            # 删除中文文件
            os.remove(项目_根路径 + "/" + 相对路径)
        elif 文件名称 == "__init__.py":  # 这里上层文件夹应该已经被翻译成英文了, 所以到底还要不要翻译其中的中文呢? 肯定是要的
            代码文件翻译_特殊(项目_根路径 + "/" + 相对路径)



if __name__ == '__main__':
    # 项目根目录的绝对路径
    # 项目_根路径 = '/Users/yangxinyi/Library/CloudStorage/OneDrive-个人/100_code/Test_Translate_Project'
    项目_根路径 = '/Users/yangxinyi/Library/CloudStorage/OneDrive-个人/100_code/Code_Chinese_to_Enghlish'
    # 项目_根路径 = '/Users/yangxinyi/Downloads/200_临时文件夹/测试文件夹'
    # 项目根目录的绝对路径
    # 待处理_代码路径 = "/Users/yangxinyi/Library/CloudStorage/OneDrive-个人/100_code/Code_Chinese_to_Enghlish/中文变量翻译.py"
    # 代码文件翻译(待处理_代码路径)

    # 关联文件判断(project_root)
    # 项目_中文目录表单, 项目_目录表单 = 创建英文文件夹(项目_根路径)
    # 日志.info(项目_中文目录表单)
    #
    # 项目_文件表单 = 全项目代码翻译(项目_根路径)
    #
    # 日志.info(项目_文件表单)
    # 日志.info(英文相对路径_列表)
    项目_翻译路径 = "/Users/yangxinyi/Downloads/200_临时文件夹/Pycode_Chinese_to_English"
    复制文件夹_删除已存在(项目_根路径, 项目_翻译路径)
    转换中文文件夹_到英文(项目_翻译路径)
    # 接下来就是文件翻译, 直接对所有获取到的文件翻译成英文就可以.
    复制项目代码翻译(项目_翻译路径)








