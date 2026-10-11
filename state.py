"""
state.py
定义整个 Agent 流程的"共享状态"。
所有节点（agent、tools）都读写这个 State。
"""

from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import MessagesState
from operator import add


class TravelState(MessagesState):
    """
    旅游 Agent 的共享状态。

    继承 MessagesState，它自带一个 messages 字段，
    专门用来存对话历史（用户说的、AI 说的、工具返回的，按顺序存在这里）。

    下面这些字段是我们自己加的，用来存结构化的旅行信息。
    目前代码里还没真正用到，是为了后续扩展预留的。
    """
    user_query: str      # 用户原始问题（比如"帮我查火车票"）
    departure: str       # 出发地（比如"北京"）
    destination: str     # 目的地（比如"成都"）
    date: str            # 出发日期（格式 2026-10-15）
    train_info: str      # 查到的车次信息（原始 JSON 或文本）
    final_plan: str      # 最终生成的完整行程