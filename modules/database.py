import os
import chromadb
import uuid

# 数据库存储路径
DB_PATH = "./chroma_db"


def get_collection():
    """初始化并获取 Chroma 集合"""
    client = chromadb.PersistentClient(path=DB_PATH)
    collection = client.get_or_create_collection(
        name="knowledge_base",
        metadata={"hnsw:space": "cosine"}
    )
    return collection


def add_to_db(chunks, vectors):
    """存入数据"""
    collection = get_collection()
    if not chunks: return 0

    ids = [str(uuid.uuid4()) for _ in chunks]
    documents = [chunk["content"] for chunk in chunks]
    metadatas = [{"source": c["source"], "page": str(c.get("page", "N/A"))} for c in chunks]

    collection.add(
        ids=ids,
        embeddings=vectors.tolist(),
        metadatas=metadatas,
        documents=documents
    )
    return len(ids)


def query_db(query_vector, top_k=10):
    """查询数据"""
    collection = get_collection()
    results = collection.query(
        query_embeddings=[query_vector.tolist()],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )

    processed_results = []
    if not results["documents"]: return []

    for i in range(len(results["documents"][0])):
        distance = results["distances"][0][i]
        similarity = 1 - distance
        doc = results["documents"][0][i]
        meta = results["metadatas"][0][i]

        processed_results.append({
            "content": doc,
            "source": meta["source"],
            "page": meta["page"],
            "score": similarity
        })
    return processed_results


def reset_db():
    """清空整个库"""
    client = chromadb.PersistentClient(path=DB_PATH)
    try:
        client.delete_collection("knowledge_base")
    except:
        pass


# 🟢 新增：获取所有文件名
def get_all_files():
    collection = get_collection()
    # 获取 metadata，数据量大时需优化，目前适用
    data = collection.get(include=["metadatas"])
    if not data or not data["metadatas"]:
        return []
    files = set([m["source"] for m in data["metadatas"]])
    return sorted(list(files))


# 🟢 新增：删除指定文件
def delete_file_from_db(filename):
    collection = get_collection()
    try:
        collection.delete(where={"source": filename})
        return True
    except Exception as e:
        print(f"删除失败: {e}")
        return False