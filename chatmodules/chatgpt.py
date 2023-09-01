import asyncio
import openai
from config import Config
from speechmodules.wakeword import PicoWakeWord
from .utils import CircularConversation, contains_delimiter
from speechmodules.edge_tts_stream import Speech

openai.api_key = Config.OPENAI_API_KEY
openai.api_base = Config.OPENAI_API_BASE
PREVIOUS_CONVERSATIONS = CircularConversation(Config.OPENAI_PREVIOUS_MESSAGES_COUNT + 1)


def build_conversation_context(text):
    Config.REPLYING = True
    messages = [
        {"role": "system", "content": Config.OPENAI_SYSTEM_PROMPT},
    ]
    PREVIOUS_CONVERSATIONS.push_ask({"role": "user", "content": text})
    messages.extend(PREVIOUS_CONVERSATIONS)
    return messages


async def build_sentence_from_stream(async_stream, limit_sentences=True) -> str:
    reply, words, idx = [], [], 0
    sentence_count = 0
    speech = Speech(voice=Config.voice)

    async for choice in async_stream:
        content: str

        if content := choice["delta"].get("content"):
            words.append(content.replace("\n", "", 1))

        is_complete_sentence = contains_delimiter(content) and len(words) > 10
        reply_finished = choice["finish_reason"] == "stop"

        if (sentence_count < 4 or not limit_sentences) and (is_complete_sentence or reply_finished):
            sentence = "".join(words).replace("\n\n", "\n")
            print(sentence, end="", flush=True)
            speech.speak_text(idx, sentence)
            reply.append(sentence)
            idx += 1
            words.clear()
            sentence_count += 1
        elif sentence_count >= 4 and reply_finished:
            break

    if words:
        sentence = "".join(words).replace("\n\n", "\n")
        print(sentence, end="", flush=True)
        speech.speak_text(idx, sentence)
        reply.append(sentence)

    await speech.wait_for_play()
    return "".join(reply)


def save_reply(raw_reply):
    reply = {"role": "assistant", "content": raw_reply}
    PREVIOUS_CONVERSATIONS.push_reply(reply)


async def build_async_stream(messages):
    stream = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.6,
        max_tokens=2048,
        stream=True,
    )
    for word in stream:
        yield await asyncio.to_thread(lambda: word["choices"][0])


async def tts(text, limit_sentences=True):
    Config.REPLYING = True
    messages = build_conversation_context(text)
    print("Reply: ", end="", flush=True)
    async_stream = build_async_stream(messages)
    reply = await build_sentence_from_stream(async_stream, limit_sentences)

    if Config.OPENAI_PREVIOUS_MESSAGES_SAVE_REPLY:
        save_reply(reply)


if __name__ == "__main__":
    while True:
        text = input("\nQuestion: ")
        asyncio.run(tts(text))