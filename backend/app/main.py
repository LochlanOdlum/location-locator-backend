from dotenv import load_dotenv
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

load_dotenv()

from .api.routes import auth, geocode, homes, locations, users
from .utils.database import Base, engine

# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Location Locator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Include Routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(locations.router)
app.include_router(homes.router)
app.include_router(geocode.router)


@app.get("/")
def read_root():
    print("Request received")
    return {"message": "Welcome to Lochlan's Location Locator API"}
