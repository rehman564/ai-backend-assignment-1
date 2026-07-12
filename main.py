from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to my smallest Python backend!"}

@app.get("/status")
def read_status():
    return {"status": "running", "language": "Python"}