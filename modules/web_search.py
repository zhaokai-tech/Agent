from tavily import TavilyClient
import streamlit as st


def search_web(query, api_key):
    """
    使用 Tavily 搜索实时网络信息
    """
    if not api_key:
        return ""

    try:
        # 初始化客户端
        tavily = TavilyClient(api_key=api_key)

        # 执行搜索 (max_results=3 控制返回数量)
        response = tavily.search(query=query, search_depth="basic", max_results=3)

        context_pieces = []
        for result in response.get('results', []):
            title = result['title']
            content = result['content']
            url = result['url']

            # 拼装格式
            piece = f"[互联网来源: {title}]({url})\n摘要: {content}"
            context_pieces.append(piece)

        if not context_pieces:
            return ""

        return "\n\n".join(context_pieces)

    except Exception as e:
        print(f"联网搜索失败: {e}")  # 打印到后台方便调试
        return ""  # 失败返回空，不影响主流程