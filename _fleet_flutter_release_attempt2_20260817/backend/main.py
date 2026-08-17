from fastapi import FastAPI
app = FastAPI(title="_fleet_flutter_release_attempt2_20260817")
@app.get("/api/health")
def health():
    return {"status": "ok"}