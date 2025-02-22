from fastapi import FastAPI
from function import handle

app = FastAPI()

@app.get("/")
def health_check():
    return {"up": True}

@app.post("/execute")
async def execute():
    print("Starting executing function...")
    handle()
    print("Finishing executing function...")