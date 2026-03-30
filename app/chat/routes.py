import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.auth.routes import get_current_user
from app.chat.rag import get_relevant_context
from app.chat.service import get_ai_response
from app.db.database import SessionLocal
from app.db.models import Chat, Session as DBSession, User
from app.db.schemas import (
    ChatMessageResponse,
    ChatRequest,
    ChatResponse,
    SessionResponse,
)

router = APIRouter(prefix="/chat", tags=["Chat"])
logger = logging.getLogger(__name__)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/send", response_model=ChatResponse)
def send_message(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        message = request.message.strip()
        if not message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message cannot be empty",
            )

        if request.session_id is not None:
            session = (
                db.query(DBSession)
                .filter(
                    DBSession.id == request.session_id,
                    DBSession.user_id == current_user.id,
                )
                .first()
            )
            if not session:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Session not found",
                )
        else:
            session = DBSession(user_id=current_user.id)
            db.add(session)
            db.commit()
            db.refresh(session)

        user_chat = Chat(
            session_id=session.id,
            role="user",
            message=message
        )
        db.add(user_chat)
        db.commit()

        context_chunks = get_relevant_context(db, message)
        ai_reply = get_ai_response(message, context_chunks=context_chunks)

        ai_chat = Chat(
            session_id=session.id,
            role="assistant",
            message=ai_reply
        )
        db.add(ai_chat)
        db.commit()

        return {
            "user_message": message,
            "ai_reply": ai_reply,
            "session_id": session.id,
            "user_id": current_user.id
        }
    except HTTPException:
        db.rollback()
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception("Database error while sending message for user_id=%s", current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while sending message",
        ) from exc
    except Exception as exc:
        db.rollback()
        logger.exception("Unexpected error while sending message for user_id=%s", current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to process chat message",
        ) from exc


@router.get("/history/{session_id}", response_model=list[ChatMessageResponse])
def get_chat_history(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        session = (
            db.query(DBSession)
            .filter(DBSession.id == session_id, DBSession.user_id == current_user.id)
            .first()
        )
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found",
            )

        chats = (
            db.query(Chat)
            .filter(Chat.session_id == session_id)
            .order_by(Chat.created_at.asc(), Chat.id.asc())
            .all()
        )
        return chats
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        logger.exception(
            "Database error while fetching history for session_id=%s user_id=%s",
            session_id,
            current_user.id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching chat history",
        ) from exc
    except Exception as exc:
        logger.exception(
            "Unexpected error while fetching history for session_id=%s user_id=%s",
            session_id,
            current_user.id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to fetch chat history",
        ) from exc


@router.get("/sessions", response_model=list[SessionResponse])
def get_user_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        sessions = (
            db.query(DBSession)
            .filter(DBSession.user_id == current_user.id)
            .order_by(DBSession.created_at.desc(), DBSession.id.desc())
            .all()
        )
        return sessions
    except SQLAlchemyError as exc:
        logger.exception("Database error while fetching sessions for user_id=%s", current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching sessions",
        ) from exc
    except Exception as exc:
        logger.exception("Unexpected error while fetching sessions for user_id=%s", current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to fetch sessions",
        ) from exc
