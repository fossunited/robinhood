# Copyright (c) 2022, zerodha and contributors
# For license information, please see license.txt

import frappe
import pdfkit
from frappe.model.document import Document
from frappe.utils import get_url
from jinja2 import Template
from robinhood.robinhood.doctype.checkin.checkin import Checkin


class RobinCertificateLog(Document):
    def before_insert(self):
        # This should be only triggered when certificate log created from the UI
        if not getattr(self, "from_checkin", None):
            c = frappe.new_doc("Checkin")
            c.owner = self.robin
            c.generate_certificate(int(self.type_of_certificate))


@frappe.whitelist(allow_guest=True)
def download_certificate():
    """
    Send certificates base64 of a particular logged in user
    """
    owner = frappe.session.user
    certificates = frappe.get_list(
        "Robin Certificate Log",
        fields=["date_of_issue", "certificate_id", "type_of_certificate"],
        filters=[["robin", "=", owner], ["certificate_id", "!=", None]],
    )
    resp = {10: None, 50: None, 100: None}
    for certificate in certificates:
        jinja_data = {
            "robin_name": (
                frappe.db.get_value("User", {"email": owner}, ["full_name"]) or ""
            ).title(),
            "base_url": get_url(),
            "robin_location": frappe.db.get_value(
                "Robin Chapter Mapping", {"user": owner}, ["chapter"]
            ),
            "certificate_date": certificate["date_of_issue"],
            "certificate_id": certificate["certificate_id"],
        }
        certificate_filename = None
        if int(certificate["type_of_certificate"]) == 10:
            certificate_filename = "ninja.html"
        elif int(certificate["type_of_certificate"]) == 50:
            certificate_filename = "gladiator.html"            
        elif int(certificate["type_of_certificate"]) == 100:
            certificate_filename = "centurion.html"

        with open(
            frappe.get_app_path(
                "robinhood",
                "robinhood",
                "doctype",
                "checkin",
                "certificate",
                certificate_filename,
            )
        ) as htmlfile:
            html_str = htmlfile.read()
            filecontent = pdfkit.from_string(
                Template(html_str).render(**jinja_data),
                None,
                options={
                    "margin-top": "0",
                    "margin-bottom": "0",
                    "margin-left": "0",
                    "margin-right": "0",
                    "page-size": "Legal",
                    "orientation": "Landscape",
                },
            )
        resp[int(certificate["type_of_certificate"])] = filecontent
    return resp
