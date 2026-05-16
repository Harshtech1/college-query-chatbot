from __future__ import annotations

from werkzeug.security import generate_password_hash

from flask import current_app

from chatbot_app.database import db
from chatbot_app.models import AdminUser, FaqEntry, KnowledgeDocument
from chatbot_app.services.document_service import ingest_text_content


STARTER_FAQS = [
    {
        "question": "What is the admission process?",
        "answer": "Students can apply online by filling out the admission form, uploading required documents, and completing fee payment after eligibility verification.",
        "category": "Admissions",
        "keywords": ["admission", "apply", "application", "documents", "enrollment"],
        "priority": 5,
    },
    {
        "question": "What is the fee structure?",
        "answer": "The fee structure depends on the selected course and semester. Students should review the latest fee circular or contact the accounts office for the exact payable amount.",
        "category": "Fees",
        "keywords": ["fee", "fees", "payment", "accounts", "tuition"],
        "priority": 5,
    },
    {
        "question": "When are exams conducted?",
        "answer": "Internal assessments are conducted during the semester, and final examinations are scheduled at the end of the academic term according to the official exam calendar.",
        "category": "Exams",
        "keywords": ["exam", "examination", "schedule", "calendar", "assessment"],
        "priority": 4,
    },
    {
        "question": "How can I check attendance details?",
        "answer": "Attendance details are updated by the department and can be checked through the student information desk or the official academic portal when available.",
        "category": "Attendance",
        "keywords": ["attendance", "present", "percentage", "classes"],
        "priority": 4,
    },
    {
        "question": "Which courses are available?",
        "answer": "The college offers undergraduate and postgraduate programs across multiple departments. Students should refer to the course brochure or academic office for the latest list.",
        "category": "Courses",
        "keywords": ["courses", "programs", "departments", "subjects"],
        "priority": 4,
    },
    {
        "question": "How can I view the timetable?",
        "answer": "Timetable updates are published by the academic section. Students should check the timetable notice or request the latest schedule from the department office.",
        "category": "Timetable",
        "keywords": ["timetable", "schedule", "class timings", "routine"],
        "priority": 3,
    },
]


STARTER_DOCUMENT = """
College Information Handbook

Admissions:
Students must complete the online application form, upload mark sheets, identity proof, passport-size photographs, and any category certificates where applicable. Once the admission office verifies the application, eligible students receive a confirmation email with payment instructions.

Fees:
Semester fees differ by program. The accounts office publishes the latest fee circular before each term. Students can pay through the college payment portal or at the accounts desk during working hours.

Examinations:
The examination section releases internal assessment schedules and end-semester timetables on the college notice board and official website. Hall tickets are distributed after attendance and fee compliance is confirmed.

Attendance:
Students are expected to maintain the minimum attendance percentage set by the institution. Shortage cases are reviewed by the department and may require written justification.

Faculty and Timetable:
Department coordinators provide faculty allotment and timetable details at the beginning of every semester. Revised schedules are announced through notice boards and departmental communication channels.
""".strip()


def seed_defaults() -> None:
    if current_app.config["ADMIN_ENABLED"]:
        create_default_admin()
    create_default_faqs()
    create_starter_document()


def create_default_admin() -> None:
    username = current_app.config["ADMIN_USERNAME"]
    password = current_app.config["ADMIN_PASSWORD"]

    admin = AdminUser.query.filter_by(username=username).first()
    if admin:
        return

    db.session.add(
        AdminUser(
            username=username,
            password_hash=generate_password_hash(password),
        )
    )
    db.session.commit()


def create_default_faqs() -> None:
    if FaqEntry.query.count() > 0:
        return

    for item in STARTER_FAQS:
        db.session.add(FaqEntry(**item))
    db.session.commit()


def create_starter_document() -> None:
    existing = KnowledgeDocument.query.filter_by(source_kind="seed", filename="starter-handbook.txt").first()
    if existing:
        db.session.delete(existing)
        db.session.commit()

    ingest_text_content(
        title="Starter College Handbook",
        filename="starter-handbook.txt",
        text=STARTER_DOCUMENT,
        content_type="text/plain",
        source_kind="seed",
    )
