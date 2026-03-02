\# 🛡️ AI-Spider-Defender | 基于行为特征与机器学习的实时爬虫识别系统



!\[Python](https://img.shields.io/badge/Python-3.9+-blue.svg)

!\[FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)

!\[XGBoost](https://img.shields.io/badge/AI\_Model-XGBoost-orange.svg)

!\[Vue](https://img.shields.io/badge/Frontend-Vue3-4fc08d.svg)

!\[License](https://img.shields.io/badge/License-MIT-lightgrey.svg)



> \*\*本项目为本科软件工程毕业设计及人工智能方向工程实践项目。\*\*

> 

> 本系统彻底抛弃了传统的“IP封禁”和“验证码”等静态反爬手段，创新性地引入了 \*\*滑动窗口流式计算\*\* 与 \*\*XGBoost 机器学习算法\*\*。通过对网关流量中的时间特征、频率特征和路径特征进行多维提取，实现了对高并发恶意爬虫的毫秒级、无感式精准拦截。



---



\## ✨ 核心亮点 (Core Features)



\- 🧠 \*\*多模型对比与调优\*\*：离线端使用海量模拟日志，横向对比了 Random Forest 与 XGBoost 算法，最终采用 AUC 表现更优的 XGBoost 作为核心推理引擎。

\- ⏱️ \*\*流式滑动窗口特征工程\*\*：在线端彻底告别“离线批处理”，基于内存状态管理实现了 `5分钟滑动窗口`，当单条孤立日志到来时，动态且实时地计算其时间差方差、路径广度等高阶聚合特征。

\- ⚡ \*\*高并发异步落库架构\*\*：基于 FastAPI 框架，将 AI 推理与数据持久化解耦。主线程保证网关的极低延迟，利用 `BackgroundTasks` 异步队列完成 SQLite 拦截日志与现场特征快照的落库。

\- 📊 \*\*沉浸式实时态势感知大屏\*\*：前端采用 `Vue 3 + ECharts + TailwindCSS` 构建，支持大屏级的实时拦截率监控与高危 IP 动态滚屏展示。



---



\## 🏗️ 系统架构设计 (Architecture)



1\. \*\*数据采集与生成\*\*：底层编写自动化脚本，模拟正常用户与极客爬虫的并发行为，生成带有真实标签的混合网关日志。

2\. \*\*特征提炼\*\*：从原始的 `(IP, Time, URL, UA)` 提炼出 `request\_count`, `std\_time\_interval` (时间间隔标准差) 等 6 维核心防爬特征。

3\. \*\*模型训练\*\*：基于 Scikit-learn 和 XGBoost 训练分类器，并序列化导出 `.pkl` 模型。

4\. \*\*在线流式推理\*\*：FastAPI 提供高性能的实时 `/detect` 接口，配合模拟攻击脚本上演自动化攻防。

5\. \*\*监控面板\*\*：纯静态前端通过跨域 API 异步拉取拦截记录，驱动大屏图表渲染。



---



\## 📂 项目目录结构 (Project Structure)



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

