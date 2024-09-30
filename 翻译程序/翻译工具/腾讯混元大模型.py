from openai import OpenAI
import json
import os
from loguru import logger as 日志
import requests
import uuid
import os


def get_session():
    # 生成一个 UUID
    new_uuid = uuid.uuid4()
    # 将 UUID 转换为字符串
    session_id = str(new_uuid)
    return session_id

session_id = get_session()

bot_app_key = "SNKXzhfT"  # 机器人密钥，不是BotBizId (从运营接口人处获取)
visitor_biz_id = "yangxinyi"  # 访客 ID（外部系统提供，需确认不同的访客使用不同的 ID）
streaming_throttle = 0  # 节流控制

req_data = {
    "content": "",
    "bot_app_key": bot_app_key,
    "visitor_biz_id": visitor_biz_id,
    "session_id": session_id,
    "streaming_throttle": streaming_throttle
}

content = "你是谁, 你会什么?"

req_data["content"] = content
resp = requests.post("https://wss.lke.cloud.tencent.com/v1/qbot/chat/sse", data=json.dumps(req_data),
                                 stream=True, headers={"Accept": "text/event-stream"})
resp.encoding = "utf-8"
print(f"resp:{resp.text}")

for i in resp.text.split("\n\n"):
    print(i)
    print("----")





