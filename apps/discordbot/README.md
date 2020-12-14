# Phillip documentation

Phillip is a discord bot for CSUA.

It verifies users' berkeley.edu email addresses and gives them the hoser role.

CSUA Discord Dev Team: https://discord.com/developers/teams/738580852191264826/information

* Ask robertq or rnithin if you need to be added.

Phillip App: https://discord.com/developers/applications/737930184837300274/information

# How to develop

For your developer machine, you will need to create a new discord app. Go to https://discord.com/developers/applications and click "New Application". Once it's created, go to the "Bot" tab on the left and create a bot user. Copy the token and paste it in your `.env` file. It should look something like:

```
DISCORD_TOKEN=Nzg2MTkyMDg4MjkwMDMzNjg0.X9C0cA.KYc0aow44Mkjel4nlscoFDKmoC4
```

Now, go to the "OAuth2" tab. Under the OAuth2 URL generator, select the "bot" scope.
Then, select the bot permissions. Phillip needs these permissions to work.

* Send Messages
* Manage Roles

Then, copy the URL and paste it into your browser. You will probably want to create a test server to test the bot with.

Testing certain things locally can be tricky.
If testing the email, be sure to set `DJANGO_FILEBASED_EMAIL_BACKEND=True` in your `.env`.
Email you send locally will be in `csua-backend/emails`.

Once you're happy with your changes to the bot behavior, get your code into the master branch.
Once it's there, then PhilBot will be updated automatically!
