from fastapi import FastAPI
from app.api import auth, bidding

app = FastAPI()

app.include_router(auth.router, prefix="", tags=["authentication"])
app.include_router(bidding.router, prefix="/bidding-room", tags=["bidding rooms"])