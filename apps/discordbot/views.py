import threading
import asyncio
import json

from django.http import HttpResponse
from django.shortcuts import render
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from . import bot
from .forms import DiscordRegisterForm
from .tokens import discord_token_generator
from .models import DiscordRegisteredUser


def register(request):
    if request.method == "POST":
        form = DiscordRegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            discord_tag = form.cleaned_data.get("discord_tag")

            token = discord_token_generator.make_token((email, discord_tag))
            html_message = render_to_string(
                "discord_register_email.html",
                {
                    "host": request.get_host(),
                    "token": token,
                    "email": email,
                    "discord_tag": discord_tag,
                },
            )
            send_mail(
                subject="CSUA Discord Email Verification",
                message=strip_tags(html_message),
                from_email="jonathan@csua.berkeley.edu",
                recipient_list=[email],
                html_message=html_message,
            )
    else:
        form = DiscordRegisterForm()
    return render(request, "discord_register.html", {"form": form})


def register_confirm(request, email, discord_tag, token):
    if discord_token_generator.check_token((email, discord_tag), token):
        if DiscordRegisteredUser.objects.filter(email=email).exists():
            pass
        if DiscordRegisteredUser.objects.filter(discord_tag=discord_tag).exists():
            pass
        user = DiscordRegisteredUser.objects.create(
            email=email, discord_tag=discord_tag
        )
        bot.promote_user(discord_tag)
        return render(request, "", {})
    else:
        return HttpResponse("Bad Token")
