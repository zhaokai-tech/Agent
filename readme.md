# 🤖 DeepSeek Pro 智能知识库 (Hybrid RAG Agent)

这是一个基于 **DeepSeek-V3** 的全能型科研助手。它采用了 **Hybrid RAG（混合检索增强生成）** 架构，结合了 **ChromaDB 本地向量库**、**Rerank 重排序技术** 以及 **Tavily 联网搜索**，能够精准地回答基于本地文档或互联网的问题。

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-red)
![DeepSeek](https://img.shields.io/badge/DeepSeek-V3-purple)

## ✨ 核心功能

* **🧠 深度思考可视化**：实时展示 AI 的思考路径（检索 -> 排序 -> 联网 -> 生成）。
* **📚 精准本地 RAG**：
    * 支持 PDF / Word 文档批量上传。
    * **Recall + Rerank 双层检索**：先粗排 Top-50，再经由 BGE-Reranker/智谱 Rerank 精选 Top-5，精度极高。
    * **持久化存储**：基于 ChromaDB，数据写入硬盘，重启不丢失。
* **🌍 联网增强模式**：本地查不到？自动调用 Tavily 搜索全网最新信息（如 2024-2025 年技术）。
* **💾 完备的历史管理**：
    * 自动保存对话历史。
    * 支持“来源回溯”：在历史记录中也能查看当时引用的原文片段。
* **🛠️ 极客控制台**：
    * 文件粒度管理（可查看、删除特定文件）。
    * 高级参数微调（Temperature, Top-K 等）。

## 📂 项目结构

```text
reading_Agent/
├── .streamlit/
│   └── secrets.toml        # [关键] 存放 API 密钥配置文件
├── history_data/           # [自动生成] 存放对话历史 JSON
├── chroma_db/              # [自动生成] 向量数据库文件
├── modules/                # 核心功能模块
│   ├── database.py         # ChromaDB 增删改查
│   ├── embedder.py         # Embedding API 封装
│   ├── reranker.py         # Rerank API 封装
│   ├── retriever.py        # 混合检索逻辑
│   ├── processor.py        # 文档解析与切分
│   ├── web_search.py       # 联网搜索模块
│   └── history.py          # 历史记录管理
├── app.py                  # Streamlit 主程序入口
├── requirements.txt        # 项目依赖
└── README.md               # 说明文档
🚀 快速开始
1. 安装依赖
确保你安装了 Python 3.8+，然后在终端运行：

Bash
pip install -r requirements.txt
2. 配置密钥
在项目根目录下创建文件夹 .streamlit，并在其中新建文件 secrets.toml。 填入你的 API Key（这是项目运行的灵魂）：

Ini, TOML
# .streamlit/secrets.toml

# 1. 大模型 (DeepSeek)
DEEPSEEK_API_KEY = "sk-xxxxxxxxxxxxxxxx"
DEEPSEEK_BASE_URL = "[https://api.deepseek.com](https://api.deepseek.com)"

# 2. Embedding 模型 (推荐智谱 / 硅基流动)
EMBEDDING_API_KEY = "your_zhipu_or_siliconflow_key"
EMBEDDING_BASE_URL = "[https://open.bigmodel.cn/api/paas/v4/](https://open.bigmodel.cn/api/paas/v4/)" 
EMBEDDING_MODEL = "embedding-2"

# 3. Rerank 模型 (推荐硅基流动 BAAI/bge-reranker-v2-m3)
RERANK_API_KEY = "your_siliconflow_key"
RERANK_BASE_URL = "[https://api.siliconflow.cn/v1/rerank](https://api.siliconflow.cn/v1/rerank)"
RERANK_MODEL = "BAAI/bge-reranker-v2-m3"

# 4. 联网搜索 (Tavily)
TAVILY_API_KEY = "tvly-xxxxxxxxxxxxxxxx"
3. 启动应用
在终端运行：

Bash
streamlit run app.py
浏览器会自动打开 http://localhost:8501，即可开始使用！

💡 使用指南
上传文档：在侧边栏上传 PDF 论文，点击“🚀 存入知识库”。

提问：

科研模式：将 Temperature 调至 0.1，AI 会严格引用文中原话。

创意模式：将 Temperature 调至 0.8，开启联网，获取发散性思路。

查看来源：AI 回答后，点击下方的 📖 查看引用片段 折叠框，核对事实。

管理文件：上传错了？在侧边栏“文件管理”中点击 🗑️ 删除对应文件即可。

📋 注意事项
Rerank 报错？ 如果遇到 Rerank API 报错，请检查 secrets.toml 中的模型名称是否正确，或者确认该服务商是否仍提供免费额度。

ChromaDB 版本：首次运行时会自动下载相关依赖，请保持网络通畅。