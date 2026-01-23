import requests
import json
import streamlit as st


class APIReranker:
    def __init__(self, api_key, base_url, model_name):
        self.api_key = api_key
        self.base_url = base_url
        self.model_name = model_name

    def rerank(self, query, candidates, top_k=5):
        """
        调用 SiliconFlow (BGE-Reranker) API 进行重排序
        """
        if not candidates:
            return []

        # 1. 准备纯文本列表
        documents = [item['content'] for item in candidates]

        # 2. 构造请求头
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # 3. 构造请求体 (SiliconFlow 格式)
        payload = {
            "model": self.model_name,
            "query": query,
            "documents": documents,
            "top_n": top_k,
            "return_documents": False  # 我们不需要它把文本传回来，只需要分数
        }

        try:
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=10)

            # 检查状态码
            if response.status_code != 200:
                error_msg = response.text
                st.warning(f"⚠️ Rerank 服务响应异常 ({response.status_code}): {error_msg} -> 已降级为普通检索")
                return candidates[:top_k]  # 降级处理

            data = response.json()
            results = data.get("results", [])

            reranked_candidates = []
            for item in results:
                # SiliconFlow 返回 index 和 relevance_score
                idx = item['index']
                score = item['relevance_score']

                # 拿回原始数据
                original_doc = candidates[idx]

                # 更新分数为 Rerank 的分数
                original_doc['score'] = score
                reranked_candidates.append(original_doc)

            # 按分数降序排序
            reranked_candidates.sort(key=lambda x: x['score'], reverse=True)

            return reranked_candidates

        except Exception as e:
            st.warning(f"⚠️ Rerank 调用失败: {e} -> 已降级为普通检索")
            return candidates[:top_k]


@st.cache_resource
def load_reranker(api_key, base_url, model_name):
    if not api_key: return None
    return APIReranker(api_key, base_url, model_name)