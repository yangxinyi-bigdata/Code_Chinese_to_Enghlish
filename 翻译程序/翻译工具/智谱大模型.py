from openai import OpenAI
from zhipuai import ZhipuAI
import json
import os
from typing import List, Dict, Any
from loguru import logger as 日志
from concurrent.futures import ThreadPoolExecutor, as_completed


def 传入大模型返回JSON(messages: List[Dict[str, str]]) -> Dict[str, str]:
    client = ZhipuAI(api_key="877422e22b0ffbb1a47dda410fa40cfa.GgvfUQ9u37cnhaaX")  # 请填写您自己的APIKey
    completion = client.chat.completions.create(
        model="glm-4-plus",  # 请填写您要调用的模型名称
        messages=messages
    )

    json_str = completion.choices[0].message.content
    # 移除代码块标记
    json_str = json_str.strip('```json\n').strip('```')
    日志.debug("返回json字符串: {}", json_str)
    # 将 JSON 字符串转换成 Python 字典
    变量映射字典 = json.loads(json_str)
    return 变量映射字典


def 处理批次(数据批次, 提示语_预备):
    提示语_完整 = 提示语_预备 + str(数据批次)
    日志.debug("提示语_完整: {}", 提示语_完整)
    messages = [{'role': 'system', 'content': '你是一个Python编程助手.'},
                {'role': 'user', 'content': 提示语_完整}]

    return 传入大模型返回JSON(messages)


def 翻译变量(变量列表, 提示语_预备):
    变量映射字典 = {}
    索引 = 0
    批次大小 = 100

    # 检查变量列表是字典还是列表，并据此创建批次列表
    if isinstance(变量列表, list):
        总数据量 = len(变量列表)
        批次列表 = [变量列表[i:i + 批次大小] for i in range(0, 总数据量, 批次大小)]
    elif isinstance(变量列表, dict):
        # 将字典项转换为列表，并分批
        变量项列表 = list(变量列表.items())
        总数据量 = len(变量项列表)
        批次列表 = [dict(变量项列表[i:i + 批次大小]) for i in range(0, 总数据量, 批次大小)]
    else:
        raise TypeError("变量列表必须是列表或字典")

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(处理批次, 批次, 提示语_预备): 批次 for 批次 in 批次列表}
        for future in as_completed(futures):
            try:
                结果 = future.result()
                变量映射字典.update(结果)
            except Exception as e:
                日志.error("批次处理出错: {}", e)
    return 变量映射字典


def 翻译中文变量(变量列表):
    提示语_预备 = """下面是我在编程中使用的变量, 变量中包含中文.
对于变量中含有中文字符串的, 请将整个变量帮助我翻译成对应的Python英文变量名称, 单词使用小写, 多个单词之间使用下划线分割.
最后将传入的原变量和翻译后的英文结果, 使用JSON格式进行返回, 确保所有变量都进行映射, 不要有任何缺失.
注意返回JSON的key不要和传入的有任何变化, 保持不变, 只改变JSON中翻译对应的结果.
返回结果中不要包含任何除了JSON字符串以外任何内容:

    """
    return 翻译变量(变量列表, 提示语_预备)

def 翻译英文变量(变量列表):
    提示语_预备 = """我希望将python代码中的英文变量翻译成中文变量, 下面是我提取的变量, 
请按照python编程原理将英文变量翻译成对应的中文变量, 中文词语之间可以使用下划线分割, 翻译结果必须要符合python变量规则, 不能包含空格或者其他非变量允许的符号.
如果变量是在编程中没有具体意义的词汇, 例如abcd等, 则不翻译直接按原样返回.
最后将传入的原变量和翻译的中文变量, 按照key和value形式, 使用JSON格式进行返回. 
确保所有变量都进行映射, 不要有任何缺失.
注意返回JSON的key不要和传入的有任何变化, 保持不变, 只改变JSON中翻译对应的结果.
返回结果中不要包含任何除了JSON字符串以外任何内容:

    """
    return 翻译变量(变量列表, 提示语_预备)

def 处理重复变量(变量字典, 提示语_预备=""):
    """
    {'合并后文件名称': 'merged_file_name', '合并文件名称': 'merged_file_name', '一章节内容': 'single_chapter_content',
     '一章内容': 'single_chapter_content', '邮件正文': 'email_body', '邮件本体': 'email_body', '发送邮箱': 'send_email',
     '发送邮件': 'send_email'}"""
    提示语_预备 = """下面是我在变量翻译中出现的重复翻译结果, 将不同的中文变量翻译成了相同英文变量.
将翻译结果相同的英文结果进行修改, 使得每一个中文变量的翻译结果都有所不同.
翻译的英文变量中单词使用小写, 多个单词之间使用下划线分割.
仍然按照原来的格式, 将中文和英文对应的结果使用JSON格式进行返回, 注意传入的中文变量不要和原来有任何变化, 必须保证完全一致.
注意: 返回结果中不要包含任何除了JSON字符串以外任何内容!:

    """
    return 翻译变量(变量字典, 提示语_预备)

def 处理英文重复变量(变量字典, 提示语_预备=""):
    """
    {'合并后文件名称': 'merged_file_name', '合并文件名称': 'merged_file_name', '一章节内容': 'single_chapter_content',
     '一章内容': 'single_chapter_content', '邮件正文': 'email_body', '邮件本体': 'email_body', '发送邮箱': 'send_email',
     '发送邮件': 'send_email'}"""
    提示语_预备 = """下面是我在变量翻译中出现的重复翻译结果, 将不同的英文变量翻译成了相同中文变量.
将翻译结果相同的中文结果进行修改, 使得每一个英文变量的翻译结果都有所不同.
可以采用在中文词语中间添加下划线, 或者添加其他附加词, 或者删减等方式进行修改.
仍然按照原来的格式, 将英文和中文对应的结果使用JSON格式进行返回, 注意传入的英文变量不要和原来有任何变化, 必须保证完全一致.
注意: 返回结果中不要包含任何除了JSON字符串以外任何内容!:

    """
    return 翻译变量(变量字典, 提示语_预备)


def 处理英文重复变量_列表(变量列表, 提示语_预备=""):
    """
    {'合并后文件名称': 'merged_file_name', '合并文件名称': 'merged_file_name', '一章节内容': 'single_chapter_content',
     '一章内容': 'single_chapter_content', '邮件正文': 'email_body', '邮件本体': 'email_body', '发送邮箱': 'send_email',
     '发送邮件': 'send_email'}"""
    提示语_预备 = """下面是我在Python变量翻译中出现的重复变量, 
对列表当中调每一个英文变量进行翻译, 要保证每个英文变量翻译的中文变量都是不同的, 但是又尽可能保留原来英文单词的含义.
可以采用在中文词语中间添加下划线, 或者添加其他附加词等方式进行处理.
但是要保证翻译的中文结果一定要可以用作Python变量, 不能添加空格或者不符合变量规则的特殊符号.
将英文和中文对应的结果使用JSON格式进行返回, 注意传入的英文变量不要和原来有任何变化, 必须保证完全一致.
注意: 返回结果中不要包含任何除了JSON字符串以外任何内容!:

    """
    return 翻译变量(变量列表, 提示语_预备)


def 翻译文件名(变量列表, 提示语_预备=""):
    提示语_预备 = """我需要将中文python代码文件名称改成英文, 将下面的中文字符串翻译成英文, 单词使用小写, 多个单词之间使用下划线分割, 注意不要翻译成拼音而是英文, 结果要适用于py文件名称.
最后将传入的字符串和对应的翻译英文结果以JSON格式进行返回, 注意JSON格式中的key要和原字符串一模一样, 不能随意添加空格, 不能有任何变化.
注意: 返回结果中不要包含任何除了JSON字符串以外任何内容.

翻译字符串为:
"""
    return 处理批次(变量列表, 提示语_预备)

def 翻译英文文件名(变量列表):
    提示语_预备 = """我需要将英文python代码文件名称改成中文, 将下面的英文字符串翻译成中文, 翻译结果要适合作为py文件名称.
最后将传入的字符串和对应的翻译结果以JSON格式进行返回, 注意JSON格式中的key要和原字符串一模一样, 不能随意添加空格, 不能有任何变化.
注意: 返回结果中不要包含任何除了JSON字符串以外任何内容.

翻译字符串为:
"""
    return 处理批次(变量列表, 提示语_预备)


if __name__ == '__main__':
    变量列表 = ['datetime', '合并文件名称', '小说内容', '输出文件_路径', '发送邮件', '已经阅读章节数量', '章节正则匹配模式',
     '结束时间', '开始时间', 'smtplib', '随机延迟时间', '消息', '随机延迟_按秒配置', '输入文件_路径', 'random',
     'encoders', 'encoding', '随机秒数', '小说内容_按行切分', '最大秒数', '发送小说文件', '当前_文件_路径', '附件',
     '当前行', '匹配结果', '延迟', '当前_文件', '已读章节数量', '合并后章节保存路径', '一章内容', 'MIMEMultipart', 're',
     '__name__', '章节数', '创建邮箱消息', 'Header', 'seconds', '发送邮箱', '一章内容列表', '随机时间', '今天所有内容',
     'filename', '小说处理器', 'QQ邮箱发送', 'MIMEText', '小说处理器_类', '保存数据', '小说名称', '邮件标题',
     '开始时间小时', '章节名称列表', '接收邮箱', '上一章节名称', '字符串格式时间', '结束时间小时', '切割文本_按照章节',
     '__init__', '邮件本体', 'e', 'time', '合并当天章节', '计数', '当前时间', '下一章节名称', '合并章节数量', '一章',
     '合并后文件名称', '邮件正文', 'self', '最终结果', '邮箱密码', 'os', '一章节内容', '读取小说内容', '秒数',
     '发送文件', '今天章节名称列表', 'QQ邮箱发送_类']
    日志.info(翻译中文变量(变量列表))
    # 日志.info(翻译文件名("传入大模型返回JSON"))





