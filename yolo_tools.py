"""
yolo_tools.py
YOLO 目标检测工具，带多规则过滤 + 难例收集 + 结果可视化 + 耗时统计。
"""

import time
import shutil
from pathlib import Path

import cv2
import yaml
from ultralytics import YOLO
from langchain_core.tools import tool


def load_config(config_path="config.yaml"):
    """读取 config.yaml，返回配置字典。"""
    path = Path(config_path)
    if not path.exists():
        print(f"警告：{config_path} 不存在，使用默认配置")
        return {
            "detection": {
                "conf_threshold": 0.5,
                "min_area_ratio": 0.005,
                "max_area_ratio": 0.8,
                "max_aspect_ratio": 5,
                "min_pixel_size": 30,
            },
            "hard_case": {
                "min_conf": 0.3,
                "max_conf": 0.65,
                "output_dir": "hard_cases",
            },
        }
    return yaml.safe_load(path.read_text())


CFG = load_config()
DET_CFG = CFG["detection"]
HC_CFG = CFG["hard_case"]

yolo_model = YOLO("yolov8n.pt")

HARD_CASE_DIR = Path(HC_CFG["output_dir"])
HARD_CASE_DIR.mkdir(exist_ok=True)


@tool
def detect_objects(image_path: str) -> str:
    """目标检测工具。输入图片路径，返回检测到的物体名称和置信度。"""
    results = yolo_model(
    image_path,
    imgsz=DET_CFG.get("imgsz", 640),
    device=DET_CFG.get("device", "cpu"),
)

    # ========== 读取 ultralytics 统计的真实推理耗时 ==========
    speed = results[0].speed
    elapsed_ms = (
        speed.get("preprocess", 0)
        + speed.get("inference", 0)
        + speed.get("postprocess", 0)
    )

    detections = []
    hard_cases = []

    orig_h, orig_w = results[0].orig_shape
    img_area = orig_h * orig_w

    for box in results[0].boxes:
        conf = float(box.conf)
        cls_name = yolo_model.names[int(box.cls)]

        # 难例收集
        if HC_CFG["min_conf"] <= conf < HC_CFG["max_conf"]:
            hard_cases.append(f"{cls_name}({conf:.2f})")

        # 规则 1：置信度过滤
        if conf < DET_CFG["conf_threshold"]:
            continue

        x1, y1, x2, y2 = box.xyxy[0].tolist()
        bw = x2 - x1
        bh = y2 - y1
        area = bw * bh
        ratio = area / img_area

        # 规则 2：小目标
        if ratio < DET_CFG["min_area_ratio"]:
            continue
        # 规则 3：大目标
        if ratio > DET_CFG["max_area_ratio"]:
            continue
        # 规则 4：长宽比
        aspect = max(bw, bh) / min(bw, bh) if min(bw, bh) > 0 else 999
        if aspect > DET_CFG["max_aspect_ratio"]:
            continue
        # 规则 5：像素
        if bw < DET_CFG["min_pixel_size"] or bh < DET_CFG["min_pixel_size"]:
            continue

        detections.append(f"{cls_name}({conf:.2f})")

    # ========== 保存可视化结果图 ==========
    if detections:
        annotated = results[0].plot()
        output_path = f"detected_{Path(image_path).stem}.jpg"
        cv2.imwrite(output_path, annotated)
        print(f"结果图已保存到 {output_path}")


        # ========== 保存难例 ==========
    if hard_cases:
        timestamp = int(time.time() * 1000)
        dst = HARD_CASE_DIR / f"hard_{timestamp}.jpg"
        try:
            shutil.copy(image_path, dst)
            # 追加到难例日志
            with open(HARD_CASE_DIR / "hard_cases.txt", "a") as f:
                f.write(f"{dst.name}: {', '.join(hard_cases)}\n")
            # 生成通知
            print(f"\n⚠️ 发现 {len(hard_cases)} 个难例：{', '.join(hard_cases)}")
            print(f"   已保存到 {dst}")
            print(f"   请人工复核后，加入下一轮训练集。\n")
        except Exception as e:
            print(f"保存难例失败：{e}")
    # ========== 返回结果（带真实推理耗时） ==========
    if not detections:
        return f"未检测到任何物体（推理耗时 {elapsed_ms:.0f} ms）。"
    return f"检测到：{', '.join(detections)}（推理耗时 {elapsed_ms:.0f} ms）"