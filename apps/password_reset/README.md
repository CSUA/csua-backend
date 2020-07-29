# CSUA Password Reset

To reset passwords we use a token-based system.

## Process

1. User requests password reset (`RequestPasswordResetView`)
2. Token is created and sent to user's email (as specified in LDAP)
3. User follows email link with token
4. User resets password (`PasswordResetView`)

## Tokens

Tokens have a few properties:

- Expire after 3 days (default `settings.PASSWORD_RESET_TIMEOUT_DAYS`)
- Are invalidated upon successful password change
- Do not leak user's password

They are generated from a timestamp and a salted HMAC of the timestamp using the hashed password from LDAP as the key.
This means that once the hashed password is changed, the token is invalidated.

```
timestamp <- days since 1/1/2001
hash_value <- LDAP hashed password + timestamp
mac <- HMAC_SHA1(timestamp, hash_value)
token <- timestamp + "-" + mac
```

See: https://github.com/django/django/blob/stable/2.2.x/django/contrib/auth/tokens.py
