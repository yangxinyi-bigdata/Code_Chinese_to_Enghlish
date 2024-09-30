import subprocess

class Git管理:
    def __init__(self, 项目_根路径):
        self.项目_根路径 = 项目_根路径

    # 初始化 git 仓库（如果没有初始化）
    def 初始化仓库(self):
        try:
            subprocess.run(["git", "-C", self.项目_根路径, "rev-parse", "--is-inside-work-tree"], check=True)
            print("已经是一个 Git 仓库.")
        except subprocess.CalledProcessError:
            print("不是一个 Git 仓库，正在初始化...")
            subprocess.run(["git", "-C", self.项目_根路径, "init"], check=True)

    # 添加所有文件到暂存区
    def 添加所有文件到git(self):
        subprocess.run(["git", "-C", self.项目_根路径, "add", "."], check=True)
        print("所有文件已添加到暂存区.")

    # 提交文件
    def 提交文件(self, 提交消息):
        subprocess.run(["git", "-C", self.项目_根路径, "commit", "-m", 提交消息], check=True)
        print(f"提交完成，提交信息: {提交消息}")
