from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.router import api_router
from models.database import engine, Base
from middleware.rate_limiter import limiter
from monitoring.sentry import init_sentry
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
import models.user
import models.opportunity
import models.company_profile
import models.past_performance

Base.metadata.create_all(bind=engine)
init_sentry()

app = FastAPI(title="GovPreneurs API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to GovPreneurs API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
