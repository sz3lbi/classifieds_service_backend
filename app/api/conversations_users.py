from typing import Any, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy import func, and_
from sqlalchemy.orm.session import Session
from starlette.responses import Response

from app.deps.db import get_db
from app.deps.users import manager
from app.deps.request_params import parse_react_admin_params
from app.models.conversation_user import ConversationUser
from app.models.conversation import Conversation
from app.models.user import User
from app.schemas.conversation_user import (
    ConversationUser as ConversationUserSchema,
    ConversationUserDelete,
)
from app.schemas.conversation_user import ConversationUserCreate
from app.schemas.request_params import RequestParams
from app.core.logger import logger

router = APIRouter(prefix="/conversations_users")


@router.get("", response_model=List[ConversationUserSchema])
def get_conversations_users(
    response: Response,
    db: Session = Depends(get_db),
    user: User = Security(manager, scopes=["conversations_users"]),
    request_params: RequestParams = Depends(parse_react_admin_params(ConversationUser)),
) -> Any:
    total = db.query(func.count(ConversationUser.conversation_id)).scalar()
    query_conversations_users = db.query(ConversationUser).order_by(
        request_params.order_by
    )
    conversations_users = (
        query_conversations_users.offset(request_params.skip)
        .limit(request_params.limit)
        .all()
    )
    response.headers["Access-Control-Expose-Headers"] = "Content-Range"
    response.headers[
        "Content-Range"
    ] = f"{request_params.skip}-{request_params.skip + len(conversations_users)}/{total}"

    logger.info(f"{user} getting all conversations_users")
    return conversations_users


@router.get("/{conversation_user_id}", response_model=ConversationUserSchema)
def get_conversation_user(
    conversation_user_id: int,
    db: Session = Depends(get_db),
    user: User = Security(manager),
) -> Any:
    conversation_user: Optional[ConversationUser] = db.get(
        ConversationUser, conversation_user_id
    )
    if not conversation_user:
        raise HTTPException(404)

    conversation: Optional[Conversation] = db.get(
        Conversation, conversation_user.conversation_id
    )
    if not conversation:
        raise HTTPException(404)

    is_user_in_conversation = (
        db.query(func.count(ConversationUser.conversation_id))
        .filter(
            and_(
                ConversationUser.conversation_id == conversation.id,
                ConversationUser.user_id == user.id,
            )
        )
        .scalar()
    )
    if not is_user_in_conversation and not user.is_superuser:
        raise HTTPException(401)

    logger.info(f"{user} getting conversation_user ID {conversation_user.id}")
    return conversation_user


@router.get(
    "/conversation/{conversation_id}", response_model=List[ConversationUserSchema]
)
def get_conversation_users(
    response: Response,
    conversation_id: int,
    db: Session = Depends(get_db),
    user: User = Security(manager),
    request_params: RequestParams = Depends(parse_react_admin_params(ConversationUser)),
) -> Any:
    conversation: Optional[Conversation] = db.get(Conversation, conversation_id)
    if not conversation:
        raise HTTPException(404)

    is_user_in_conversation = (
        db.query(func.count(ConversationUser.conversation_id))
        .filter(
            and_(
                ConversationUser.conversation_id == conversation.id,
                ConversationUser.user_id == user.id,
            )
        )
        .scalar()
    )
    if not is_user_in_conversation and not user.is_superuser:
        raise HTTPException(401)

    total = (
        db.query(func.count(ConversationUser.conversation_id))
        .filter(ConversationUser.conversation_id == conversation.id)
        .scalar()
    )
    query_conversations_users = (
        db.query(ConversationUser)
        .filter(ConversationUser.conversation_id == conversation.id)
        .order_by(request_params.order_by)
    )
    conversations_users = (
        query_conversations_users.offset(request_params.skip)
        .limit(request_params.limit)
        .all()
    )
    response.headers["Access-Control-Expose-Headers"] = "Content-Range"
    response.headers[
        "Content-Range"
    ] = f"{request_params.skip}-{request_params.skip + len(conversations_users)}/{total}"

    logger.info(
        f"{user} getting all conversations_users for conversation ID {conversation.id}"
    )
    return conversations_users


@router.get("/user/{user_id}", response_model=List[ConversationUserSchema])
def get_conversations_users_for_user(
    response: Response,
    user_id: UUID,
    db: Session = Depends(get_db),
    user: User = Security(manager),
    request_params: RequestParams = Depends(parse_react_admin_params(ConversationUser)),
) -> Any:
    user_queried: Optional[User] = db.get(User, user_id)
    if not user_queried:
        raise HTTPException(404)

    if user.id != user_queried.id and not user.is_superuser:
        raise HTTPException(401)

    total = (
        db.query(func.count(ConversationUser.user_id))
        .filter(ConversationUser.user_id == user_queried.id)
        .scalar()
    )
    query_conversations_users = (
        db.query(ConversationUser)
        .filter(ConversationUser.user_id == user_queried.id)
        .order_by(request_params.order_by)
    )
    conversations_users = (
        query_conversations_users.offset(request_params.skip)
        .limit(request_params.limit)
        .all()
    )
    response.headers["Access-Control-Expose-Headers"] = "Content-Range"
    response.headers[
        "Content-Range"
    ] = f"{request_params.skip}-{request_params.skip + len(conversations_users)}/{total}"

    logger.info(f"{user} getting conversations_users for user ID {user_queried.id}")
    return conversations_users


@router.post("", response_model=ConversationUserSchema, status_code=201)
def create_conversation_user(
    conversation_user_in: ConversationUserCreate,
    db: Session = Depends(get_db),
    user: User = Security(manager, scopes=["conversations_users_create"]),
) -> Any:
    conversation: Optional[Conversation] = db.get(
        Conversation, conversation_user_in.conversation_id
    )
    if not conversation:
        raise HTTPException(404)

    is_user_in_conversation: Optional[ConversationUser] = db.get(
        ConversationUser,
        {"conversation_id": conversation.id, "user_id": user.id},
    )
    if not is_user_in_conversation and not user.is_superuser:
        raise HTTPException(401)

    user_queried: Optional[User] = db.get(User, conversation_user_in.user_id)
    if not user_queried:
        raise HTTPException(404)

    is_user_queried_in_conversation: Optional[ConversationUser] = db.get(
        ConversationUser,
        {"conversation_id": conversation.id, "user_id": user_queried.id},
    )
    if is_user_queried_in_conversation:
        raise HTTPException(409)

    conversation_user = ConversationUser(**conversation_user_in.dict())
    db.add(conversation_user)
    db.commit()

    logger.info(
        f"{user} creating conversation_user ID {conversation_user.id} "
        f"for user ID {conversation_user.user_id} and conversation ID {conversation_user.conversation_id}"
    )
    return conversation_user


@router.delete(
    "/conversation_user/{conversation_user_id}", response_model=ConversationUserDelete
)
def delete_conversation_user(
    conversation_user_id: int,
    db: Session = Depends(get_db),
    user: User = Security(manager, scopes=["conversations_users_delete"]),
) -> Any:
    conversation_user: Optional[ConversationUser] = db.get(
        ConversationUser,
        conversation_user_id,
    )
    if not conversation_user:
        raise HTTPException(404)
    db.delete(conversation_user)
    db.commit()

    logger.info(
        f"{user} deleting conversation_user ID {conversation_user.id} "
        f"(user ID {conversation_user.user_id}, conversation ID {conversation_user.conversation_id})"
    )
    return conversation_user
