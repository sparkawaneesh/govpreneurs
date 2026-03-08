from typing import Optional
from datetime import datetime
import sentry_sdk
from sqlalchemy.orm import Session
from models.user import User
from .security import get_password_hash, verify_password, create_access_token
import logging

logger = logging.getLogger(__name__)

class AuthService:
    @staticmethod
    def register_user(db: Session, email: str, password: str) -> Optional[User]:
        """
        Registers a new user in the database.
        """
        timestamp = datetime.utcnow().isoformat()
        logger.info(f"timestamp={timestamp}, service=AuthService, operation=register_user, status=started, email={email}")
        
        try:
            # Check if user already exists
            existing_user = db.query(User).filter(User.email == email).first()
            if existing_user:
                logger.warning(f"timestamp={timestamp}, service=AuthService, operation=register_user, status=failed, reason=email_exists, email={email}")
                return None
            
            # Create new user
            new_user = User(
                email=email,
                password_hash=get_password_hash(password)
            )
            
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            logger.info(f"timestamp={timestamp}, service=AuthService, operation=register_user, status=success, user_id={new_user.id}")
            return new_user
        except Exception as e:
            sentry_sdk.capture_exception(e)
            logger.error(f"timestamp={timestamp}, service=AuthService, operation=register_user, status=error, error={str(e)}")
            raise

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """
        Authenticates a user and returns the user object if successful.
        """
        timestamp = datetime.utcnow().isoformat()
        logger.info(f"timestamp={timestamp}, service=AuthService, operation=authenticate_user, status=started, email={email}")
        
        try:
            user = db.query(User).filter(User.email == email).first()
            if not user or not verify_password(password, user.password_hash):
                logger.warning(f"timestamp={timestamp}, service=AuthService, operation=authenticate_user, status=failed, email={email}")
                return None
            
            logger.info(f"timestamp={timestamp}, service=AuthService, operation=authenticate_user, status=success, user_id={user.id}")
            return user
        except Exception as e:
            sentry_sdk.capture_exception(e)
            logger.error(f"timestamp={timestamp}, service=AuthService, operation=authenticate_user, status=error, error={str(e)}")
            raise

    @staticmethod
    def create_token_for_user(user: User) -> str:
        """
        Creates a JWT access token for the given user.
        """
        return create_access_token(data={"sub": str(user.id), "email": user.email})
