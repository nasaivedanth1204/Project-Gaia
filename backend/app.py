from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from routes import (
    analyze_routes,
    assess_routes,
    classify_routes,
    identify_routes,
    preprocess_routes,
    status_routes,
    upload_routes,
)

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

app = FastAPI(
    title="Project Gaia - eDNA Biodiversity Backend",
    description=(
        "Prototype backend pipeline for taxonomic identification and "
        "biodiversity assessment from eDNA datasets (SIH hackathon prototype)."
    ),
    version="0.1.0-prototype",
)

# Prototype has no auth and is not deployed; a permissive policy keeps the
# UI usable when it is opened straight from disk or served on another port.
# TODO: Restrict allow_origins before any non-local deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_routes.router)
app.include_router(preprocess_routes.router)
app.include_router(identify_routes.router)
app.include_router(classify_routes.router)
app.include_router(assess_routes.router)
app.include_router(analyze_routes.router)
app.include_router(status_routes.router)


@app.get("/", tags=["Root"])
def root():
    return {
        "service": "Project Gaia eDNA Biodiversity Backend",
        "status": "running",
        "docs": "/docs",
        "ui": "/ui" if FRONTEND_DIR.is_dir() else None,
    }


# Serve the prototype UI alongside the API so there is no separate dev
# server or build step. Mounted last so it cannot shadow any API route.
if FRONTEND_DIR.is_dir():
    app.mount("/ui", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="ui")
