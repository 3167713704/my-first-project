"""
agent.py
LangGraph 的核心文件：把模型、工具、节点、边组合成一张图。

整体流程：
    用户输入 → agent 节点（思考）→ 判断要不要调工具？
                                    ├─ 要 → tools 节点（执行）→ 回到 agent
                                    └─ 不要 → 结束，输出回答
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import SystemMessage

from state import TravelState
from tools import query_train_tickets, search_attractions
from yolo_tools import detect_objects

load_dotenv()

# ============================================================
# 1. 初始化模型
# 用智谱 GLM-4-Flash（免费），兼容 OpenAI 接口格式
# ============================================================
llm = ChatOpenAI(
    base_url="https://open.bigmodel.cn/api/paas/v4",
    api_key=os.getenv("ZHIPU_API_KEY"),
    model="glm-4-flash",
    temperature=0,      # 0 表示输出尽量稳定、不随机发挥
    timeout=60,         # 超时 60 秒
)

# ============================================================
# 2. 把工具绑定到模型
# 三个工具：查火车票、查景点、图片检测
# ============================================================
tools = [query_train_tickets, search_attractions, detect_objects]
llm_with_tools = llm.bind_tools(tools)

# ============================================================
# 3. 系统提示词
# ============================================================
SYSTEM_PROMPT = """你是一位专业的智能旅行规划师。

# 工具调用规则
- 遇到火车票查询，调用 query_train_tickets
- 遇到景点、餐厅搜索，调用 search_attractions
- 遇到图片检测请求，调用 detect_objects，输入图片路径
- 所有信息必须来自工具返回结果，严禁编造

# 强制规则
- 只要用户提供了出发站、到达站、日期，就立即调用 query_train_tickets 工具，不要反问用户，直接返回查询结果
- 只要用户提供了城市名，就立即调用 search_attractions 工具，不要反问用户想了解什么类型
- 只要用户提供了图片路径，就立即调用 detect_objects 工具，直接返回检测结果

# 当前日期
当前日期是 2026年10月9日。用户说日期但没带年份时，默认按 2026 年处理。
"""

# ============================================================
# 4. Agent 节点（"接待员"）
# ============================================================
def agent_node(state: TravelState):
    messages = state["messages"]

    # 如果第一条不是 system 提示词，就补上
    if not messages or messages[0].type != "system":
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages

    # 把整个对话历史发给模型
    response = llm_with_tools.invoke(messages)

    # 把模型的回复追加到 messages 里
    return {"messages": [response]}

# ============================================================
# 5. 工具节点（"跑腿员"）
# ToolNode 自动执行工具，把结果追加到 messages
# ============================================================
tool_node = ToolNode(tools)

# ============================================================
# 6. 建图
# ============================================================
workflow = StateGraph(TravelState)

workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)

workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", tools_condition)
workflow.add_edge("tools", "agent")

# ============================================================
# 7. 编译
# ============================================================
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)