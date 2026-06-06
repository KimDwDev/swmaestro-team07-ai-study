from fastapi import FastAPI

app = FastAPI()

# 테스트 url
@app.get("/test")
def home():
    return {"message": "fastapi 테스트"}