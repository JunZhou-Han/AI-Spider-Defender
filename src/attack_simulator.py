import requests
import time
import random

# 我们 FastAPI 后端的接口地址
API_URL = "http://127.0.0.1:8000/api/v1/track_and_detect"

def send_request(ip, url, user_agent):
    """发送单次请求并打印结果"""
    payload = {
        "ip": ip,
        "url": url,
        "user_agent": user_agent
    }
    
    try:
        # 发送 POST 请求到我们的检测接口
        response = requests.post(API_URL, json=payload)
        result = response.json()
        
        # 为了在终端看效果更明显，我们做点颜色高亮 (适用于大多数终端)
        action = result.get("action")
        prob = result.get("crawler_probability", 0)
        
        if action == "BLOCK":
            # 红色高亮显示拦截
            print(f"[\033[91m拦截 BLOCK\033[0m] IP: {ip} | 爬虫概率: {prob:.4f} | 目标: {url}")
            return True # 返回 True 表示已经被拦截了
        else:
            # 绿色高亮显示放行
            print(f"[\033[92m放行 ALLOW\033[0m] IP: {ip} | 爬虫概率: {prob:.4f} | 目标: {url}")
            return False
            
    except Exception as e:
        print(f"请求失败: {e}")
        return False

def simulate_normal_user():
    """模拟正常用户：看网页很慢，时间间隔长，使用正常浏览器"""
    print("\n" + "="*50)
    print("开始模拟【正常用户】访问...")
    print("="*50)
    
    ip = "192.168.1.100" # 正常用户 IP
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    
    for i in range(5):
        url = f"/article/{random.randint(1, 20)}"
        send_request(ip, url, user_agent)
        
        # 正常人看一篇文章需要几秒钟
        sleep_time = random.uniform(2.0, 5.0)
        print(f"  -> 正常用户正在阅读，停留 {sleep_time:.1f} 秒...")
        time.sleep(sleep_time)

def simulate_crawler_attack():
    """模拟疯狂爬虫：毫秒级并发，固定间隔，携带可疑 UA"""
    print("\n" + "="*50)
    print("开始模拟【疯狂爬虫】攻击！(注意观察概率飙升和拦截动作)")
    print("="*50)
    
    ip = "203.0.113.50" # 恶意爬虫 IP
    # 嚣张的爬虫，直接用默认库的 UA
    user_agent = "python-requests/2.28.1" 
    
    for i in range(20):
        url = f"/data/api/page_{i}"
        
        is_blocked = send_request(ip, url, user_agent)
        
        if is_blocked:
            print(f"\n\033[91m!!! 攻击受挫，爬虫已被系统成功封杀 !!!\033[0m")
            # 真实场景中，如果被拦截（比如返回了 403 或验证码），爬虫往往会报错或停止
            break 
            
        # 爬虫的请求间隔极短，且方差极小（固定 0.1 秒）
        time.sleep(0.1)

if __name__ == "__main__":
    # 1. 先跑一个正常用户，证明系统不会乱杀无辜
    simulate_normal_user()
    
    # 等待两秒，分割一下日志
    time.sleep(2)
    
    # 2. 释放爬虫，测试系统的实时防守能力
    simulate_crawler_attack()