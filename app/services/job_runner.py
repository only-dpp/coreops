<<<<<<< HEAD
import httpx

async def run_job(job_type: str, payload: dict) -> dict:
    if job_type == "http_check":
        url = payload["url"]
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(url)
        return {"url": url, "status_code": r.status_code}

    if job_type == "page_snapshot":
        url = payload["url"]
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(url)
        return {"url": url, "length": len(r.text)}

    if job_type == "keyword_watch":
        url = payload["url"]
        keyword = payload["keyword"]
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(url)
        found = keyword.lower() in r.text.lower()
        return {"url": url, "keyword": keyword, "found": found}

=======
import httpx

async def run_job(job_type: str, payload: dict) -> dict:
    if job_type == "http_check":
        url = payload["url"]
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(url)
        return {"url": url, "status_code": r.status_code}

    if job_type == "page_snapshot":
        url = payload["url"]
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(url)
        return {"url": url, "length": len(r.text)}

    if job_type == "keyword_watch":
        url = payload["url"]
        keyword = payload["keyword"]
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(url)
        found = keyword.lower() in r.text.lower()
        return {"url": url, "keyword": keyword, "found": found}

>>>>>>> 21599b0b39eba37876fc43d9838497fbe2974000
    raise ValueError(f"Unknown job type: {job_type}")