import json
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, ValidationError
from typing import List, Any, Optional
from loader import bot
import logging

app = FastAPI()
logger = logging.getLogger(__name__)

class Button(BaseModel):
    text: str
    url: str

class PostData(BaseModel):
    text: str
    buttons: List[Button]

class PostTerms(BaseModel):
    post_message: bool
    pin_message: bool

class Post(BaseModel):
    id: int
    order_id: int
    chat_id: int
    post_data: PostData
    post_terms: PostTerms

class ReturnPost(BaseModel):
    id: int
    order_id: int
    complete: bool
    error: Optional[str]

@app.post("/send_message/")
async def send_message(request: Request):
    try:
        data = await request.json()
        logger.info(f"Received request data: {data}")

        # Try to parse the incoming request data into Post objects
        try:
            options = [Post(**item) for item in data]
        except ValidationError as e:
            logger.error(f"Validation error: {e.json()}")
            raise HTTPException(status_code=422, detail=e.errors())

        orders_return_data = []

        for option in options:
            order_return_data = ReturnPost(id=option.id, order_id=option.order_id, complete=False, error=None)
            try:
                # Build inline keyboard markup
                markup = InlineKeyboardBuilder()
                for button in option.post_data.buttons:
                    markup.row(InlineKeyboardButton(text=button.text, url=button.url))

                # Send message with inline keyboard
                msg = await bot.send_message(chat_id=option.chat_id, text=option.post_data.text, reply_markup=markup.as_markup())
                if option.post_terms.pin_message:
                    await bot.pin_chat_message(chat_id=option.chat_id, message_id=msg.message_id)
                order_return_data.complete = True
            except Exception as e:
                logger.error(f"Error processing option ID {option.order_id}: {e}")
                order_return_data.error = e
            orders_return_data.append(order_return_data)

        return orders_return_data
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
