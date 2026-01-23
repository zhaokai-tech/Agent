from modules.database import query_db


def search_vectors(embedder, query, reranker=None, top_k_recall=50, top_k_rerank=5):
    """
    支持动态参数的智能检索
    """
    # 1. 向量化
    q_vec = embedder.encode([query])[0]

    # 2. 粗排 (Recall) - 使用动态参数 top_k_recall
    # 如果没有 Rerank，直接用 rerank 的数量作为最终数量，避免过多
    initial_k = top_k_recall if reranker else top_k_rerank
    candidates = query_db(q_vec, top_k=initial_k)

    if not candidates:
        return ""

    final_results = candidates

    # 3. 精排 (Rerank) - 使用动态参数 top_k_rerank
    if reranker:
        final_results = reranker.rerank(query, candidates, top_k=top_k_rerank)

    # 4. 格式化输出
    valid_results = []
    for item in final_results:
        page_info = f"第 {item['page']} 页" if item['page'] != "N/A" else "文本"
        piece = f"[本地: {item['source']} | {page_info} | 相关度: {item['score']:.4f}]\n{item['content']}"
        valid_results.append(piece)

    if not valid_results:
        return ""

    return "\n\n".join(valid_results)