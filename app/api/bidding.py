from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.user import UserDB
from app.utils.auth import get_current_user, get_db
from ..models.bidding import BiddingRoom, BiddingRoomCreate, ChatMessage, ChatMessageCreate
from ..utils.bidding import get_bidding_room

router = APIRouter()

@router.post("/create-room", response_model=None)
async def create_bidding_room(
    room_data: BiddingRoomCreate,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if the room name is unique
    existing_room = db.query(BiddingRoom).filter(BiddingRoom.name == room_data.name).first()
    if existing_room:
        raise HTTPException(status_code=400, detail="Room name already exists")

    user = db.query(UserDB).filter(UserDB.username == current_user).first()

    # Create the bidding room
    new_room = BiddingRoom(
        name=room_data.name,
        description=room_data.description,
        owner=user
    )

    db.add(new_room)
    db.commit()
    db.refresh(new_room)

    return new_room


@router.get("/bidding-room/{room_id}", response_model=None)
async def read_bidding_room(room_id: int, db: Session = Depends(get_db)):
    db_room = db.query(BiddingRoom).filter(BiddingRoom.id == room_id).first()
    if db_room is None:
        raise HTTPException(status_code=404, detail="Bidding Room not found")
    return db_room


@router.post("/enter-room/{room_id}")
async def enter_bidding_room(
    room_id: int,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if the room exists
    bidding_room = db.query(BiddingRoom).filter(BiddingRoom.id == room_id).first()
    if not bidding_room:
        raise HTTPException(status_code=404, detail="Bidding room not found")
    
    if current_user in bidding_room.bidders:
        raise HTTPException(status_code=400, detail="User is already a bidder in the room")


    # Add the user as a bidder to the room
    bidding_room.bidders.append(current_user)
    db.commit()

    return {"message": "Entered bidding room successfully", "room_id": room_id}

@router.post("/bid/{room_id}")
async def place_bid(
    room_id: int,
    bid_amount: float,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if the room exists
    bidding_room = db.query(BiddingRoom).filter(BiddingRoom.id == room_id).first()
    if not bidding_room:
        raise HTTPException(status_code=404, detail="Bidding room not found")

    # Check if the bid amount is higher than the current highest bid
    if bid_amount <= bidding_room.current_highest_bid:
        raise HTTPException(status_code=400, detail="Bid amount must be higher than the current highest bid")

    # Update the current highest bid
    bidding_room.current_highest_bid = bid_amount
    bidding_room.current_highest_bidder = current_user
    db.commit()

    return {"message": "Bid placed successfully", "room_id": room_id, "bid_amount": bid_amount}

@router.put("/bid/{room_id}/{user_id}")
async def update_bid(
    room_id: int,
    user_id: int,
    bid_amount: float,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if the room exists
    bidding_room = db.query(BiddingRoom).filter(BiddingRoom.id == room_id).first()
    if not bidding_room:
        raise HTTPException(status_code=404, detail="Bidding room not found")

    # Check if the user is the current highest bidder in the room
    if user_id != current_user.id or user_id != bidding_room.current_highest_bidder_id:
        raise HTTPException(status_code=403, detail="User does not have permission to update this bid")

    # Check if the bid amount is higher than the current highest bid
    if bid_amount <= bidding_room.current_highest_bid:
        raise HTTPException(status_code=400, detail="Bid amount must be higher than the current highest bid")

    # Update the current highest bid and bidder
    bidding_room.current_highest_bid = bid_amount
    db.commit()

    return {"message": "Bid updated successfully", "room_id": room_id, "bid_amount": bid_amount}


@router.post("/bidding_room/{room_id}/send_message")
async def send_message(
    room_id: int,
    message_content: ChatMessageCreate,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if the room exists
    bidding_room = db.query(BiddingRoom).filter(BiddingRoom.id == room_id).first()
    if not bidding_room:
        raise HTTPException(status_code=404, detail="Bidding room not found")

    # Create a new chat message
    new_message = ChatMessage(room_id=room_id, sender_id=current_user.id, content=message_content)
    db.add(new_message)
    db.commit()
    db.refresh(new_message)

    return {"message": "Message sent successfully", "message_id": new_message.id}
