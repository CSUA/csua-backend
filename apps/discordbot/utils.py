from .tokens import discord_token_generator
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from django.utils.http import (
    urlsafe_base64_encode as b64_encode,
    urlsafe_base64_decode as b64_decode,
)

def send_verify_mail(email, discord_tag, host="csua.berkeley.edu"):
    emailb64 = b64_encode(email.encode("utf8"))
    discord_tagb64 = b64_encode(discord_tag.encode("utf8"))
    
    token = discord_token_generator.make_token((email, discord_tag))
    html_message = render_to_string(
        "discord_register_email.html",
        {
            "host": host,
            "token": token,
            "email": email,
            "discord_tag": discord_tag,
            "emailb64": emailb64,
            "discord_tagb64": discord_tagb64,
        },
    )
    send_mail(
        subject="CSUA Discord Email Verification",
        message=strip_tags(html_message),
        from_email="noreply@csua.berkeley.edu",
        recipient_list=[email],
        html_message=html_message,
        )
