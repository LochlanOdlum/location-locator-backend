from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI

from .api.routes import auth, homes, locations, users
from .utils.database import Base, engine

# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Location Locator API")

# Include Routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(locations.router)
app.include_router(homes.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Lochlan's Location Locator API"}
