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
current_file_path = os.path.abspath(__file__)
# 获取该路径的目录部分
current_dir = os.path.dirname(current_file_path)
# 将工作目录切换到代码所在目录
os.chdir(current_dir)

# 打印当前工作目录（确认更改）
print("当前工作目录：", os.getcwd())
# 思路, 设置几个类呢?
# 第一个 小说处理类
# 第二个 邮件发送类

class NovelHandle:
    def __init__(self, noval_name, input_file_path, output_dir):
        self.noval_name = noval_name
        self.input_file_path = input_file_path
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        self.output_dir = output_dir

    def read_noval_content(self):
        # 第一次的时候执行, 后面不执行
        self.chapter_pattern = r'(第\s*(\d+|[零一二两三四五六七八九十百千万]+)\s*章\s*.*)'
        with open(self.input_file_path, "r", encoding="utf8") as f:
            self.novel_content_lines = f.readlines()

    def cut_by_chapter(self):
        """第一次执行, 后面不执行"""
        self.read_noval_content()

        n = 0
        chapter_num = 0
        content_list = []
        one_content = ""
        last_chapter_name = "前言"
        self.chapter_name_list = []
        for line in self.novel_content_lines:
            line_strip = line.strip()
            line_chapter_name = line.lstrip()
            # 判断这行符不符合标准 第XX章
            r = re.search(self.chapter_pattern, line_strip)
            if (len(line_strip) <= 30) and r:
                # 找到一个新的章节的内容, 说明上一章节结束
                # 添加到总的列表当中content_list
                content_list.append(one_content)

                if last_chapter_name == "前言":  # 刚开始
                    # 保存上一个章节的名称
                    last_chapter_name = line_strip
                else:
                    last_chapter_name = next_chapter_name

                # 当找到新的章节的时候, 记录下来这个章节名称叫做
                next_chapter_name = line_strip

                # 将 one_content 保存到硬盘中
                with open(self.output_dir + "/" + f"{chapter_num:03}" + last_chapter_name + ".txt", "w") as f:
                    f.write(one_content)
                self.chapter_name_list.append(f"{chapter_num:03}" + last_chapter_name + ".txt" + "\n")
                # 清空one_content, 重新添加
                one_content = ""
                chapter_num += 1

            # else: # 这个分支代表不是章节标题
            #     one_content += line
            one_content += line_strip + "\n"
            n += 1
        with open("./chapter_name_list.txt", "w") as f:
            f.writelines(self.chapter_name_list)

    """这个函数的功能, 应该是这样的: 每天定时执行一次, 每次执行都继续上一次的结果, 然后生成当天的章节内容.
    而不是一口气全部生成完成.
    那么如果记录昨天发送到哪里呢? 应该是设置一个文件夹, confg.ini文件, 然后将一个记录保存到配置中.
    每次读取, 然后继续
    """

    def merge_some_chapters(self, merge_chapter_nums):
        """更新函数功能:
        改成每次合并的内容, 包含昨天的上一章节内容.
        思路: """
        # 读取config.ini文件
        with open("config.ini") as f:
            chapter_has_read_num = int(f.read()) # chapter_has_read_num 已经读到哪章
        chapter_merge_save_path = f"./{merge_chapter_nums}章合并"
        if not os.path.exists(chapter_merge_save_path):
            os.mkdir(chapter_merge_save_path)
        # 获取这几章内容文本
        with open("./chapter_name_list.txt") as f:
            chapter_name_list = f.readlines()
        today_content_chapter_name = chapter_name_list[(chapter_has_read_num-1):(chapter_has_read_num + merge_chapter_nums)]
        # 读取章节的名称
        today_all_content = ""
        # 对每个章节进行遍历, 然后合并成一个文本
        for one in today_content_chapter_name:
            one = one.strip()  # 去掉章节两侧空格
            with open(self.output_dir + "/" + one) as f:
                one_content = f.read()
                today_all_content += one_content
                today_all_content += "\n"
        save_merge_file_name = chapter_merge_save_path + "/" + f"{chapter_has_read_num:03}_{self.noval_name}.txt"
        with open(save_merge_file_name, "w") as f:
            f.write(today_all_content)
        # 保存config.ini
        with open("config.ini", "w") as f:
            save_data = str(chapter_has_read_num + merge_chapter_nums)
            f.write(save_data)
        return save_merge_file_name


class QQEmailSend:
    def __init__(self, sender_email, password, receiver_email):
        self.sender_email = sender_email
        self.password = password
        self.receiver_email = receiver_email

    def create_message(self, email_title, body, filename):
        # 创建多部分的消息
        self.message = MIMEMultipart()
        self.message['From'] = self.sender_email
        self.message['To'] = self.receiver_email
        self.message['Subject'] = email_title

        # 邮件正文内容
        self.message.attach(MIMEText(body, 'plain'))

        # 附件文件路径
        filename = filename  # 替换为你的附件文件路径
        send_filename = filename.split("/")[-1]
        attachment = open(filename, "rb")

        # 实例化 MIMEBase 并将文件内容加入
        part = MIMEBase('application', 'octet-stream')
        part.set_payload((attachment).read())

        part['Content-Type'] = 'application/octet-stream'
        # 正确设置附件的头部，并确保文件名被双引号包围
        part.add_header('Content-Disposition', 'attachment', filename=Header(send_filename, 'utf-8').encode())

        encoders.encode_base64(part)
        # 关闭文件
        attachment.close()

        # 将附件添加到邮件消息体中
        self.message.attach(part)

    def send_email(self, chapter_has_read_num):
        # 获取当前的日期和时间
        current_time = datetime.datetime.now()
        gettime = current_time.strftime("%Y-%m-%d" "%H:%M:%S")
        # 使用SSL发送邮件
        try:
            with smtplib.SMTP_SSL("smtp.qq.com", 465) as server:
                server.login(self.sender_email, self.password)
                server.sendmail(self.sender_email, self.receiver_email, self.message.as_string())
                return f"发送章节数{chapter_has_read_num}章, 邮件成功发送！发送时间:{gettime}"
        except Exception as e:
            return f"邮件发送失败 {e}：发送时间:{gettime}"

def random_sleep(seconds, start_time_hour, end_time_hour):
    # 计算今天的 20:00 和 21:00
    now = datetime.datetime.now()
    start_time = datetime.datetime(now.year, now.month, now.day, start_time_hour, 0, 0)
    end_time = datetime.datetime(now.year, now.month, now.day, end_time_hour, 0, 0)
    # 生成随机时间
    random_time = start_time + datetime.timedelta(seconds=random.randint(0, seconds))
    # 计算当前时间与随机时间的差异（以秒为单位）
    delay = (random_time - now).total_seconds()
    # 如果当前时间早于随机时间，则等待
    if delay > 0:
        time.sleep(delay)

def random_sleep_seconds(seconds):
    # 计算今天的 20:00 和 21:00
    # 如果当前时间早于随机时间，则等待
    random_seconds = random.randint(0, seconds)
    time.sleep(random_seconds)

if __name__ == '__main__':
    # 从21点开始, 延迟3600秒以内随机
    # random_sleep(3600, 21, 22)
    # random_sleep_seconds(3600)
    novel_handle = NovelHandle("末世大回炉", input_file_path="./原文件/末世大回炉.txt",
                               output_dir="./处理后")
    if not os.path.exists("config.ini"):
        # 第一次执行, 没有配置文件, 运行获取文本内容代码
        with open("config.ini", "w") as f:
            f.write("0")
    with open("config.ini") as f:
        chapter_has_read_num = int(f.read())
    if chapter_has_read_num == 0:  # 没有切割过
        novel_handle.cut_by_chapter()

    # 合并当天6章内容, 并返回合并文件路径
    save_merge_file_name = novel_handle.merge_some_chapters(10)

    # 发送邮件
    qq_email_send = QQEmailSend(sender_email = "yangyuehaha@qq.com",
                                password = "yunkrcylslptcada",   # 使用QQ邮箱提供的授权码，而不是你的QQ密码,
            receiver_email = "yangyuehaha_kindle@kindle.cn") # "yangyuehaha_kindle@kindle.cn"
    qq_email_send.create_message("小说发送", body="发送", filename=save_merge_file_name)


    result = qq_email_send.send_email(chapter_has_read_num)
    print(result)



# 测试












