from fastapi import FastAPI, HTTPException, Depends, Response, status
from sqlalchemy.orm import Session
from typing import Annotated, Optional
import models, crud, database
from schemas import ItemIn, ItemOut, ClaimIn, ClaimOut, ItemStats
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

DB = Annotated[Session, Depends(get_db)]

# ✅ PROVIDED — Get all items with optional category filter
@app.get("/item", response_model=list[ItemOut])
async def get_items(
    db: DB,
    skip: int = 0,
    limit: int = 10,
    category: Optional[str] = None,
    response: Response = None,
):
    items = crud.get_all_items(db, skip=skip, limit=limit)
    if category:
        items = [i for i in items if i.category == category]
    response.headers["X-Total-Count"] = str(db.query(models.Item).count())
    return items

# TODO #10 — Implement GET /item/unresolved
# Requirements:
#   - Call crud.get_unresolved_items() with skip and limit params
#   - Return the list of unresolved items
#   - IMPORTANT: This route must be defined BEFORE /item/{item_id}
#     in the final file — move it above get_item() when submitting
@app.get("/item/unresolved", response_model=list[ItemOut])
async def get_unresolved_items(db: DB, skip: int = 0, limit: int = 10):
    return crud.get_unresolved_items(db, skip=skip, limit=limit)

# ✅ PROVIDED — Get one item by ID
@app.get("/item/{item_id}", response_model=ItemOut)
async def get_item(item_id: int, db: DB):
    item = crud.get_one_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

# ✅ PROVIDED — Get all claims for an item
@app.get("/item/{item_id}/claim", response_model=list[ClaimOut])
async def get_claims(item_id: int, db: DB):
    if not crud.get_one_item(db, item_id):
        raise HTTPException(status_code=404, detail="Item not found")
    return crud.get_claims_for_item(db, item_id)

# TODO #7 — Implement POST /item
# Requirements:
#   - Accept ItemIn body and DB dependency
#   - Call crud.create_item(), return result with status 201
@app.post("/item", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
async def create_item(item_in: ItemIn, db: DB):
    return crud.create_item(db, item_in)

# TODO #8 — Implement PUT /item/{item_id}
# Requirements:
#   - Call crud.update_item(); raise 404 if None returned
#   - Return the updated ItemOut
@app.put("/item/{item_id}", response_model=ItemOut)
async def update_item(item_id: int, item_in: ItemIn, db: DB):
    updated = crud.update_item(db, item_id, item_in)
    if not updated:
        raise HTTPException(status_code=404, detail="Item not found")
    return updated

# TODO #9 — Implement DELETE /item/{item_id}
# Requirements:
#   - Call crud.delete_item(); raise 404 if False returned
#   - Return HTTP 204 No Content
@app.delete("/item/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int, db: DB):
    deleted = crud.delete_item(db, item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Item not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

 #TODO #10 — Implement GET /item/unresolved
# Requirements:
#   - Call crud.get_unresolved_items() with skip and limit params
#   - Return the list of unresolved items
#   - IMPORTANT: This route must be defined BEFORE /item/{item_id}
#     in the final file — move it above get_item() when submitting
# @app.get("/item/unresolved", response_model=list[ItemOut])
#async def get_unresolved_items(db: DB, skip: int = 0, limit: int = 10):
   # return crud.get_unresolved_items(db, skip=skip, limit=limit)

# ✅ PROVIDED — Get stats for one item
@app.get("/item/{item_id}/stats", response_model=ItemStats)
async def get_item_stats(item_id: int, db: DB):
    stats = crud.get_item_stats(db, item_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Item not found")
    return stats

# ✅ PROVIDED — Delete a claim
@app.delete("/item/{item_id}/claim/{claim_id}",
            status_code=status.HTTP_204_NO_CONTENT)
async def delete_claim(item_id: int, claim_id: int, db: DB):
    if not crud.get_one_item(db, item_id):
        raise HTTPException(status_code=404, detail="Item not found")
    deleted = crud.delete_claim(db, item_id, claim_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Claim not found")

# ✅ PROVIDED — Add a claim (with resolved check)
# Study this route carefully — TODO #4 in crud.py must work for this to pass
@app.post("/item/{item_id}/claim", response_model=ClaimOut,
          status_code=status.HTTP_201_CREATED)
async def add_claim(item_id: int, claim_in: ClaimIn, db: DB):
    item = crud.get_one_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.resolved:
        raise HTTPException(status_code=400, detail="Item is already resolved")
    return crud.create_claim(db, item_id, claim_in)
