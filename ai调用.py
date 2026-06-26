import os
from openai import OpenAI

#创建与AI大模型交互的客户端对象（MIMO_API_KEY 环境变量的名字，值就是api key）
client = OpenAI(
    api_key=os.environ.get("MIMO_API_KEY"),
    base_url="https://token-plan-cn.xiaomimimo.com/v1"
)
#与AI大模型进行交互（）
completion = client.chat.completions.create(
    model="mimo-v2.5-pro",
    messages=[
        {
            "role": "system",
            "content": "你是一个ai助理，请你用温柔的预期回答用户的问题"
        },
        {
            "role": "user",
            "content": "你是谁，你能帮我干什么"
        }
    ],
    max_completion_tokens=1024,
    temperature=1.0,
    top_p=0.95,
    stream=False,
    stop=None,
    frequency_penalty=0,
    presence_penalty=0
)
#输出大模型返回的结果
print(completion.model_dump_json())