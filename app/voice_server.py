import asyncio
import base64
import json
import logging
from typing import AsyncIterator, List, Dict, Any

import websockets

from .config import settings
from .stt_tts import stt_stream, tts_stream
from .llm import call_claude_with_tools

logger = logging.getLogger(__name__)
async def _incoming_audio(websocket) -> AsyncIterator[bytes]:
    caller_phone = None
    async for message in websocket:
        data = json.loads(message)

        event = data.get("event")
        if event == "start":
            caller_phone = (
                data.get("start", {})
                .get("customerParameters", {})
                .get("caller_phone")
            )
            logger.info(f"Call started, caller_phone={caller_phone}")
        elif event == "media":
            payload = data["media"]["payload"]
            yield base64.b16decode(payload)
        elif event == "stop":
            logger.info("Call stopped")
            break

async def handler_twilio_stream(websocket):
    logger.info("Twilio client connected")

    history: List[Dict[str, Any]] = [
        {
            "role": "system",
            "content": (
                "You are a customer support voice agent for ABC.\n"
                "- You can look up orders using the lookup_order tool.\n"
                "- You can create support tickets using the create_ticket tool.\n"
                "- Always confirm key details with the caller.\n"
                "- Speak in short, clear sentences suitable for phone audio.\n"
            ),
        }
    ]

    async for user_text in stt_stream(_incoming_audio(websocket)):
        if not user_text:
            continue
        logger.info(f"Caller: {user_text}")
        history.append({"role": "user", "content": user_text})

        try:
            reply_text = await call_claude_with_tools(history)
        except Exception as e:
            logger.exception(f"LLM error: {e}")
            reply_text = (
                " I'm having trouble accessing our system right now."
                "Let me transfer you to a human agent."
            )
        logger.info(f"Agent: {reply_text}")

        async for audio_chunk in tts_stream(reply_text):
            await websocket.send(
                json.dumps(
                    {
                        "event": "media",
                        "media": {
                            "payload": base64.b64encode(audio_chunk).decode()
                        }
                    }
                )
            )

async def start_server():
    server = await websockets.serve(
        handler_twilio_stream, settings.server_host, settings.server_port
    )
    logger.info(
        f"Voice agent server running on ws://{settings.server_host}: {settings.server_port}"
    )
    await server.wait_closed()

import aiohttp.web

async def health(request):
    return aiohttp.web.Response(text="OK")

def create_app():
    app = aiohttp.web.Application()
    app.router.add_get("/health", health)
    return app

