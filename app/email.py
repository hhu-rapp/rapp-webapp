from flask import current_app, render_template
from flask.ctx import AppContext
from flask_mail import Message
from threading import Thread

from . import mail


def send_async_email(app_context: AppContext, msg: str) -> None:
    app_context.push()
    mail.send(msg)


def send_email(to: str, subject: str, template: str, **kwargs):
    """ Send an email to the provided address.

    Parameters
    ----------
    to : str
        The email address the email will be sent to.
    subject : str
        The subject of the email.
    template : str
        The template the email will use.
    **kwargs
        Additional arguments for email creation or use in template.
    """
    msg: Message = Message(
        current_app.config['RAPP_MAIL_SUBJECT_PREFIX'] + subject,
        sender=current_app.config['RAPP_MAIL_SENDER'],
        recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)

    thr: Thread = Thread(
        target=send_async_email,
        args=[current_app.app_context(), msg]
    )
    thr.start()
    return thr
