import asyncio
import json
import threading

from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_decode as b64_decode
from django.utils.http import urlsafe_base64_encode as b64_encode

from .bot import csua_bot
from .forms import DiscordRegisterForm
from .models import DiscordRegisteredUser
from .tokens import discord_token_generator
from .utils import send_verify_mail


def register(request):
    if request.method == "POST":
        form = DiscordRegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            discord_tag = form.cleaned_data.get("discord_tag")
            host = request.get_host()
            emailb64 = b64_encode(email.encode("utf8"))
            send_verify_mail(email, discord_tag, host)
            return redirect(
                reverse("discord_register_email_sent", kwargs={"emailb64": emailb64})
            )
    else:
        form = DiscordRegisterForm()
    return render(request, "discord_register.html", {"form": form})


def email_sent(request, emailb64):
    email = b64_decode(emailb64).decode("utf8")
    return render(request, "discord_register_email_sent.html", {"email": email})


def register_confirm(request, emailb64, discord_tagb64, token):
    try:
        discord_tag = b64_decode(discord_tagb64).decode("utf8")
        email = b64_decode(emailb64).decode("utf8")
    except UnicodeDecodeError:
        return redirect("/")
    errors = False
    if discord_token_generator.check_token((email, discord_tag), token):
        if request.method == "POST":
            if DiscordRegisteredUser.objects.filter(email=email).exists():
                messages.error(request, f"{email} already registered!")
                errors = True

            if DiscordRegisteredUser.objects.filter(discord_tag=discord_tag).exists():
                messages.error(request, f"{discord_tag} already registered!")
                errors = True

            if not errors:
                if csua_bot.promote_user_to_hoser(discord_tag):
                    DiscordRegisteredUser.objects.create(
                        email=email, discord_tag=discord_tag
                    )
                    messages.info(
                        request,
                        f"{discord_tag} was successfully registered with email {email}",
                    )
                else:
                    messages.error(
                        request,
                        f"Failed to register {discord_tag}. "
                        "Please check for any typos. "
                        "If you still have problems, please contact the moderators.",
                    )
    else:
        messages.error(request, "Bad Token!")
    return render(request, "discord_register_confirm.html", {})
