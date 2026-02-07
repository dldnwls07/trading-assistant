from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import api 

app = FastAPI(
    title="Trading Assistant API",
    description="API for providing stock analysis and data.",
    version="0.1.0",
)

# Allow all origins for development purposes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include the router from api.py
app.include_router(api.router, prefix="/api")

@app.get("/")
async def root():
    """
    Root endpoint to check if the server is running.
    """
    return {"message": "Welcome to the Trading Assist API. Go to /docs for documentation."}