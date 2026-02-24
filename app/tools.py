
from typing import Dict, Any
from . import db, jira

TOOLS = [
    {
        "name": "lookup_order",
        "description": "Loop up an order in the company database.",
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string"},
            },
            "required": ["order_id"],
        },
    },
    {
        "name": "create_ticket",
        "description": "Create a Jira support ticket for the customer.",
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_phone": {"type": "string"},
                "issue_description": {"type": "string"},
            },
            "required": ["customer_phone", "issue_description"]
        },
    },
]

async def run_tool(name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
    if name == "lookup_order":
        return await db.lookup_order(tool_input["order_id"])
    if name == "create_ticket":
        return await jira.create_ticket(
            customer_phone=tool_input["customer_phone"],
            issue_description=tool_input["issue_description"],
        )
    return {"error": f"Unknown tool: {name}"}
