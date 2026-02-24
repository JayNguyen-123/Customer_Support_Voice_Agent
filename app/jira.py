import logging
from typing import Dict, Any
import httpx
from config import settings

logger = logging.getLogger(__name__)


async def create_ticket(customer_phone: str, issue_description: str) -> Dict[str, Any]:
    url = f"{settings.jira_base}/rest/api/3/issue"
    payload = {
        "fields": {
            "project": {"key": settings.jira_project_key},
            "summary": f"Voice Support Ticket from {customer_phone}",
            "description": issue_description,
            "issuetype": {"name": "Task"},
        }
    }

    auth = (settings.jira_email, settings.jira_api_token)

    async with httpx.AsyncClient(timeout=10.0) as client:
        for attempt in range(3):
            try:
                resp = await client.post(
                    url,
                    json=payload,
                    auth=auth,
                    headers={
                        "Accept": "application/json",
                        "Content-Type": "application/json",
                    },
                )


                # Check for an unsuccessful status code (e.g., 4xx or 5xx)
                if resp.status_code >= 300:
                    logger.error(
                        "Jira error %s: %s", resp.status_code, resp.text[:500]
                    )
                    return {
                        "error": f"Jira error {resp.status_code}",
                        "details": resp.text,
                    }

                # If the code reaches here, the request was successful (e.g., 201 Created)
                data = resp.json()
                return {
                    "ticket_id": data.get("key"),
                    "url": f"{settings.jira_base}/browse/{data.get('key')}",
                    "status": "created",
                }
            except Exception as e:
                logger.warning(f"Jira request attempt {attempt + 1} failed: {e}")
        return {"error": "Failed to create Jira ticket after retries"}
