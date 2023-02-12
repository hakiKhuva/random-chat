from flask import Blueprint, render_template, request, redirect, url_for, session
from datetime import timedelta, datetime, timezone
from sqlalchemy import func
from flask_socketio import emit

from ..socketio import socketio
from ..models.db import db
from ..models.chat_user import ChatUser


message = Blueprint("Message", __name__, url_prefix="/message")


@message.route("/")
def index():
    if session.get("timestat") is None or (datetime.now(timezone.utc) - session["timestat"]) > timedelta(hours=1):
        return redirect(url_for('Home.index'))

    return render_template(
        "message/index.html",
        live_users_count = ChatUser.query.with_entities(func.count(ChatUser.id)).first()[0]
    )


@socketio.on("connect")
def on_connect():
    current_user_sid = request.sid

    user = ChatUser(
        name=session["chat-name"],
        age=session["chat-age"],
        looking_age=session["chat-looking-age"],
        gender=session["chat-gender"],
        looking_gender=session["chat-looking-gender"],
        sid=current_user_sid,
        message_to=None,
        status="free"
    )
    db.session.add(user)
    db.session.commit()

    free_user = ChatUser.query.filter(
        ChatUser.status == "free",
        ChatUser.sid != current_user_sid,
        ChatUser.age == session["chat-looking-age"],
        ChatUser.gender == session["chat-looking-gender"]
    ).first()

    if free_user is None:
        free_user = ChatUser.query.filter(
            ChatUser.status == "free",
            ChatUser.sid != current_user_sid,
            ChatUser.looking_age == session["chat-age"],
            ChatUser.looking_gender == session["chat-gender"]
        ).first()

    if free_user is not None:
        user.message_to = free_user.sid
        user.status = "busy"
        free_user.message_to = current_user_sid
        free_user.status = "busy"
        db.session.commit()

        emit("join-user",{
            "status": "found"
        }, broadcast=False, to=current_user_sid)

        emit("status-message", {
                "message": "You're connected to a stranger!",
                "mimetype": "text"
            }, broadcast=False, to=current_user_sid)

        emit("new-message", {
            "data": f"Hello, I am {free_user.name}, my age is {free_user.age} and my gender is {free_user.gender}",
            "s_name": free_user.name,
            "mimetype": "text"
        }, broadcast=False, to=current_user_sid)

        emit("join-user",{
            "status": "found"
        }, broadcast=False, to=free_user.sid)

        emit("status-message", {
                "message": "You're connected to a stranger!",
                "mimetype": "text"
            }, broadcast=False, to=free_user.sid)
        
        emit("new-message", {
            "data": f"Hello, I am {user.name}, my age is {user.age} and my gender is {user.gender}",
            "s_name": user.name,
            "mimetype": "text"
        }, broadcast=False, to=free_user.sid)


@socketio.on("disconnect")
def on_disconnect():
    current_user_sid = request.sid

    user = ChatUser.query.filter(ChatUser.sid == current_user_sid).first()
    if user is not None:
        db.session.delete(user)
        db.session.commit()

    if user is not None and user.status == "busy":
        message_to_sid = user.message_to
        message_to_user = ChatUser.query.filter(ChatUser.message_to == message_to_sid).first()

        if message_to_user is not None:
            message_to_user.delete(message_to_user)
            db.session.commit()
        
        if message_to_sid is not None:
            emit("status-message", {
                "message": "Stranger is disconnected!"
            }, broadcast=False, to=message_to_sid)

            emit("disconnect", {}, broadcast=False, to=message_to_sid)


@socketio.on("send-message")
def on_send_message(data:dict):
    current_user_sid = request.sid

    current_user = ChatUser.query.filter(ChatUser.sid == current_user_sid).first()
    
    if current_user is not None:
        message_to_user = ChatUser.query.filter(ChatUser.sid == current_user.message_to).first()

        if message_to_user is not None:
            message_to_sid = message_to_user.sid
    
            if data.get("data"):
                data.update({
                    "s_name": current_user.name
                })
                emit("new-message", data, broadcast=False, to=message_to_sid)