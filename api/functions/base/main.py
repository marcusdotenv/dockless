from fastapi import FastAPI
from function import handle

app = FastAPI()

@app.get("/")
def health_check():
    return {"up": True}

@app.post("/execute")
async def execute(body: dict):
    print("Starting executing function...")
    result = handle(**body)
    print("Finishing executing function...")

    return result
    