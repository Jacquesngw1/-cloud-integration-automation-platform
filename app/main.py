from contextlib import asynccontextmanager
from typing import Any, Dict, List

import httpx
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import transform as transformer
from .database import engine, get_db
from .models import Base, Post

EXTERNAL_API_URL = "https://jsonplaceholder.typicode.com/posts"


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Create database tables on startup."""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Cloud Integration Automation Platform",
    description="A production-ready API integration platform that fetches, "
    "transforms, and stores data across services.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/", tags=["health"])
def root() -> Dict[str, str]:
    """Health-check endpoint."""
    return {"status": "ok", "service": "Cloud Integration Automation Platform"}


async def _fetch_and_transform() -> List[Dict[str, Any]]:
    """Fetch raw data from the external API and return transformed records."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(EXTERNAL_API_URL)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=502,
                detail=f"External API returned {exc.response.status_code}",
            ) from exc
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=503,
                detail=f"Could not reach external API: {exc}",
            ) from exc

    return transformer.transform_posts(response.json())


@app.get("/fetch-data", tags=["pipeline"])
async def fetch_data() -> Dict[str, Any]:
    """Fetch data from the external API and return it transformed.

    Calls the upstream posts API, normalises every record through the
    transformation layer, and returns the result without persisting it.
    """
    transformed = await _fetch_and_transform()
    return {"status": "success", "count": len(transformed), "data": transformed}


@app.post("/store-data", status_code=201, tags=["pipeline"])
async def store_data(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Fetch data from the external API, transform it, and persist to PostgreSQL.

    Already-existing records (matched by ``external_id``) are skipped so that
    the endpoint is safe to call multiple times (idempotent inserts).  All new
    records are written in a single transaction for efficiency.
    """
    transformed = await _fetch_and_transform()

    # Determine which external_ids are already stored (single query)
    incoming_ids = [r["external_id"] for r in transformed]
    existing_ids: set = {
        row
        for (row,) in db.execute(
            select(Post.external_id).where(Post.external_id.in_(incoming_ids))
        )
    }

    new_records = [r for r in transformed if r["external_id"] not in existing_ids]
    if new_records:
        db.bulk_insert_mappings(Post, new_records)
        db.commit()

    return {
        "status": "success",
        "stored": len(new_records),
        "skipped": len(transformed) - len(new_records),
    }

