import discord
import json
import openai
import requests
from config import *

openai.api_key = OPENAI_API_KEY


def split_message(message: str) -> list[str]:
    messages = []
    while len(message) > 2000:
        index = message[:2000].rfind('\n')
        if index == -1:
            index = message[:2000].rfind(' ')
            if index == -1:
                index = 1999
        messages.append(message[:index])
        message = message[index+1:]
    messages.append(message)
    return messages


async def translation(message: str, lang: str):
    completion = openai.ChatCompletion.create(
        model=MODEL,
        messages=[{'role': 'system', 'content': f'translate to {lang}'}, {
            'role': 'user', 'content': message}]
    )
    return completion.choices[0].message.content


async def Voice(voice: discord.VoiceClient, voice_id: int, message: str):
    jp = await translation(message, 'japanese')
    print(f'translation: {jp}')
    speak('127.0.0.1', 50021, jp, voice_id, 'temp')
    voice.play(discord.FFmpegPCMAudio(
        source='temp',
        executable='C:/ffmpeg/bin/ffmpeg.exe')
    )


def speak(host, port, text: str, speaker: int, filename='temp'):

    params = (
        ("text", text),
        ("speaker", speaker)
    )

    init_q = requests.post(
        f"http://{host}:{port}/audio_query",
        params=params
    )

    res = requests.post(
        f"http://{host}:{port}/synthesis",
        headers={"Content-Type": "application/json"},
        params=params,
        data=json.dumps(init_q.json())
    )

    with open(filename, 'wb') as f:
        f.write(res.content)


async def make_completion(data: dict, message: str) -> str:
    history: list = data['history']
    history.append({'role': 'user', 'content': message})
    if len(history) > data['limit']:
        history = history[-data['limit']:]

    completion = openai.ChatCompletion.create(
        model=MODEL,
        messages=[
            {'role': 'system', 'content': data['prompt']}] + data['history']
    )
    reply: str = completion.choices[0].message.content
    history.append({"role": "assistant", "content": reply})
    data['history'] = history
    return reply
