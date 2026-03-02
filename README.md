AI-Spider-Defender | 基于行为特征与机器学习的实时爬虫识别系统
项目定位：本科软件工程毕业设计 / 人工智能方向工程实践。

本项目放弃了传统的 IP 黑名单和静态规则库，采用 滑动窗口特征提取 与 XGBoost 机器学习模型。通过对流量数据中的访问频率、时间间隔分布、路径广度等多维行为特征进行建模，实现了对自动化爬虫的毫秒级识别与精准拦截。

 核心技术点
流式特征工程：实现了一个基于内存管理的 5分钟滑动窗口。当单条访问日志进入网关时，系统会实时聚合计算该 IP 的 6 维高阶特征（如访问间隔标准差、URL 熵等），解决了离线批处理的滞后性问题。

模型选型与优化：离线阶段对 Random Forest 与 XGBoost 进行了对比实验，最终选用测试集 AUC 表现更优的 XGBoost 作为核心推理引擎。

异步高性能网关：基于 FastAPI 异步框架开发，利用 BackgroundTasks 将模型推理与日志落库解耦，确保在高并发请求下网关的响应延迟保持在低水平。

实时可视化看板：前端使用 Vue 3 + ECharts 开发，通过异步接口实时拉取拦截数据，展示拦截成功率、高危 IP 动态及攻击趋势图表。

 系统架构
流量仿真：编写模拟脚本模拟“正常用户”与“低/中/高频爬虫”的并发行为，生成带有真实标签的混合访问日志。

特征提炼：从原始的 (IP, Time, URL, UA) 维度转化为 request_count (访问频率)、std_time_interval (时间差标准差) 等结构化特征。

在线推理：FastAPI 网关接收请求，从 Redis/内存中调取滑动窗口特征，输入 XGBoost 模型进行二分类判定。

拦截持久化：识别为爬虫的请求将被拦截，拦截记录与现场特征快照异步存入 SQLite 数据库，供前端展示。


 项目目录结构 (Project Structure)



```text

AI-Spider-Defender/

├── data/

│   └── web\_access\_logs.csv         # 原始模拟流量数据集 (自动生成)

├── src/

│   ├── generate\_data.py            # 数据流生成脚本 (模拟正常用户与爬虫)

│   ├── feature\_engineering.py      # 特征工程脚本 (聚合计算)

│   ├── model\_training.py           # 模型训练与评估对比 (RF vs XGB)

│   ├── app.py                          # FastAPI 流式推理与拦截网关核心代码

│   ├── attack\_simulator.py             # 自动化爬虫攻击模拟脚本 (用于测试防御)

│   ├── xgboost\_crawler\_model.pkl       # 序列化后的 AI 模型

│   └── interception\_logs.db            # SQLite 拦截日志持久化数据库

├── web/

│   └── dashboard.html              # Vue3 + ECharts 可视化拦截大屏

└── README.md                       # 项目说明文档


