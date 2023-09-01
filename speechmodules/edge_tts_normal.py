

#调用方式

#from speechmodules.edge_tts_normal import EdgeTTS_N
#tts = EdgeTTS_N(voice = Config.voice)
#asyncio.run(tts.text_to_speech_and_play("我先退下喽！有事儿您叫我"))


import pygame # 导入pygame，playsound报错或运行不稳定时直接使用
import asyncio

import edge_tts



class EdgeTTS_N():
    def __init__(self, voice: str = "zh-CN-XiaoyiNeural", rate: str = "+0%", volume: str = "+0%"):
        self.voice = voice
        self.rate = rate
        self.volume = volume


#常规播放TTS
    async def text_to_speech_and_play(self, text):
        communicate = edge_tts.Communicate(text, self.voice)
        await communicate.save('./audio.mp3')
        # playsound('./audio.wav') # playsound无法运行时删去此行改用pygame，若正常运行择一即可
        self.play_audio_with_pygame('audio.mp3')  # 注意pygame只能识别mp3格式


    def play_audio_with_pygame(self, audio_file_path):
        pygame.mixer.init()
        pygame.mixer.music.load(audio_file_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.quit()


if __name__ == '__main__':

    edgetts = EdgeTTS_N()
    asyncio.run(edgetts.text_to_speech_and_play("嗯,我在,请讲！"))

