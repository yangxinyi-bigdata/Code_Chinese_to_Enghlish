from pathlib import Path
import json
import shutil
import re
from loguru import logger as 日志
import pandas as pd
from rope.base.project import Project
from rope.refactor.rename import Rename
from rope.base import libutils, pynamesdef
from rope.base.pyobjectsdef import PyFunction, PyClass
from rope.base.pyscopes import ComprehensionScope
from rope.base.exceptions import RefactoringError, BadIdentifierError
from 翻译程序.代码工具 import *
from 翻译程序.翻译工具 import 通义千问模型
from 配置 import 载入配置

关联文件_列表 = []
# 中英映射变量_路径 = "翻译程序/中英映射字典.json"
# 英中映射变量_路径 = "翻译程序/英中映射字典.json"
# 英中重复变量_路径 = "翻译程序/英中重复变量.txt"

dir_path = os.path.dirname(os.path.realpath(__file__))

中英映射变量_路径 = os.path.join(dir_path, "中英映射字典.json")
英中映射变量_路径 = os.path.join(dir_path, "英中映射字典.json")
英中重复变量_路径 = os.path.join(dir_path, "英中重复变量.txt")
# 已保存变量_路径 = "翻译程序/中英映射字典.json"

任务进度 = 0
状态信息 = "初始状态"

配置 = 载入配置()


def 设置进度值(任务进度值):
    global 任务进度
    任务进度 = 任务进度值


def 设置状态值(状态信息值):
    global 状态信息
    状态信息 = 状态信息值


def 获取状态值():
    return 状态信息


def 获取进度值():
    return 任务进度


class Rope管理器:
    def __init__(self, 项目路径):
        self.我的资源 = None
        self.监控范围 = None
        self.项目路径 = 项目路径

        self.py文件列表, self.相对文件列表, self.相对目录列表 = 收集项目资源(项目路径)
        self.导入模块列表: list = []
        self.导入目录列表: list = []
        self.生成导入名称()
        self.资源路径 = None
        self.提取变量表格 = pd.DataFrame(
            columns=["监控范围标识", "变量名称", "翻译变量", "去重变量", "变量种类", "推断类型", "变量对象",
                     "变量对象_数据类型", "变量资源"])
        self.提取导入变量表格 = pd.DataFrame(
            columns=["监控范围标识", "变量名称", "翻译变量", "去重变量", "变量种类", "推断类型", "变量对象",
                     "变量对象_数据类型", "变量资源"])
        self.我的项目 = Project(项目路径)

    def 关闭项目(self):
        # 保存项目，确保所有更改被写入文件
        self.我的项目.close()

    def 创建资源(self, 资源名称, 类型=None):
        self.我的资源 = libutils.path_to_resource(self.我的项目,
                                                  self.项目路径 + "/" + 资源名称, 类型)

    def 搜索变量偏移量(self, 行号, 变量, 变量资源):
        """这里不应该简单的计算偏移量, 应该按照代码实际来进行计算
        如果行号传进来是None, 则重新自己进行计算"""
        # 首先对于当前资源按照行号进行切割
        self.资源路径 = 变量资源.real_path
        with open(self.资源路径, "r") as f:
            内容列表 = f.readlines()
        pattern = fr'\b{变量}\b'
        if 行号:
            内容切割 = 内容列表[行号 - 1]
            # 这个地方存在bug, except Exception as exc:  对于这行代码, 搜索exc的时候会搜索到前边的 except
            # 怎么处理呢? 不能直接用find, 应该确定是变量才可以
            搜索变量 = re.search(pattern, 内容切割)
            if 搜索变量:
                偏移量 = 搜索变量.start()
                前面内容 = 内容列表[:行号 - 1]
                前面偏移量 = len("".join(前面内容))
                return 前面偏移量 + 偏移量
        else:
            # 对每一行进行搜索, 如果这行不是# 开头,定位井号的位置, 如果在井号前边搜索到了, 那么就用这个行号和位置
            for 行号, 一行 in enumerate(内容列表):
                if not 一行.strip().startswith("#"):
                    替换结果 = 删除单行代码注释和字符串(一行)
                    搜索变量 = re.search(pattern, 替换结果)
                    if 搜索变量:
                        偏移量 = 搜索变量.start()
                        前面内容 = 内容列表[:行号]
                        前面偏移量 = len("".join(前面内容))
                        return 前面偏移量 + 偏移量

    def 重命名(self, 行号, 修改变量, 新变量, 变量资源):
        偏移量 = self.搜索变量偏移量(行号, 修改变量, 变量资源)
        重命名_对象 = Rename(self.我的项目, 变量资源, 偏移量)
        # 执行重命名操作
        改变_对象 = 重命名_对象.get_changes(new_name=新变量)
        self.我的项目.do(改变_对象)

    def 获取监控范围(self):
        self.监控范围 = libutils.get_string_scope(self.我的项目, self.我的资源.read(), self.我的资源)

    def 生成导入名称(self):
        """根据项目中的py代码, 分析项目内都有哪些路径和代码可以import"""
        for py文件 in self.py文件列表:
            if py文件.endswith("__init__.py"):
                self.导入模块列表.append(py文件.replace("/__init__.py", "").replace("/", "."))
            else:
                self.导入模块列表.append(py文件.replace("/", ".").removesuffix(".py"))
        for 目录 in self.相对目录列表:
            self.导入目录列表.append(目录.replace("/", "."))

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

    def 过滤变量字典(self, 监控范围, 全局变量字典):
        """需求: 传入一个变量, 和对应的监控范围, 查询变量的pyname和变量类型
        同时必须是不包含中文的变量."""
        处理变量字典 = {}
        for 变量 in 全局变量字典:
            if not 判断中文变量(变量) and any([
                isinstance(全局变量字典[变量], pynamesdef.AssignedName),
                isinstance(全局变量字典[变量], pynamesdef.DefinedName),
                isinstance(全局变量字典[变量], pynamesdef.ParameterName),
                isinstance(全局变量字典[变量], pynamesdef.EvaluatedName),
                isinstance(全局变量字典[变量], pynamesdef.AssignmentValue)
            ]):
                推断类型, 变量对象, 变量对象_数据类型 = self.获取变量类型(变量, 监控范围)
                处理变量字典[变量] = [全局变量字典[变量], 推断类型, 变量对象, 变量对象_数据类型]
        return 处理变量字典

    def 提取导入变量(self):
        # 思考一下, 这个提取出来应该最终给出一个什么数据呢? 也放到一个DataFrame里面吧
        # 和原来那个表合并到一起吗? 好像没有那么多的值啊
        with open(self.我的资源.real_path) as f:
            代码文本 = f.read()
        变量列表_key, 变量_as = 提取导入变量_通用(代码文本)
        日志.debug(变量列表_key)
        日志.debug(变量_as)

        当前监控区域 = self.我的资源.path
        for 变量 in 变量列表_key:
            # 判断变量是否项目内部导入
            if 变量 in self.导入模块列表 or 变量 in self.导入目录列表:
                for 一个变量 in 变量.split("."):
                    self.提取导入变量表格.loc[len(self.提取导入变量表格)] = [
                        当前监控区域, 一个变量, "", "", "import var", "", "", "", self.我的资源]
                for j in 变量列表_key[变量]:
                    self.提取导入变量表格.loc[len(self.提取导入变量表格)] = [
                        当前监控区域, j, "", "", "import var", "", "", "", self.我的资源]
        for 变量 in 变量_as:
            self.提取导入变量表格.loc[len(self.提取导入变量表格)] = [
                当前监控区域, 变量, "", "", "import var", "", "", "", self.我的资源]

        # self.提取导入变量表格 = pd.DataFrame(
        #     columns=["监控范围标识", "变量名称", "翻译变量", "去重变量", "变量种类", "推断类型", "变量对象",
        #              "变量对象_数据类型", "变量资源"])

        # if 模块名称 != 变量资源.path.removesuffix(".py").replace("/", ".") and (
        #         模块名称 != 变量资源.path.removesuffix(".py").split("/")[-1]):  # 不是当前处理模块, 则判断是否内置模块
        #     if 模块名称 not in self.导入模块列表 or 模块名称 not in self.导入目录列表:

    def 提取范围变量(self):
        """输入监控范围, 监控路径, 返回当前监控范围内提取的变量DataFrame
        然后获取当前变量范围的子范围, 再提取变量DataFrame"""
        当前监控区域 = f"{self.我的资源.path}/{self.监控范围.get_kind()}(行号 {self.监控范围.get_start()})"
        if isinstance(self.监控范围, ComprehensionScope):
            # 全局变量字典 = self.监控范围.get_defined_names()
            return
        else:
            全局变量字典 = self.监控范围.get_names()
        处理变量字典 = self.过滤变量字典(self.监控范围, 全局变量字典)
        for 变量 in 处理变量字典:
            # 提取变量类型
            self.提取变量表格.loc[len(self.提取变量表格)] = [当前监控区域, 变量, "", "", 处理变量字典[变量][0],
                                                             处理变量字典[变量][1], 处理变量字典[变量][2],
                                                             处理变量字典[变量][3], self.我的资源]
        # 处理子范围
        子监控范围列表 = self.监控范围.get_scopes()
        for 子监控范围 in 子监控范围列表:
            self.监控范围 = 子监控范围
            self.提取范围变量()

    def 过滤变量并翻译(self):
        """rope管理.提取变量表格 这里面已经保存了当前代码提取出来的所有变量
        接下来判断哪个变量需要进行翻译, 然后调用rope里面的Rename功能进行重命名
        """
        翻译导入变量列表 = self.提取导入变量表格.变量名称.to_list()
        翻译导入变量映射字典 = 过滤并查询英文变量_V2(翻译导入变量列表)
        for index in self.提取导入变量表格.index:

            if 翻译导入变量映射字典.get(self.提取导入变量表格.loc[index, "变量名称"]):
                if self.提取导入变量表格.loc[index, "变量名称"] == 翻译导入变量映射字典.get(
                        self.提取导入变量表格.loc[index, "变量名称"]):
                    continue
                self.提取导入变量表格.loc[index, "翻译变量"] = 翻译导入变量映射字典[
                    self.提取导入变量表格.loc[index, "变量名称"]]

        翻译变量列表 = self.提取变量表格.变量名称.to_list()
        翻译变量映射字典 = 过滤并查询英文变量_V2(翻译变量列表)
        for index in self.提取变量表格.index:

            if 翻译变量映射字典.get(self.提取变量表格.loc[index, "变量名称"]):
                if self.提取变量表格.loc[index, "变量名称"] == 翻译变量映射字典.get(
                        self.提取变量表格.loc[index, "变量名称"]):
                    continue
                elif isinstance(self.提取变量表格.loc[index, "推断类型"], PyFunction):
                    self.提取变量表格.loc[index, "翻译变量"] = 翻译变量映射字典[
                                                                   self.提取变量表格.loc[
                                                                       index, "变量名称"]] + 配置.获取配置项("函数后缀")
                elif isinstance(self.提取变量表格.loc[index, "推断类型"], PyClass):
                    self.提取变量表格.loc[index, "翻译变量"] = 翻译变量映射字典[
                                                                   self.提取变量表格.loc[
                                                                       index, "变量名称"]] + 配置.获取配置项("类后缀")
                else:
                    self.提取变量表格.loc[index, "翻译变量"] = 翻译变量映射字典[
                        self.提取变量表格.loc[index, "变量名称"]]

        # 到这里当前所有变量都翻译完成了, 但是这只有一个代码, 我应该将所有的都翻译完成之后, 再去处理
        # 重复值改成如果在改名之前, 发现存在重复, 再去进行重复值处理, 并且将重复值处理结果保存到另外一个配置文件中.
        # 对 变量名称不同, 但是 翻译变量相同的, 就是重复值.如果计算呢?  提取所有翻译变量重复值

    def 处理重复变量(self, 处理表格):
        """传入表格, 处理数据"""
        处理表格 = 处理表格[处理表格.翻译变量 != ""].copy()
        处理表格.reset_index(drop=True, inplace=True)
        表格去重 = 处理表格.drop_duplicates(subset=["变量名称", "翻译变量"])
        表格提取重复数据 = 表格去重[表格去重.duplicated(subset=["翻译变量"], keep=False)]
        重复数据 = 表格提取重复数据.set_index('变量名称')[
            '翻译变量']  # {'Config': '配置目录', 'config': '配置目录', 'plugin_config': '插件配置', 'pconf': '插件配置'}

        # 将重复数据字典传入大模型
        if 重复数据.shape[0] > 0:  # 如果存在重复数据, 那么就应该进行处理, 但是要判断去重变量表里面是否已经有了, 如果有则不需要进行大模型翻译
            # 如果没用, 再使用大模型处理
            # 如果原来有{'plugin_config': '插件配置', 'pconf': '插件配置_'}
            # 现在重复字典中是 {'plugin_config': '插件配置', 'plugin_conf': '插件配置'} 应该把几项都搞出来, 传入大模型中进行处理
            日志.debug("检测到重复项: {}", 重复数据)
            去重变量表: pd.DataFrame = 读取英中重复变量()  # DataFrame格式
            # 找出没有在的, 使用表格之间的交叉关联
            # 这里还有一种可能, 就是完全没有交集, 以前没有过这类词组, 那么这里应该如何处理呢?
            未保存重复变量_英文 = 重复数据.index.difference(去重变量表.index)
            # 未保存重复变量 是英文结果, 代表在当前代码中需要翻译, 但是在原来的重复码表里面没有的 英文单词, 有 config
            # 翻译变量, 这些原来重复码表没有的英文单词对应的中文, 还有 "配置目录" 存在
            翻译变量 = set(重复数据[未保存重复变量_英文].values)
            if 未保存重复变量_英文.shape[0] > 0:  # 这说明和原来的去重变量表是有交集的
                if (未保存重复变量_英文.shape[0] < 重复数据.shape[0]) and sum(去重变量表.翻译变量.isin(翻译变量)) != 0:
                    # 这里是找出未保存的重复变量对应的翻译, 此处有两种可能
                    # 1. 一组重复词语原来在词表中完全没有 command commands都没有
                    # 2. 可能已经有一部分了, 例如 command commands cmd已经有 cmd command了

                    # 找出翻译变量对应的所有英文变量数据, 如果原来完全没有保存过, 那么 提取去重变量 应该为空
                    # 原来的重复码表里面这些, 需要翻译的中文变量中对应的数据, 有可能有一部分已经有了, 没有config, 也没有相同翻译结果单词.
                    提取去重变量 = 去重变量表[去重变量表.翻译变量.isin(翻译变量)]["翻译变量"]

                    # 这步骤有错误, 这个只能过滤那种, 原来已经有一部分的单词, 如果是一个全新的重复单词, 则过滤不出来
                    # 重复数据是全部的重复数据, 这里应该是要合并全部的要大模型翻译的数据, 有哪部分数据是不需要大模型翻译的?
                    重复数据_过滤 = 重复数据[重复数据.isin(翻译变量)]
                    合并表 = pd.concat([提取去重变量, 重复数据_过滤], axis=1)
                    合并表.columns = ['翻译变量', '翻译变量2']
                    合并表.翻译变量 = 合并表.翻译变量.fillna(合并表.翻译变量2)

                    重复变量列表 = 合并表.index.to_list()
                    含有交叉 = True
                else:
                    重复变量列表 = 未保存重复变量_英文.to_list()
                    含有交叉 = False

                去重字典 = 通义千问模型.处理英文重复变量_列表(重复变量列表)
                日志.debug("大模型去重后: {}", 去重字典)

                # 更新回原来的csv中
                for 变量 in 去重字典:
                    if 变量 not in 去重变量表.index:
                        if 含有交叉:
                            去重变量表.loc[变量, "翻译变量"] = 合并表.loc[变量, "翻译变量"]
                        else:
                            去重变量表.loc[变量, "翻译变量"] = 重复数据.loc[变量]
                    去重变量表.loc[变量, "去重变量"] = 去重字典[变量]
                去重变量表.sort_values(["翻译变量"], inplace=True)
                保存英中重复变量(去重变量表)

            for index in 表格提取重复数据.index:
                # 这里要将所有同样的变量, 都改名, 例如config可能有很多个, 要全部添加进去
                处理表格.loc[
                    处理表格.变量名称 == 处理表格.loc[index, "变量名称"], "去重变量"
                ] = 去重变量表.loc[
                    处理表格.loc[index, "变量名称"], "去重变量"]
        return 处理表格

    def 批量替换变量_backup(self):
        """self.提取变量表格, 根据这个进行已翻译"""
        for index in self.提取变量表格.index:
            # 根据当前变量所在文件, 替换资源
            模块, 行号 = self.提取变量表格.loc[index, "变量种类"].get_definition_location()
            # 发现这里行号有可能存在错误, 这里判断module, 如果module不是当前资源, 判断是不是在项目内的模块, 如果不是, 则跳过
            if 模块:
                模块名称 = 模块.get_name()
                # 判断模块是否在项目内, 如果是当前处理的代码
                if 模块名称 != self.我的资源.path.removesuffix(".py").replace("/", "."):  # 不是当前处理模块, 则判断是否内置模块
                    if 模块名称 not in self.导入模块列表 or 模块名称 not in self.导入目录列表:
                        continue
            else:
                continue

            # 如果存在去重变量, 则使用 去重变量, 否则使用 翻译变量
            变量名称 = self.提取变量表格.loc[index, "变量名称"]
            if self.提取变量表格.loc[index, "去重变量"]:
                翻译变量 = self.提取变量表格.loc[index, "去重变量"]
                self.重命名变量(行号, 变量名称, 翻译变量)
            elif self.提取变量表格.loc[index, "翻译变量"]:
                翻译变量 = self.提取变量表格.loc[index, "翻译变量"]
                self.重命名变量(行号, 变量名称, 翻译变量)
        # 充值变量表格为空? 还是要全部保留呢, 不清楚哪个更好, 如果保留的话, 可以监控到所有的
        self.提取变量表格 = pd.DataFrame(
            columns=["监控范围标识", "变量名称", "翻译变量", "去重变量", "变量种类", "推断类型", "变量对象",
                     "变量对象_数据类型"])

    def 批量替换变量(self):
        """self.提取变量表格, 根据这个进行已翻译"""
        总任务数量 = self.提取变量表格.index.shape[0]
        for index in self.提取变量表格.index:
            # 根据当前变量所在文件, 替换资源
            模块, 行号 = self.提取变量表格.loc[index, "变量种类"].get_definition_location()
            # 发现这里行号有可能存在错误, 这里判断module, 如果module不是当前资源, 判断是不是在项目内的模块, 如果不是, 则跳过
            if 模块:
                模块名称 = 模块.get_name()
                变量资源 = self.提取变量表格.loc[index, "变量资源"]
                # 判断模块是否在项目内, 如果是当前处理的代码
                if 模块名称 != 变量资源.path.removesuffix(".py").replace("/", ".") and (
                        模块名称 != 变量资源.path.removesuffix(".py").split("/")[-1]):  # 不是当前处理模块, 则判断是否内置模块
                    if 模块名称 not in self.导入模块列表 or 模块名称 not in self.导入目录列表:
                        continue
            else:
                continue

            # 如果存在去重变量, 则使用 去重变量, 否则使用 翻译变量
            变量名称 = self.提取变量表格.loc[index, "变量名称"]
            if self.提取变量表格.loc[index, "去重变量"]:
                翻译变量 = self.提取变量表格.loc[index, "去重变量"]
            elif self.提取变量表格.loc[index, "翻译变量"]:
                翻译变量 = self.提取变量表格.loc[index, "翻译变量"]
            self.重命名变量(行号, 变量资源, 变量名称, 翻译变量)

            # 计算任务进度
            设置进度值(50 + int(((index + 1) / 总任务数量) * 100 * 0.5))

    def 批量替换导入变量(self):
        """self.提取变量表格, 根据这个进行已翻译
        无法替换成功:
        RecursionError: maximum recursion depth exceeded while calling a Python object"""
        for index in self.提取导入变量表格.index:
            # 对于导入变量, 需要判断行号, 然后搜索从范围监控标识字段中获取文件名称, 然后计算偏移量
            文件路径 = self.提取导入变量表格.loc[index, "监控范围标识"]
            变量资源 = self.提取导入变量表格.loc[index, "变量资源"]
            # 发现这里行号有可能存在错误, 这里判断module, 如果module不是当前资源, 判断是不是在项目内的模块, 如果不是, 则跳过

            # 如果存在去重变量, 则使用 去重变量, 否则使用 翻译变量
            变量名称 = self.提取导入变量表格.loc[index, "变量名称"]
            if self.提取导入变量表格.loc[index, "去重变量"]:
                翻译变量 = self.提取导入变量表格.loc[index, "去重变量"]
            elif self.提取导入变量表格.loc[index, "翻译变量"]:
                翻译变量 = self.提取导入变量表格.loc[index, "翻译变量"]
            self.重命名变量(None, 变量资源, 变量名称, 翻译变量)

    def 批量修改目录名称(self):
        """修改文件名称:
        思路: """
        目录列表 = [目录.split("/")[-1] for 目录 in self.相对目录列表]
        翻译目录映射字典 = 过滤并查询英文变量_V2(目录列表)

        for 目录 in self.相对目录列表:
            目录最后一层 = 目录.split("/")[-1]
            翻译结果 = 翻译目录映射字典.get(目录最后一层)
            if 翻译结果 and 目录 != 翻译结果:
                self.创建资源(目录)
                # 重命名文件
                # 批量获取py文件
                self.重命名变量(None, self.我的资源, 翻译变量=None, 变量翻译结果=翻译结果)
                日志.debug("重命名py文件: {}, 翻译结果: {}", self.我的资源.real_path, 翻译结果)

        self.py文件列表, self.相对文件列表, self.相对目录列表 = 收集项目资源(self.项目路径)

    def 批量修改py文件名称(self):
        """修改文件名称:
        思路: 获取文件有哪些py文件列表存在, 然后进行处理? 对是可以的"""
        py文件_去路径 = [file.split("/")[-1].removesuffix(".py") for file in self.py文件列表]
        翻译py文件映射字典 = 过滤并查询英文变量_V2(py文件_去路径)

        for py文件 in self.py文件列表:

            文件名 = py文件.split("/")[-1].removesuffix(".py")
            if 翻译py文件映射字典.get(文件名):
                self.创建资源(py文件)
                self.获取监控范围()
                # 重命名文件
                # 批量获取py文件
                self.重命名变量(None, self.我的资源, 翻译变量=None, 变量翻译结果=翻译py文件映射字典[文件名])
                日志.debug("重命名py文件: {}, 翻译结果: {}", self.我的资源.real_path, 翻译py文件映射字典[文件名])

        self.py文件列表, self.相对文件列表, self.相对目录列表 = 收集项目资源(self.项目路径)

    def 重命名变量(self, 行号, 变量资源, 翻译变量=None, 变量翻译结果=None, 翻译资源: list = None):
        if not 翻译变量:
            renamer = Rename(self.我的项目, 变量资源)
            change = renamer.get_changes(变量翻译结果)
            self.我的项目.do(change)
        else:
            偏移量 = self.搜索变量偏移量(行号, 翻译变量, 变量资源)
            日志.debug("翻译变量: {} 偏移量: {} ", 翻译变量, 偏移量)
            if 偏移量:
                try:
                    renamer = Rename(self.我的项目, 变量资源, 偏移量)
                    # 获取重命名变更
                    change = renamer.get_changes(变量翻译结果, resources=翻译资源)
                    self.我的项目.do(change)
                except (RefactoringError, BadIdentifierError, RecursionError) as e:
                    日志.error("报错类型: {} 报错信息: {} 翻译变量: {} 行号: {} 偏移量: {} 翻译文件: {}",
                               type(e).__name__, e, 翻译变量, 行号, 偏移量,
                               变量资源.real_path)


class Rope单文件管理器(Rope管理器):
    def __init__(self, 文件路径):
        self.我的资源 = None
        self.监控范围 = None
        self.资源路径 = 文件路径
        self.上层文件夹, self.文件名称 = 文件路径.rsplit("/", maxsplit=1)
        项目路径 = self.上层文件夹

        self.导入模块列表: list = []
        self.导入目录列表: list = []
        self.提取变量表格 = pd.DataFrame(
            columns=["监控范围标识", "变量名称", "翻译变量", "去重变量", "变量种类", "推断类型", "变量对象",
                     "变量对象_数据类型", "变量资源"])
        self.提取导入变量表格 = pd.DataFrame(
            columns=["监控范围标识", "变量名称", "翻译变量", "去重变量", "变量种类", "推断类型", "变量对象",
                     "变量对象_数据类型", "变量资源"])
        self.我的项目 = Project(项目路径)

    def 创建复制资源(self, 类型="file"):
        """ 不管是py文件还是ipynb文件, 都可以成功复制

        这里在翻译过程中要考虑, 如果要翻译的是英文变量, 但文件名称是中文的, 那么就无法获得翻译结果.
        因此这种情况应该重新指定名称, 后面添加后缀 _翻译"""
        文件前缀, 文件后缀 = self.文件名称.rsplit(".", maxsplit=1)
        翻译py文件映射字典 = 过滤并查询英文变量_V2([文件前缀])
        if 翻译py文件映射字典.get(文件前缀):
            翻译文件名称 = 翻译py文件映射字典[文件前缀] + "." + 文件后缀
            翻译文件路径 = self.上层文件夹 + "/" + 翻译文件名称
            shutil.copy(self.资源路径, 翻译文件路径)
            self.我的资源 = libutils.path_to_resource(self.我的项目, 翻译文件路径, 类型)
        else:  # 没翻译到结果, 直接复制一个添加后缀的
            翻译文件路径 = self.上层文件夹 + "/" + 文件前缀 + "_翻译" + "." + 文件后缀
            shutil.copy(self.资源路径, 翻译文件路径)
            self.我的资源 = libutils.path_to_resource(self.我的项目, 翻译文件路径, 类型)


    def 创建资源(self, 资源名称, 类型=None):
        self.我的资源 = libutils.path_to_resource(self.我的项目, 资源名称, 类型)

    def 批量替换变量(self):
        """self.提取变量表格, 根据这个进行已翻译"""
        总任务数量 = self.提取变量表格.index.shape[0]
        for index in self.提取变量表格.index:
            # 根据当前变量所在文件, 替换资源
            模块, 行号 = self.提取变量表格.loc[index, "变量种类"].get_definition_location()
            # 发现这里行号有可能存在错误, 这里判断module, 如果module不是当前资源, 判断是不是在项目内的模块, 如果不是, 则跳过
            if 模块:
                模块名称 = 模块.get_name()
                变量资源 = self.提取变量表格.loc[index, "变量资源"]
                # 判断模块是否在项目内, 如果是当前处理的代码
                if 模块名称 != 变量资源.path.removesuffix(".py").replace("/", ".") and (
                        模块名称 != 变量资源.path.removesuffix(".py").split("/")[-1]):  # 不是当前处理模块, 则判断是否内置模块
                    if 模块名称 not in self.导入模块列表 or 模块名称 not in self.导入目录列表:
                        continue
            else:
                continue

            # 如果存在去重变量, 则使用 去重变量, 否则使用 翻译变量
            变量名称 = self.提取变量表格.loc[index, "变量名称"]
            if self.提取变量表格.loc[index, "去重变量"]:
                翻译变量 = self.提取变量表格.loc[index, "去重变量"]
            elif self.提取变量表格.loc[index, "翻译变量"]:
                翻译变量 = self.提取变量表格.loc[index, "翻译变量"]
            self.重命名变量(行号, 变量资源, 变量名称, 翻译变量, 翻译资源=[变量资源])

            # 计算任务进度
            设置进度值(50 + int(((index + 1) / 总任务数量) * 100 * 0.5))




def 过滤并查询英文变量_V2(英文变量列表):
    """读取已保存变量, 对其中已经保存的变量进行替换
    # 现在是获取到了一个集合, 我需要获取已保存变量, 这是一个字典, 然后
    :param 变量位置, 文件名称, 类名, 函数名, for循环, 等关键字, 根据不同的位置进行不同的处理
    """
    英中映射变量 = 读取英中映射变量()
    # 去重
    英文变量列表 = list(set(英文变量列表))

    def 检查是否含有英文(text):
        # 使用正则表达式查找长度大于等于3的英文单词
        pattern = r'[a-zA-Z]{3,}'
        result = re.search(pattern, text)
        return result is not None

    def 检查是否python英文变量(name):
        # 检查是否是字母或下划线开头
        if not name or not name[0].isalpha() and name[0] != '_':
            return False
        # 检查是否包含非ASCII字符
        if not name.isascii():
            return False
        # 检查剩余字符是否仅由字母、数字或下划线构成
        if not all(c.isalnum() or c == '_' for c in name):
            return False
        return True

    英文变量列表 = [元素 for 元素 in 英文变量列表 if len(元素) > 1
                    and 元素 != "self" and not 元素.startswith(".")
                    and not (元素.startswith("__") and 元素.endswith("__"))
                    and 检查是否python英文变量(元素)]

    # 如果有多个英文变量, 判断其中每一个是否含有英文单词, 如果没有, 则去掉.

    # 有一个集合和一个字典, 现在需要从集合中提取出所有不在字典的key当中的数据
    未保存变量 = [元素 for 元素 in 英文变量列表 if not 英中映射变量.get(元素)]
    # 考虑未保存变量为空的情况, 不需要连接大模型
    if 未保存变量:
        # 如果要翻译的变量超过500个, 则进行切割后分批次翻译
        新变量_字典 = 通义千问模型.翻译英文变量(未保存变量)

        # 发现这里大模型返回的字典有可能存在, 部分传入的变量没有翻译回来, 这里添加一个缺失检测功能
        # 如何检测呢? 未保存变量是我要查询的变量, 新变量_字典 查询这个key里面不存在的 未保存变量 元素
        缺失变量 = [元素 for 元素 in 未保存变量 if not 新变量_字典.get(元素)]

        if 缺失变量:
            日志.debug("查询到缺失变量: {}", 缺失变量)
            缺失变量翻译_字典 = 通义千问模型.翻译英文变量(缺失变量)
            新变量_字典.update(缺失变量翻译_字典)
        新变量_字典.update(英中映射变量)  # 放在后面的是保留的, 历史变量优先级更高

        # 这里遇到 `传入大模型返回JSON`被大模型变成了 `传入大模型返回_json`, 导致翻译缺失key.
        # 考虑这里可能出现大模型没有将传入的英文变量key, 按照原样进行返回, 进行一个检测
        # 如何处理呢? 再次检测是否存在缺失, 如果存在缺失则换成单独翻译添加进去.

        缺失变量 = [元素 for 元素 in 未保存变量 if not 新变量_字典.get(元素)]
        if 缺失变量:
            日志.debug("第二次查询到缺失变量: {}", 缺失变量)
            缺失变量翻译_字典 = 通义千问模型.翻译英文文件名(缺失变量)
            新变量_字典.update(缺失变量翻译_字典)

        # 检测翻译结果是否符合python变量, 如果不符合, 则单独提取出来, 重新让大模型翻译
        过滤_错误变量 = [变量 for 变量 in 新变量_字典 if not 变量.isidentifier()]
        if 过滤_错误变量:
            错误变量_字典 = 通义千问模型.翻译英文文件名(过滤_错误变量)
            新变量_字典.update(错误变量_字典)

        合并后英中变量 = 新变量_字典
    else:
        合并后英中变量 = 英中映射变量

    # 到这里已经翻译完成了, 这里不再进行重复值检测
    # 下一步应该是判断是不是 _类 还是 函数, 然后添加后缀了.

    保存英中变量(合并后英中变量)

    翻译变量映射字典 = {}
    for 翻译变量 in 英文变量列表:
        if 合并后英中变量.get(翻译变量):
            翻译变量映射字典[翻译变量] = 合并后英中变量.get(翻译变量)

    return 翻译变量映射字典


def 读取代码文本(绝对路径):
    with open(绝对路径) as f:
        return f.read()


def 判断子目录(父目录, 子目录):
    # 转换为 Path 对象
    父目录_路径 = Path(父目录).resolve()
    子目录_路径 = Path(子目录).resolve()

    # 使用 .parents 检查 parent_path 是否是 child_path 的父目录
    return 父目录_路径 in 子目录_路径.parents


def 遍历目录和文件列表(开始目录='.', 忽略目录=None):
    """
    列出指定路径下的所有目录和文件，忽略指定的目录。

    :param 开始目录: 起始目录，默认为当前目录。
    :param 忽略目录: 要忽略的目录列表。
    """
    目录列表_收集 = []
    文件列表_收集 = []
    if 忽略目录 is None:
        忽略目录 = ['__pycache__', '.git', '.idea']
    # 遍历目录
    for 目录路径, 目录列表, 文件列表 in os.walk(开始目录):
        # 修改 目录列表，移除忽略的目录，影响 os.walk 的遍历行为
        目录列表[:] = [d for d in 目录列表 if d not in 忽略目录]

        目录列表_收集.append(目录路径)

        # 输出当前目录下的所有文件
        for 文件 in 文件列表:
            文件列表_收集.append(os.path.join(目录路径, 文件))
    return 目录列表_收集, 文件列表_收集


def 收集项目资源(项目_根路径):
    目录列表, 文件列表 = 遍历目录和文件列表(项目_根路径)  # 收集_目录列表 收集_文件列表
    相对目录列表 = [元素.replace(项目_根路径 + "/", "") for 元素 in 目录列表[1:]]  # 去掉根目录
    相对文件列表 = [元素.replace(项目_根路径 + "/", "") for 元素 in 文件列表]
    py文件列表 = [元素 for 元素 in 相对文件列表 if 元素.endswith(".py")]
    return py文件列表, 相对文件列表, 相对目录列表


def 读取中英映射变量():
    # 检查文件是否存在

    # # 获取当前文件的绝对路径
    # current_file_path = os.path.abspath(__file__)
    # # 获取当前文件所在的目录
    # current_directory = os.path.dirname(current_file_path)
    # # 改变工作目录到当前文件所在的目录
    # os.chdir(current_directory)
    # 日志.info("工作目录已改变为: {}", os.getcwd())
    if not os.path.exists(中英映射变量_路径):
        with open(中英映射变量_路径, 'w', encoding='utf-8') as f:
            json.dump({"键": "key", "值": "value", "self": "self"}, f, ensure_ascii=False, indent=4)

    with open(中英映射变量_路径, 'r', encoding='utf-8') as f:
        中英映射变量 = json.load(f)
    return 中英映射变量


def 读取英中映射变量():
    # 检查文件是否存在

    if not os.path.exists(英中映射变量_路径):
        with open(英中映射变量_路径, 'w', encoding='utf-8') as f:
            json.dump({"key": "键", "value": "值", "self": "self"}, f, ensure_ascii=False, indent=4)

    with open(英中映射变量_路径, 'r', encoding='utf-8') as f:
        英中映射变量 = json.load(f)
    return 英中映射变量


def 读取英中重复变量():
    """"""

    if not os.path.exists(英中重复变量_路径):
        去重变量表 = pd.DataFrame(columns=["翻译变量", "去重变量"])
        去重变量表.index = pd.Series(name="变量名称")
        去重变量表.to_csv(英中重复变量_路径, index=True)
    else:
        去重变量表 = pd.read_csv(英中重复变量_路径, index_col=0)
    return 去重变量表


def 保存中英变量(合并后变量):
    """传入的应该是一个完整的字典, 然后将字典的值保存进来? """
    with open(中英映射变量_路径, 'w', encoding='utf-8') as f:
        json.dump(合并后变量, f, ensure_ascii=False, indent=4)


def 保存英中变量(合并后变量):
    """传入的应该是一个完整的字典, 然后将字典的值保存进来? """
    with open(英中映射变量_路径, 'w', encoding='utf-8') as f:
        json.dump(合并后变量, f, ensure_ascii=False, indent=4)


def 保存英中重复变量(重复变量: pd.DataFrame):
    """传入的应该是一个完整的字典, 然后将字典的值保存进来? """
    重复变量.to_csv(英中重复变量_路径, index=True)


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


def 检测字典重复值(输入字典):
    # 找出所有值的列表长度大于1的条目
    重复项 = {}
    for 键, 值 in 输入字典.items():
        if len(值) > 1:
            for i in 值:
                重复项[i] = 键

    return 重复项


def 翻转字典_调转(输入字典):
    """直接将key和value调转, 注意要保证value中没有重复值.
    而且value必须可以作key"""
    翻转字典 = {}
    for 键, 值 in 输入字典.items():
        翻转字典[值] = 键
    return 翻转字典


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


def 替换代码变量_函数(代码文本, 变量映射, 引号=0):
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
    变量匹配模式 = r'\b(' + '|'.join(re.escape(翻译变量) for 翻译变量 in 变量映射.keys()) + r')\b'

    if not 引号:
        # 合并字符串匹配模式和变量匹配模式
        综合匹配模式 = 注释匹配模式 + r'|' + 多行字符串匹配模式 + r'|' + 字符串匹配模式 + r'|' + 变量匹配模式
    else:
        综合匹配模式 = 注释匹配模式 + r'|' + 多行字符串匹配模式 + r'|' + 变量匹配模式

    # 使用 sub 函数进行替换，结合字符串的保护
    代码文本 = re.sub(综合匹配模式, 替换函数, 代码文本, flags=re.DOTALL)

    return 代码文本


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
    替换结果 = re.sub(综合匹配模式, lambda m: '""' + (m.group(2) if m.lastindex == 2 else ''), 代码文本,
                      flags=re.DOTALL)

    return 替换结果


def 删除单行代码注释和字符串(代码文本):
    注释匹配模式 = r'(#.*)'
    字符串匹配模式 = r'(\"\"\".*\"\"\"|\'\'\'.*\'\'\'|\".*\"|\'.*\')'
    综合匹配模式 = 字符串匹配模式 + r'|' + 注释匹配模式
    替换结果 = re.sub(综合匹配模式, "''", 代码文本)
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


def 提取导入变量_通用(代码文本):
    """提取所有import 变量和 from xxx import xxx"""

    变量列表_key = dict()
    变量_as = []
    关联文件_列表 = []
    for 一行 in 代码文本.split("\n"):
        一行 = 一行.lstrip()
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
                    # 这里出现bug, pandas as pd 中  前边也有 as 字符

                    变量列表_key[一个.split(" as ")[0].strip()] = []
                    关联文件_列表.append(一个.split(" as ")[0].strip())
                    变量_as.append(一个.split(" as ")[-1].strip())

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
                if 一个.find(" as ") < 0:  # 没有as, 直接保存
                    变量列表_key[import_前面变量].append(一个.strip())

                    关联文件_列表.append(一个.strip())
                else:  # 有as, 提取后面部分
                    变量列表_key[import_前面变量].append(一个.split(" as ")[0].strip())

                    变量_as.append(一个.split(" as ")[-1].strip())
                    关联文件_列表.append(一个.split(" as ")[0].strip())

    return 变量列表_key, 变量_as


def 提取导入变量_行号(代码文本):
    """提取所有import 变量和 from xxx import xxx
    对提取出的每个变量记录行号, 以及位置.
    就和Rope的那个一样, 这样可以精准的定位.

    首先思考一下用什么格式保存数据, 还是DataFrame吧.
    """
    导入变量表格 = pd.DataFrame(
        columns=["行号", "from变量", "from拆分", "import变量", "import拆分", "import变量翻译", "import位置",
                 "as变量", "as变量翻译", "as位置", "项目内部标识", "包含中文", "关联文件"])
    导入变量表格["import变量翻译"] = 导入变量表格["import变量翻译"].astype(object)

    for 索引, 一行 in enumerate(代码文本.split("\n")):
        行号 = 索引 + 1
        一行_去空 = 一行.lstrip()  # 去掉前边空格
        # 判断这行是不是以import 开头的
        if 一行_去空.startswith("import "):
            # 如果是以import 开头的, 分成四种情况,
            """import 张三
                import 宋六, 李四
                import 王五, sunqi as 孙七
                import pandas as 数据处理
                import re as 正则表达式, os as 文件管理包
                import plugins.banwords.banwords
                import plugins.banwords.banwords as bb
                """
            # 凡是有from的一定是有import 的, 需要的是import后面的内容, 前边from ... import 去掉
            import_后面文本 = 一行_去空.split("import ")[-1]
            import_后面文本_切分 = import_后面文本.split(",")
            for 一个 in import_后面文本_切分:
                if 一个.find("as") < 0:  # 没有as, 这个需要单独添加到一个队列当中去, 后续判断是否中文
                    import拆分 = []
                    if 一个.find(".") > 0:
                        import拆分 = 一个.split(".")
                    导入变量表格.loc[len(导入变量表格)] = {
                        "行号": 行号,
                        "from变量": "",
                        "from拆分": [],
                        "import变量": 一个.strip(),
                        "import拆分": import拆分,
                        "import变量翻译": [],
                        "import位置": 一行.index(一个.strip()),
                        "as变量": "",
                        "as位置": -1
                    }
                else:  # 有as, 提取后面部分
                    # 这里我假设有这种 import 通义千问大模型 as 通义, 两个都是中文, 完全有可能
                    # 这里出现bug, pandas as pd 中  前边也有 as 字符
                    import拆分 = []
                    if 一个.find(".") > 0:
                        import拆分 = 一个.split(" as ")[0].strip().split(".")
                    导入变量表格.loc[len(导入变量表格)] = {
                        "行号": 行号,
                        "from变量": "",
                        "from拆分": [],
                        "import变量": 一个.split(" as ")[0].strip(),
                        "import拆分": import拆分,
                        "import变量翻译": [],
                        "import位置": 一行.index(一个.split(" as ")[0].strip()),
                        "as变量": 一个.split(" as ")[-1].strip(),
                        "as位置": 一行.index(一个.split(" as ")[-1].strip())
                    }

        """from numpy import 测试1
            from numpy import ndarray as 测试1
            from datetime import 测试3, date as 测试4
            from datetime import datetime as 测试5, date as 测试6"""
        if 一行_去空.startswith("from "):
            # 提取from后面的变量
            from变量 = 一行_去空.split("import ")[0].strip("from").strip()
            # 凡是有from的一定是有import 的, 需要的是import后面的内容, 前边from ... import 去掉
            from拆分_列表 = []
            for i in from变量.split("."):
                from拆分_列表.append([i, "", 行号, 一行.index(i)])

            import_后面文本 = 一行_去空.split("import ")[-1]
            import_后面文本_切分 = import_后面文本.split(",")
            for 一个 in import_后面文本_切分:
                if 一个.find(" as ") < 0:  # 没有as, 直接保存
                    import拆分 = []
                    if 一个.find(".") > 0:
                        import拆分 = 一个.split(".")
                    导入变量表格.loc[len(导入变量表格)] = {
                        "行号": 行号,
                        "from变量": from变量,
                        "from拆分": from拆分_列表,
                        "import变量": 一个.strip(),
                        "import拆分": import拆分,
                        "import变量翻译": [],
                        "import位置": 一行.index(一个.strip()),
                        "as变量": "",
                        "as位置": -1
                    }

                else:  # 有as, 提取后面部分
                    import拆分 = []
                    if 一个.find(".") > 0:
                        import拆分 = 一个.split(" as ")[0].strip().split(".")
                    导入变量表格.loc[len(导入变量表格)] = {
                        "行号": 行号,
                        "from变量": from变量,
                        "from拆分": from拆分_列表,
                        "import变量": 一个.split(" as ")[0].strip(),
                        "import拆分": import拆分,
                        "import变量翻译": [],
                        "import位置": 一行.index(一个.strip()),
                        "as变量": 一个.split(" as ")[-1].strip(),
                        "as位置": 一行.index(一个.split(" as ")[-1].strip()),
                    }
    return 导入变量表格


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


def 检查变量字典错误():
    英中映射变量 = 读取英中映射变量()
    import keyword
    for 变量 in 英中映射变量:
        if not 英中映射变量[变量].isidentifier() or keyword.iskeyword(英中映射变量[变量]):
            日志.error("变量: {}, 映射变量: {}", 变量, 英中映射变量[变量])



def ipynb转换成py(notebook):
    py_code = ""
    for cell in notebook['cells']:
        if cell['cell_type'] == 'code':
            # 将代码转换成字符串
            code = ''.join(cell['source'])

            # 检测并处理魔法命令
            code_lines = code.splitlines()
            for line in code_lines:
                if re.match(r'^\s*%', line):  # 如果该行是魔法命令
                    # 将魔法命令转换为注释，或者可以选择跳过这一行
                    py_code += '# ' + line + '\n'
                else:
                    py_code += line + '\n'

        elif cell['cell_type'] == 'markdown':
            # 将 Markdown 内容转换为注释
            comments = ''.join(cell['source'])
            comment_lines = comments.splitlines()
            for line in comment_lines:
                py_code += '# ' + line + '\n'

    return py_code

def 提取jupyter代码(notebook: dict):
    """只提取jupyter代码部分, 在每个cell中间添加区分符号, 可以还原回原来的code当中
    :arg notebook: ipynb读取的json, 转换成dict
    :return py_code: 提取出的代码, 用户传入rope提取变量和翻译"""
    py_code = ""
    for cell in notebook['cells']:
        if cell['cell_type'] == 'code':

            # 将代码转换成字符串
            code = ''.join(cell['source'])
            if code:
                # 检测并处理魔法命令
                code_lines = code.splitlines()
                for line in code_lines:
                    if re.match(r'^\s*%', line):  # 如果该行是魔法命令
                        # 将魔法命令转换为注释，或者可以选择跳过这一行
                        py_code += '# ' + line + '\n'
                    else:
                        py_code += line + '\n'
            py_code += "# Ú" + "\n"
    return py_code


def 替换jupyter代码(notebook, 代码文本):
    # 将 代码文本 处理回去
    id_cell = 0
    py_code_split_cell = 代码文本.split("# Ú\n")
    for cell in notebook['cells']:
        if cell['cell_type'] == 'code':
            # 将py_code处理回去
            cell_code = py_code_split_cell[id_cell].removesuffix("\n").splitlines(keepends=True)
            cell['source'] = cell_code
            id_cell += 1


if __name__ == '__main__':
    检查变量字典错误()