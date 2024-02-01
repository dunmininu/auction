from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.utils.auth import get_user
from ..models.bidding import BiddingRoom

def create_bidding_room_util(
    db: Session, 
    room: BiddingRoom, 
    creator_username: str
):
    db_user = get_user(db, username=creator_username)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db_room = BiddingRoom(**room.dict(), creator_id=db_user.id)
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room

def get_bidding_room(db: Session, room_id: int):
    return db.query(BiddingRoom).filter(BiddingRoom.id == room_id).first()
