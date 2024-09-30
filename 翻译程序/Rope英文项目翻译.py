import re
import os

from 翻译程序.通用处理 import *

from 翻译程序.英文项目翻译 import 复制文件夹_删除已存在

关联文件_列表 = []
dir_path = os.path.dirname(os.path.realpath(__file__))
中英映射变量_路径 = os.path.join(dir_path, "翻译程序", "中英映射字典.json")
英中映射变量_路径 = os.path.join(dir_path, "翻译程序", "英中映射字典.json")
# 中英映射变量_路径 = "翻译程序/中英映射字典.json"
# 英中映射变量_路径 = "翻译程序/英中映射字典.json"

配置 = 载入配置()


if __name__ == '__main__':
    项目_根路径 = '/Users/yangxinyi/Downloads/200_临时文件夹/english_test_project'
    项目_翻译路径 = "/Users/yangxinyi/Downloads/200_临时文件夹/项目翻译测试"

    复制文件夹_删除已存在(项目_根路径, 项目_翻译路径)

    rope管理 = Rope管理器(项目_翻译路径)
    file_name = 'bot/session_manager.py'
    # rope管理.创建资源(file_name)
    # rope管理.获取监控范围()
    # rope管理.提取导入变量()
    # rope管理.提取范围变量()
    # rope管理.过滤变量并翻译()
    # rope管理.处理重复变量()
    # rope管理.批量替换变量()
    # rope管理.批量修改目录名称()
    # rope管理.批量修改py文件名称()



    for py文件 in rope管理.py文件列表:
        日志.debug(py文件)
        rope管理.创建资源(py文件)
        rope管理.获取监控范围()
        rope管理.提取导入变量()
        rope管理.提取范围变量()

    rope管理.过滤变量并翻译()
    rope管理.提取导入变量表格 = rope管理.处理重复变量(rope管理.提取导入变量表格)
    rope管理.提取变量表格 = rope管理.处理重复变量(rope管理.提取变量表格)

    # 上面对所有文件资源进行处理, 这里仍然需要循环对所有进行处理, 虽然
    # rope管理.批量替换导入变量()

    rope管理.批量替换变量()


    pass

    # for py文件 in rope管理.py文件列表:
    #     日志.debug(py文件)
    #     rope管理.创建资源(py文件)
    #     rope管理.获取监控范围()
    #     rope管理.提取导入变量()
    #     rope管理.提取范围变量()
    #     rope管理.过滤变量并翻译()
    #     rope管理.处理重复变量()
    #     rope管理.批量替换变量()
