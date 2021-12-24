# Copyright (c) 2021, zerodha and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class RobinChapterMapping(Document):
    """Mapping."""

    def before_insert(self):
        if not self.user:
            self.user = frappe.session.user
