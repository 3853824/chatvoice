import pvporcupine
import pyaudio
import struct
import asyncio

PICOVOICE_API_KEY = "Zi94o/VlkBMGKtF99VSqdPlO34A9Bt1kUsG1i93FhG48hwjhdC7uGQ=="
keyword_path = 'hi-moss_en_windows_v2_1_0.ppn'


class PicoWakeWord:
    def __init__(self, PICOVOICE_API_KEY, keyword_path):

        self.PICOVOICE_API_KEY = PICOVOICE_API_KEY
        self.keyword_path = keyword_path
        self.porcupine = pvporcupine.create(
            access_key=self.PICOVOICE_API_KEY,
            keyword_paths=[self.keyword_path]
        )
        self.myaudio = pyaudio.PyAudio()
        self.stream = self.myaudio.open(
            input_device_index=0,
            rate=self.porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=self.porcupine.frame_length
        )

    async def detect_wake_word(self):
        while True:
            audio_obj = self.stream.read(self.porcupine.frame_length, exception_on_overflow=False)
            audio_obj_unpacked = struct.unpack_from("h" * self.porcupine.frame_length, audio_obj)
            keyword_idx = self.porcupine.process(audio_obj_unpacked)
            if keyword_idx >= 0:
                print("我听到了！")


if __name__ == '__main__':
    picowakeword = PicoWakeWord(PICOVOICE_API_KEY, keyword_path)
    try:
        asyncio.run(picowakeword.detect_wake_word())
    except KeyboardInterrupt:
        pass