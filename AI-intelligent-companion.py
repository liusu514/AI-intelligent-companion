import streamlit as st
import os
import json
from openai import OpenAI

print("------->重新执行此文件,渲染展示界面")

#数据持久化存储文件路径（项目目录下）
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ai history")
SETTINGS_FILE = os.path.join(DATA_DIR, "user_settings.json")
CHAT_FILE = os.path.join(DATA_DIR, "chat_history.json")

print(f"------->数据目录: {DATA_DIR}")
print(f"------->设置文件: {SETTINGS_FILE}")
print(f"------->聊天文件: {CHAT_FILE}")

#确保数据目录存在
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
    print(f"------->创建数据目录: {DATA_DIR}")
else:
    print(f"------->数据目录已存在: {DATA_DIR}")

def load_settings():
    """加载用户设置"""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"加载用户设置失败: {e}")
    return None

def load_chat_history():
    """加载聊天历史"""
    if os.path.exists(CHAT_FILE):
        try:
            with open(CHAT_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"加载聊天历史失败: {e}")
    return None

def save_settings():
    """保存用户设置"""
    try:
        data = {
            "ai_name": st.session_state.ai_name,
            "custom_personality": st.session_state.custom_personality
        }
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.flush()  # 确保立即写入磁盘
        print(f"------->用户设置已保存到 {SETTINGS_FILE}")
        print(f"------->保存的内容: {data}")
    except Exception as e:
        print(f"保存用户设置失败: {e}")

def save_chat_history():
    """保存聊天历史"""
    try:
        data = {
            "chat_history": st.session_state.chat_history,
            "current_chat_id": st.session_state.current_chat_id,
            "messages": st.session_state.messages
        }
        with open(CHAT_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"------->聊天历史已保存到 {CHAT_FILE}")
    except Exception as e:
        print(f"保存聊天历史失败: {e}")

def save_data():
    """保存所有数据"""
    save_settings()
    save_chat_history()

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

#默认提示词（后台）
DEFAULT_SYSTEM_PROMPT = """现在是用户的真实伴侣，请完全代入伴侣角色。
                            规则：
                            1.每次只回复1条消息
                            2.禁止任何场景或状态描述性文字
                            3.匹配用户的语言
                            4.回复简短，像微信聊天一样
                            5.有需要的话可以用emoji表情
                            6.用符合伴侣性格的方式对话
                            7.回复的内容，要充分体现伴侣的性格特征
                            你必须严格遵守上述规则来回答用户
                        """

#初始化session_state中的参数（优先从文件加载）
if "initialized" not in st.session_state:
    #加载用户设置
    settings = load_settings()
    if settings:
        st.session_state.ai_name = settings.get("ai_name", "ai伴侣")
        st.session_state.custom_personality = settings.get("custom_personality", "")
        print(f"------->加载用户设置成功")
    else:
        st.session_state.ai_name = "ai伴侣"
        st.session_state.custom_personality = ""

    #加载聊天历史
    chat_data = load_chat_history()
    if chat_data:
        st.session_state.chat_history = chat_data.get("chat_history", {})
        st.session_state.current_chat_id = chat_data.get("current_chat_id", None)
        st.session_state.messages = chat_data.get("messages", [])
        print(f"------->加载聊天历史成功，历史会话数量: {len(st.session_state.chat_history)}")
    else:
        st.session_state.chat_history = {}
        st.session_state.current_chat_id = None
        st.session_state.messages = []

    st.session_state.initialized = True

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
        print(f"------->伴侣名字已更新为: {new_ai_name}")
        save_data()
        st.rerun()

    st.divider()

    #自定义性格设置
    st.subheader("自定义性格")
    new_custom_personality = st.text_area(
        "请输入性格",
        value=st.session_state.custom_personality,
        height=100,
        help="描述你希望伴侣的性格，例如：温柔体贴、活泼开朗、高冷傲娇等"
    )
    if new_custom_personality != st.session_state.custom_personality:
        st.session_state.custom_personality = new_custom_personality
        print(f"------->自定义性格已更新为: {new_custom_personality}")
        save_data()
        st.rerun()

    st.divider()

    #对话管理
    st.subheader("对话管理")

    #新建对话按钮
    if st.button("新建对话", type="primary"):
        import uuid
        from datetime import datetime
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
                "custom_personality": st.session_state.custom_personality,
                "summary": summary if summary else "新对话",
                "last_time": datetime.now().strftime("%m-%d %H:%M")
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
        save_data()
        st.rerun()

    #显示历史会话列表
    if st.session_state.chat_history:
        st.subheader("历史会话")
        for chat_id, chat_data in st.session_state.chat_history.items():
            #显示会话预览和删除按钮
            summary = chat_data.get("summary", "新对话")
            last_time = chat_data.get("last_time", "")
            preview = f"{summary} ({last_time})" if last_time else summary
            col1, col2 = st.columns([4, 1])
            with col1:
                if st.button(preview, key=f"chat_{chat_id}", use_container_width=True):
                    import uuid
                    from datetime import datetime
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
                            "custom_personality": st.session_state.custom_personality,
                            "summary": current_summary if current_summary else "新对话",
                            "last_time": datetime.now().strftime("%m-%d %H:%M")
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
                    st.session_state.custom_personality = chat_data["custom_personality"]
                    save_data()
                    st.rerun()
            with col2:
                if st.button("🗑️", key=f"delete_{chat_id}", help="删除此会话"):
                    del st.session_state.chat_history[chat_id]
                    #如果删除的是当前会话，清空当前对话
                    if st.session_state.current_chat_id == chat_id:
                        st.session_state.current_chat_id = None
                        st.session_state.messages = []
                    save_data()
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

#构建完整的系统提示词（默认提示词 + 用户自定义性格）
system_prompt = DEFAULT_SYSTEM_PROMPT + "\n伴侣性格：\n- " + st.session_state.custom_personality

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

        #更新当前会话的时间戳
        from datetime import datetime
        if st.session_state.current_chat_id and st.session_state.current_chat_id in st.session_state.chat_history:
            st.session_state.chat_history[st.session_state.current_chat_id]["last_time"] = datetime.now().strftime("%m-%d %H:%M")

        save_data()
    except Exception as e:
        error_msg = f"调用AI大模型时出现错误: {str(e)}"
        print(error_msg)
        st.error(error_msg)

    
    
