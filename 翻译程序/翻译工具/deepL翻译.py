import deepl
from loguru import logger as 日志

auth_key = "09a1ee9a-436a-4d9a-b9bf-cd8af5c7854e:fx"  # Replace with your key
翻译器 = deepl.Translator(auth_key)
def 翻译文本_函数(翻译文本):
    翻译结果 = 翻译器.translate_text(翻译文本, source_lang="ZH", target_lang="EN-US")
    return 翻译结果.text


def 获取翻译结果(翻译文本):
    """首先将返回的单词转换成小写"""
    翻译结果 = 翻译文本_函数(翻译文本)
    翻译结果_小写 = 翻译结果.lower()
    # 拼接几个单词
    处理后变量 = "_".join(翻译结果_小写.split(" "))
    return 处理后变量


def 翻译多个文本_函数(翻译文本_列表):
    翻译结果 = 翻译器.translate_text(翻译文本_列表, source_lang="ZH", target_lang="EN-US")
    变量映射字典 = {}
    计数 = 0
    for 元素 in 翻译结果:
        翻译文本_小写 = 元素.text.lower()
        处理后变量 = "_".join(翻译文本_小写.split(" "))
        变量映射字典[翻译文本_列表[计数]] = 处理后变量
        计数 += 1

    return 变量映射字典



if __name__ == '__main__':

    # 处理后变量 = 获取翻译结果("翻译文本_函数")
    # 日志.info(处理后变量)
    变量映射字典 = 翻译多个文本_函数(["当前_文件_路径", "文件名前缀", "小说处理器_类"])
    日志.info(变量映射字典)
