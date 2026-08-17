from fastapi import FastAPI
app = FastAPI(title="_live_flutter_verification_20260817")
@app.get("/api/health")
def health():
    return {"status": "ok"}