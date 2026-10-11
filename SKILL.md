---
name: travel-agent-skill
description: >
  智能旅游助手，能查火车票、查景点、检测图片。
  当用户说"查火车票"、"北京到上海"、"成都有哪些景点"、
  "检测这张图"时激活此 skill。
---

# 智能旅游 Agent Skill

把旅游规划、火车票查询、景点搜索、图片检测整合成一个 Agent 能调用的技能包。

## 能力清单

| 能力 | 工具名 | 触发条件 |
|------|--------|----------|
| 查火车票 | `query_train_tickets` | 用户提到出发地、目的地、日期 |
| 查景点 | `search_attractions` | 用户提到城市名 + 景点/餐厅 |
| 图片检测 | `detect_objects` | 用户提到图片路径或"检测" |

## 使用示例

### 查火车票
用户："帮我查一下2026年10月15号北京到上海的火车票"
→ 调用 `query_train_tickets(departure_station="北京", arrival_station="上海", date="2026-10-15")`

### 查景点
用户："成都有哪些景点适合老人"
→ 调用 `search_attractions(city="成都", keywords="适合老人景点")`

### 图片检测
用户："帮我检测一下 ./test_image.jpg 这张图里有什么"
→ 调用 `detect_objects(image_path="./test_image.jpg")`

## 输出格式

- **查票**：车次、出发到达时间、票价
- **查景点**：名称、地址、评分
- **检测**：物体名称、置信度

## 强制规则

- 只要用户提供了出发站、到达站、日期 → **立即调用** `query_train_tickets`，不要反问
- 只要用户提供了城市名 → **立即调用** `search_attractions`，不要反问
- 只要用户提供了图片路径 → **立即调用** `detect_objects`
- 所有信息必须来自工具返回结果，**严禁编造**

## 当前日期

当前日期是 2026年10月9日。用户说日期但没带年份时，默认按 2026 年处理。

## 入口

- 文字输入：`python3 main.py`
- 语音输入：`python3 voice_main.py`