
def 绝对值(*args, **kwargs):
    """ Return the absolute value of the argument. """
    return abs(*args, **kwargs)


# 二进制 = bin

def 二进制(*args, **kwargs):
    """返回一个整数的二进制结果
>>> bin(2796202)
'0b1010101010101010101010'"""
    return bin(*args, **kwargs)


def 打印(*args, 分隔符=' ', 结尾='\n', 文件=None):
    """
将值打印到一个流，默认打印到系统标准输出:  sys.stdout。

  分隔符
    插入在值之间的字符串，默认为一个空格。
  结尾
    附加在最后一个值之后的字符串，默认为一个换行符。
  文件
    一个类似文件的对象（流）；默认为当前的 sys.stdout。
  flush
    是否强制刷新流。
    """
    return print(*args, sep=分隔符, end=结尾, file=文件)


def 输出(*args, 分隔符=' ', 结尾='\n', 文件=None):
    """
将值打印到一个流，默认打印到系统标准输出:  sys.stdout。

  分隔符
    插入在值之间的字符串，默认为一个空格。
  结尾
    附加在最后一个值之后的字符串，默认为一个换行符。
  文件
    一个类似文件的对象（流）；默认为当前的 sys.stdout。
  flush
    是否强制刷新流。
    """
    return print(*args, sep=分隔符, end=结尾, file=文件)