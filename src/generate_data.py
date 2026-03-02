import pandas as pd
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()

def generate_normal_user_logs(num_users=50):
    """模拟正常用户行为"""
    logs = []
    base_time = datetime.now() - timedelta(days=1) # 从昨天开始模拟
    
    for _ in range(num_users):
        ip = fake.ipv4()
        user_agent = fake.user_agent()
        num_requests = random.randint(3, 15) # 一个正常用户通常看几个页面就走了
        current_time = base_time + timedelta(minutes=random.randint(0, 1440))
        
        for _ in range(num_requests):
            # 正常用户的时间间隔：较长且随机性大 (5秒到60秒)
            sleep_time = random.uniform(5, 60)
            current_time += timedelta(seconds=sleep_time)
            
            # 正常用户的访问路径：偏好首页或随机文章
            url = random.choice(['/index', '/category/tech', f'/article/{random.randint(1, 100)}'])
            
            logs.append([ip, current_time.strftime("%Y-%m-%d %H:%M:%S"), url, user_agent, 0])
            
    return logs

def generate_crawler_logs(num_crawlers=5):
    """模拟爬虫行为"""
    logs = []
    base_time = datetime.now() - timedelta(days=1)
    
    for _ in range(num_crawlers):
        ip = fake.ipv4()
        # 爬虫可能伪装不好，或者频繁更换
        use_default_ua = random.choice([True, False]) 
        current_time = base_time + timedelta(minutes=random.randint(0, 1440))
        
        # 爬虫的抓取量大
        num_requests = random.randint(50, 200) 
        
        for i in range(num_requests):
            # 爬虫的时间间隔：极短 (0.1秒到1秒) 或者 极度固定
            sleep_time = random.uniform(0.1, 1.0)
            current_time += timedelta(seconds=sleep_time)
            
            # 爬虫的路径：通常是深度遍历
            url = f'/article/{i+1}'
            
            user_agent = "python-requests/2.26.0" if use_default_ua else fake.user_agent()
            
            logs.append([ip, current_time.strftime("%Y-%m-%d %H:%M:%S"), url, user_agent, 1])
            
    return logs

if __name__ == "__main__":
    print("开始生成数据...")
    normal_logs = generate_normal_user_logs(num_users=200) # 生成200个正常用户
    crawler_logs = generate_crawler_logs(num_crawlers=20)  # 生成20个爬虫
    
    # 合并数据并打乱顺序 (模拟真实的无序日志流)
    all_logs = normal_logs + crawler_logs
    random.shuffle(all_logs)
    
    # 转为 Pandas DataFrame 并保存
    df = pd.DataFrame(all_logs, columns=['ip', 'timestamp', 'url', 'user_agent', 'label'])
    
    # 按时间戳重新排序，这才是真实的日志按时间发生的顺序
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values(by='timestamp').reset_index(drop=True)
    
    # 保存到 data 目录下
    df.to_csv('web_access_logs.csv', index=False)
    print(f"数据生成完毕！共 {len(df)} 条日志。文件已保存为 web_access_logs.csv")
    
    # 打印前几行看看样子
    print("\n数据预览：")
    print(df.head())