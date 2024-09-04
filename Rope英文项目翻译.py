import pandas as pd
import rope
from rope.base.project import Project
from rope.refactor.rename import Rename
from rope.base import libutils, pynamesdef
from rope.base.pyobjectsdef import PyFunction, PyClass, PyModule, PyPackage, PyComprehension
from rope.base.pyobjects import PyObject
from rope.refactor.extract import ExtractVariable
from rope.contrib import codeassist
from rope.base.evaluate import eval_location
from rope.base import builtins
from rope.contrib.codeassist import get_definition_location, code_assist

from 英文项目翻译 import 查询英文变量, 复制文件夹_删除已存在


class Rope管理器:
    def __init__(self, 项目路径):
        self.我的资源 = None
        self.监控范围 = None
        self.项目路径 = 项目路径
        self.资源路径 = None
        self.提取变量表格 = pd.DataFrame(columns=["监控范围标识", "变量名称", "翻译变量", "变量种类", "推断类型", "变量对象", "变量对象_数据类型"])
        self.我的项目 = Project(项目路径)

    def 关闭项目(self):
        # 保存项目，确保所有更改被写入文件
        self.我的项目.close()

    def 创建资源(self, 资源名称):
        self.我的资源 = libutils.path_to_resource(self.我的项目,
                                              self.项目路径 + "/" + 资源名称)

    def 搜索变量偏移量(self, 行号, 变量):
        """这里不应该简单的计算偏移量, 应该按照代码实际来进行计算"""
        # 首先对于当前资源按照行号进行切割
        self.资源路径 = self.我的资源.real_path
        with open(self.资源路径, "r") as f:
            内容列表 = f.readlines()
        内容切割 = 内容列表[行号-1]
        偏移量 = 内容切割.find(变量)
        前面内容 = 内容列表[:行号-1]
        前面偏移量 = len("".join(前面内容))

        return 前面偏移量 + 偏移量

    def 重命名(self, 行号, 修改变量, 新变量):
        偏移量 = self.搜索变量偏移量(行号, 修改变量)
        重命名_对象 = Rename(self.我的项目, self.我的资源, 偏移量)
        # 执行重命名操作
        改变_对象 = 重命名_对象.get_changes(new_name=新变量)
        self.我的项目.do(改变_对象)

    def 获取监控范围(self):
        self.监控范围 = libutils.get_string_scope(self.我的项目, self.我的资源.read(), self.我的资源)

    def 获取变量类型(self, 变量名称, 监控范围):
        pyname = 监控范围.get_names().get(变量名称)
        推断类型 = pyname.get_object()
        变量对象 = 推断类型.get_type()
        try:
            变量对象_数据类型 = 变量对象.get_name()
        except Exception as e:
            变量对象_数据类型 = ""
        return 推断类型, 变量对象, 变量对象_数据类型

    def 搜索变量(self, 监控范围, 监控路径: str, 监控变量字典: dict):
        """思考: 这个函数应该什么功能呢? 我那边需要的是什么? 变量, 变量作用域, 变量类型.
        监控变量字典: 应该有全局变量"""
        当前监控路径 = f"{监控路径}/{监控范围.get_kind()}(Line {监控范围.get_start()})"
        全局变量字典 = 监控范围.get_names()

        监控变量字典[当前监控路径] = 全局变量字典

        self.过滤自定义变量(监控范围, 全局变量字典)
        子监控范围列表 = 监控范围.get_scopes()
        for 子监控范围 in 子监控范围列表:
            self.搜索变量(子监控范围, 监控路径, 监控变量字典)

    def 过滤自定义变量_废弃(self, 监控范围, 全局变量字典):
        # 监控变量字典 当中保存所有提取的结果
        for 变量 in 全局变量字典:
            if isinstance(全局变量字典[变量], pynamesdef.AssignedName):
                print(变量, "AssignedName")
                推断类型, 变量数据类型 = self.获取变量类型(变量, 监控范围)
                print(推断类型)
                print(变量数据类型)
            if isinstance(全局变量字典[变量], pynamesdef.DefinedName):
                print(变量, "DefinedName")
                推断类型, 变量数据类型 = self.获取变量类型(变量, 监控范围)
                print(推断类型)
                print(变量数据类型)

            elif isinstance(全局变量字典[变量], pynamesdef.ParameterName):
                print(变量, "ParameterName")
                推断类型, 变量数据类型 = self.获取变量类型(变量, 监控范围)
                print(推断类型)
                print(变量数据类型)

            elif isinstance(全局变量字典[变量], pynamesdef.ImportedModule):
                print(变量, "ImportedModule")
                推断类型, 变量数据类型 = self.获取变量类型(变量, 监控范围)
                print(推断类型)
                print(变量数据类型)
            print("-------")

    def 提取范围变量(self, 监控范围, 监控路径):
        """输入监控范围, 监控路径, 返回当前监控范围内提取的变量DataFrame
        然后获取当前变量范围的子范围, 再提取变量DataFrame"""
        当前监控区域 = f"{监控路径}/{监控范围.get_kind()}(行号 {监控范围.get_start()})"
        全局变量字典 = 监控范围.get_names()
        处理变量字典 = self.过滤变量字典(监控范围, 全局变量字典)
        for 变量 in 处理变量字典:
            # 提取变量类型
            self.提取变量表格.loc[len(self.提取变量表格)] = [当前监控区域, 变量, "", 处理变量字典[变量][0],
                                                             处理变量字典[变量][1], 处理变量字典[变量][2], 处理变量字典[变量][3]]
        # 处理子范围
        子监控范围列表 = 监控范围.get_scopes()
        for 子监控范围 in 子监控范围列表:
            self.提取范围变量(子监控范围, 监控路径)

    def 过滤变量字典(self, 监控范围, 全局变量字典):
        """需求: 传入一个变量, 和对应的监控范围, 查询变量的pyname和变量类型"""
        处理变量字典 = {}
        for 变量 in 全局变量字典:
            if any([
                    isinstance(全局变量字典[变量], pynamesdef.AssignedName),
                   isinstance(全局变量字典[变量], pynamesdef.DefinedName),
                   isinstance(全局变量字典[变量], pynamesdef.ParameterName),
                   isinstance(全局变量字典[变量], pynamesdef.EvaluatedName),
                   isinstance(全局变量字典[变量], pynamesdef.AssignmentValue)
                ]
                   ):
                推断类型, 变量对象, 变量对象_数据类型 = self.获取变量类型(变量, 监控范围)
                处理变量字典[变量] = [全局变量字典[变量], 推断类型, 变量对象, 变量对象_数据类型]
        return 处理变量字典

    def 过滤变量并翻译(self):
        """rope管理.提取变量表格 这里面已经保存了当前代码提取出来的所有变量
        接下来判断哪个变量需要进行翻译, 然后调用rope里面的Rename功能进行重命名
        """
        翻译变量列表 = self.提取变量表格.变量名称.to_list()
        全部提取变量_字典 = 查询英文变量(翻译变量列表)
        翻译变量映射字典 = {}
        for 翻译变量 in 翻译变量列表:
            if 全部提取变量_字典.get(翻译变量):
                翻译变量映射字典[翻译变量] = 全部提取变量_字典.get(翻译变量)

        for index in self.提取变量表格.index:
            if 翻译变量映射字典.get(self.提取变量表格.loc[index, "变量名称"]):
                if isinstance(self.提取变量表格.loc[index, "推断类型"], PyFunction):
                    self.提取变量表格.loc[index, "翻译变量"] = 翻译变量映射字典[self.提取变量表格.loc[index, "变量名称"]] + "_类"
                if isinstance(self.提取变量表格.loc[index, "推断类型"], PyClass):
                    self.提取变量表格.loc[index, "翻译变量"] = 翻译变量映射字典[self.提取变量表格.loc[index, "变量名称"]] + "_函数"
                if isinstance(self.提取变量表格.loc[index, "推断类型"], PyObject):
                    self.提取变量表格.loc[index, "翻译变量"] = 翻译变量映射字典[self.提取变量表格.loc[index, "变量名称"]]

                module, 行号 = self.提取变量表格.loc[index, "变量种类"].get_definition_location()
                self.重命名变量(行号, self.提取变量表格.loc[index, "变量名称"],
                                self.提取变量表格.loc[index, "翻译变量"])


    def 重命名变量(self, 行号, 翻译变量=None, 变量翻译结果=None):
        if not 翻译变量:
            renamer = Rename(self.我的项目, self.我的资源)
        else:
            偏移量 = self.搜索变量偏移量(行号, 翻译变量)
            print(翻译变量, 偏移量)
            renamer = Rename(self.我的项目, self.我的资源, 偏移量)

        # 获取重命名变更
        change = renamer.get_changes(变量翻译结果)
        self.我的项目.do(change)


if __name__ == '__main__':
    项目_根路径 = '/Users/yangxinyi/Downloads/200_临时文件夹/english_test_project'
    项目_翻译路径 = "/Users/yangxinyi/Downloads/200_临时文件夹/项目翻译测试"

    复制文件夹_删除已存在(项目_根路径, 项目_翻译路径)

    rope管理 = Rope管理器(项目_翻译路径)
    file_name = 'config.py'
    # file_name = 'bridge/context.py'
    rope管理.创建资源(file_name)
    rope管理.获取监控范围()
    rope管理.提取范围变量(rope管理.监控范围, file_name)
    rope管理.过滤变量并翻译()


    # print(rope管理.提取变量表格)
    # rope管理.重命名变量("json", "错误")
    # rope管理.重命名变量("上下文")


    # print(rope管理.我的项目.get_python_path_folders())




