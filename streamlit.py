import streamlit as st
import os
from openai import OpenAI

print("------->重新执行此文件,渲染展示界面")

#设置页面的配置项
st.set_page_config(
    page_title="AI智能伴侣", 
    page_icon=":👾:", 
    #布局
    layout="wide",
    #初始侧边栏状态
    initial_sidebar_state="expanded",
    menu_items={}
    )

#大标题
st.title("AI智能伴侣")
#logo
st.logo("resources/logo.png")
#系统提示词
system_prompt = "你是一个ai助理,请你用温柔的预期回答用户的问题"

#初始化聊天信息
if "messages" not in st.session_state:
    st.session_state.messages = []

#展示聊天信息
for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])

#创建与AI大模型交互的客户端对象（MIMO_API_KEY 环境变量的名字，值就是api key）
client = OpenAI(
    api_key=os.environ.get("MIMO_API_KEY"),
    base_url="https://token-plan-cn.xiaomimimo.com/v1"
)

#输入框
prompt = st.chat_input("请输入您要问的问题：")
if prompt:#字符串会自动转换为布尔值，如果字符串为空，则为False，否则为True
    st.chat_message("user").write(prompt)
    print("------->调用AI大模型,提示词:",prompt)
    #保存用户输入的提示词
    st.session_state.messages.append({"role": "user", "content": prompt})

    #调用ai大模型
    #与AI大模型进行交互
    completion = client.chat.completions.create(
        model="mimo-v2.5-pro",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            *st.session_state.messages
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
    print("<-------AI大模型返回的结果:", completion.model_dump_json())
    st.chat_message("assistant").write(completion.choices[0].message.content)
    #保存大模型返回的结果
    st.session_state.messages.append({"role": "assistant", "content": completion.choices[0].message.content})

    
    
