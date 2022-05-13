"""Update username."""
import frappe

import string
import random


def username(doc, method=None):
    """Update username."""
    size = 6
    chars = string.ascii_uppercase + string.digits

    username = ''.join(random.choice(chars) for _ in range(size))
    while(frappe.db.get_value("User", {"username": username}, "name")):
        username = ''.join(random.choice(chars) for _ in range(size))

    doc.username = username.upper()
