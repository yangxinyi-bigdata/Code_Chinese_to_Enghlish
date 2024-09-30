# encoding:utf-8

import os
from loguru import logger as 日志
from configparser import ConfigParser


class 配置_类:
    """配置文件读取
    config = Config()
    config.basedirectory"""

    def __init__(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        配置文件 = os.path.join(dir_path, "配置.ini")
        # 配置文件 = "配置.ini"
        # 创建一个 ConfigParser 实例，保留原始大小写
        config = ConfigParser(interpolation=None)
        config.read(配置文件, encoding="utf-8")

        config.optionxform = str  # 使用 str 函数而不是默认的 str.lower
        self.config = config

    def 获取配置项(self, 名称):
        if self.config.has_option("默认配置", 名称):
            return self.config.get('默认配置', 名称)


配置 = 配置_类()


def 载入配置():
    return 配置


if __name__ == '__main__':
    配置 = 载入配置()
    print(配置.config.sections())