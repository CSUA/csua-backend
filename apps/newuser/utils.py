def valid_password(password):
    """
    The password must be at least nine characters long. Also, it must include
    characters from two of:

    -alphabetical
    -numerical
    -punctuation/other
    """
    punctuation = set("""!@#$%^&*()_+|~-=\\`{}[]:";'<>?,./""")
    alpha = False
    num = False
    punct = False

    if len(password) < 9:
        return False

    for character in password:
        if character.isalpha():
            alpha = True
        if character.isdigit():
            num = True
        if character in punctuation:
            punct = True
    return (alpha + num + punct) >= 2
