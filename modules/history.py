# modules/history.py
import os
import json
import uuid
from datetime import datetime
import streamlit as st

# 历史记录存储路径
HISTORY_DIR = "history_data"


def init_history_dir():
    """确保存储目录存在"""
    if not os.path.exists(HISTORY_DIR):
        os.makedirs(HISTORY_DIR)


def save_chat(chat_id, messages):
    """保存当前对话到 JSON 文件"""
    if not messages:
        return

    init_history_dir()

    # 提取第一条用户消息作为标题，如果没消息则叫"新对话"
    title = "新对话"
    for msg in messages:
        if msg["role"] == "user":
            title = msg["content"][:20] + "..."  # 截取前20个字
            break

    filepath = os.path.join(HISTORY_DIR, f"{chat_id}.json")

    data = {
        "id": chat_id,
        "title": title,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "messages": messages
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_chat(chat_id):
    """读取指定 ID 的对话记录"""
    filepath = os.path.join(HISTORY_DIR, f"{chat_id}.json")
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("messages", [])
    return []


def get_history_list():
    """获取所有历史记录列表（按时间倒序）"""
    init_history_dir()
    history_list = []

    files = os.listdir(HISTORY_DIR)
    for f in files:
        if f.endswith(".json"):
            filepath = os.path.join(HISTORY_DIR, f)
            try:
                with open(filepath, "r", encoding="utf-8") as file:
                    data = json.load(file)
                    history_list.append({
                        "id": data.get("id"),
                        "title": data.get("title", "未知对话"),
                        "timestamp": data.get("timestamp", "")
                    })
            except:
                continue

    # 按时间戳倒序排列（最新的在最前）
    history_list.sort(key=lambda x: x["timestamp"], reverse=True)
    return history_list


def delete_chat(chat_id):
    """删除指定对话"""
    filepath = os.path.join(HISTORY_DIR, f"{chat_id}.json")
    if os.path.exists(filepath):
        os.remove(filepath)