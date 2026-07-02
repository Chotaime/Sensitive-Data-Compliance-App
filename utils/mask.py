import re


# -----------------------------------------
# Email Masking
# -----------------------------------------

def mask_email(email):
    """
    john@gmail.com
    -> jo**@gmail.com
    """

    try:
        username, domain = email.split("@")

        if len(username) <= 2:
            masked = username[0] + "*" * (len(username) - 1)
        else:
            masked = username[:2] + "*" * (len(username) - 2)

        return f"{masked}@{domain}"

    except Exception:
        return email


# -----------------------------------------
# Phone Number Masking
# -----------------------------------------

def mask_phone(phone):
    """
    9876543210
    -> 98XXXXXX10
    """

    phone = re.sub(r"\D", "", str(phone))

    if len(phone) < 4:
        return phone

    return phone[:2] + "X" * (len(phone) - 4) + phone[-2:]


# -----------------------------------------
# Aadhaar Masking
# -----------------------------------------

def mask_aadhaar(aadhaar):
    """
    123456789123
    -> XXXX XXXX 9123
    """

    aadhaar = re.sub(r"\D", "", str(aadhaar))

    if len(aadhaar) != 12:
        return aadhaar

    return "XXXX XXXX " + aadhaar[-4:]


# -----------------------------------------
# PAN Masking
# -----------------------------------------

def mask_pan(pan):
    """
    ABCDE1234F
    -> ABCDXXXXF
    """

    pan = str(pan).upper()

    if len(pan) != 10:
        return pan

    return pan[:4] + "XXXX" + pan[-1]


# -----------------------------------------
# Credit Card Masking
# -----------------------------------------

def mask_credit_card(card):
    """
    1234567812345678
    -> XXXX XXXX XXXX 5678
    """

    card = re.sub(r"\D", "", str(card))

    if len(card) < 4:
        return card

    return "XXXX XXXX XXXX " + card[-4:]


# -----------------------------------------
# Password Masking
# -----------------------------------------

def mask_password(password):
    """
    password123
    -> ***********
    """

    return "*" * len(str(password))


# -----------------------------------------
# API Key Masking
# -----------------------------------------

def mask_api_key(key):
    """
    sk-123456789abcdef
    -> sk-1*********cdef
    """

    key = str(key)

    if len(key) <= 8:
        return "*" * len(key)

    return key[:4] + "*" * (len(key) - 8) + key[-4:]


# -----------------------------------------
# Employee ID Masking
# -----------------------------------------

def mask_employee_id(emp):
    """
    EMP123456
    -> EM*****56
    """

    emp = str(emp)

    if len(emp) <= 4:
        return "*" * len(emp)

    return emp[:2] + "*" * (len(emp) - 4) + emp[-2:]


# -----------------------------------------
# Salary Masking (Optional)
# -----------------------------------------

def mask_salary(salary):
    """
    60000
    -> *****0
    """

    salary = str(salary)

    if len(salary) <= 2:
        return "*" * len(salary)

    return "*" * (len(salary) - 1) + salary[-1]