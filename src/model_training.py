import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_curve, auc
import joblib

# 设置中文字体，防止画图时中文乱码（如果你使用的是 Windows/Mac，可能需要微调字体名称）
plt.rcParams['font.sans-serif'] = ['SimHei']  # Windows用黑体
plt.rcParams['axes.unicode_minus'] = False

def evaluate_model(model_name, y_true, y_pred, y_prob):
    """计算并打印模型评估指标"""
    acc = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred)
    recall = recall_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)
    
    print(f"--- {model_name} 评估结果 ---")
    print(f"准确率 (Accuracy):  {acc:.4f}")
    print(f"精确率 (Precision): {precision:.4f}  (预测为爬虫的IP中，真正是爬虫的比例 - 关乎是否误杀正常用户)")
    print(f"召回率 (Recall):    {recall:.4f}  (真正的爬虫中，被找出来的比例 - 关乎是否漏放爬虫)")
    print(f"F1-Score:           {f1:.4f}\n")
    return acc, precision, recall, f1

def train_and_compare(features_csv):
    # 1. 加载特征数据
    df = pd.read_csv(features_csv)
    
    # 2. 划分特征 (X) 和 标签 (y)
    # 注意：'ip' 是唯一标识符，不能作为特征喂给模型，否则模型会过拟合（死记硬背IP）
    X = df.drop(columns=['ip', 'label'])
    y = df['label']
    
    # 3. 划分训练集和测试集 (80% 训练，20% 测试)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    print(f"训练集大小: {X_train.shape[0]}, 测试集大小: {X_test.shape[0]}")
    
    # ===============================
    # 模型 1：随机森林 (Random Forest)
    # ===============================
    print("正在训练 随机森林 模型...")
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_model.fit(X_train, y_train)
    
    rf_y_pred = rf_model.predict(X_test)
    rf_y_prob = rf_model.predict_proba(X_test)[:, 1] # 获取预测为正类(1)的概率
    evaluate_model("随机森林 (Random Forest)", y_test, rf_y_pred, rf_y_prob)
    
    # ===============================
    # 模型 2：XGBoost
    # ===============================
    print("正在训练 XGBoost 模型...")
    # XGBoost 官方推荐使用 hist 树方法，速度更快
    xgb_model = xgb.XGBClassifier(n_estimators=100, learning_rate=0.1, random_state=42, use_label_encoder=False, eval_metric='logloss')
    xgb_model.fit(X_train, y_train)
    
    xgb_y_pred = xgb_model.predict(X_test)
    xgb_y_prob = xgb_model.predict_proba(X_test)[:, 1]
    evaluate_model("XGBoost", y_test, xgb_y_pred, xgb_y_prob)
    joblib.dump(xgb_model, 'xgboost_crawler_model.pkl')
    print("模型已成功保存为 xgboost_crawler_model.pkl")

    # ===============================
    # 核心亮点：绘制 ROC 曲线对比图 (论文必备)
    # ===============================
    rf_fpr, rf_tpr, _ = roc_curve(y_test, rf_y_prob)
    rf_auc = auc(rf_fpr, rf_tpr)
    
    xgb_fpr, xgb_tpr, _ = roc_curve(y_test, xgb_y_prob)
    xgb_auc = auc(xgb_fpr, xgb_tpr)
    
    plt.figure(figsize=(8, 6))
    plt.plot(rf_fpr, rf_tpr, label=f'Random Forest (AUC = {rf_auc:.3f})', color='blue')
    plt.plot(xgb_fpr, xgb_tpr, label=f'XGBoost (AUC = {xgb_auc:.3f})', color='red')
    plt.plot([0, 1], [0, 1], 'k--', label='Random Guess')
    
    plt.xlabel('False Positive Rate (误判率)')
    plt.ylabel('True Positive Rate (命中率/召回率)')
    plt.title('爬虫识别模型 ROC 曲线对比')
    plt.legend(loc='lower right')
    plt.grid(True, alpha=0.3)
    
    # 保存图片，你可以直接插到毕设论文里
    plt.savefig('roc_comparison.png', dpi=300)
    print("ROC 对比曲线已保存为 roc_comparison.png")
    plt.show()

if __name__ == "__main__":
    # 填入上一节生成的特征文件路径
    train_and_compare('ip_features.csv')