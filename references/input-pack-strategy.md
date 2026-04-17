# Input Pack Strategy

> 目标：将单章输入包拆成两条轨道，分别服务模型与人工。

## 一、模型输入版
- 目标：低 token、可直接喂给模型
- 默认只带：summary / packet / style overlay / object state summary
- 不主动展开完整对象卡

## 二、人工审阅版
- 目标：给人快速核对本章准备状态
- 除核心输入外，增加 active indexes
- 适合人在正式开写前做快速检查

## 三、为什么要双轨
同一个输入包同时满足模型和人工，往往会两边都不够好。
所以分成：
- 模型输入版：更轻
- 人工审阅版：更完整
