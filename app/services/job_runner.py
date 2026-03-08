import httpx


async def run_job(job_type: str, payload: dict) -> dict:
    if job_type == "http_check":
        url = payload["url"]
        expected_status = payload.get("expected_status", 200)

        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(url)

        if r.status_code != expected_status:
            raise ValueError(f"Expected status {expected_status}, got {r.status_code}")

        return {
            "url": url,
            "status_code": r.status_code,
        }

    if job_type == "page_snapshot":
        url = payload["url"]

        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(url)

        if r.status_code >= 400:
            raise ValueError(f"HTTP {r.status_code}")

        return {
            "url": url,
            "length": len(r.text),
        }

    if job_type == "keyword_watch":
        url = payload["url"]
        keyword = payload["keyword"]
        expected_status = payload.get("expected_status", 200)

        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(url)

        if r.status_code != expected_status:
            raise ValueError(f"Expected status {expected_status}, got {r.status_code}")

        found = keyword.lower() in r.text.lower()

        return {
            "url": url,
            "keyword": keyword,
            "found": found,
            "status_code": r.status_code,
        }

    raise ValueError(f"Unknown job type: {job_type}")