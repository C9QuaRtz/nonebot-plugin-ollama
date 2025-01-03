# 功能介绍
通过ollama提供的接口，
将你的nonebot连接到本地部署的基于ollama框架的LLM模型。

暂时只支持与单个模型进行纯文本聊天。

### 主要功能
使用自定义命令前缀进行对话。

当前版本：v0.2.3-c1.0

# 配置项示例
```python
# config.py
class ScopedConfig:
    model: str = "qwen2.5:14b" # 标准响应使用的模型名
    model_img: str = "llava:7b" # 仅用于响应图片请求的视觉模型名
    url: str = "http://127.0.0.1:11434/" # 与Ollama的通信地址 本地默认可填 http://127.0.0.1:11434/
    min_priority: int = 5 # Nonebot 事件优先级
    max_histories: int = 100 # 某方对话的最大消息记忆数
    listening_group: str = ["12700721"] # 希望提供服务的群聊号
    listening_private: str = ["10001"] # 希望提供服务的私聊对象QQ号
    cmd: str = ["ollama"] # 触发消息处理的消息前缀
    cmd_img: str = ["ollama_img"] # 改用视觉LLM处理的消息前缀
    user: str = [["10001", "马化腾"]] # 自定义对象QQ号所代表的名字
```

推荐先修改你所使用模型Modelfile的System项，调整后能够更加胜任工作。

输入至你的模型的消息格式如下（已自动删去命令前缀）:

[2024-12-14 19:12:52] UserName: 这是一条测试消息。

### 隐私数据管理
机器人所使用的所有聊天记录均储存于本地，且随机器人重启而清空。

在仅使用本地LLM的情况下，你的聊天数据不会被上传至任何第三方服务器进行处理。

### 未来开发方向：

~~1. 自动切换llava进行图片处理~~
~~2. 在config.py内添加对Modelfile的支持~~ 已放弃，请自行参阅官方文档，本项需求定位不属于本项目
3. 聊天记录（日志）导出

最终目标：提供API，为其他开发者实现跨插件事件响应与处理。

# 相关链接
nonebot: https://nonebot.dev/   
ollama: https://ollama.org.cn/

# 开源协议
MIT