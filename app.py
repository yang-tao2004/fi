# 导入 Streamlit 库用于构建 Web 界面
import streamlit as st
# 导入 OpenAI 库用于调用大语言模型 API
from openai import OpenAI

# 初始化 OpenAI 客户端,配置 ModelScope 的 API 地址和认证令牌
openai_client = OpenAI(
    base_url='https://api-inference.modelscope.cn/v1',
    api_key='ms-69d69ea4-af07-47bd-9082-6adca7e3a510',  # ModelScope Token
)


# 定义生成响应的函数,接收消息列表作为参数
def generate_response(messages):
    """
    调用 AI 模型生成流式响应
    参数: messages - 包含对话历史的列表
    返回: 流式响应对象,失败则返回 None
    """
    try:
        # 调用 ModelScope API,使用 DeepSeek-V4-Flash 模型进行流式对话
        response = openai_client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V4-Flash",  # 指定使用的 AI 模型
            messages=messages,  # 传入完整的对话历史
            stream=True,  # 启用流式输出,实现逐字显示效果
        )
        return response  # 返回流式响应对象
    except Exception as e:
        # 如果 API 调用失败,显示错误信息并返回 None
        st.error(f"调用 API 失败: {str(e)}")
        return None


# 设置页面标题
st.title("AI 助手")

# 创建下拉框,让用户选择功能模式:对话、翻译或摘要
mode = st.selectbox("选择功能", ["对话", "翻译", "摘要"])

# 检查会话状态中是否存在消息列表,如果不存在则初始化为空列表
if "messages" not in st.session_state:
    st.session_state.messages = []

# 遍历历史消息并在界面上显示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):  # 根据角色(用户/助手)创建聊天消息框
        st.markdown(message["content"])  # 渲染消息内容

# 创建聊天输入框,获取用户输入
prompt = st.chat_input("请输入内容")

# 当用户输入内容时执行以下逻辑
if prompt:
    # 在界面上显示用户输入的消息
    with st.chat_message("user"):
        st.markdown(prompt)

    # 将用户消息添加到会话状态的历史记录中
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 定义不同功能模式对应的系统提示词
    system_prompts = {
        "对话": "你是一个友好的AI助手。",  # 普通对话模式
        "翻译": "你是一个专业的翻译助手,请将用户输入的内容翻译成中文。",  # 翻译模式
        "摘要": "你是一个文本摘要助手,请对用户输入的内容进行简洁的总结。"  # 摘要模式
    }

    # 构建完整的消息列表,将系统提示词放在最前面,后面跟随对话历史
    messages_with_system = [
                               {"role": "system", "content": system_prompts[mode]}  # 根据选择的模式添加对应的系统提示
                           ] + st.session_state.messages

    # 调用 AI 模型生成流式响应
    stream = generate_response(messages_with_system)

    # 如果成功获取到响应流
    if stream:
        # 在助手的聊天消息框中显示流式响应
        with st.chat_message("assistant"):
            response = st.write_stream(stream)  # 逐字显示 AI 的回答

        # 将 AI 的完整回答保存到会话状态的历史记录中
        st.session_state.messages.append({"role": "assistant", "content": response})
