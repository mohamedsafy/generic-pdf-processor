from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse

import tasks.pdf_watermark as tasks_pdf_watermark

app = FastAPI()

@app.get("/ping")
async def ping():
    return {"message": "pong"}

@app.post("/upload-pdf/")
async def upload_pdf(file: UploadFile, tasks: list[str]):
    content = file.file
    ret_file, status_code, task = await process_pdf(content, tasks)
    
    if status_code != 200:
        raise HTTPException(status_code=404, detail=f"Task '{task}' was not found")
    
    return StreamingResponse(ret_file, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename={file.filename}"})



async def process_pdf(file: File, tasks: list[str]):
    ret_file = None

    for task in tasks:
        if task == "add_watermark":
            ret_file = tasks_pdf_watermark.add_watermark(file)
        else:
            return file, 404, task
        
        
    return file, 200, "no_task" if not tasks else ret_file


'''test_pdf_file_obj = io.BytesIO()
with open("sample.pdf", "rb") as f:
    test_pdf_file_obj.write(f.read())


processed_pdf = process_pdf(test_pdf_file_obj)

with open("processed_sample.pdf", "wb") as f:
    f.write(processed_pdf.read())'''