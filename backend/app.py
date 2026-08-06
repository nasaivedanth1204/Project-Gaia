from fastapi import FastAPI

from routes import (
    analyze_routes,
    assess_routes,
    classify_routes,
    identify_routes,
    preprocess_routes,
    status_routes,
    upload_routes,
)

app = FastAPI(
    title="Project Gaia - eDNA Biodiversity Backend",
    description=(
        "Prototype backend pipeline for taxonomic identification and "
        "biodiversity assessment from eDNA datasets (SIH hackathon prototype)."
    ),
    version="0.1.0-prototype",
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
    }
