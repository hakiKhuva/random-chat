from flask import Blueprint, request, session, redirect, url_for
from datetime import datetime, timezone
from ..functions import render

home = Blueprint("Home", __name__)

@home.route("/")
def index():
    return render(
        "home/index.html",
    )

@home.route("/", methods=["POST"])
def index_post():
    name = request.form.get("m-name")
    age = request.form.get("m-age")
    looking_age = request.form.get("m-looking-age")
    gender = request.form.get("m-gender")
    looking_gender = request.form.get("m-looking-gender")

    if name is None or name == "" or name.strip() == "":
        name = "stranger"
    
    if age is None or age == "" or age == "unknown" or age not in ("unknown", "13-17", "18-30", "31-40", "41-50", "51+"):
        age = "unknown"
    
    if looking_age is None or looking_age == "" or looking_age == "unknown" or looking_age not in ("unknown", "13-17", "18-30", "31-40", "41-50", "51+"):
        looking_age = "unknown"
    
    if gender is None or gender not in ("unknown", "male", "female"):
        gender = "unknown"
    
    if looking_gender is None or looking_gender not in ("unknown", "male", "female"):
        looking_gender = "unknown"
    
    session["chat-name"] = name
    session["chat-age"] = age
    session["chat-looking-age"] = looking_age
    session["chat-gender"] = gender
    session["chat-looking-gender"] = looking_gender
    session["timestat"] = datetime.now(timezone.utc)
    return redirect(url_for("Message.index"))


@home.route("/about")
def about():
    return render(
        "home/about.html",
        title="About"
    )


@home.route("/terms")
def terms():
    return render(
        "home/terms.html",
        title="Terms"
    )