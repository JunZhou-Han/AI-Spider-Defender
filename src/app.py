import os
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import pandas as pd
import numpy as np
import time
import sqlite3
import json
from datetime import datetime  # 【新增】引入 Python 本地时间模块

# ==========================================
# 1. 初始化 FastAPI 与 CORS 跨域配置
# ==========================================
app = FastAPI(
    title="基于机器学习的实时流式爬虫识别系统 API",
    description="支持实时特征计算与 SQLite 拦截日志持久化，已修复跨时区 Bug",
    version="3.2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 2. 数据库初始化模块
# ==========================================
DB_FILE = 'interception_logs.db'

def init_db():
    """初始化 SQLite 数据库，创建拦截日志表"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # 【核心修复】：去掉了 DEFAULT CURRENT_TIMESTAMP，改为纯文本存储，由 Python 提供绝对时间
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS blocked_ips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT NOT NULL,
            target_url TEXT,
            user_agent TEXT,
            crawler_probability REAL,
            features_json TEXT,
            intercept_time TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print(f"✅ 数据库初始化完成！文件路径: {DB_FILE}")

init_db()

# ==========================================
# 3. 模型与内存状态初始化
# ==========================================
try:
    model = joblib.load('xgboost_crawler_model.pkl')
    print("✅ XGBoost 模型加载成功！")
except FileNotFoundError:
    print("❌ 警告：未找到 xgboost_crawler_model.pkl 模型文件！请确保已运行训练脚本。")

ip_history_store = {}
TIME_WINDOW_SECONDS = 300  # 5分钟滑动窗口

class RawAccessLog(BaseModel):
    ip: str
    url: str
    user_agent: str

# ==========================================
# 4. 核心功能函数
# ==========================================
def calculate_realtime_features(ip: str) -> dict:
    """从历史记录中提取模型所需特征"""
    history = ip_history_store.get(ip, [])
    if not history: return None
        
    request_count = len(history)
    unique_urls = len(set([item['url'] for item in history]))
    url_diversity = unique_urls / request_count if request_count > 0 else 0
    is_suspicious_ua = max([item['is_suspicious_ua'] for item in history])
    
    if request_count > 1:
        timestamps = [item['timestamp'] for item in history]
        timestamps.sort() 
        time_diffs = np.diff(timestamps)
        avg_time_interval = float(np.mean(time_diffs))
        std_time_interval = float(np.std(time_diffs))
    else:
        avg_time_interval = 0.0
        std_time_interval = 0.0
        
    return {
        'request_count': request_count,
        'unique_urls': unique_urls,
        'url_diversity': url_diversity,
        'avg_time_interval': avg_time_interval,
        'std_time_interval': std_time_interval,
        'is_suspicious_ua': is_suspicious_ua
    }

def clean_old_records(ip: str, current_time: float):
    """清理滑动窗口之外的过期数据"""
    if ip in ip_history_store:
        cutoff_time = current_time - TIME_WINDOW_SECONDS
        ip_history_store[ip] = [record for record in ip_history_store[ip] if record['timestamp'] >= cutoff_time]
        if not ip_history_store[ip]:
            del ip_history_store[ip]

def save_to_database(ip: str, url: str, ua: str, prob: float, features: dict):
    """将拦截记录异步写入 SQLite"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        features_str = json.dumps(features) 
        
        # 【核心修复】：强行使用 Python 获取系统当前的本地时间，格式化为字符串存入
        local_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute('''
            INSERT INTO blocked_ips (ip, target_url, user_agent, crawler_probability, features_json, intercept_time)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (ip, url, ua, prob, features_str, local_time))
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"❌ 数据库写入失败: {e}")

# ==========================================
# 5. API 路由接口
# ==========================================
@app.post("/api/v1/track_and_detect")
async def track_and_detect(log: RawAccessLog, background_tasks: BackgroundTasks):
    current_time = time.time()
    
    suspicious_keywords = ['python', 'requests', 'curl', 'bot', 'spider']
    is_suspicious_ua = 1 if any(kw in log.user_agent.lower() for kw in suspicious_keywords) else 0
    
    if log.ip not in ip_history_store:
        ip_history_store[log.ip] = []
    ip_history_store[log.ip].append({"timestamp": current_time, "url": log.url, "is_suspicious_ua": is_suspicious_ua})
    
    background_tasks.add_task(clean_old_records, log.ip, current_time)
    
    features = calculate_realtime_features(log.ip)
    
    df_features = pd.DataFrame([features])
    try:
        crawler_probability = float(model.predict_proba(df_features)[0][1])
    except Exception as e:
        print(f"模型预测出错: {e}")
        crawler_probability = 0.0

    is_crawler = bool(crawler_probability > 0.6) 
    
    if is_crawler:
        background_tasks.add_task(
            save_to_database, 
            log.ip, log.url, log.user_agent, crawler_probability, features
        )
    
    return {
        "code": 200,
        "ip": log.ip,
        "crawler_probability": round(crawler_probability, 4),
        "action": "BLOCK" if is_crawler else "ALLOW"
    }

@app.get("/api/v1/blocked_logs")
async def get_blocked_logs(limit: int = 15):
    """前端大屏拉取拦截日志的接口"""
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row 
        cursor = conn.cursor()
        # 按 id 倒序排列，确保拉到的是最新插入的数据
        cursor.execute('SELECT * FROM blocked_ips ORDER BY id DESC LIMIT ?', (limit,))
        rows = cursor.fetchall()
        conn.close()
        return {"code": 200, "data": [dict(row) for row in rows]}
    except Exception as e:
        return {"code": 500, "message": str(e), "data": []}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)