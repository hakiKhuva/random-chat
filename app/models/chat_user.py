from .db import Base, db

class ChatUser(Base):
    __tablename__ = "chat_users"

    name = db.Column(db.String(20), nullable=False)
    age = db.Column(db.String(20), nullable=False)
    looking_age = db.Column(db.String(20), nullable=False)
    gender = db.Column(db.String(30), nullable=False)
    looking_gender = db.Column(db.String(30), nullable=False)
    sid = db.Column(db.String(50), nullable=False, unique=True)
    message_to = db.Column(db.String(50), nullable=True, unique=True)    
    status = db.Column(db.String(20), nullable=False, default="free")

    def __repr__(self) -> str:
        return f"<ChatUser>"