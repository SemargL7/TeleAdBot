from datetime import datetime

from gino.schema import GinoSchemaVisitor
from sqlalchemy import sql
from bot.data.config import POSTGRES_URL
from . import db


class User(db.Model):
    __tablename__ = "users"
    query: sql.Select

    id = db.Column(db.BigInteger(), primary_key=True)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    username = db.Column(db.String(32), nullable=False)
    created_at = db.Column(db.TIMESTAMP(), default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP(), default=datetime.utcnow)


class Chat(db.Model):
    __tablename__ = "chats"
    query: sql.Select

    id = db.Column(db.BigInteger(), primary_key=True)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    username = db.Column(db.String(32), nullable=False)
    title = db.Column(db.String(128), nullable=False)
    invite_link = db.Column(db.Text(), nullable=False)
    chat_type = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.TIMESTAMP(), default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP(), default=datetime.utcnow)


class ChatMember(db.Model):
    __tablename__ = "chat_members"
    query: sql.Select

    user_id = db.Column(db.BigInteger(), db.ForeignKey('users.id'))
    chat_id = db.Column(db.BigInteger(), db.ForeignKey('chats.id'))
    status = db.Column(db.String(128), nullable=False)
    updated_at = db.Column(db.TIMESTAMP(), default=datetime.utcnow)


async def init_database():
    # Create tables
    await db.set_bind(POSTGRES_URL)
    db.gino: GinoSchemaVisitor
    await db.gino.create_all()
