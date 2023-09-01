from playsound import playsound
from chatmodules.chatgpt import tts
from speechmodules.wakeword import PicoWakeWord
from speechmodules.speech2text import BaiduASR
import struct
import asyncio
from config import Config

async def run_wake_word_detection(picowakeword):
    print("请说 'hi moss'!")
    while True:
        audio_obj = picowakeword.stream.read(picowakeword.porcupine.frame_length, exception_on_overflow=False)
        audio_obj_unpacked = struct.unpack_from("h" * picowakeword.porcupine.frame_length, audio_obj)
        keyword_idx = picowakeword.porcupine.process(audio_obj_unpacked)
        if keyword_idx >= 0:
            picowakeword.porcupine.delete()
            picowakeword.stream.close()
            picowakeword.myaudio.terminate()
            print("嗯,我在,请讲！")
            playsound("./wakeup.mp3")
            break

async def run_speech_to_text(asr):
    while True:
        q = asr.speech_to_text()
        print(f'识别到的文字, text={q}')
        if not q or "退下" in q:
            break
        else:
            await tts(q)

def Orator():
    picowakeword = PicoWakeWord(Config.PICOVOICE_API_KEY, Config.keyword_path)
    asr = BaiduASR(Config.BD_APP_ID, Config.BD_API_KEY, Config.BD_SECRET_KEY)

    try:
        asyncio.run(run_wake_word_detection(picowakeword))
        asyncio.run(run_speech_to_text(asr))
    except KeyboardInterrupt:
        if picowakeword.porcupine is not None:
            picowakeword.porcupine.delete()
        if picowakeword.stream is not None:
            picowakeword.stream.close()
        if picowakeword.myaudio is not None:
            picowakeword.myaudio.terminate()
        exit(0)
    finally:
        print('本轮对话结束')
        playsound("./wake.mp3")
        try:
            Orator()
        except KeyboardInterrupt:
            exit(0)

if __name__ == '__main__':
    Orator()