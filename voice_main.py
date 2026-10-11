"""
voice_main.py
语音输入入口：录音 → 转文字 → 传给 Agent。
"""

from voice_asr import record_audio, transcribe


def main():
    """录音 → 识别 → 传给 Agent。"""
    # 延迟导入，避免循环导入
    from main import run

    # 1. 录音 + 识别
    audio_file = record_audio()
    text = transcribe(audio_file)
    print(f"你说的是：{text}")

    # 2. 把识别结果传给 Agent
    run(text)


if __name__ == "__main__":
    main()