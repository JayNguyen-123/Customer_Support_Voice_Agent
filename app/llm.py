import asyncio
import json
import logging
from typing import List, Dict, Any
from anthropic import Anthropic  # Added import
from .config import settings
from .tools import TOOLS, run_tool

logger = logging.getLogger(__name__)

# Correct client initialization
client = Anthropic(api_key=settings.anthropic_api_key)


async def call_claude_with_tools(history: List[Dict[str, Any]]) -> str:
    def _call():
        # Removed trailing comma and fixed 'max_tokens'
        return client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=400,
            tools=TOOLS,  # Ensure this matches Anthropic's tool schema
            messages=history,
        )

    response = await asyncio.to_thread(_call)

    # Save Claude's response to history immediately
    history.append({"role": "assistant", "content": response.content})

    tool_calls = [
        block for block in response.content if block.type == "tool_use"
    ]

    if tool_calls:
        tool_result_blocks = []
        for call in tool_calls:
            result = await run_tool(call.name, call.input)
            tool_result_blocks.append({
                "type": "tool_result",
                "tool_use_id": call.id,
                "content": json.dumps(result),
            })

        # Add tool results back to history
        history.append({"role": "user", "content": tool_result_blocks})

        def _call_final():
            return client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=400,
                messages=history
            )

        final_resp = await asyncio.to_thread(_call_final)
        final_text = "".join(
            block.text for block in final_resp.content if block.type == "text"
        )
        history.append({"role": "assistant", "content": final_text})
        return final_text

    # Default case: no tool use
    text = "".join(block.text for block in response.content if block.type == "text")
    return text
