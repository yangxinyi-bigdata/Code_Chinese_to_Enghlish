import os
from loguru import logger as 日志
# from 示例代码.novel_send import 小说_发送_脚本
#
# import 示例代码.案例1
#
# import 示例代码
# print(示例代码.__file__)
# print(示例代码.__name__)
# print(示例代码.__package__)
# print(示例代码.__path__)
# print(dir(示例代码))
# print(示例代码.案例1.a)
#
# # print(dir(小说_发送_脚本))
# print(小说_发送_脚本.__file__)
# print(小说_发送_脚本.__name__)
# # print(通义千问模型.__path__)

日志.info("工作目录: {}", os.getcwd())
# 获取当前文件的绝对路径
current_file_path = os.path.abspath(__file__)
# 获取当前文件所在的目录
current_directory = os.path.dirname(current_file_path)
# 改变工作目录到当前文件所在的目录
os.chdir(current_directory)
日志.info("工作目录已改变为: {}", os.getcwd())
