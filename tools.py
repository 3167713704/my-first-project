"""
tools.py
定义 Agent 可以调用的两个工具：
1. query_train_tickets —— 查火车票（调聚合数据 API）
2. search_attractions  —— 查景点/地点（调高德地图 API）
"""
from pathlib import Path
import os
import requests
from dotenv import load_dotenv
from langchain_core.tools import tool

load_dotenv()

JUHE_API_KEY = os.getenv("JUHE_API_KEY")
AMAP_API_KEY = os.getenv("AMAP_API_KEY")


@tool
def query_train_tickets(departure_station: str, arrival_station: str, date: str) -> str:
    """查询火车票。输入出发站、到达站、日期（格式 YYYY-MM-DD），返回车次、时间、票价。"""
    url = "https://apis.juhe.cn/fapigw/train/query"
    params = {
        "key": JUHE_API_KEY,
        "search_type": "1",
        "departure_station": departure_station,
        "arrival_station": arrival_station,
        "date": date,
    }
    try:
        resp = requests.get(url, params=params, timeout=15)
        data = resp.json()
        if data.get("error_code") != 0:
            return f"查询失败：{data.get('reason', '未知错误')}"
        return str(data.get("result", {}))
    except Exception as e:
        return f"查询火车票出错：{e}"


@tool
def search_attractions(keywords: str, city: str) -> str:
    """搜索景点、餐厅等地点。输入关键词和城市名，返回地点名称、地址、评分。"""
    url = "https://restapi.amap.com/v3/place/text"
    params = {
        "key": AMAP_API_KEY,
        "keywords": keywords,
        "city": city,
        "offset": 5,
        "page": 1,
        "extensions": "all",
    }
    try:
        resp = requests.get(url, params=params, timeout=15)
        data = resp.json()
        if data.get("status") != "1":
            return f"搜索失败：{data.get('info', '未知错误')}"
        pois = data.get("pois", [])
        if not pois:
            return "没有找到相关地点。"
        results = []
        for p in pois:
            results.append(
                f"{p.get('name')}｜地址：{p.get('address')}｜评分：{p.get('biz_ext', {}).get('rating', '无')}"
            )
        return "\n".join(results)
    except Exception as e:
        return f"搜索地点出错：{e}"
@tool
def validate_dataset(dataset_dir: str) -> str:
    """验证 YOLO 数据集完整性。检查 images/ 和 labels/ 里的文件是否一一对应。"""
    dataset_path = Path(dataset_dir)
    if not dataset_path.exists():
        return f"数据集目录不存在：{dataset_dir}"

    images_dir = dataset_path / "images"
    labels_dir = dataset_path / "labels"

    if not images_dir.exists():
        return f"缺少 images/ 目录：{images_dir}"

    # 收集图片文件
    image_exts = {".jpg", ".jpeg", ".png", ".bmp"}
    images = [p.stem for p in images_dir.rglob("*") if p.suffix.lower() in image_exts]

    # 收集标注文件
    labels = [p.stem for p in labels_dir.rglob("*.txt")] if labels_dir.exists() else []

    # 比对
    missing_labels = set(images) - set(labels)   # 有图无标注
    missing_images = set(labels) - set(images)   # 有标注无图

    # 生成报告
    report = [
        f"数据集验证：{dataset_dir}",
        f"图片数量：{len(images)}",
        f"标注数量：{len(labels)}",
    ]

    if missing_labels:
        report.append(f"⚠️ 有图无标注：{len(missing_labels)} 个")
        for name in list(missing_labels)[:5]:
            report.append(f"  - {name}")
    if missing_images:
        report.append(f"⚠️ 有标注无图：{len(missing_images)} 个")
        for name in list(missing_images)[:5]:
            report.append(f"  - {name}")

    if not missing_labels and not missing_images:
        report.append("✅ 图片和标注一一对应，数据集完整。")

    return "\n".join(report)