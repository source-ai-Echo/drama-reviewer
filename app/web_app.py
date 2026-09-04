from __future__ import annotations

import io
import json
import zipfile
from pathlib import Path
from xml.etree import ElementTree

import uvicorn
from starlette.applications import Starlette
from starlette.datastructures import UploadFile
from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse
from starlette.routing import Route
from starlette.staticfiles import StaticFiles

from agent import review_text
from knowledge import get_corpus
from main import friendly_error
from providers import ProviderConfig, provider_catalog


APP_ROOT = Path(__file__).resolve().parent
WEB_ROOT = APP_ROOT / "web"
MAX_UPLOAD_BYTES = 20 * 1024 * 1024


def _no_store(response: JSONResponse | FileResponse) -> JSONResponse | FileResponse:
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response


def _docx_from_bytes(data: bytes) -> str:
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        xml = archive.read("word/document.xml")
    root = ElementTree.fromstring(xml)
    namespace = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    paragraphs: list[str] = []
    for paragraph in root.iter(namespace + "p"):
        text = "".join(node.text or "" for node in paragraph.iter(namespace + "t"))
        if text.strip():
            paragraphs.append(text.strip())
    return "\n".join(paragraphs)


async def _material_from_form(form: object) -> str:
    upload = form.get("file")  # type: ignore[attr-defined]
    pasted = str(form.get("text", "")).strip()  # type: ignore[attr-defined]
    if isinstance(upload, UploadFile) and upload.filename:
        data = await upload.read(MAX_UPLOAD_BYTES + 1)
        if len(data) > MAX_UPLOAD_BYTES:
            raise ValueError("文件超过20MB，请先拆分后上传。")
        suffix = Path(upload.filename).suffix.lower()
        if suffix in {".txt", ".md"}:
            return data.decode("utf-8")
        if suffix == ".docx":
            return _docx_from_bytes(data)
        raise ValueError("目前支持 .txt、.md 和 .docx 文件。")
    if pasted:
        return pasted
    raise ValueError("请上传剧本文件，或粘贴剧本文字。")


async def home(_: Request) -> FileResponse:
    return _no_store(FileResponse(WEB_ROOT / "index.html"))  # type: ignore[return-value]


async def health(_: Request) -> JSONResponse:
    payload = {
        "status": "ok",
        "service": "Drama Reviewer Agent",
        "knowledge": get_corpus().policy_summary(),
    }
    return _no_store(JSONResponse(payload))  # type: ignore[return-value]


async def providers(_: Request) -> JSONResponse:
    return _no_store(JSONResponse(provider_catalog()))  # type: ignore[return-value]


async def review(request: Request) -> JSONResponse:
    try:
        form = await request.form(max_files=1, max_fields=20, max_part_size=MAX_UPLOAD_BYTES)
        material = await _material_from_form(form)
        provider_name = str(form.get("provider", "openai")).strip().lower()
        model = str(form.get("model", "")).strip()
        base_url = str(form.get("base_url", "")).strip() or None
        api_key = str(form.get("api_key", "")).strip() or None
        if provider_name != "local" and not api_key:
            raise ValueError("请填写你自己的 API Key；网页不会读取或保存项目中的密钥。")
        api_mode = "responses" if provider_name == "openai" else "chat_completions"
        config = ProviderConfig.from_environment(
            provider=provider_name,
            model=model,
            base_url=base_url,
            api_key_env="WEB_REQUEST_API_KEY_DO_NOT_READ_FROM_ENV",
            api_mode=api_mode,
        )
        config = ProviderConfig(
            provider=config.provider,
            model=config.model,
            base_url=config.base_url,
            api_key_env=config.api_key_env,
            api_mode=config.api_mode,
            tools_enabled=config.tools_enabled,
            api_key=api_key,
        )
        report = await review_text(
            material,
            title=str(form.get("title", "未命名项目")).strip() or "未命名项目",
            material_type=str(form.get("material_type", "自动判断")).strip() or "自动判断",
            concerns=str(form.get("concerns", "未指定")).strip() or "未指定",
            provider_config=config,
        )
        return _no_store(
            JSONResponse(
                {
                    "ok": True,
                    "markdown": report.to_markdown(),
                    "report": report.model_dump(mode="json"),
                    "provider": config.safe_summary(),
                }
            )
        )  # type: ignore[return-value]
    except Exception as exc:
        return _no_store(JSONResponse({"ok": False, "error": friendly_error(exc)}, status_code=400))  # type: ignore[return-value]


routes = [
    Route("/", home),
    Route("/health", health),
    Route("/api/providers", providers),
    Route("/api/review", review, methods=["POST"]),
]

app = Starlette(debug=False, routes=routes)
app.mount("/static", StaticFiles(directory=WEB_ROOT / "static"), name="static")


def run_server(host: str = "127.0.0.1", port: int = 8765) -> None:
    uvicorn.run(app, host=host, port=port, log_level="warning")
