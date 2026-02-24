import asyncio
import json
import websockets
from typing import AsyncIterator
from deepgram import DeepgramClient, LiveTranscriptionEvents, LiveOptions
from .config import settings

DEEPGRAM_API_KEY = settings.deepgram_api_key  # add to .env

async def stt_stream(audio_chunks: AsyncIterator[bytes]) -> AsyncIterator[str]:
    """
    Streams audio chunks to Deepgram and yields transcripts in real time.
    """

    dg = DeepgramClient(DEEPGRAM_API_KEY)

    # Queue for transcripts coming back from Deepgram
    transcript_queue = asyncio.Queue()

    # Deepgram event handlers
    def on_transcript(event, result, **kwargs):
        if result.channel.alternatives:
            text = result.channel.alternatives[0].transcript
            if text.strip():
                transcript_queue.put_nowait(text)

    # Create Deepgram live connection
    dg_socket = dg.listen.live.v("1")

    dg_socket.on(LiveTranscriptionEvents.Transcript, on_transcript)

    options = LiveOptions(
        model="nova-2-phonecall",
        encoding="mulaw",
        sample_rate=8000,
        channels=1,
        punctuate=True,
        interim_results=True,
    )

    await dg_socket.start(options)

    async def send_audio():
        async for chunk in audio_chunks:
            await dg_socket.send(chunk)
        await dg_socket.finish()

    sender = asyncio.create_task(send_audio())

    while True:
        try:
            text = await transcript_queue.get()
            yield text
        except asyncio.CancelledError:
            break

    await sender


import base64
import websockets
from typing import AsyncIterator
from .config import settings

ELEVEN_API_KEY = settings.elevenlabs_api_key  # add to .env
ELEVEN_VOICE_ID = "Rachel"  # or any voice you prefer

async def tts_stream(text: str) -> AsyncIterator[bytes]:
    """
    Streams TTS audio from ElevenLabs as raw PCM bytes.
    """

    url = (
        f"wss://api.elevenlabs.io/v1/text-to-speech/{ELEVEN_VOICE_ID}/stream"
        f"?optimize_streaming_latency=2"
    )

    headers = {
        "xi-api-key": ELEVEN_API_KEY,
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
    }

    async with websockets.connect(url, extra_headers=headers) as ws:
        await ws.send(
            json.dumps(
                {
                    "text": text,
                    "voice_settings": {
                        "stability": 0.4,
                        "similarity_boost": 0.8,
                    },
                }
            )
        )

        async for msg in ws:
            # ElevenLabs sends binary audio frames
            if isinstance(msg, bytes):
                yield msg
