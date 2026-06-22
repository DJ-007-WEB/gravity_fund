from fastapi import FastAPI

app = FastAPI(
    title="Gravity Fund API",
    description="Quantitative Retail Wealth Optimization Platform",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {"message": "Welcome to Gravity Fund API"}
