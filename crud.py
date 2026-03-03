from sqlalchemy.orm import Session
from sqlalchemy import func
from models import Item, Claim
from schemas import ItemIn, ClaimIn

# ✅ PROVIDED
def get_all_items(db: Session, skip: int = 0, limit: int = 10) -> list[Item]:
    return db.query(Item).offset(skip).limit(limit).all()

# ✅ PROVIDED
def get_one_item(db: Session, item_id: int) -> Item | None:
    return db.query(Item).filter(Item.id == item_id).first()

# ✅ PROVIDED
def get_claims_for_item(db: Session, item_id: int) -> list[Claim]:
    return db.query(Claim).filter(Claim.item_id == item_id).all()

# TODO #1 — Implement create_item()
def create_item(db: Session, item_in: ItemIn) -> Item:
    new_item = Item(**item_in.model_dump())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

# TODO #2 — Implement update_item()
def update_item(db: Session, item_id: int, item_in: ItemIn) -> Item | None:
    item = get_one_item(db, item_id)
    if not item:
        return None
    for key, value in item_in.model_dump().items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item

# TODO #3 — Implement delete_item()
def delete_item(db: Session, item_id: int) -> bool:
    item = get_one_item(db, item_id)
    if not item:
        return False
    db.delete(item)
    db.commit()
    return True

# TODO #4 — Implement create_claim()
def create_claim(db: Session, item_id: int, claim_in: ClaimIn) -> Claim:
    new_claim = Claim(item_id=item_id, **claim_in.model_dump())
    db.add(new_claim)
    db.commit()
    db.refresh(new_claim)
    return new_claim

# TODO #5 — Implement get_unresolved_items()
def get_unresolved_items(db: Session, skip: int = 0, limit: int = 10) -> list[Item]:
    return (
        db.query(Item)
        .filter(Item.resolved == False)
        .offset(skip)
        .limit(limit)
        .all()
    )

# TODO #6 — Implement get_item_stats()
def get_item_stats(db: Session, item_id: int):
    item = get_one_item(db, item_id)
    if not item:
        return None

    total_claims = (
        db.query(func.count(Claim.id))
        .filter(Claim.item_id == item_id)
        .scalar()
    )

    approved = (
        db.query(func.count(Claim.id))
        .filter(Claim.item_id == item_id, Claim.approved == True)
        .scalar()
    )

    return {
        "item_id": item_id,
        "name": item.name,
        "total_claims": total_claims,
        "approved": approved,
        "resolved": item.resolved,
    }
