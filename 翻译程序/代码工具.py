import os


def 判断子目录(子目录路径, 父目录路径):
    # 获取绝对路径并规范化路径
    子目录路径 = os.path.abspath(子目录路径)
    父目录路径 = os.path.abspath(父目录路径)

    # 获取公共路径
    公共路径 = os.path.commonpath([子目录路径, 父目录路径])

    # 判断公共路径是否等于父目录路径
    return 公共路径 == 父目录路径


if __name__ == '__main__':

    # 示例
    父目录路径 = "/home/user/documents/test"
    子目录路径 = "/home/user/documents/projects"
    print(判断子目录(父目录路径, 子目录路径))  # 输出: True