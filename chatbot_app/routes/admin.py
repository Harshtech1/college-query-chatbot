from __future__ import annotations

from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from chatbot_app.auth import admin_login_required
from chatbot_app.models import AdminUser, ChatLog, FaqEntry, KnowledgeDocument


admin_bp = Blueprint("admin", __name__)


@admin_bp.before_request
def block_admin_in_hosted_demo():
    if current_app.config["ADMIN_ENABLED"]:
        return None
    return render_template("admin_unavailable.html"), 403


@admin_bp.route("/admin/login", methods=["GET", "POST"])
def login():
    if session.get("admin_user_id"):
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        admin = AdminUser.query.filter_by(username=username).first()

        if admin and check_password_hash(admin.password_hash, password):
            session["admin_user_id"] = admin.id
            session["admin_username"] = admin.username
            flash("Signed in successfully.", "success")
            return redirect(url_for("admin.dashboard"))

        flash("Invalid username or password.", "error")

    return render_template("admin_login.html")


@admin_bp.get("/admin")
@admin_login_required
def dashboard():
    faqs = FaqEntry.query.order_by(FaqEntry.priority.desc(), FaqEntry.updated_at.desc()).all()
    documents = KnowledgeDocument.query.order_by(KnowledgeDocument.created_at.desc()).limit(12).all()
    logs = ChatLog.query.order_by(ChatLog.created_at.desc()).limit(15).all()

    stats = {
        "faq_count": len(faqs),
        "document_count": KnowledgeDocument.query.count(),
        "processed_count": KnowledgeDocument.query.filter_by(status="processed").count(),
        "log_count": ChatLog.query.count(),
    }
    return render_template(
        "admin_dashboard.html",
        faqs=faqs,
        faqs_json=[faq.to_dict() for faq in faqs],
        documents=documents,
        logs=logs,
        stats=stats,
    )


@admin_bp.post("/admin/logout")
@admin_login_required
def logout():
    session.pop("admin_user_id", None)
    session.pop("admin_username", None)
    flash("You have been signed out.", "success")
    return redirect(url_for("admin.login"))
