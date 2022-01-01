# Copyright (c) 2021, zerodha and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class RobinChapterMapping(Document):
    """Mapping."""

    def before_insert(self):
        if not self.user:
            self.user = frappe.session.user


@frappe.whitelist()
def get_mapped_city():
    """Return mapped cities."""
    data = frappe.db.sql("""
        SELECT c.city as value
        FROM `tabChapter` c
        INNER JOIN `tabRobin Chapter Mapping` as r
            ON c.name = r.chapter
        WHERE r.user = %(user)s

    """, {"user": frappe.session.user}, as_dict=True)
    return data
