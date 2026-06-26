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

#初始化聊天信息
if "messages" not in st.session_state:
    st.session_state.messages = []

#初始化session_state中的参数
if "ai_name" not in st.session_state:
    st.session_state.ai_name = "小美"
if "personality" not in st.session_state:
    st.session_state.personality = """现在是用户的真实伴侣，请完全代入伴侣角色。
    规则：
        1.每次只回复1条消息 
        2.禁止任何场景或状态描述性文字 
        3.匹配用户的语言 
        4.回复简短，像微信聊天一样
        5.有需要的话可以用emoji表情
        6.用符合伴侣性格的方式对话
        7.回复的内容，要充分体现伴侣的性格特征
    伴侣性格：
        - 可爱温柔的台湾人
        你必须严格遵守上述规则来回答用户
        """
if "chat_history" not in st.session_state:
    st.session_state.chat_history = {}
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

#大标题
st.title(st.session_state.ai_name)
#logo
st.logo("resources/logo.png")

#侧边栏
with st.sidebar:
    st.header("设置")

    #自定义名字设置
    st.subheader("伴侣名字")
    new_ai_name = st.text_input(
        "给伴侣起个名字",
        value=st.session_state.ai_name,
        max_chars=20
    )
    if new_ai_name != st.session_state.ai_name:
        st.session_state.ai_name = new_ai_name
        st.rerun()

    st.divider()

    #人物性格设置
    st.subheader("人物性格")
    new_personality = st.text_area(
        "描述AI的性格特点",
        value=st.session_state.personality,
        height=100,
        help="描述你希望AI扮演的角色性格"
    )
    if new_personality != st.session_state.personality:
        st.session_state.personality = new_personality
        st.rerun()

    st.divider()

    #对话管理
    st.subheader("对话管理")

    #新建对话按钮
    if st.button("新建对话", type="primary"):
        import uuid
        #保存当前对话到历史（如果有消息的话）
        if st.session_state.messages:
            #如果没有current_chat_id，先创建一个
            if not st.session_state.current_chat_id:
                st.session_state.current_chat_id = f"chat_{uuid.uuid4().hex[:8]}"
            #获取最后一条用户消息作为摘要
            summary = ""
            for msg in reversed(st.session_state.messages):
                if msg["role"] == "user":
                    summary = msg["content"][:20] + "..." if len(msg["content"]) > 20 else msg["content"]
                    break
            #保存到历史
            st.session_state.chat_history[st.session_state.current_chat_id] = {
                "messages": st.session_state.messages.copy(),
                "name": st.session_state.ai_name,
                "personality": st.session_state.personality,
                "summary": summary if summary else "新对话"
            }
            #限制最多保留3个历史会话
            while len(st.session_state.chat_history) > 3:
                #获取最旧的会话ID（第一个）
                oldest_chat_id = list(st.session_state.chat_history.keys())[0]
                del st.session_state.chat_history[oldest_chat_id]
        #创建新对话
        new_chat_id = f"chat_{uuid.uuid4().hex[:8]}"
        st.session_state.current_chat_id = new_chat_id
        st.session_state.messages = []
        st.rerun()

    #显示历史会话列表
    if st.session_state.chat_history:
        st.subheader("历史会话")
        for chat_id, chat_data in st.session_state.chat_history.items():
            #显示会话预览
            summary = chat_data.get("summary", "新对话")
            preview = f"{summary}"
            if st.button(preview, key=f"chat_{chat_id}"):
                import uuid
                #保存当前对话
                if st.session_state.messages:
                    #如果没有current_chat_id，先创建一个
                    if not st.session_state.current_chat_id:
                        st.session_state.current_chat_id = f"chat_{uuid.uuid4().hex[:8]}"
                    #获取最后一条用户消息作为摘要
                    current_summary = ""
                    for msg in reversed(st.session_state.messages):
                        if msg["role"] == "user":
                            current_summary = msg["content"][:20] + "..." if len(msg["content"]) > 20 else msg["content"]
                            break
                    #保存到历史
                    st.session_state.chat_history[st.session_state.current_chat_id] = {
                        "messages": st.session_state.messages.copy(),
                        "name": st.session_state.ai_name,
                        "personality": st.session_state.personality,
                        "summary": current_summary if current_summary else "新对话"
                    }
                    #限制最多保留3个历史会话
                    while len(st.session_state.chat_history) > 3:
                        #获取最旧的会话ID（第一个）
                        oldest_chat_id = list(st.session_state.chat_history.keys())[0]
                        del st.session_state.chat_history[oldest_chat_id]
                #切换到选中的对话
                st.session_state.current_chat_id = chat_id
                st.session_state.messages = chat_data["messages"].copy()
                st.session_state.ai_name = chat_data["name"]
                st.session_state.personality = chat_data["personality"]
                st.rerun()

    st.divider()

    #关于
    st.subheader("关于")
    st.markdown(f"""
    **{st.session_state.ai_name}** 是你的专属智能伴侣 ✨

    🌟 **特色功能**
    - 记得你说过的每一句话
    - 像真人一样实时回复
    - 可以扮演任何你想要的角色
    - 支持多个平行时空的对话

    💝 用心陪伴，温暖每一刻
    """)

#使用session_state中的参数
system_prompt = st.session_state.personality

#展示聊天信息
for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])
#调用ai大模型
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


    #与AI大模型进行交互
    try:
        #构建消息列表，包含系统提示和历史消息
        messages_for_api = [
            {
                "role": "system",
                "content": system_prompt
            },
            *st.session_state.messages
        ]
        print(f"------->发送给API的消息数量: {len(messages_for_api)}")
        print(f"------->历史消息数量: {len(st.session_state.messages)}")

        #流式输出
        stream = client.chat.completions.create(
            model="mimo-v2.5-pro",
            messages=messages_for_api,
            max_completion_tokens=1024,
            temperature=1.0,
            top_p=0.95,
            stream=True,
            stop=None,
            frequency_penalty=0,
            presence_penalty=0
        )

        #使用st.write_stream处理流式输出
        response = st.chat_message("assistant").write_stream(stream)

        #保存大模型返回的结果
        st.session_state.messages.append({"role": "assistant", "content": response})
        print(f"------->保存消息后，session_state中的消息数量: {len(st.session_state.messages)}")
    except Exception as e:
        error_msg = f"调用AI大模型时出现错误: {str(e)}"
        print(error_msg)
        st.error(error_msg)

    
    
