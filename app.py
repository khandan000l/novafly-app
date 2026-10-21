import httpx
from fastapi import FastAPI, Request
from fastapi.responses import Response

UPSTREAM = "https://ai-store-fa.nova-14b105.workers.dev"
app = FastAPI()

DROP_REQ = {"host", "content-length", "connection"}
DROP_RES = {"content-length", "transfer-encoding", "connection", "content-encoding"}

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
async def proxy(path: str, req: Request):
    url = UPSTREAM + "/" + path
    if req.url.query:
        url += "?" + req.url.query
    body = await req.body()
    headers = {k: v for k, v in req.headers.items() if k.lower() not in DROP_REQ}
    headers["accept-encoding"] = "gzip"
    try:
        async with httpx.AsyncClient(timeout=120, follow_redirects=False) as client:
            r = await client.request(req.method, url, content=body, headers=headers)
    except Exception:
        return Response(content='{"ok":false,"code":"upstream_down"}', status_code=502, media_type="application/json")
    out = {k: v for k, v in r.headers.items() if k.lower() not in DROP_RES}
    return Response(content=r.content, status_code=r.status_code, headers=out, media_type=r.headers.get("content-type"))
