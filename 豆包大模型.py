from openai import OpenAI
import json
import os
from loguru import logger as 日志

client = OpenAI(
    api_key="6cdd6e93-a62d-4b22-a821-8eb3c5bfd245",
    base_url="https://ark.cn-beijing.volces.com/api/v3",
)

def 翻译中文变量(变量列表, 提示语_预备=""):
    提示语_预备 = """下面是我在编程中使用的变量, 变量中包含英文.
    对于中文变量, 请帮助我翻译成对应的Python英文变量名称, 单词使用小写, 多个单词之间使用下划线分割.
    对于其中的英文变量直接忽略, 最后将中文和英文对应的结果使用JSON格式进行返回, 确保所有变量都进行映射, 不要有任何缺失.
    返回结果中不要包含任何除了JSON字符串以外任何内容:
        """
    提示语_完整 = 提示语_预备 + str(变量列表)
    日志.debug("提示语_完整: {}", 提示语_完整)
    messages = [{'role': 'system', 'content': '你是一个Python编程助手.'},
                {'role': 'user', 'content': 提示语_完整}]
    completion = client.chat.completions.create(
        model="ep-20240801193759-nqxc7",  # your model endpoint ID
        messages=messages,
        temperature=0.3
    )
    json_str = completion.choices[0].message.content
    # 移除代码块标记
    json_str = json_str.strip('```json\n').strip('```')
    日志.debug("返回json字符串: {}", json_str)
    # 将 JSON 字符串转换成 Python 字典
    变量映射字典 = json.loads(json_str)
    return 变量映射字典


def 处理重复变量(变量字典, 提示语_预备=""):
    """
    {'合并后文件名称': 'merged_file_name', '合并文件名称': 'merged_file_name', '一章节内容': 'single_chapter_content',
     '一章内容': 'single_chapter_content', '邮件正文': 'email_body', '邮件本体': 'email_body', '发送邮箱': 'send_email',
     '发送邮件': 'send_email'}"""

    提示语_预备 = """下面是我在变量翻译中出现的重复翻译结果, 将不同的中文变量翻译成了相同英文变量.
将翻译结果相同的英文结果进行修改, 使得每一个中文变量的翻译结果都有所不同.
翻译的英文变量中单词使用小写, 多个单词之间使用下划线分割.
仍然按照原来的格式, 将中文和英文对应的结果使用JSON格式进行返回, 
注意: 返回结果中不要包含任何除了JSON字符串以外任何内容!:

    """
    提示语_完整 = 提示语_预备 + str(变量字典)
    日志.debug("提示语_完整: {}", 提示语_完整)
    messages = [{'role': 'system', 'content': '你是一个Python编程助手.'},
                {'role': 'user', 'content': 提示语_完整}]
    completion = client.chat.completions.create(
        model="ep-20240801193759-nqxc7",  # your model endpoint ID
        messages=messages,
        temperature=0.3
    )
    json_str = completion.choices[0].message.content
    # 移除代码块标记
    json_str = json_str.strip('```json\n').strip('```')
    日志.debug("返回json字符串: {}", json_str)
    # 将 JSON 字符串转换成 Python 字典
    变量映射字典 = json.loads(json_str)
    return 变量映射字典


def 翻译文件名(变量列表, 提示语_预备=""):
    提示语_预备 = """将下面的中文字符串翻译成英文, 单词使用小写, 多个单词之间使用下划线分割, 注意不要翻译成拼音而是英文, 
最后将中文和英文对应的结果以JSON格式进行返回, 注意JSON格式中的key要和原字符串一模一样, 不能随意添加空格.
注意: 返回结果中不要包含任何除了JSON字符串以外任何内容: 
"""
    提示语_完整 = 提示语_预备 + str(变量列表)
    日志.debug("提示语_完整: {}", 提示语_完整)
    messages = [{'role': 'system', 'content': '你是一个Python编程助手.'},
                {'role': 'user', 'content': 提示语_完整}]
    completion = client.chat.completions.create(
        model="ep-20240801193759-nqxc7",  # your model endpoint ID
        messages=messages,
        temperature=0.3
    )
    json_str = completion.choices[0].message.content
    # 移除代码块标记
    json_str = json_str.strip('```json\n').strip('```')
    日志.debug("返回json字符串: {}", json_str)
    # 将 JSON 字符串转换成 Python 字典
    变量映射字典 = json.loads(json_str)
    return 变量映射字典


if __name__ == '__main__':
    变量列表 = {'datetime', '合并文件名称', '小说内容', '输出文件_路径', '发送邮件', '已经阅读章节数量', '章节正则匹配模式',
     '结束时间', '开始时间', 'smtplib', '随机延迟时间', '消息', '随机延迟_按秒配置', '输入文件_路径', 'random',
     'encoders', 'encoding', '随机秒数', '小说内容_按行切分', '最大秒数', '发送小说文件', '当前_文件_路径', '附件',
     '当前行', '匹配结果', '延迟', '当前_文件', '已读章节数量', '合并后章节保存路径', '一章内容', 'MIMEMultipart', 're',
     '__name__', '章节数', '创建邮箱消息', 'Header', 'seconds', '发送邮箱', '一章内容列表', '随机时间', '今天所有内容',
     'filename', '小说处理器', 'QQ邮箱发送', 'MIMEText', '小说处理器_类', '保存数据', '小说名称', '邮件标题',
     '开始时间小时', '章节名称列表', '接收邮箱', '上一章节名称', '字符串格式时间', '结束时间小时', '切割文本_按照章节',
     '__init__', '邮件本体', 'e', 'time', '合并当天章节', '计数', '当前时间', '下一章节名称', '合并章节数量', '一章',
     '合并后文件名称', '邮件正文', 'self', '最终结果', '邮箱密码', 'os', '一章节内容', '读取小说内容', '秒数',
     '发送文件', '今天章节名称列表', 'QQ邮箱发送_类'}
    日志.info(翻译中文变量(变量列表))




