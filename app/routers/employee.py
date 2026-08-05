from fastapi import APIRouter, Depends, Form, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.auth import require_employee
from app.database import get_db
from app.models import Question, QuestionStatus, User
from app.rag import answer_question

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/employee")
def employee_page(
    request: Request, user: User = Depends(require_employee), db: Session = Depends(get_db)
):
    history = (
        db.query(Question)
        .filter(Question.asked_by == user.id)
        .order_by(Question.asked_at.asc())
        .all()
    )
    return templates.TemplateResponse(
        request, "employee.html", {"user": user, "history": history}
    )


@router.post("/questions")
def ask_question(
    request: Request,
    question_text: str = Form(...),
    user: User = Depends(require_employee),
    db: Session = Depends(get_db),
):
    result = answer_question(db, question_text)

    question = Question(asked_by=user.id, question_text=question_text)
    if result["confident"] and result["answer"]:
        question.status = QuestionStatus.answered_by_ai
        question.ai_answer = result["answer"]
        question.sources = ", ".join(result["sources"])
    else:
        question.status = QuestionStatus.pending

    db.add(question)
    db.commit()
    db.refresh(question)

    return templates.TemplateResponse(
        request, "_question_result.html", {"question": question}
    )
