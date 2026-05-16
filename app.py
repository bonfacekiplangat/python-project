from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello from the Cloud!", "status": "Live"}

@app.get("/calculate/{val}")
def add_ten(val: int):
    # Just a simple logic example
    return {"result": val + 10}