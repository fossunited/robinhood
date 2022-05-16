"""Update username."""
import frappe

import string
import random


def execute():
    """Update username."""
    size = 6
    chars = string.ascii_uppercase + string.digits
    userlist = frappe.db.sql(
        "SELECT name FROM `tabUser`",
        as_dict=True
    )

    for user in userlist:
        user_doc = frappe.get_doc("User", user.name)
        username = ''.join(random.choice(chars) for _ in range(size))
        while(frappe.db.get_value("User", {"username": username}, "name")):
            username = ''.join(random.choice(chars) for _ in range(size))

        user_doc.username = username.upper()
        user_doc.save()
        frappe.db.commit()
