import streamlit as st
import numpy as np
from openai import OpenAI


class APIEmbedder:
    def __init__(self, api_key, base_url, model_name):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model_name = model_name

    def encode(self, texts, batch_size=10):
        """
        分批调用 API，防止一次性发送过多导致报错
        """
        if not texts: return np.array([])

        all_embeddings = []

        # 移除换行符 (API 最佳实践)
        clean_texts = [t.replace("\n", " ") for t in texts]

        try:
            # --- 核心修改：分批循环发送 ---
            for i in range(0, len(clean_texts), batch_size):
                batch = clean_texts[i: i + batch_size]

                # 调用 API
                response = self.client.embeddings.create(
                    input=batch,
                    model=self.model_name
                )

                # 收集结果
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)

            return np.array(all_embeddings)

        except Exception as e:
            st.error(f"Embedding API 调用失败: {e}")
            return np.array([])


@st.cache_resource
def load_embedder(api_key, base_url, model_name):
    return APIEmbedder(api_key, base_url, model_name)