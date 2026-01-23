import streamlit as st
from io import BytesIO


@st.cache_data(show_spinner=False)
def process_file(_model, file_name, file_bytes):
    """
    输入：模型、文件名、文件字节流
    输出：chunks (带页码元数据), vectors, error_message
    """
    # 延迟导入，防止启动卡顿
    import fitz  # PyMuPDF
    import docx

    chunks = []

    try:
        # --- 1. 处理 PDF (支持精确页码) ---
        if file_name.lower().endswith('.pdf'):
            # 使用 PyMuPDF 打开
            with fitz.open(stream=file_bytes, filetype="pdf") as doc:
                for page_index, page in enumerate(doc):
                    # 获取当前页的文本
                    page_text = page.get_text()

                    if not page_text.strip():
                        continue  # 跳过空白页

                    # --- 页内切分逻辑 ---
                    # 如果这一页字数太多（超过600），我们也需要把它切开
                    # 但它们都属于同一个页码
                    page_num = page_index + 1  # 人类习惯从第1页开始

                    chunk_size = 600
                    overlap = 50
                    start = 0

                    while start < len(page_text):
                        end = start + chunk_size
                        chunk_content = page_text[start:end]

                        # 存入 chunk，额外记录 'page' 字段
                        chunks.append({
                            "content": chunk_content,
                            "source": file_name,
                            "page": page_num  # <--- 核心修改：记录页码
                        })

                        # 如果一页还没切完，继续切下一段；如果切完了，就break
                        if end >= len(page_text):
                            break

                        start += (chunk_size - overlap)

        # --- 2. 处理 Word (Word流式排版，无固定页码) ---
        elif file_name.lower().endswith('.docx'):
            doc = docx.Document(BytesIO(file_bytes))
            # Word 只能把所有段落拼起来
            text = "\n".join([p.text for p in doc.paragraphs])

            # 标准切分
            chunk_size = 600
            overlap = 60
            start = 0
            while start < len(text):
                chunks.append({
                    "content": text[start:start + chunk_size],
                    "source": file_name,
                    "page": "N/A"  # Word 暂时无法提取页码
                })
                start += (chunk_size - overlap)

        # --- 3. 处理 TXT ---
        elif file_name.lower().endswith('.txt'):
            text = file_bytes.decode("utf-8")
            chunk_size = 600
            overlap = 60
            start = 0
            while start < len(text):
                chunks.append({
                    "content": text[start:start + chunk_size],
                    "source": file_name,
                    "page": "N/A"
                })
                start += (chunk_size - overlap)

    except Exception as e:
        return None, None, f"文件处理失败: {e}"

    if not chunks:
        return None, None, "未能提取到有效文本"

    # --- 4. 生成向量 ---
    # 调用传入的模型（或者是 RemoteModel）进行计算
    try:
        texts_to_embed = [c["content"] for c in chunks]
        vectors = _model.encode(texts_to_embed)
        return chunks, vectors, None
    except Exception as e:
        return None, None, f"向量计算失败: {e}"