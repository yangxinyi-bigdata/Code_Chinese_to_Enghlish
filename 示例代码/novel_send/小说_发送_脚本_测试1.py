import re
import os
import smtplib
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import datetime
import time
import random

# 获取当前代码文件的绝对路径
当前_文件_路径 = os.path.abspath(__file__)
# 获取该路径的目录部分
当前_文件 = os.path.dirname(当前_文件_路径)

# 将工作目录切换到代码所在目录
os.chdir(当前_文件)

# 打印当前工作目录（确认更改）
print("当前工作目录：", os.getcwd())
# 思路, 设置几个类呢?
# 第一个 小说处理类
# 第二个 邮件发送类

class 小说处理器_类:
    def __init__(self, 小说名称, 输入文件_路径, 输出文件_路径):
        self.小说内容 = None
        self.章节正则匹配模式 = None
        self.小说名称 = 小说名称
        if not os.path.exists(输出文件_路径):
            os.mkdir(输出文件_路径)
        self.输入文件_路径 = 输入文件_路径
        self.输出文件_路径 = 输出文件_路径

    def 读取小说内容(self):
        # 第一次的时候执行, 后面不执行
        self.章节正则匹配模式 = r'(第\s*(\d+|[零一二两三四五六七八九十百千万]+)\s*章\s*.*)'
        with open(self.输入文件_路径, "r", encoding="utf8") as 文件:
            # 按行模式读取整本小说内容
            self.小说内容_按行切分 = 文件.readlines()

    def 切割文本_按照章节(self):
        """第一次执行, 后面不执行"""
        self.读取小说内容()
        计数 = 0
        章节数 = 0
        一章内容列表 = []
        一章节内容 = ""
        上一章节名称 = "前言"
        下一章节名称 = ""
        self.章节名称列表 = []
        for 每行 in self.小说内容_按行切分:
            当前行 = 每行.strip()
            # 判断这行符不符合标准 第XX章
            匹配结果 = re.search(self.章节正则匹配模式, 当前行)
            if (len(当前行) <= 30) and 匹配结果:
                # 找到一个新的章节的内容, 说明上一章节结束
                # 添加到总的列表当中content_list
                一章内容列表.append(一章节内容)

                if 上一章节名称 == "前言":  # 刚开始
                    # 保存上一个章节的名称
                    上一章节名称 = 当前行
                else:
                    上一章节名称 = 下一章节名称

                # 当找到新的章节的时候, 记录下来这个章节名称叫做
                下一章节名称 = 当前行
                with open(self.输出文件_路径 + "/" + f"{章节数:03}" + 上一章节名称 + ".txt", "w") as 文件:
                    文件.write(一章节内容)
                self.章节名称列表.append(f"{章节数:03}" + 上一章节名称 + ".txt" + "\n")
                # 清空一章节内容, 重新添加
                一章节内容 = ""
                章节数 += 1
            # else: # 这个分支代表不是章节标题
            #     one_content += line
            一章节内容 += 当前行 + "\n"
            计数 += 1
        with open("./章节名称列表.txt", "w") as 文件:
            文件.writelines(self.章节名称列表)


    """这个函数的功能, 应该是这样的: 每天定时执行一次, 每次执行都继续上一次的结果, 然后生成当天的章节内容.
    而不是一口气全部生成完成.
    那么如果记录昨天发送到哪里呢? 应该是设置一个文件夹, confg.ini文件, 然后将一个记录保存到配置中.
    每次读取, 然后继续
    """

    def 合并当天章节(self, 合并章节数量):
        """更新函数功能:
        改成每次合并的内容, 包含昨天的上一章节内容.
        思路: """
        # 读取config.ini文件
        with open("config.ini") as 文件:
            已经阅读章节数量 = int(文件.read())  # 已经读到哪章
        合并后章节保存路径 = f"./{合并章节数量}章合并"
        if not os.path.exists(合并后章节保存路径):
            os.mkdir(合并后章节保存路径)
        # 获取这几章内容文本
        with open("./章节名称列表.txt") as 文件:
            章节名称列表 = 文件.readlines()
        今天章节名称列表 = 章节名称列表[(已经阅读章节数量-1):(已经阅读章节数量 + 合并章节数量)]
        # 读取章节的名称
        今天所有内容 = ""
        # 对每个章节进行遍历, 然后合并成一个文本
        for 一章 in 今天章节名称列表:
            一章 = 一章.strip()  # 去掉章节两侧空格
            with open(self.输出文件_路径 + "/" + 一章) as 文件:
                一章内容 = 文件.read()
                今天所有内容 += 一章内容
                今天所有内容 += "\n"
        合并后文件名称 = 合并后章节保存路径 + "/" + f"{已经阅读章节数量:03}_{self.小说名称}.txt"
        with open(合并后文件名称, "w") as 文件:
            文件.write(今天所有内容)
        # 保存config.ini
        with open("config.ini", "w") as 文件:
            保存数据 = str(已经阅读章节数量 + 合并章节数量)
            文件.write(保存数据)
        return 合并后文件名称


class QQ邮箱发送_类:
    def __init__(self, 发送邮箱, 邮箱密码, 接收邮箱):
        self.消息 = None
        self.发送邮箱 = 发送邮箱
        self.邮箱密码 = 邮箱密码
        self.接收邮箱 = 接收邮箱

    def 创建邮箱消息(self, 邮件标题, 邮件正文, 发送小说文件):
        # 创建多部分的消息
        self.消息 = MIMEMultipart()
        self.消息['From'] = self.发送邮箱
        self.消息['To'] = self.接收邮箱
        self.消息['Subject'] = 邮件标题

        # 邮件正文内容
        self.消息.attach(MIMEText(邮件正文, 'plain'))

        # 附件文件路径
        发送文件 = 发送小说文件.split("/")[-1]
        附件 = open(发送小说文件, "rb")

        # 实例化 MIMEBase 并将文件内容加入
        邮件本体 = MIMEBase('application', 'octet-stream')
        邮件本体.set_payload(附件.read())

        邮件本体['Content-Type'] = 'application/octet-stream'
        # 正确设置附件的头部，并确保文件名被双引号包围
        邮件本体.add_header('Content-Disposition', 'attachment', filename=Header(发送文件, 'utf-8').encode())

        encoders.encode_base64(邮件本体)
        # 关闭文件
        附件.close()

        # 将附件添加到邮件消息体中
        self.消息.attach(邮件本体)

    def 发送邮件(self, 已读章节数量):
        # 获取当前的日期和时间
        当前时间 = datetime.datetime.now()
        字符串格式时间 = 当前时间.strftime("%Y-%m-%d" "%H:%M:%S")
        # 使用SSL发送邮件
        try:
            with smtplib.SMTP_SSL("smtp.qq.com", 465) as 邮件服务:
                邮件服务.login(self.发送邮箱, self.邮箱密码)
                邮件服务.sendmail(self.发送邮箱, self.接收邮箱, self.消息.as_string())
                return f"发送章节数{已读章节数量}章, 邮件成功发送！发送时间:{字符串格式时间}"
        except Exception as 异常报告:
            return f"邮件发送失败 {异常报告}：发送时间:{字符串格式时间}"


def 随机延迟时间(秒数, 开始时间小时, 结束时间小时):
    当前时间 = datetime.datetime.now()
    开始时间 = datetime.datetime(当前时间.year, 当前时间.month, 当前时间.day, 开始时间小时, 0, 0)
    结束时间 = datetime.datetime(当前时间.year, 当前时间.month, 当前时间.day, 结束时间小时, 0, 0)
    # 生成随机时间
    随机时间 = 开始时间 + datetime.timedelta(seconds=random.randint(0, 秒数))
    # 计算当前时间与随机时间的差异（以秒为单位）
    延迟 = (随机时间 - 当前时间).total_seconds()
    # 如果当前时间早于随机时间，则等待
    if 延迟 > 0:
        time.sleep(延迟)

def 随机延迟_按秒配置(最大秒数):
    # 计算今天的 20:00 和 21:00
    # 如果当前时间早于随机时间，则等待
    随机秒数 = random.randint(0, 最大秒数)
    time.sleep(随机秒数)

if __name__ == '__main__':
    # 从21点开始, 延迟3600秒以内随机
    # random_sleep(3600, 21, 22)
    # random_sleep_seconds(3600)
    小说处理器 = 小说处理器_类("宿命之环", 输入文件_路径="./原文件/宿命之环.txt",
                               输出文件_路径="./处理后")
    if not os.path.exists("config.ini"):
        # 第一次执行, 没有配置文件, 运行获取文本内容代码
        with open("config.ini", "w") as 文件:
            文件.write("0")
    with open("config.ini") as 文件:
        已读章节数量 = int(文件.read())
    if 已读章节数量 == 0:  # 没有切割过
        小说处理器.切割文本_按照章节()

    # 合并当天6章内容, 并返回合并文件路径
    合并文件名称 = 小说处理器.合并当天章节(6)

    # 发送邮件
    QQ邮箱发送 = QQ邮箱发送_类(发送邮箱="yangyuehaha@qq.com",
                                邮箱密码="yunkrcylslptcada",   # 使用QQ邮箱提供的授权码，而不是你的QQ密码,
            接收邮箱="yangyuegaga@qq.com")  # "yangyuehaha_kindle@kindle.cn"
    QQ邮箱发送.创建邮箱消息("小说发送", 邮件正文="发送", 发送小说文件=合并文件名称)

    最终结果 = QQ邮箱发送.发送邮件(已读章节数量)
    print(最终结果)












