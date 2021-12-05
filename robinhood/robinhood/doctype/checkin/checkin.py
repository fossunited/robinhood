# Copyright (c) 2021, zerodha and contributors
# For license information, please see license.txt


import frappe
from frappe.model.document import Document


class Checkin(Document):
    pass


@frappe.whitelist()
def fetch_sub_chapter(email):
    # if frappe.session.user != "Administrator":
    return frappe.db.get_value(
        "Robin Chapter Mapping", {"user": email}, ["sub_chapter"]
    )

    return {}
