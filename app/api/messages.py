from typing import Any, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy import func
from sqlalchemy.orm.session import Session
from starlette.responses import Response

from app.deps.db import get_db
from app.deps.users import manager
from app.deps.request_params import parse_react_admin_params
from app.models.conversation import Conversation
from app.models.conversation_user import ConversationUser
from app.models.message import Message
from app.models.user import User
from app.schemas.message import Message as MessageSchema, MessageDelete, MessageUpdate
from app.schemas.message import MessageCreate
from app.schemas.request_params import RequestParams
from app.core.logger import logger

router = APIRouter(prefix="/messages")


@router.get("/conversation/{conversation_id}", response_model=List[MessageSchema])
def get_conversation_messages(
    response: Response,
    conversation_id: int,
    db: Session = Depends(get_db),
    user: User = Security(manager, scopes=["messages"]),
    request_params: RequestParams = Depends(parse_react_admin_params(Message)),
) -> Any:
    conversation: Optional[Conversation] = db.get(Conversation, conversation_id)
    if not conversation:
        raise HTTPException(404)

    is_user_in_conversation = (
        db.query(func.count(ConversationUser.conversation_id))
        .filter(
            ConversationUser.conversation_id == conversation.id
            and ConversationUser.user_id == user.id
        )
        .scalar()
    )
    if not is_user_in_conversation and not user.is_superuser:
        raise HTTPException(401)

    total = (
        db.query(func.count(Message.conversation_id))
        .filter(Message.conversation_id == conversation.id)
        .scalar()
    )
    query_messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation.id)
        .order_by(request_params.order_by)
    )
    messages = (
        query_messages.offset(request_params.skip).limit(request_params.limit).all()
    )
    response.headers["Access-Control-Expose-Headers"] = "Content-Range"
    response.headers[
        "Content-Range"
    ] = f"{request_params.skip}-{request_params.skip + len(messages)}/{total}"

    logger.info(f"{user} getting all messages of conversation {conversation.id}")
    return messages


@router.get("/user/{user_id}", response_model=List[MessageSchema])
def get_user_messages(
    response: Response,
    user_id: UUID,
    db: Session = Depends(get_db),
    user: User = Security(manager, scopes=["messages"]),
    request_params: RequestParams = Depends(parse_react_admin_params(Message)),
) -> Any:
    user_queried: Optional[User] = db.get(User, user_id)
    if not user_queried:
        raise HTTPException(404)

    if user.id != user_queried.id and not user.is_superuser:
        raise HTTPException(401)

    total = (
        db.query(func.count(Message.conversation_id))
        .filter(Message.author_id == user_queried.id)
        .scalar()
    )
    query_messages = (
        db.query(Message)
        .filter(Message.author_id == user_queried.id)
        .order_by(request_params.order_by)
    )
    messages = (
        query_messages.offset(request_params.skip).limit(request_params.limit).all()
    )
    response.headers["Access-Control-Expose-Headers"] = "Content-Range"
    response.headers[
        "Content-Range"
    ] = f"{request_params.skip}-{request_params.skip + len(messages)}/{total}"

    logger.info(f"{user} getting all messages of {user_queried}")
    return messages


@router.post("", response_model=MessageSchema, status_code=201)
def create_message(
    message_in: MessageCreate,
    db: Session = Depends(get_db),
    user: User = Security(manager, scopes=["messages_create"]),
) -> Any:
    conversation: Optional[Conversation] = db.get(
        Conversation, message_in.conversation_id
    )
    if not conversation:
        raise HTTPException(404)

    is_user_in_conversation: Optional[ConversationUser] = db.get(
        ConversationUser,
        {"conversation_id": conversation.id, "user_id": user.id},
    )
    if not is_user_in_conversation and not user.is_superuser:
        raise HTTPException(401)

    message = Message(**message_in.dict())
    message.author_id = user.id
    db.add(message)
    db.commit()

    logger.info(
        f"{user} creating message (ID {message.id}) in conversation ID {conversation.id}"
    )
    return message


@router.put("/{message_id}", response_model=MessageSchema)
def update_message(
    message_id: int,
    message_in: MessageUpdate,
    db: Session = Depends(get_db),
    user: User = Security(manager, scopes=["messages_update"]),
) -> Any:
    message: Optional[Message] = db.get(Message, message_id)
    if not message:
        raise HTTPException(404)
    update_data = message_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(message, field, value)
    db.add(message)
    db.commit()

    logger.info(f"{user} updating message ID {message.id}")
    return message


@router.delete("/{message_id}", response_model=MessageDelete)
def delete_message(
    message_id: int,
    db: Session = Depends(get_db),
    user: User = Security(manager, scopes=["messages_delete"]),
) -> Any:
    message: Optional[Message] = db.get(Message, message_id)
    if not message:
        raise HTTPException(404)
    db.delete(message)
    db.commit()

    logger.info(f"{user} deleting message ID {message.id}")
    return message
