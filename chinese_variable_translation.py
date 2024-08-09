import json
import re
import os
from loguru import logger as log
from translation_tool import tongyi_qianwen_model

related_files_list = []
collect_directories_list = []
collect_files_list = []

# 原始代码
code_text = '''
import zhang_san
import zhang_san, li_si
import pandas as data_processing
import re as regular_expression, os as file_management_package
from numpy import array
from numpy import ndarray as array
from datetime import datetime as time, date as date

import re
import re, os
import pandas as data_processing
import re as regular_expression, os as file_management_package
from numpy import array
from numpy import ndarray as array
from datetime import datetime as time, date as date

# 获取当前代码文件的绝对路径
current_file_path = os.path.abspath(__file__)
# 获取该路径的目录部分
current_file = os.path.dirname(current_file_path)

# 将工作目录切换到代码所在目录
os.chdir(current_file)

# 打印当前工作目录（确认更改）
print("当前工作目录：", os.getcwd())
# 思路, 设置几个类呢?
# 第一个 小说处理类
# 第二个 邮件发送类

class novel_processor_class:
    def __init__(self, novel_name, input_file_path, output_file_path):
        self.novel_content = None
        self.chapter_regex_pattern = None
        self.novel_name = novel_name
        if not os.path.exists(output_file_path):
            os.mkdir(output_file_path)
        self.input_file_path = input_file_path
        self.output_file_path = output_file_path
        regular_expression.

    def read_novel_content(self):
        # 第一次的时候执行, 后面不执行
        self.chapter_regex_pattern = r'(第\s*(\d+|[零一二两三四五六七八九十百千万]+)\s*章\s*.*)'
        with open(self.input_file_path, "r", encoding="utf8") as file:
            # 按行模式读取整本小说内容
            self.novel_content_split_by_line = file.readlines()
'''




def match_code_define_variable(code_text):
    matched_variables_list = []
    for single_line in code_text.split("\n"):
        single_line = single_line.strip()
        # 首先判断不是注释内容, 注释不匹配
        if not single_line.startswith("#"):  # 注释不处理
            # 正则表达式匹配使用等号定义的变量 a = b
            # var_pattern = re.compile(r'([0-9a-zA-Z_\u4e00-\u9fa5]+)\s*=\s*')
            var_pattern = re.compile(r'\s*([0-9a-zA-Z_\u4e00-\u9fa5, ]+)\s*=\s*[^\s=]+')
            # 返回有可能是一个变量, 也可能是逗号分割的多个变量组成的字符串
            # 提取所有变量名
            match_results_list = var_pattern.findall(single_line)

            # 对变量列表进行循环, 如果包含逗号, 说明需要进一步处理
            # ['c, d_d ']
            for element in match_results_list:
                if "," in element:  # ['c, d_d ']
                    for variable in element.split(","):
                        matched_variables_list.append(variable.strip())
                else:
                    matched_variables_list.append(element.strip())

    return matched_variables_list


def extract_imported_variables(code_text):
    """提取所有import 变量和 from xxx import xxx"""

    variable_list = []
    for single_line in code_text.split("\n"):
        # 判断这行是不是以import 开头的
        if single_line.startswith("import "):
            # 如果是以import 开头的, 分成四种情况,
            """import zhang_san
                import 宋六, li_si
                import 王五, sunqi as 孙七
                import pandas as data_processing
                import re as regular_expression, os as file_management_package"""
            # 凡是有from的一定是有import 的, 需要的是import后面的内容, 前边from ... import 去掉
            import_post_text = single_line.split("import ")[-1]
            import_post_text_split = import_post_text.split(",")
            for one in import_post_text_split:
                if one.find("as") < 0:  # 没有as, 这个需要单独添加到一个队列当中去, 后续判断是否中文
                    variable_list.append(one.strip())
                    related_files_list.append(one.strip())
                else:  # 有as, 提取后面部分
                    # 这里我假设有这种 import 通义千问大模型 as 通义, 两个都是中文, 完全有可能
                    variable_list.append(one.split("as")[0].strip())
                    variable_list.append(one.split("as")[-1].strip())
                    related_files_list.append(one.split("as")[0].strip())

        """from numpy import 测试1
            from numpy import ndarray as 测试1
            from datetime import 测试3, date as 测试4
            from datetime import datetime as 测试5, date as 测试6"""
        if single_line.startswith("from "):
            # 提取from后面的变量
            import_prefix_variables = single_line.split("import ")[0].strip("from").strip()
            variable_list.append(import_prefix_variables)
            related_files_list.append(import_prefix_variables)

            # 凡是有from的一定是有import 的, 需要的是import后面的内容, 前边from ... import 去掉
            import_post_text = single_line.split("import ")[-1]
            import_post_text_split = import_post_text.split(",")
            for one in import_post_text_split:
                if one.find("as") < 0:  # 没有as, 直接保存
                    variable_list.append(one.strip())
                    related_files_list.append(one.strip())
                else:  # 有as, 提取后面部分
                    variable_list.append(one.split("as")[0].strip())
                    variable_list.append(one.split("as")[-1].strip())
                    related_files_list.append(one.split("as")[0].strip())

    return variable_list


def fixed_syntax_matching(code_text):
    def_pattern = r"def ([0-9a-zA-Z_\u4e00-\u9fa5]+)\((.*)\):"

    variable_list = []
    function_match_results_list = re.findall(def_pattern, code_text)
    for one in function_match_results_list:
        # 每一项应该返回的都是两个元素的元组
        function_name, function_argument_name = one
        variable_list.append(function_name)
        if function_argument_name:
            function_argument_names_list = [i.strip().split("=")[0] for i in function_argument_name.split(",")]
            variable_list.extend(function_argument_names_list)

    class_pattern = r"class ([0-9a-zA-Z_\u4e00-\u9fa5]+).*\:"
    class_name_match_results_list = re.findall(class_pattern, code_text)
    variable_list.extend(class_name_match_results_list)

    for_pattern = r"for\s+([0-9a-zA-Z_\u4e00-\u9fa5]+)\s+in"
    loop_match_results_list = re.findall(for_pattern, code_text)
    variable_list.extend(loop_match_results_list)

    with_pattern = r"with.*as\s(.+):"
    with_match_results_list = re.findall(with_pattern, code_text)
    variable_list.extend(with_match_results_list)

    return variable_list


def extract_chinese_variables(variable_list):

    # 过滤掉英文变量, 如果是中英文混合的, 只要其中包含中文变量
    chinese_variable_list = {variable for variable in variable_list if any('\u4e00' <= char <= '\u9fff' for char in variable)}
    return chinese_variable_list


def traverse_directories_and_files_list(start_directory='.', ignore_directory=None):
    """
    列出指定路径下的所有目录和文件，忽略指定的目录。

    :param start_directory: 起始目录，默认为当前目录。
    :param ignore_directory: 要忽略的目录列表。
    """
    if ignore_directory is None:
        ignore_directory = ['__pycache__', '.git', '.idea']
    # 遍历目录
    for 目录路径, 目录列表, 文件列表 in os.walk(start_directory):
        # 修改 目录列表，移除忽略的目录，影响 os.walk 的遍历行为
        目录列表[:] = [d for d in 目录列表 if d not in ignore_directory]

        collect_directories_list.append(目录路径)

        # 输出当前目录下的所有文件
        for file in 文件列表:
            collect_files_list.append(os.path.join(目录路径, file))

def related_file_judgment(project_absolute_path):
    """函数功能:
    公共列表, related_files_list 中保存着import的其他文件,

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
    related_chinese_files_list = extract_chinese_variables(related_files_list)
    log.debug("related_chinese_files_list: {}", related_chinese_files_list)
    traverse_directories_and_files_list(project_absolute_path)  # collect_directories_list collect_files_list
    # 对 related_chinese_files_list 中的进行判断
    log.debug("collect_directories_list: {}", collect_directories_list)
    log.debug("collect_files_list: {}", collect_files_list)
    directory_name_mapping_dict = {}
    for full_directory in collect_directories_list:
        directory_name = full_directory.split("/")[-1]
        directory_name_mapping_dict[directory_name] = full_directory

    file_name_mapping_dict = {}
    for full_file in collect_files_list:
        file_name = full_file.split("/")[-1]
        file_name_mapping_dict[file_name] = full_file

    for chinese_variable in related_chinese_files_list:
        # /Users/yangxinyi/Library/CloudStorage/OneDrive-个人/100_code/Code_Chinese_to_Enghlish/示例代码/__init__.py
        # 注意这里面提取出的中文变量, 很可能并没有运行.
        if chinese_variable in directory_name_mapping_dict.keys():  # 目录
            # 在同一层级, 创建一个文件夹
            directory_mapping_dict = tongyi_qianwen_model.翻译文件名(chinese_variable)
            translated_english_name = directory_mapping_dict[chinese_variable]
            full_directory = directory_name_mapping_dict[chinese_variable]
            parent_directory = full_directory[:-len(chinese_variable)]
            log.debug(parent_directory + "/" + translated_english_name)
            os.mkdir(parent_directory + "/" + translated_english_name)


        elif chinese_variable in collect_files_list:
            # 传到递归函数里面再次进行处理
            # todo
            pass



def read_saved_variables():
    # 检查文件是否存在
    saved_variables_path = "saved_variables.json"
    # 获取当前文件的绝对路径
    current_file_path = os.path.abspath(__file__)
    # 获取当前文件所在的目录
    current_directory = os.path.dirname(current_file_path)
    # 改变工作目录到当前文件所在的目录
    os.chdir(current_directory)
    log.info("工作目录已改变为: {}", os.getcwd())
    if not os.path.exists(saved_variables_path):
        with open(saved_variables_path, 'w', encoding='utf-8') as f:
            json.dump({"测试": "test"}, f, ensure_ascii=False, indent=4)

    with open(saved_variables_path, 'r', encoding='utf-8') as f:
        saved_variables = json.load(f)
    return saved_variables


def reverse_dictionary_function(input_dict):
    # 创建一个反转的字典，键是原来的值，值是原来的键的列表
    reverse_dictionary = {}
    for key, value in input_dict.items():
        if value in reverse_dictionary:
            reverse_dictionary[value].append(key)
        else:
            reverse_dictionary[value] = [key]
    return reverse_dictionary

def dictionary_duplicate_value_check(input_dict):
    # 找出所有值的列表长度大于1的条目
    duplicate_items = {}
    for key, value in input_dict.items():
        if len(value) > 1:
            for i in value:
                duplicate_items[i] = key

    return duplicate_items

def query_and_merge_variables(chinese_variable_list):
    saved_variables_path = "saved_variables.json"
    # read_saved_variables, 对其中已经保存的变量进行替换
    # 现在是获取到了一个集合, 我需要获取已保存变量, 这是一个字典, 然后
    saved_variables = read_saved_variables()
    # 我想要进行代码文件的替换, 需要一个字典, 不需要过滤, 只要保存的是所有的变量就可以了
    # 有一个集合和一个字典, 现在需要从集合中提取出所有不在字典的key当中的数据
    unsaved_variable = [element for element in chinese_variable_list if not saved_variables.get(element)]
    # 几个函数下来, 应该会获取到一个完整的变量列表, 然后将这个变量列表传入到
    # 考虑未保存变量为空的情况, 不需要连接大模型
    if unsaved_variable:
        new_variable_dict = tongyi_qianwen_model.翻译中文变量(unsaved_variable)

        # 发现这里大模型返回的字典有可能存在确实, 部分传入的变量没有翻译回来, 这里添加一个缺失检测功能
        # 如何检测呢? 未保存变量是我要查询的变量, new_variable_dict 查询这个key里面不存在的 unsaved_variable element
        missing_variable = [element for element in unsaved_variable if not new_variable_dict.get(element)]
        log.debug("查询到缺失变量: {}", missing_variable)
        if missing_variable:
            missing_variable_translation_dict = tongyi_qianwen_model.翻译中文变量(missing_variable)
            new_variable_dict.update(missing_variable_translation_dict)
        new_variable_dict.update(saved_variables)  # 放在后面的是保留的, 历史变量优先级更高
        merged_variable = new_variable_dict
    else:
        merged_variable = saved_variables
    # 防止出现两个中文变量被翻译成同样的中文, 这里要进行重复数据检查.
    reverse_dictionary = reverse_dictionary_function(merged_variable)
    duplicate_items = dictionary_duplicate_value_check(reverse_dictionary)
    if duplicate_items:
        log.debug("检测到重复项: {}", duplicate_items)
        deduplication_dict = tongyi_qianwen_model.处理重复变量(duplicate_items)
        log.debug("大模型去重后: {}", deduplication_dict)
        # 去重后的字典应该, 把这些值覆盖原来的key和value
        merged_variable.update(deduplication_dict)
    else:
        log.debug("未检测到重复项")
    with open(saved_variables_path, 'w', encoding='utf-8') as f:
        json.dump(merged_variable, f, ensure_ascii=False, indent=4)
    return merged_variable


def code_file_translation(code_absolute_path):
    with open(code_absolute_path, "r") as file:
        code_text = file.read()
    variable_list = []
    variable_list_1 = match_code_define_variable(code_text)
    variable_list_2 = extract_imported_variables(code_text)
    variable_list_3 = fixed_syntax_matching(code_text)
    variable_list.extend(variable_list_1)
    variable_list.extend(variable_list_2)
    variable_list.extend(variable_list_3)
    variable_list_set = set(variable_list)

    chinese_variable_list = extract_chinese_variables(variable_list_set)
    log.debug(chinese_variable_list)
    merged_variable_dict = query_and_merge_variables(chinese_variable_list)
    # 替换变量名
    for variable in chinese_variable_list:
        if variable in merged_variable_dict:
            code_text = re.sub(r'\b' + re.escape(variable) + r'\b', merged_variable_dict[variable], code_text)

    # 保存修改后英文代码, 保存在同一个路径, file_name, 原来的中文文件名称翻译成一个英文的文件名称
    code_directory = os.path.dirname(code_absolute_path)
    # 提取文件名部分
    filename = os.path.basename(code_absolute_path)
    filename_prefix, filename_suffix = filename.split(".")
    filename_prefix_translation = tongyi_qianwen_model.翻译文件名(filename_prefix)

    english_code_save_path = code_directory + "/" + filename_prefix_translation[filename_prefix] + "." + filename_suffix
    with open(english_code_save_path, "w") as f:
        f.write(code_text)


if __name__ == '__main__':
    # 项目根目录的绝对路径
    project_root = '/Users/yangxinyi/Library/CloudStorage/OneDrive-个人/100_code/Code_Chinese_to_Enghlish'
    # 项目根目录的绝对路径
    pending_code_path = "/Users/yangxinyi/Library/CloudStorage/OneDrive-个人/100_code/Code_Chinese_to_Enghlish/中文变量翻译.py"
    code_file_translation(pending_code_path)
    log.info(related_files_list)
    # log.info(collect_files_list)
    related_file_judgment(project_root)















