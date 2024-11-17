from flask import Flask
from flask import (request)
from 工具包 import restful
from 翻译程序.中文项目翻译 import 开始翻译_中文项目
from 翻译程序.英文项目翻译 import 开始翻译_英文项目, 开始翻译_英文文件, 开始翻译_jupyter英文文件翻译
from 通用 import 跨域访问
from threading import Thread
from 翻译程序.通用处理 import 获取进度值, 获取状态值
import sys

app = Flask(__name__)

# 替换现有的CORS配置

跨域访问.init_app(app, resources={r"/*": {"origins": "*"}})

@app.post("/开始翻译_中文项目")
def 翻译中文项目_视图():
    """那边应该是传过来两个路径, 原路径和翻译路径."""
    项目路径 = request.form.get("项目路径")
    翻译路径 = request.form.get("翻译路径")
    任务 = Thread(target=开始翻译_中文项目, args=(项目路径, 翻译路径))
    print(项目路径, 翻译路径)
    任务.start()
    return restful.ok()  # 返回任务ID


@app.post("/开始翻译_英文项目")
def 翻译英文项目_视图():
    """那边应该是传过来两个路径, 原路径和翻译路径."""
    项目路径 = request.form.get("项目路径")
    翻译路径 = request.form.get("翻译路径")
    任务 = Thread(target=开始翻译_英文项目, args=(项目路径, 翻译路径))
    print(项目路径, 翻译路径)
    任务.start()
    return restful.ok()  # 返回任务ID


@app.post("/开始翻译_英文文件")
def 翻译英文文件_视图():
    """那边应该是传过来两个路径, 原路径和翻译路径.
    一个接口对应两个"""
    文件路径 = request.form.get("文件路径")
    if 文件路径.endswith(".py"):
        任务 = Thread(target=开始翻译_英文文件, args=(文件路径, ))
        任务.start()
    elif 文件路径.endswith(".ipynb"):
        任务 = Thread(target=开始翻译_jupyter英文文件翻译, args=(文件路径,))
        任务.start()
    return restful.ok()  # 返回任务ID


@app.get("/停止翻译_英文项目")
def 停止翻译英文项目_视图():
    """那边应该是传过来两个路径, 原路径和翻译路径."""
    return restful.ok()  # 返回任务ID

@app.get("/停止翻译_中文项目")
def 停止翻译中文项目_视图():
    """那边应该是传过来两个路径, 原路径和翻译路径."""
    return restful.ok()  # 返回任务ID

@app.route("/获取进度", methods=['GET'])
def 获取进度():
    任务进度 = 获取进度值()
    print(任务进度)
    return restful.ok(data={'任务进度': 任务进度})


@app.route("/获取状态信息", methods=['GET'])
def 获取状态():
    状态信息 = 获取状态值()
    print(状态信息)
    return restful.ok(data={'状态信息': 状态信息})


if __name__ == '__main__':
    # app.run(debug=True, port=5001)
    if getattr(sys, 'frozen', False):
        # 应用程序被打包
        app.run(debug=False, use_reloader=False, port=5002)
    else:
        # 开发环境
        app.run(debug=True, port=5124)



