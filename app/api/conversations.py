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
from app.models.user import User
from app.schemas.conversation import (
    Conversation as ConversationSchema,
    ConversationDelete,
)
from app.schemas.conversation import ConversationCreate
from app.schemas.request_params import RequestParams
from app.core.logger import logger

router = APIRouter(prefix="/conversations")


@router.get("", response_model=List[ConversationSchema])
def get_conversations(
    response: Response,
    db: Session = Depends(get_db),
    user: User = Security(manager, scopes=["conversations"]),
    request_params: RequestParams = Depends(parse_react_admin_params(Conversation)),
) -> Any:
    total = db.query(func.count(Conversation.id)).scalar()
    query_conversations = db.query(Conversation).order_by(request_params.order_by)
    conversations = (
        query_conversations.offset(request_params.skip)
        .limit(request_params.limit)
        .all()
    )

    response.headers["Access-Control-Expose-Headers"] = "Content-Range"
    response.headers[
        "Content-Range"
    ] = f"{request_params.skip}-{request_params.skip + len(conversations)}/{total}"

    logger.info(f"{user} getting all conversations")
    return conversations


@router.get("/user/{user_id}", response_model=List[ConversationSchema])
def get_user_conversations(
    response: Response,
    user_id: UUID,
    db: Session = Depends(get_db),
    user: User = Security(manager),
    request_params: RequestParams = Depends(parse_react_admin_params(Conversation)),
) -> Any:
    user_queried: Optional[User] = db.get(User, user_id)
    if not user_queried:
        raise HTTPException(404)
    if user_queried.id != user.id and not user.is_superuser:
        raise HTTPException(401)

    user_conversations = user_queried.conversations_users
    conversations_ids = [
        user_conversation.conversation_id for user_conversation in user_conversations
    ]

    total = (
        db.query(func.count(Conversation.id))
        .filter(Conversation.id.in_(conversations_ids))
        .scalar()
    )
    query_conversations = (
        db.query(Conversation)
        .filter(Conversation.id.in_(conversations_ids))
        .order_by(request_params.order_by)
    )
    conversations = (
        query_conversations.offset(request_params.skip)
        .limit(request_params.limit)
        .all()
    )

    response.headers["Access-Control-Expose-Headers"] = "Content-Range"
    response.headers[
        "Content-Range"
    ] = f"{request_params.skip}-{request_params.skip + len(conversations)}/{total}"

    logger.info(f"{user} getting conversations for {user_queried}")
    return conversations


@router.post("", response_model=ConversationSchema, status_code=201)
def create_conversation(
    conversation_in: ConversationCreate,
    db: Session = Depends(get_db),
    user: User = Security(manager, scopes=["conversations_create"]),
) -> Any:
    conversation = Conversation(**conversation_in.dict())
    db.add(conversation)
    db.commit()

    logger.info(
        f"{user} creating conversation {conversation.subject} (ID {conversation.id})"
    )
    return conversation


@router.get("/{conversation_id}", response_model=ConversationSchema)
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    user: User = Security(manager),
) -> Any:
    conversation: Optional[Conversation] = db.get(Conversation, conversation_id)
    if not conversation:
        raise HTTPException(404)

    conversation_users = conversation.conversations_users
    users_ids = [conversation_user.user_id for conversation_user in conversation_users]
    if not user.id in users_ids and not user.is_superuser:
        raise HTTPException(401)

    logger.info(
        f"{user} getting conversation {conversation.subject} (ID {conversation.id})"
    )
    return conversation


@router.delete("/{conversation_id}", response_model=ConversationDelete)
def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    user: User = Security(manager, scopes=["conversations_delete"]),
) -> Any:
    conversation: Optional[Conversation] = db.get(Conversation, conversation_id)
    if not conversation:
        raise HTTPException(404)
    db.delete(conversation)
    db.commit()

    logger.info(f"{user} deleting conversation (ID {conversation.id})")
    return conversation
