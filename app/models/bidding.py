from pydantic_sqlalchemy import sqlalchemy_to_pydantic
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship


from app.models.user import UserDB

from ..database import Base

class BiddingRoom(Base):
    __tablename__ = "bidding_rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True)
    description = Column(String)

    # Define a relationship with the UserDB model (assuming each room has an owner)
    owner_id = Column(Integer, ForeignKey('users.id'))
    owner = relationship("UserDB", back_populates="bidding_rooms", foreign_keys=[owner_id])

    # Establish a relationship with the UserDB model for bidders
    bidders = relationship("UserDB", secondary="bidding_room_bidder", back_populates="bidding_rooms")

    # Add a column to store the user who placed the current highest bid
    current_highest_bidder_id = Column(Integer, ForeignKey('users.id'))
    current_highest_bidder = relationship("UserDB", foreign_keys=[current_highest_bidder_id])


    messages = relationship("ChatMessage", back_populates="room")


class BiddingRoomBidder(Base):
    __tablename__ = "bidding_room_bidder"

    room_id = Column(Integer, ForeignKey('bidding_rooms.id'), primary_key=True)
    bidder_id = Column(Integer, ForeignKey('users.id'), primary_key=True)


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey('bidding_rooms.id'))
    sender_id = Column(Integer, ForeignKey('users.id'))
    content = Column(String)

    # Define relationships
    room = relationship("BiddingRoom", back_populates="messages")
    sender = relationship("UserDB", back_populates="sent_messages")





class BiddingRoomCreate(BaseModel):
    name: str
    description: str

    class Config:
        from_attributes = True

class ChatMessageCreate(BaseModel):
    content: str

    class Config:
        from_attributes = True


# BiddingRoom_Pydantic = sqlalchemy_to_pydantic(BiddingRoom)