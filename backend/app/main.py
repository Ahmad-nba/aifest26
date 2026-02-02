from fastapi import FastAPI

app = FastAPI(title="AI Fest – Malaria Risk Agent")

@app.get("/health")
def health():
    return {"status": "ok"}
