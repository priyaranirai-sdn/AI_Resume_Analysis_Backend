# routers/hr.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List
from app.models.database import get_db
from app.models.hr import HR
from app.schemas.hr import HRCreate, HRResponse, HRUpdate, HRLogin,Token
from app.auth import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.auth import get_current_user, superadmin_required
import logging

logger = logging.getLogger("uvicorn")
router = APIRouter(prefix="/hr", tags=["HR"])


# --------------------
# CREATE HR (SuperAdmin only)
# --------------------
@router.post("/", response_model=HRResponse)
def create_hr(
    hr: HRCreate,
    db: Session = Depends(get_db),
    current_user = Depends(superadmin_required)  # ensures only SuperAdmin
):
    existing_hr = db.query(HR).filter(HR.email == hr.email).first()
    if existing_hr:
        raise HTTPException(status_code=400, detail="HR with this email already exists")

    hashed_pwd = HR.hash_password(hr.password)
    new_hr = HR(
        full_name=hr.full_name,
        email=hr.email,
        phone=hr.phone,
        hashed_password=hashed_pwd,
        created_by_id=current_user.id  # track which SuperAdmin created HR
    )
    db.add(new_hr)
    db.commit()
    db.refresh(new_hr)
    return new_hr


# --------------------
# READ ALL HRs (SuperAdmin only)
# --------------------
@router.get("/", response_model=List[HRResponse])
def get_all_hrs(
    db: Session = Depends(get_db),
    current_user = Depends(superadmin_required)
):
    # return db.query(HR).all()
    return db.query(HR).filter(HR.created_by_id == current_user.id).all()


# --------------------
# READ SINGLE HR (SuperAdmin or the HR themselves)
# --------------------
@router.get("/{hr_id}", response_model=HRResponse)
def get_hr(
    hr_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    hr = db.query(HR).filter(HR.id == hr_id).first()
    if not hr:
        raise HTTPException(status_code=404, detail="HR not found")
    
    # HR can only access their own profile, SuperAdmin can access any
    if current_user.role != "superadmin" and current_user.id != hr.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this HR")
    
    return hr


# --------------------
# UPDATE HR (SuperAdmin only)
# --------------------
@router.put("/{hr_id}", response_model=HRResponse)
def update_hr(
    hr_id: int,
    hr_update: HRUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(superadmin_required)
):
    hr = db.query(HR).filter(HR.id == hr_id).first()
    if not hr:
        raise HTTPException(status_code=404, detail="HR not found")

    for field, value in hr_update.dict(exclude_unset=True).items():
        setattr(hr, field, value)

    db.commit()
    db.refresh(hr)
    return hr


# --------------------
# DELETE HR (SuperAdmin only)
# --------------------
@router.delete("/{hr_id}")
def delete_hr(
    hr_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(superadmin_required)
):
    hr = db.query(HR).filter(HR.id == hr_id).first()
    if not hr:
        raise HTTPException(status_code=404, detail="HR not found")
    db.delete(hr)
    db.commit()
    return {"detail": "HR deleted successfully"}


# --------------------
# HR LOGIN (no auth required)
# --------------------
@router.post("/login")
def hr_login(login_data: HRLogin, db: Session = Depends(get_db)):
    hr = db.query(HR).filter(HR.email == login_data.email).first()
    if not hr or not hr.verify_password(login_data.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not hr.is_active:
        raise HTTPException(status_code=403, detail="HR is inactive")
    
    token = create_access_token({"sub": hr.id})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/login/hr", response_model=Token)
def hr_login(hr: HRLogin, db: Session = Depends(get_db)):
    """
    Safe HR login endpoint:
    - Verifies email & password
    - Checks is_active
    - Ensures required fields exist before returning Token
    """

    # Fetch HR by email
    db_hr = db.query(HR).filter(HR.email == hr.email).first()
    if not db_hr:
        logger.warning(f"HR not found: {hr.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify password
    if not db_hr.verify_password(hr.password):
        logger.warning(f"Incorrect password attempt for HR: {hr.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if HR is active
    if not db_hr.is_active:
        logger.info(f"Inactive HR login attempt: {hr.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="HR account is inactive"
        )

    # Validate required fields
    if db_hr.id is None or not db_hr.email or not db_hr.role:
        logger.error(f"HR record corrupted: id={db_hr.id}, email={db_hr.email}, role={db_hr.role}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="HR account data is corrupted. Contact administrator."
        )

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(db_hr.id)}, expires_delta=access_token_expires
    )

    # Return Token
    res = {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": db_hr.id,
        "user_email": db_hr.email,
        "role": db_hr.role,
        "user_name":db_hr.full_name
    }

    logger.info(f"HR login successful: {db_hr.email}")
    return res