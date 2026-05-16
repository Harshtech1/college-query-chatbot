from __future__ import annotations

from functools import wraps

from flask import flash, redirect, session, url_for


def admin_login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not session.get("admin_user_id"):
            flash("Please sign in to access the admin dashboard.", "error")
            return redirect(url_for("admin.login"))
        return view(*args, **kwargs)

    return wrapped_view

