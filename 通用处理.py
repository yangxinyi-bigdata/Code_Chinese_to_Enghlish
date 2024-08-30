import re
from pathlib import Path


def 判断子目录(父目录, 子目录):
    # 转换为 Path 对象
    父目录_路径 = Path(父目录).resolve()
    子目录_路径 = Path(子目录).resolve()

    # 使用 .parents 检查 parent_path 是否是 child_path 的父目录
    return 父目录_路径 in 子目录_路径.parents


def 提取中文变量(代码文本, 引号=0):
    """引号:
    1: 开启引号中的中文匹配
    0: 去掉引号中的中文提取"""
    # 匹配注释部分
    注释匹配模式 = r'(#.*?)\n'
    字符串匹配模式 = r'(\"\"\".*?\"\"\"|\'\'\'.*?\'\'\'|\".*?\"|\'.*?\')'
    # 修改为跨行匹配模式
    多行字符串匹配模式 = r'(\"\"\".*?\"\"\"|\'\'\'.*?\'\'\')'
    变量匹配模式 = r'\b(\w*[\u4e00-\u9fff]+\w*)\b'
    # 合并所有模式
    if 引号 == 0:
        综合匹配模式 = 注释匹配模式 + r'|' + 多行字符串匹配模式 + r'|' + 字符串匹配模式 + r'|' + 变量匹配模式
        匹配结果列表 = re.findall(综合匹配模式, 代码文本, flags=re.DOTALL)
        # 暂时不要注释和字符串, 提取中文变量
        中文变量_集合 = {i[3] for i in 匹配结果列表 if i[3]}
    elif 引号 == 1:
        综合匹配模式 = 注释匹配模式 + r'|' + 多行字符串匹配模式 + r'|' + 变量匹配模式
        匹配结果列表 = re.findall(综合匹配模式, 代码文本, flags=re.DOTALL)
        # 暂时不要注释和字符串, 提取中文变量
        中文变量_集合 = {i[2] for i in 匹配结果列表 if i[2]}

    return 中文变量_集合


def 过滤中文变量(变量列表):
    # 过滤掉英文变量, 如果是中英文混合的, 只要其中包含中文变量
    中文变量列表 = {变量 for 变量 in 变量列表 if any('\u4e00' <= char <= '\u9fff' for char in 变量)}
    return 中文变量列表


def 判断中文变量(变量):
    if any('\u4e00' <= char <= '\u9fff' for char in 变量):
        return True


def 删除代码注释和字符串(代码文本, 引号=0):
    """引号:
    1: 开启引号中的中文匹配
    0: 去掉引号中的中文提取"""

    # 匹配注释部分，保留换行符
    注释匹配模式 = r'(#.*?)(\n)'

    # 字符串匹配模式，包括多行和单行字符串
    字符串匹配模式 = r'(\"\"\".*?\"\"\"|\'\'\'.*?\'\'\'|\".*?\"|\'.*?\')'

    # 修改为跨行匹配模式的多行字符串匹配
    多行字符串匹配模式 = r'(\"\"\".*?\"\"\"|\'\'\'.*?\'\'\')'

    # 合并所有模式
    综合匹配模式 = 注释匹配模式 + r'|' + 多行字符串匹配模式 + r'|' + 字符串匹配模式

    # 替换时保留换行符
    替换结果 = re.sub(综合匹配模式, lambda m: '""' + (m.group(2) if m.lastindex == 2 else ''), 代码文本, flags=re.DOTALL)

    return 替换结果


def 匹配代码定义变量(代码文本):
    """用于匹配代码中的 a = 6 赋值的变量"""
    匹配到变量_列表 = []
    for 一行 in 代码文本.split("\n"):
        一行 = 一行.strip()
        # 首先判断不是注释内容, 注释不匹配
        if not 一行.startswith("#"):  # 注释不处理
            # 正则表达式匹配使用等号定义的变量 a = b
            # var_pattern = re.compile(r'([0-9a-zA-Z_\u4e00-\u9fa5]+)\s*=\s*')
            var_pattern = re.compile(r'^\s*([0-9a-zA-Z_\u4e00-\u9fa5, ]+?)\s*=\s*[^\s=]+')
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

    变量列表_key = dict()
    变量_as = []
    关联文件_列表 = []
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
                    变量列表_key[一个.strip()] = []
                    关联文件_列表.append(一个.strip())
                else:  # 有as, 提取后面部分
                    # 这里我假设有这种 import 通义千问大模型 as 通义, 两个都是中文, 完全有可能
                    变量列表_key[一个.split("as")[0].strip()] = []
                    关联文件_列表.append(一个.split("as")[0].strip())
                    变量_as.append(一个.split("as")[-1].strip())

        """from numpy import 测试1
            from numpy import ndarray as 测试1
            from datetime import 测试3, date as 测试4
            from datetime import datetime as 测试5, date as 测试6"""
        if 一行.startswith("from "):
            # 提取from后面的变量
            import_前面变量 = 一行.split("import ")[0].strip("from").strip()
            变量列表_key[import_前面变量] = []
            关联文件_列表.append(import_前面变量)

            # 凡是有from的一定是有import 的, 需要的是import后面的内容, 前边from ... import 去掉
            import_后面文本 = 一行.split("import ")[-1]
            import_后面文本_切分 = import_后面文本.split(",")
            for 一个 in import_后面文本_切分:
                if 一个.find("as") < 0:  # 没有as, 直接保存
                    变量列表_key[import_前面变量].append(一个.strip())

                    关联文件_列表.append(一个.strip())
                else:  # 有as, 提取后面部分
                    变量列表_key[import_前面变量].append(一个.split("as")[0].strip())

                    变量_as.append(一个.split("as")[-1].strip())
                    关联文件_列表.append(一个.split("as")[0].strip())

    return 变量列表_key, 变量_as


def 固定语法匹配(代码文本):
    变量列表 = []
    # def 传入大模型返回JSON(messages: List[Dict[str, str]]) -> Dict[str, str]:
    def_pattern = r"def ([0-9a-zA-Z_\u4e00-\u9fa5]+?)\((.*?)\).*:"
    class_pattern = r"class ([0-9a-zA-Z_\u4e00-\u9fa5]+?)\(.*\):"
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


def 是否符合类名规则(变量: str) -> bool:
    # 正则表达式解释：
    # ^[A-Z]：字符串必须以大写字母开始
    # [a-zA-Z]*：之后跟着任意多个大小写字母
    # $：字符串必须在此结束
    匹配模式 = r'^[A-Z][a-z]*([A-Z][a-z]*)*$'
    return bool(re.match(匹配模式, 变量))


def 是否符合常量命名规则(名称: str) -> bool:
    # 检查字符串是否为空
    if not 名称:
        return False

    # 检查字符串是否全为大写字母和下划线
    if not 名称.isupper():
        return False

    # 检查字符串是否是有效的Python标识符
    if not 名称.isidentifier():
        return False

    return True


def 变量名称处理(变量字典):
    """对翻译结果进行处理, 如果有大写字母开头的, 则添加 _类, 如果全部是大写构成, 则添加 _常量"""
    for 英文变量 in 变量字典:
        if 是否符合常量命名规则(英文变量):
            变量字典[英文变量] = 变量字典[英文变量] + "_常量"
        elif 是否符合类名规则(英文变量):
            变量字典[英文变量] = 变量字典[英文变量] + "_类"

    return 变量字典
