import pandas as pd
import numpy as np

def extract_features(input_csv, output_csv):
    print(f"正在读取原始日志：{input_csv}")
    df = pd.read_csv(input_csv)
    
    # 1. 数据预处理：转换时间格式，并按 IP 和 时间 排序
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values(by=['ip', 'timestamp'])
    
    # 2. 计算时间间隔 (Time Interval)
    # 计算同一个 IP 上下两条日志的时间差（秒）
    df['time_diff'] = df.groupby('ip')['timestamp'].diff().dt.total_seconds()
    # 填补空值（每个 IP 的第一次访问没有时间差，设为 0）
    df['time_diff'] = df['time_diff'].fillna(0)
    
    # 3. 提取可疑 User-Agent 特征
    # 如果 UA 里有常见的代码库或爬虫工具，标记为 1，否则为 0
    suspicious_keywords = ['python', 'requests', 'curl', 'wget', 'urllib', 'bot', 'spider']
    df['is_suspicious_ua'] = df['user_agent'].str.lower().apply(
        lambda x: 1 if any(keyword in str(x) for keyword in suspicious_keywords) else 0
    )
    
    # 4. 按 IP 进行聚合，构建特征矩阵 (Group By IP)
    print("正在进行特征聚合计算...")
    grouped = df.groupby('ip')
    
    features = pd.DataFrame()
    features['request_count'] = grouped['timestamp'].count()
    features['unique_urls'] = grouped['url'].nunique()
    features['url_diversity'] = features['unique_urls'] / features['request_count']
    features['avg_time_interval'] = grouped['time_diff'].mean()
    features['std_time_interval'] = grouped['time_diff'].std().fillna(0) # 只有一个请求的 IP 标准差为 NaN，填补为 0
    
    # 对于 UA 和 标签，我们取该 IP 的最大值（只要用过一次可疑 UA 就记为 1；只要带了爬虫标签就是爬虫）
    features['is_suspicious_ua'] = grouped['is_suspicious_ua'].max()
    features['label'] = grouped['label'].max()
    
    # 5. 整理并保存特征矩阵
    features = features.reset_index() # 把 ip 重新变成普通列
    features.to_csv(output_csv, index=False)
    
    print(f"特征提取完毕！共提取了 {len(features)} 个独立 IP 的特征。")
    print(f"特征矩阵已保存至：{output_csv}")
    
    # 预览特征
    print("\n特征矩阵预览：")
    # 设置 pandas 显示所有列，方便在终端查看
    pd.set_option('display.max_columns', None) 
    print(features.head())

if __name__ == "__main__":
    # 假设你的原始日志叫 web_access_logs.csv，生成的特征文件叫 ip_features.csv
    extract_features('web_access_logs.csv', 'ip_features.csv')