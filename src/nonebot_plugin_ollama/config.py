from pydantic import BaseModel, field_validator

class ScopedConfig(BaseModel):
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
    @field_validator('min_priority')
    @classmethod
    def check_priority(cls, v: int):
        if v >= 1:
            return v
        raise ValueError('ollama command priority must be greater than 1')
    
    @field_validator('url')
    @classmethod
    def check_url(cls, v: str):
        if v.startswith('http://') and v.endswith('/'):
            return v
        raise ValueError('ollama url must start with http:// and end with /')
    
class Config(BaseModel):
    ollama: ScopedConfig = ScopedConfig()