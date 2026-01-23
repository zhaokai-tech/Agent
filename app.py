import streamlit as st
import uuid
from openai import OpenAI

# 导入所有模块 (保持不变)
from modules.embedder import load_embedder
from modules.processor import process_file
from modules.web_search import search_web
from modules.history import save_chat, load_chat, get_history_list, delete_chat
from modules.database import add_to_db, reset_db, get_collection, get_all_files, delete_file_from_db
from modules.retriever import search_vectors
from modules.reranker import load_reranker

# --- 页面配置 ---
st.set_page_config(page_title="DeepSeek Pro 知识库", layout="wide", page_icon="🧠")


def main():
    st.title("🤖 DeepSeek Pro 知识库 (v4.1)")
    st.caption("全功能版: 引用持久化 | 参数详解 | 深度思考")

    # --- Session State 初始化 ---
    if "messages" not in st.session_state: st.session_state.messages = []
    if "current_chat_id" not in st.session_state: st.session_state.current_chat_id = str(uuid.uuid4())

    # --- 侧边栏 ---
    with st.sidebar:
        tab1, tab2 = st.tabs(["⚙️ 控制台", "🕒 历史"])

        # === Tab 1: 设置与管理 ===
        with tab1:
            # 1. 模型状态仪表盘
            st.subheader("1. 系统状态")
            ds_key = st.secrets.get("DEEPSEEK_API_KEY")
            ds_url = st.secrets.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
            emb_key = st.secrets.get("EMBEDDING_API_KEY")
            emb_base = st.secrets.get("EMBEDDING_BASE_URL")
            emb_model = st.secrets.get("EMBEDDING_MODEL")
            rerank_key = st.secrets.get("RERANK_API_KEY")
            rerank_base = st.secrets.get("RERANK_BASE_URL")
            rerank_model = st.secrets.get("RERANK_MODEL")
            tavily_key = st.secrets.get("TAVILY_API_KEY")

            c1, c2, c3 = st.columns(3)
            c1.markdown("🟢 **LLM**" if ds_key else "🔴 **LLM**")
            c2.markdown("🟢 **RAG**" if emb_key else "🔴 **RAG**")
            c3.markdown("🟢 **Web**" if tavily_key else "⚪ **Web**")

            st.divider()

            # 2. 知识库上传
            st.subheader("2. 导入文档")
            files = st.file_uploader("上传 PDF/Word", accept_multiple_files=True)
            if st.button("🚀 存入知识库", type="primary") and files:
                if not emb_key: st.stop()
                embedder = load_embedder(emb_key, emb_base, emb_model)
                total = 0
                prog = st.progress(0)
                for i, f in enumerate(files):
                    fc, fv, _ = process_file(embedder, f.name, f.getvalue())
                    if fc: total += add_to_db(fc, fv)
                    prog.progress((i + 1) / len(files))
                if total > 0: st.success(f"存入 {total} 片段")
                st.rerun()

            # 3. 文件管理列表
            st.subheader("3. 文件管理")
            existing_files = get_all_files()
            if existing_files:
                with st.expander(f"已存储 {len(existing_files)} 个文件", expanded=False):
                    for f in existing_files:
                        c1, c2 = st.columns([0.85, 0.15])
                        c1.text(f[:20] + "..." if len(f) > 20 else f)
                        if c2.button("🗑️", key=f"del_{f}"):
                            delete_file_from_db(f)
                            st.rerun()
                if st.button("💣 清空所有数据"):
                    reset_db()
                    st.rerun()
            else:
                st.caption("知识库为空")

            st.divider()

            # 4. 🟢 优化：高级参数设置 (带详细说明)
            with st.expander("🎛️ 参数微调 (新手必读)"):
                st.markdown("""
                **参数说明书：**
                * **创造性**: 越低越严谨(适合科研)，越高越发散(适合创意)。
                * **粗排 (Recall)**: 从数据库里先捞出多少条“可能相关”的内容。
                * **精排 (Rerank)**: 让 AI 老师仔细打分，最终给大模型看前几名。
                """)

                temperature = st.slider(
                    "创造性 (Temperature)", 0.0, 1.3, 0.3, 0.1,
                    help="建议：科研查询设为 0.1，日常对话设为 0.7"
                )
                top_k_recall = st.slider(
                    "粗排数量 (Recall)", 10, 100, 50,
                    help="增加此值可减少漏找，但会增加 Rerank 时间"
                )
                top_k_rerank = st.slider(
                    "精排数量 (Rerank)", 1, 10, 5,
                    help="最终喂给 DeepSeek 的片段数。建议 5 左右，太多会干扰模型"
                )
                use_web = st.toggle("联网增强", value=False)

            if st.button("➕ 新建对话"):
                st.session_state.messages = []
                st.session_state.current_chat_id = str(uuid.uuid4())
                st.rerun()

        # === Tab 2: 历史 ===
        with tab2:
            for chat in get_history_list():
                c1, c2 = st.columns([0.85, 0.15])
                label = f"**{chat['title']}**\n\n_{chat['timestamp'][5:-3]}_"
                if c1.button(label, key=f"h_{chat['id']}", use_container_width=True):
                    st.session_state.messages = load_chat(chat['id'])
                    st.session_state.current_chat_id = chat['id']
                    st.rerun()
                if c2.button("❌", key=f"d_{chat['id']}"):
                    delete_chat(chat['id'])
                    st.rerun()

    # --- 🟢 优化：聊天主界面 (支持历史引用渲染) ---
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            # 关键修改：如果历史消息里包含 sources 字段，则渲染折叠框
            if "sources" in msg and msg["sources"]:
                with st.expander("📖 查看引用片段 (Source Context)"):
                    st.info(msg["sources"])

    query = st.chat_input("向知识库提问...")

    if query:
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.write(query)

        local_context = ""
        web_context = ""

        # 可视化思考过程
        with st.status("🚀 AI 正在深度思考...", expanded=True) as status:

            # Step 1: 本地检索
            if get_collection().count() > 0:
                st.write("📚 正在检索本地知识库...")
                embedder = load_embedder(emb_key, emb_base, emb_model)
                reranker = load_reranker(rerank_key, rerank_base, rerank_model)

                local_context = search_vectors(
                    embedder, query, reranker,
                    top_k_recall=top_k_recall,
                    top_k_rerank=top_k_rerank
                )
                if local_context:
                    st.write(f"✅ 找到 {top_k_rerank} 个相关片段 (已重排序)")
                else:
                    st.write("⚠️ 本地未找到足够相关内容")

            # Step 2: 联网搜索
            if use_web and tavily_key:
                st.write("🌍 正在扫描互联网最新信息...")
                web_context = search_web(query, tavily_key)
                st.write("✅ 互联网数据获取成功")

            status.update(label="🧠 思考完成，正在生成回答", state="complete", expanded=False)

        # 组装 Prompt
        prompt = ""
        if local_context: prompt += f"【本地知识】:\n{local_context}\n\n"
        if web_context: prompt += f"【网络信息】:\n{web_context}\n\n"

        system_prompt = f"请基于以下背景回答问题。必须标注来源 [来源: xxx]。\n\n{prompt}"

        # 生成回答
        client = OpenAI(api_key=ds_key, base_url=ds_url)
        with st.chat_message("assistant"):
            try:
                stream = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": query}
                    ],
                    temperature=temperature,
                    stream=True
                )
                response = st.write_stream(stream)

                # 🟢 优化：保存时将 sources 也存入 history
                message_data = {
                    "role": "assistant",
                    "content": response,
                    "sources": local_context  # 将引用内容持久化保存
                }
                st.session_state.messages.append(message_data)
                save_chat(st.session_state.current_chat_id, st.session_state.messages)

                # 当前轮次的引用展示 (为了即时反馈)
                if local_context:
                    with st.expander("📖 查看引用片段 (Source Context)"):
                        st.info(local_context)

            except Exception as e:
                st.error(f"Error: {e}")


if __name__ == "__main__":
    main()