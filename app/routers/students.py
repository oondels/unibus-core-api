from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List

from app.db import get_db
from app.models import Student
from app.schemas import StudentCreate, StudentUpdate, StudentResponse
from app.services import validate_student_eligibility, validate_cep

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
async def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    """Cria um novo estudante com validação de CEP via ViaCEP e validação via API externa"""
    
    # 1. Valida o CEP usando ViaCEP
    cep_result = await validate_cep(student.cep)
    
    if not cep_result["is_valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid CEP: {cep_result['reason']}",
        )
    
    # 2. Valida o estudante via API externa (usando CEP como registration)
    validation_result = await validate_student_eligibility(
        student.name, student.email, student.cep
    )
    
    # Se não for válido, retorna erro 400
    if not validation_result["is_valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Student validation failed: {validation_result['reason']}",
        )
    
    # 3. Cria o estudante no banco com dados do ViaCEP
    db_student = Student(
        name=student.name,
        email=student.email,
        cep=student.cep,
        city=cep_result["city"],
        city_ibge_code=cep_result["city_ibge_code"],
    )
    
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
async def update_student(
    student_id: int, student: StudentUpdate, db: Session = Depends(get_db)
):
    """Atualiza um estudante com validação de CEP"""
    db_student = db.query(Student).filter(Student.id == student_id).first()
    if not db_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id {student_id} not found",
        )

    # Valida o CEP usando ViaCEP
    cep_result = await validate_cep(student.cep)
    
    if not cep_result["is_valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid CEP: {cep_result['reason']}",
        )

    # Atualiza os campos
    db_student.name = student.name
    db_student.email = student.email
    db_student.cep = student.cep
    db_student.city = cep_result["city"]
    db_student.city_ibge_code = cep_result["city_ibge_code"]

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
