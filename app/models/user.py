from pydantic import BaseModel, EmailStr
from ..database import Base
from sqlalchemy.orm import relationship

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    hashed_password: str

    class Config:
        from_attributes = True


from sqlalchemy import Column, Integer, String

class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    
    # Add a relationship with the BiddingRoom model
    bidding_rooms = relationship("BiddingRoom", back_populates="owner")
    highest_bidder_rooms = relationship("BiddingRoom", back_populates="current_highest_bidder")
    sent_messages = relationship("ChatMessage", back_populates="sender")


