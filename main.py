from fastapi import FastAPI

from controller import studentController

app = FastAPI()

#导入子路由
app.include_router(studentController.stu_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8001)