import streamlit as st
from openai import OpenAI

def get_api_client():
    """安全获取 API Client"""
    try:
        api_key = st.secrets.get("DEEPSEEK_API_KEY", None)
        base_url = st.secrets.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    except Exception:
        return None, None
    return api_key, base_url

def ask_deepseek(client, context, query, model_name="deepseek-chat"):
    """
    构建 Prompt 并请求流式响应
    """
    system_prompt = f"""
你是一个严谨的学术助手。基于以下检索到的上下文回答问题。

上下文内容：
{context}

回答要求：
1. 引用来源：在提到具体观点时，必须在句末标注来源文件名，格式如 (来源: xxx.pdf)。
2. 如果上下文没有相关信息，请直接说明。
"""
    try:
        stream = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            stream=True
        )
        return stream
    except Exception as e:
        raise e