"""
main.py
运行入口：支持多种模式（文字问答、图片检测、语音输入）。
"""

import argparse
from langchain_core.messages import HumanMessage
from agent import app


def run(query: str):
    """执行一次完整的 Agent 流程。"""
    config = {"configurable": {"thread_id": "test-1"}}
    print(f"\n用户：{query}\n")

    for event in app.stream(
        {"messages": [HumanMessage(content=query)]},
        config,
        stream_mode="values",
    ):
        last = event["messages"][-1]

        if last.type == "ai" and last.content and not last.tool_calls:
            print(f"AI：{last.content}\n")
        elif last.type == "ai" and last.tool_calls:
            print(f"[调用工具] {[t['name'] for t in last.tool_calls]}\n")
        elif last.type == "tool":
            print(f"[工具返回] {last.content[:200]}...\n")


def main():
    parser = argparse.ArgumentParser(description="智能旅游 Agent")
    parser.add_argument(
        "--mode",
        choices=["chat", "detect", "voice"],
        default="chat",
        help="运行模式：chat=文字问答，detect=图片检测，voice=语音输入",
    )
    parser.add_argument("--input", default="", help="输入内容（问题或图片路径）")
    args = parser.parse_args()

    if args.mode == "chat":
        query = args.input or "成都哪些景点适合老人"
        run(query)

    elif args.mode == "detect":
        image_path = args.input or "./test_image.jpg"
        run(f"帮我检测一下 {image_path} 这张图里有什么")

    elif args.mode == "voice":
        from voice_main import main as voice_main
        voice_main()


if __name__ == "__main__":
    main()