from requests import *
from nonebot import require
from nonebot.adapters import Bot, Event
import re
require("nonebot_plugin_alconna")
from nonebot_plugin_alconna import Image as acnImage, UniMessage
from nonebot_plugin_alconna.uniseg import reply_fetch
import httpx
import io
from nonebot.params import Depends
from PIL import Image as pilImage

# 用于组合需要发送给Ollama进行处理的元素
def getParameters(isGroup, plugin_config, messages_group, index, messages_private):
    if(isGroup):
        return {
            "model": plugin_config.model,
            "messages": messages_group[index],
            "stream": False
        }
    else:
        return {
            "model": plugin_config.model,
            "messages": messages_private[index],
            "stream": False
        }

# 删除消息本身所包含的命令前缀
def msgPurify(msg, cmd):
    for i in range(len(cmd)):
        msg = msg.replace(cmd[i], "", 1)
        break
    return msg

# 检查发送消息的对方（群聊）是否在白名单内 若是则返回其索引
def getIndex(id, group, private):
    for i in range(len(group)):
        if(group[i] == id or private[i] == id):
            return i
    return "NaN"

# 检查消息发送对象是否有自定义用户名
def getUserName(id, user):
    for i in range(len(user)):
        if(id == user[i][0]):
            return user[i][1]
    return False

# 过滤session_id，保留响应场景ID（群聊号或私聊对方QQ号）
def getGroupID(s):
    match = re.search(r'\d+', s)
    if match:
        id = match.group()
        return id
    return None

# 获取消息中的（或同时引用的）图片
def Images():
    async def main(bot: Bot, event: Event):
        reply = await reply_fetch(event, bot)
        msg = UniMessage.generate_without_reply(event=event, bot=bot)
        if reply:
            msg.extend(UniMessage.generate_without_reply(message=reply.msg))  # type: ignore
        return msg.get(acnImage)
    return Depends(main)

# 从URL下载图片
async def download_image(url: str) -> pilImage.Image:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        image_data = io.BytesIO(response.content)
        return image_data