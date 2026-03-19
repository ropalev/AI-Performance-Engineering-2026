from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from starlette.responses import JSONResponse

from api import router

app = FastAPI(title="GitHub Repository Summarizer")
app.include_router(router)



@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "message": exc.detail},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
