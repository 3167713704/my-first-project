import sounddevice as sd
import scipy.io.wavfile as wav

sample_rate = 16000    # DMIC16kHz 原生支持
duration = 5

DEVICE_INDEX = 9       # 对应 hw:1,7 (DMIC16kHz)

print(f"开始录音（{duration} 秒），请对着麦克风说话...")
audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate,
               channels=1, dtype='int16', device=DEVICE_INDEX)
sd.wait()
wav.write("audio.wav", sample_rate, audio)
print("录音结束，已保存为 audio.wav")