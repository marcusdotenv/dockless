from fastapi import FastAPI
from function import handle

app = FastAPI()

@app.post("/execute")
async def execute():
    print("Starting executing function...")
    handle()
    print("Finishing executing function...")