import os
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Form, HTTPException, Request, UploadFile
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth import require_hr
from app.config import MAX_UPLOAD_MB, UPLOAD_DIR
from app.database import get_db
from app.models import Document, DocumentChunk, Question, QuestionStatus, User
from app.rag import chunk_text, embed_texts, extract_pdf_text

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("/hr")
def hr_dashboard(
    request: Request, user: User = Depends(require_hr), db: Session = Depends(get_db)
):
    documents = (
        db.query(Document, func.count(DocumentChunk.id).label("chunk_count"))
        .outerjoin(DocumentChunk, DocumentChunk.document_id == Document.id)
        .group_by(Document.id)
        .order_by(Document.uploaded_at.desc())
        .all()
    )
    pending_questions = (
        db.query(Question)
        .filter(Question.status == QuestionStatus.pending)
        .order_by(Question.asked_at.desc())
        .all()
    )
    return templates.TemplateResponse(
        request,
        "hr.html",
        {
            "user": user,
            "documents": documents,
            "pending_questions": pending_questions,
        },
    )


@router.post("/hr/documents")
def upload_document(
    request: Request,
    file: UploadFile,
    user: User = Depends(require_hr),
    db: Session = Depends(get_db),
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    contents = file.file.read()
    if len(contents) > MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"File exceeds {MAX_UPLOAD_MB}MB limit.")

    storage_filename = f"{uuid.uuid4().hex}_{file.filename}"
    storage_path = os.path.join(UPLOAD_DIR, storage_filename)
    with open(storage_path, "wb") as f:
        f.write(contents)

    text = extract_pdf_text(storage_path)
    chunks = chunk_text(text)

    document = Document(
        filename=file.filename, uploaded_by=user.id, storage_path=storage_path
    )
    db.add(document)
    db.flush()

    if chunks:
        embeddings = embed_texts(chunks)
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            db.add(
                DocumentChunk(
                    document_id=document.id,
                    chunk_text=chunk,
                    embedding=embedding,
                    chunk_index=i,
                )
            )

    db.commit()
    return RedirectResponse(url="/hr", status_code=303)


@router.post("/hr/documents/{document_id}/delete")
def delete_document(
    document_id: int, user: User = Depends(require_hr), db: Session = Depends(get_db)
):
    document = db.query(Document).filter(Document.id == document_id).first()
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    if os.path.exists(document.storage_path):
        os.remove(document.storage_path)
    db.delete(document)
    db.commit()
    return RedirectResponse(url="/hr", status_code=303)


@router.post("/hr/questions/{question_id}/resolve")
def resolve_question(
    question_id: int,
    hr_answer: str = Form(...),
    user: User = Depends(require_hr),
    db: Session = Depends(get_db),
):
    question = db.query(Question).filter(Question.id == question_id).first()
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found.")
    question.hr_answer = hr_answer
    question.status = QuestionStatus.resolved_by_hr
    question.resolved_by = user.id
    question.resolved_at = datetime.utcnow()
    db.commit()
    return RedirectResponse(url="/hr", status_code=303)
