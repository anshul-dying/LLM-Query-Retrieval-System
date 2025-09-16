from fastapi import FastAPI
from api.routes import documents, queries, analytics
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Bajaj Finserv Hackathon")

# Enable CORS for public access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router, prefix="/api/v1")
app.include_router(queries.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")