from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from generic_pdf_processor.services.pdf_processor import (
    UnknownPdfTaskError,
    process_pdf,
)

app = FastAPI(title="Generic PDF Processor")


@app.get("/ping")
async def ping() -> dict[str, str]:
    return {"message": "pong"}


@app.post("/upload-pdf/")
async def upload_pdf(file: UploadFile, tasks: list[str]) -> StreamingResponse:
    try:
        processed_file = process_pdf(file.file, tasks)
    except UnknownPdfTaskError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return StreamingResponse(
        processed_file,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{file.filename}"',
        },
    )

