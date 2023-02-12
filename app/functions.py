from flask import render_template
from .config import APP_NAME

def render(template_name: str, **kwargs):
    if "title" not in kwargs:
        kwargs['title'] = f"Chat with stranger - {APP_NAME}"

    kwargs['app_name'] = APP_NAME

    return render_template(
        template_name_or_list=template_name,
        **kwargs
    )