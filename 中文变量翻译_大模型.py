import json
import re
import os
from loguru import logger as 日志
from 翻译工具 import 通义千问模型
from 翻译工具.deepL翻译 import 翻译多个文本_函数

关联文件_列表 = []
收集_目录列表 = []
收集_文件列表 = []

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
    # 正则表达式匹配使用等号定义的变量 a = b
    # var_pattern = re.compile(r'([0-9a-zA-Z_\u4e00-\u9fa5]+)\s*=\s*')
    var_pattern = re.compile(r'\s*([0-9a-zA-Z_\u4e00-\u9fa5, ]+)\s*=\s*[^\s=]+')
    # 返回有可能是一个变量, 也可能是逗号分割的多个变量组成的字符串

    # 提取所有变量名
    匹配结果_列表 = var_pattern.findall(代码文本)
    匹配到变量_列表 = []
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
                else:  # 有as, 提取后面部分
                    变量列表.append(一个.split("as")[0].strip())
                    变量列表.append(一个.split("as")[-1].strip())

    return 变量列表


def 固定语法匹配(代码文本):
    def_pattern = r"def ([0-9a-zA-Z_\u4e00-\u9fa5]+)\((.*)\)"

    变量列表 = []
    函数匹配结果_列表 = re.findall(def_pattern, 代码文本)
    for 一个 in 函数匹配结果_列表:
        # 每一项应该返回的都是两个元素的元组
        函数名称, 函数参数名称 = 一个
        变量列表.append(函数名称)
        if 函数参数名称:
            函数参数名称_列表 = [i.strip() for i in 函数参数名称.split(",")]
            变量列表.extend(函数参数名称_列表)

    class_pattern = r"class ([0-9a-zA-Z_\u4e00-\u9fa5]+).*\:"
    类名匹配结果_列表 = re.findall(class_pattern, 代码文本)
    变量列表.extend(类名匹配结果_列表)

    for_pattern = r"for\s+([0-9a-zA-Z_\u4e00-\u9fa5]+)\s+in"
    循环匹配结果_列表 = re.findall(for_pattern, 代码文本)
    变量列表.extend(循环匹配结果_列表)

    with_pattern = r"with.*as\s(.+):"
    with匹配结果_列表 = re.findall(with_pattern, 代码文本)
    变量列表.extend(with匹配结果_列表)

    return 变量列表


def 提取中文变量(变量列表):

    # 过滤掉英文变量, 如果是中英文混合的, 只要其中包含中文变量
    中文变量列表 = {变量 for 变量 in 变量列表 if any('\u4e00' <= char <= '\u9fff' for char in 变量)}
    return 中文变量列表


def 遍历目录和文件列表(开始目录='.', 忽略目录=None):
    """
    列出指定路径下的所有目录和文件，忽略指定的目录。

    :param 开始目录: 起始目录，默认为当前目录。
    :param 忽略目录: 要忽略的目录列表。
    """
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

def 关联文件判断():
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
    关联中文文件_列表 = 中文变量列表(关联文件_列表)
    遍历目录和文件列表()  # 收集_目录列表 收集_文件列表
    # 对 关联中文文件_列表 中的进行判断
    for 中文变量 in 关联中文文件_列表:
        if 中文变量 in 收集_目录列表:
            # 进行目录相关处理
            # todo
            pass
        elif 中文变量 in 收集_文件列表:
            # 传到递归函数里面再次进行处理
            # todo
            pass



def 读取已保存变量():
    # 检查文件是否存在
    已保存变量_路径 = "已保存变量.json"
    # 获取当前文件的绝对路径
    current_file_path = os.path.abspath(__file__)
    # 获取当前文件所在的目录
    current_directory = os.path.dirname(current_file_path)
    # 改变工作目录到当前文件所在的目录
    os.chdir(current_directory)
    日志.info("工作目录已改变为: {}", os.getcwd())
    if not os.path.exists(已保存变量_路径):
        with open(已保存变量_路径, 'w', encoding='utf-8') as f:
            json.dump({"测试": "test"}, f, ensure_ascii=False, indent=4)

    with open(已保存变量_路径, 'r', encoding='utf-8') as f:
        已保存变量 = json.load(f)
    return 已保存变量


def 翻转字典_函数(输入字典):
    # 创建一个反转的字典，键是原来的值，值是原来的键的列表
    翻转字典 = {}
    for key, value in 输入字典.items():
        if value in 翻转字典:
            翻转字典[value].append(key)
        else:
            翻转字典[value] = [key]
    return 翻转字典

def 字典重复值检测(输入字典):
    # 找出所有值的列表长度大于1的条目
    重复项 = {}
    for key, value in 输入字典.items():
        if len(value) > 1:
            for i in value:
                重复项[i] = key

    return 重复项

def 查询并合并变量(中文变量列表):
    已保存变量_路径 = "已保存变量.json"
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
        日志.debug("查询到缺失变量: {}", 缺失变量)
        if 缺失变量:
            缺失变量翻译_字典 = 通义千问模型.翻译中文变量(缺失变量)
            新变量_字典.update(缺失变量翻译_字典)
        新变量_字典.update(已保存变量)  # 放在后面的是保留的, 历史变量优先级更高
        合并后变量 = 新变量_字典
    else:
        合并后变量 = 已保存变量
    # 防止出现两个中文变量被翻译成同样的中文, 这里要进行重复数据检查.
    翻转字典 = 翻转字典_函数(合并后变量)
    重复项 = 字典重复值检测(翻转字典)
    if 重复项:
        日志.debug("检测到重复项: {}", 重复项)
        去重字典 = 通义千问模型.处理重复变量(重复项)
        日志.debug("大模型去重后: {}", 去重字典)
        # 去重后的字典应该, 把这些值覆盖原来的key和value
        合并后变量.update(去重字典)
    else:
        日志.debug("未检测到重复项")
    with open(已保存变量_路径, 'w', encoding='utf-8') as f:
        json.dump(合并后变量, f, ensure_ascii=False, indent=4)
    return 合并后变量


if __name__ == '__main__':
    待处理_代码路径 = "/Users/yangxinyi/Library/CloudStorage/OneDrive-个人/100_code/Code_Chinese_to_Enghlish/中文变量翻译.py"
    with open(待处理_代码路径, "r") as 文件:
        代码文本 = 文件.read()
    变量列表 = []
    变量列表1 = 匹配代码定义变量(代码文本)
    变量列表2 = 提取导入变量(代码文本)
    变量列表3 = 固定语法匹配(代码文本)
    变量列表.extend(变量列表1)
    变量列表.extend(变量列表2)
    变量列表.extend(变量列表3)
    变量列表_集合 = set(变量列表)

    中文变量列表 = 提取中文变量(变量列表_集合)
    日志.debug(中文变量列表)
    合并后变量_字典 = 查询并合并变量(中文变量列表)

    # 替换变量名
    for 变量 in 中文变量列表:
        if 变量 in 合并后变量_字典:
            代码文本 = re.sub(r'\b' + re.escape(变量) + r'\b', 合并后变量_字典[变量], 代码文本)

    # 保存修改后英文代码, 保存在同一个路径, 文件名称, 原来的中文文件名称翻译成一个英文的文件名称
    代码所在目录 = os.path.dirname(待处理_代码路径)
    # 提取文件名部分
    文件名 = os.path.basename(待处理_代码路径)
    文件名前缀, 文件名后缀 = 文件名.split(".")
    文件名前缀_翻译 = 通义千问模型.翻译文件名(文件名前缀)

    英文代码_保存路径 = 代码所在目录 + "/" + 文件名前缀_翻译[文件名前缀] + "." + 文件名后缀
    with open(英文代码_保存路径, "w") as f:
        f.write(代码文本)








