import httpx


def send_discord_webhook(
    webhook_url: str,
    *,
    username: str,
    embeds: list[dict],
) -> None:
    if not webhook_url:
        return

    payload = {
        "username": username,
        "embeds": embeds,
    }

    with httpx.Client(timeout=10) as client:
        response = client.post(webhook_url, json=payload)
        response.raise_for_status()