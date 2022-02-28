# Copyright (c) 2022, zerodha and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from robinhood.robinhood.doctype.checkin.checkin import Checkin


class RobinCertificateLog(Document):
    def before_insert(self):
        if not getattr(self, "from_checkin", None):
            c = frappe.new_doc("Checkin")
            c.owner = self.robin
            c.generate_certificate(int(self.type_of_certificate))
