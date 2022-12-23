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


@frappe.whitelist()
def download_certificate(certificate_type):
    """
    Send certificates base64 of a particular logged in user
    """
    owner = frappe.session.user
    certificates = frappe.get_list(
        "Robin Certificate Log",
        fields=["date_of_issue", "certificate_id", "type_of_certificate"],
        filters=[["robin", "=", owner], ["certificate_id", "!=", ""], ["type_of_certificate", "=", certificate_type]],
    )
    resp = {
        "message": f"Certificate sent to your email {owner}"
    }
    if certificates:
        certificate = certificates[0]
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
        certificate_meta = frappe.db.get_value(
            "Certificate",
            filters={"number_of_checkins": int(certificate_type)},
            fieldname=["certificate_name", "html"],
            as_dict=True, cache=True
        )

        filecontent = pdfkit.from_string(
            Template(certificate_meta.html).render(**jinja_data),
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
        filename = f"{owner}_certificate.pdf"
        certificate_pdf = {
                "fname": filename,
                "fcontent": filecontent,
            }

        frappe.sendmail(
            recipients=[owner],
            bcc=['info@robinhoodarmy.com'],
            subject="Congratulations! You won a certificate in recognition to your work",
            message="Congratulations! You won a certificate in recognition to your work",
            attachments=[certificate_pdf],
            delayed=False,
        )
    else:
        resp['message'] = "Certificate not generated"

    return resp
