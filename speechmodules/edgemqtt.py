import asyncio
import os
import pygame
import pygame.mixer
from typing import List
import paho.mqtt.client as mqtt

import edge_tts
from config import Config


class Speech:
    def __init__(self, voice: str = "zh-CN-XiaoyiNeural", rate: str = "+0%", volume: str = "+0%") -> None:
        self.audio_queue = asyncio.Queue()
        self.consumer_task = asyncio.create_task(self.audio_consumer())
        self.play_tasks = []
        self.voice = voice
        self.rate = rate
        self.volume = volume
        self.stop_requested = False  # Flag to indicate if stop was requested

    async def process_audio_stream(self, idx, stream):
        if not stream:
            await self.audio_queue.put((idx, None))
            return

        audio_bytes: List[bytes] = []

        async for msg in stream:
            if msg["type"] == "audio" and (data := msg["data"]):
                audio_bytes.append(data)
                if self.stop_requested:  # Check if stop was requested
                    break
        await stream.aclose()
        if len(audio_bytes) > 10:
            audio_bytes = audio_bytes[1:-5]
        await self.audio_queue.put((idx, b"".join(audio_bytes)))

    def get_stream(self, text):
        return edge_tts.Communicate(text, self.voice).stream()

    async def wait_for_play(self):
        await asyncio.gather(*self.play_tasks)
        await self.do_speak(len(self.play_tasks), "<END>")
        await self.consumer_task

    async def audio_consumer(self):
        expected_idx = 0
        while True:
            idx, audio_data = await self.audio_queue.get()
            if not audio_data and self.audio_queue.qsize() == 0:
                Config.REPLYING = False
                break
            if expected_idx != idx:
                # 下标不对，放回
                await asyncio.sleep(0.1)
                await self.audio_queue.put((idx, audio_data))
                continue
            try:
                file_path = f"audio_{expected_idx}.mp3"  # Save audio to disk
                with open(file_path, "wb") as audio_file:
                    audio_file.write(audio_data)
                await self.play_audio(file_path)
                os.remove(file_path)  # Remove the audio file
            except Exception as e:
                print(f"Exception during audio processing: {e}")
            expected_idx += 1

    async def play_audio(self, file_path):
        pygame.mixer.init()  # Initialize the mixer
        pygame.mixer.music.load(file_path)  # Load the audio file
        pygame.mixer.music.play()  # Play the audio

        while pygame.mixer.music.get_busy():
            if self.stop_requested:  # Check if stop was requested
                pygame.mixer.music.stop()
                break
            await asyncio.sleep(0.1)  # Wait for the audio to finish playing

        pygame.mixer.quit()  # Quit the mixer

    async def do_speak(self, idx, text):
        end_marker = "<END>"
        if text == end_marker:
            stream = None
        else:
            stream = self.get_stream(text)
        await self.process_audio_stream(idx, stream)

    def speak_text(self, idx, text):
        if not text:
            return
        task = asyncio.create_task(self.do_speak(idx, text))
        self.play_tasks.append(task)

    def stop_playback(self):
        self.stop_requested = True
        for task in self.play_tasks:
            task.cancel()
        self.play_tasks = []


async def te():
    sp = Speech()

    def on_message(client, userdata, msg):
        # Handle received MQTT message
        text = msg.payload.decode("utf-8")
        idx = msg.topic  # Use the MQTT topic as the index
        sp.speak_text(idx, text)

    # MQTT connection details
    mqtt_broker = "1307.wgb888.xyz"
    mqtt_port = 1883
    mqtt_username = "jsfer888"  # Update with your MQTT username
    mqtt_password = "wuguibing888"  # Update with your MQTT password

    # MQTT topic to subscribe
    mqtt_topic = "mqtt/voice"  # Update with your MQTT topic

    # Create MQTT client and set the callback
    client = mqtt.Client()
    client.username_pw_set(mqtt_username, mqtt_password)
    client.on_message = on_message

    # Connect to MQTT broker and subscribe to the topic
    client.connect(mqtt_broker, mqtt_port, 60)
    client.subscribe(mqtt_topic)

    # Start MQTT event loop
    client.loop_start()

    # Stop playback after a certain duration
    await asyncio.sleep(7)
    sp.stop_playback()

    await sp.wait_for_play()

    # Disconnect MQTT client
    client.loop_stop()
    client.disconnect()


if __name__ == "__main__":
    asyncio.run(te())