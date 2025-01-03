from .utils import getParameters, msgPurify, getIndex, getUserName, getGroupID, Images, download_image

from requests import *
from nonebot import on_message, on_command, require
from nonebot.adapters import Bot, Event
from nonebot.plugin import PluginMetadata
from nonebot import get_plugin_config
from .config import Config
require("nonebot_plugin_userinfo")
from nonebot_plugin_userinfo import get_user_info # type: ignore
from datetime import datetime
require("nonebot_plugin_alconna")
import base64

__plugin_meta__ = PluginMetadata(
    name="nonebot-plugin-ollama",
    description="使用Ollama框架下的LLM进行消息处理",
    usage="使用自定义前缀进行交互响应",
    type="application",
    config=Config,
    homepage="https://github.com/C9QuaRtz/nonebot-plugin-ollama"
)

# 配置文件载入
plugin_config = get_plugin_config(Config).ollama
group = plugin_config.listening_group
private = plugin_config.listening_private
cmd = plugin_config.cmd
cmd_img = plugin_config.cmd_img
user = plugin_config.user

# 消息记录初始化
messages_group = [[ None for _ in range(0) ] for _ in range(len(group))]
messages_private = [[ None for _ in range(0) ] for _ in range(len(private))]

# 全局流程控制变量初始化
doRec = True
didServe = False
index = 0x0d000721 # suki

# 消息监听记录模块
rec = on_message(priority=plugin_config.min_priority+3, block=False)
@rec.handle()
async def main(bot=Bot, event=Event):

    # 判断在之前的处理中是否已记录 避免重复记录
    if(didServe):
        return

    # 获取消息
    msg = str(event.get_message())

    # 获取消息发送对象属性
    user_info = await get_user_info(bot, event, event.get_user_id())
    userName = getUserName(user_info.user_id, user) # 获取用户名
    if(not userName):
        userName = user_info.user_name # 若未自定义，则使用对象QQ昵称

    # 获取时间
    now = datetime.now()
    formatted_now = now.strftime("[%Y-%m-%d %H:%M:%S] ")

    # 获取群聊号或私聊对象QQ号
    msgID = event.get_session_id()
    groupID = getGroupID(msgID)

    # 获取消息所属对象（群聊或私聊）在配置中的索引 准备存储消息
    global index
    index = getIndex(groupID, group, private)
    if(index == "NaN"): # 若不在配置文件内（白名单内）则结束流程 不储存
        return

    # 若本消息之前未进行过储存
    if(doRec):
        if(msgID.startswith("group")): # 判断是否为群聊
            messages_group[index].append({
                    "role": 'user',
                    "content": formatted_now + userName + ": " + msg,
                })
        else:
            messages_private[index].append({
                    "role": 'user',
                    "content": formatted_now + userName + ": " + msg,
                })

# 标准响应方法
ollama = on_command(cmd[0], aliases=set(cmd), priority=plugin_config.min_priority+2, block=False)
@ollama.handle()
async def ollama_handle(bot: Bot, event: Event):
    
    # 在视觉响应命令与标准响应命令有重复的情况下，将优先选用视觉处理
    # 在此情况下，此语句用于判断本消息是否已经过视觉LLM的回答
    if(didServe):
        return

    # 运行到此处时，本消息应是第一次被处理
    # 默认未被存储
    global doRec
    doRec = True

    # 获取消息
    msg = str(event.get_message())
    msg = msgPurify(msg, cmd)

    # 获取群聊号或私聊对象QQ号
    msgID = event.get_session_id()
    groupID = getGroupID(msgID)

    # 获取消息所属对象（群聊或私聊）在配置中的索引 准备存储消息
    global index
    index = getIndex(groupID, group, private)
    if(index == "NaN"):
        return

    # 判断是否达到记录上限
    if len(messages_group[index]) >= plugin_config.max_histories:
        del messages_group[index][0]
        # await ollama.send(f"Warning: 对话记录已达到{plugin_config.max_histories}条的上限，现已清空.")
    if len(messages_private[index]) >= plugin_config.max_histories:
        del messages_private[index][0]
    
    # 获取用户名
    user_info = await get_user_info(bot, event, event.get_user_id())
    userName = getUserName(user_info.user_id, user)
    if(not userName):
        userName = user_info.user_name

    # 获取时间
    now = datetime.now()
    formatted_now = now.strftime("[%Y-%m-%d %H:%M:%S] ")
    
    # 进行（必然会发生的）存储
    if(doRec):
        if(msgID.startswith("group")):
            messages_group[index].append({
                "role": 'user',
                "content": formatted_now + userName + ": " + msg,
            })
        else:
            messages_private[index].append({
                "role": 'user',
                "content": formatted_now + userName + ": " + msg,
            })
        doRec = False # 告诉下一个响应的方法（rec）不必再存储
    
    # 组合向Ollama请求的内容
    parameters = getParameters(msgID.startswith("group"), plugin_config, messages_group, index, messages_private)
    
    # 向ollama发送请求
    response = post(plugin_config.url+'api/chat', json=parameters)
    if response.status_code == 200:
        await ollama.send(response.json()["message"]["content"]) # 发送回答
        if(msgID.startswith("group")): # 记忆回答
            messages_group[index].append(response.json()["message"])
        else:
            messages_private[index].append(response.json()["message"])
        doRec = False # 再次强调（
    else:
        await ollama.send(f"Error: {response.status_code}") # 直接发送通信报错信息

# 使用视觉LLM进行特别响应的方法
ollama_img = on_command(cmd_img[0], aliases=set(cmd_img), priority=plugin_config.min_priority+1, block=False)
@ollama_img.handle()
async def main(bot: Bot, event: Event, img = Images()):
    
    # 最高优先级 必然进行消息记忆
    global doRec
    doRec = True
    
    # 获取消息
    msg = str(event.get_message())
    msg = msgPurify(msg, cmd)

    # 获取群聊号或QQ号
    msgID = event.get_session_id()
    groupID = getGroupID(msgID)

    # 检查白名单并获取索引
    global index
    index = getIndex(groupID, group, private)
    if(index == "NaN"):
        return
    
    # 检查是否超过消息记忆量
    if len(messages_group[index]) >= plugin_config.max_histories:
        del messages_group[index][0]
    if len(messages_private[index]) >= plugin_config.max_histories:
        del messages_private[index][0]

    img_list = [] # 未完成的多图片并行处理
    if img:
        url = img[0].url # 我知道0索引是在偷懒的（
        FinImg = await download_image(url) # 下载图片
        b64 = base64.b64encode(FinImg.read()).decode('utf-8') # 转码为base64
        img_list = [b64]

    # 获取用户名
    user_info = await get_user_info(bot, event, event.get_user_id())
    userName = getUserName(user_info.user_id, user)
    if(not userName):
        userName = user_info.user_name

    # 获取时间
    now = datetime.now()
    formatted_now = now.strftime("[%Y-%m-%d %H:%M:%S] ")
    
    # 消息记忆
    if(doRec):
        if(msgID.startswith("group")):
            messages_group[index].append({
                "role": 'user',
                "content": formatted_now + userName + ": " + msg,
                "images": img_list
            })
        else:
            messages_private[index].append({
                "role": 'user',
                "content": formatted_now + userName + ": " + msg,
                "images": img_list
            })
        doRec = False

    # 请求内容整合
    parameters = getParameters(msgID.startswith("group"), plugin_config, messages_group, index, messages_private)
    
    # 发送请求
    response = post(plugin_config.url+'api/chat', json=parameters)
    if response.status_code == 200:
        await ollama_img.send(response.json()["message"]["content"])
        if(msgID.startswith("group")):
            messages_group[index].append(response.json()["message"])
        else:
            messages_private[index].append(response.json()["message"])
        doRec = False
    else:
        await ollama_img.send(f"Error: {response.status_code}")
    
    # 告诉后面响应的方法（ollama、rec）不必再进行处理
    global didServe
    didServe = True