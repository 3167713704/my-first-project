"""
voice_asr.py
录音（按回车开始/停止）+ 通义云端 ASR 识别。
"""

import threading
import numpy as np
import sounddevice as sd
import scipy.io.wavfile as wav
import dashscope
from dashscope.audio.asr import Recognition
from http import HTTPStatus

# 你的通义 API Key
dashscope.api_key = "sk-ws-H.PEHYDPE.8er9.MEUCIBCJY02BK58hPdacOR0Uo1ZrKrQ_XgL-F_HaMn5BfBtFAiEAl_MZ-hCHbeIi9-Ws4j8cdTf7VLY7ikmawER96IFpLdY"


def record_audio(filename="audio.wav", sample_rate=16000, device=9):
    """
    按回车开始录音，再按回车停止。
    适合说长句子（火车票查询等），不受固定时长限制。
    """
    print("按回车开始录音...")
    input()

    print("录音中... 说完后按回车停止")
    audio_chunks = []

    def callback(indata, frames, time, status):
        audio_chunks.append(indata.copy())

    stream = sd.InputStream(
        samplerate=sample_rate,
        channels=1,
        dtype='int16',
        device=device,
        callback=callback,
    )
    stream.start()
    input()          # 等用户再按一次回车
    stream.stop()
    stream.close()

    audio = np.concatenate(audio_chunks, axis=0)
    wav.write(filename, sample_rate, audio)
    print(f"录音结束，已保存为 {filename}")
    return filename


def transcribe(filename):
    """用通义实时识别接口转写音频文件。"""
    recognition = Recognition(
        model="paraformer-realtime-v2",
        format="wav",
        sample_rate=16000,
        callback=None,
    )
    result = recognition.call(filename)

    if result.status_code == HTTPStatus.OK:
        sentences = result.get_sentence()
        if sentences:
            return sentences[0].get("text", "")
        return ""
    else:
        return f"识别失败：{result.message}"


if __name__ == "__main__":
    audio_file = record_audio()
    print("正在识别...")
    text = transcribe(audio_file)
    print("识别结果：", text)