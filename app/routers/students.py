from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List

from app.db import get_db
from app.models import Student
from app.schemas import StudentCreate, StudentUpdate, StudentResponse

router = APIRouter(prefix="/students", tags=["students"])


@router.get("/", response_model=List[StudentResponse])
def get_students(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Busca todos estudantes com paginação"""
    students = db.query(Student).offset(skip).limit(limit).all()
    return students


@router.get("/{student_id}", response_model=StudentResponse)
def get_student(student_id: int, db: Session = Depends(get_db)):
    """Busca um estudante pelo ID"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id {student_id} not found",
        )
    return student


@router.post("/", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    """Cria um novo estudante"""
    db_student = Student(**student.model_dump())
    
    try:
        db.add(db_student)
        db.commit()
        db.refresh(db_student)
        return db_student
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Student with email {student.email} already exists",
        )


@router.put("/{student_id}", response_model=StudentResponse)
def update_student(
    student_id: int, student: StudentUpdate, db: Session = Depends(get_db)
):
    """Atualiza um estudante"""
    db_student = db.query(Student).filter(Student.id == student_id).first()
    if not db_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id {student_id} not found",
        )

    for key, value in student.model_dump().items():
        setattr(db_student, key, value)

    try:
        db.commit()
        db.refresh(db_student)
        return db_student
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Student with email {student.email} already exists",
        )


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    """Deleta um estudante"""
    db_student = db.query(Student).filter(Student.id == student_id).first()
    if not db_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id {student_id} not found",
        )

    db.delete(db_student)
    db.commit()
    return None
