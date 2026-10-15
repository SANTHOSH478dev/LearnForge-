from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, StudentProfile, Achievement
from app.schemas.auth import UserRegister, UserLogin, Token, UserOut, PasswordResetRequest
from app.services.auth_service import get_password_hash, verify_password, create_access_token
from app.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=Token)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists"
        )

    # Create User
    new_user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role="student",
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create Student Profile
    profile = StudentProfile(
        user_id=new_user.id,
        academic_level=user_in.academic_level or "Undergraduate",
        primary_subjects=user_in.primary_subjects or "[]",
        learning_goals=user_in.learning_goals or "Master exam syllabus with high confidence",
        daily_goal_minutes=45,
        current_streak=1,
        longest_streak=1
    )
    db.add(profile)

    # Award Welcome Achievement
    welcome_badge = Achievement(
        user_id=new_user.id,
        badge_type="welcome",
        badge_title="Cadet of Knowledge",
        badge_description="Joined LearnForge AI and activated personalized study forge.",
        icon_name="Sparkles"
    )
    db.add(welcome_badge)
    db.commit()

    token = create_access_token(data={"user_id": new_user.id, "email": new_user.email, "role": new_user.role})
    return Token(
        access_token=token,
        token_type="bearer",
        user_id=new_user.id,
        email=new_user.email,
        full_name=new_user.full_name,
        role=new_user.role
    )

@router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Account is deactivated")

    token = create_access_token(data={"user_id": user.id, "email": user.email, "role": user.role})
    return Token(
        access_token=token,
        token_type="bearer",
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role
    )

@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/reset-password")
def reset_password(req: PasswordResetRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.hashed_password = get_password_hash(req.new_password)
    db.commit()
    return {"message": "Password successfully reset"}
