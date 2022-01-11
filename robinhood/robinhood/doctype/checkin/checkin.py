# Copyright (c) 2021, zerodha and contributors
# For license information, please see license.txt


import time

import frappe
from frappe.model.document import Document
from frappe.utils import get_url
from frappe.utils.background_jobs import enqueue
from pdf_text_overlay import pdf_from_template


class Checkin(Document):
    def generate_certificate(self, checkin_count):
        """
        Generate a certificate after every 10 and 100 checkins to be sent to the respective robin.
        """

        jinja_data = {
            "robin_name": frappe.db.get_value(
                "User", {"email": self.user}, ["first_name"]
            ),
            "base_url": get_url(),
            # "base_url": "http://0.0.0.0:8010",
            "robin_location": "Hyderabad",
            "certificate_date": time.strftime("%d %B %Y"),  # 12 December 2022
        }

        certificate_filename = None
        if checkin_count == 10:
            certificate_filename = "ninja.html"
        elif checkin_count == 100:
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
            filecontent = pdf_from_template(html_str, jinja_data)
            filename = f"{self.user}_certificate.pdf"
            with open(filename, "wb") as attachment:
                attachment.write(filecontent)

            certificate_pdf = {
                "fname": filename,
                "fcontent": filecontent,
            }

            frappe.sendmail(
                recipients=self.user,
                subject="Congratulations! You won a certificate in recognition to your work",
                message="Congratulations! You won a certificate in recognition to your work",
                attachments=[certificate_pdf],
                delayed=False,
            )

    def after_insert(self):
        res = frappe.db.sql(
            """
        SELECT COUNT(*) AS count
        FROM `tabCheckin`
        WHERE user=%s
        GROUP BY user
        """,
            [self.user],
            as_dict=True,
        )
        if res[0]["count"] in [10, 100]:
            enqueue(self.generate_certificate, checkin_count=res[0]["count"])


@frappe.whitelist()
def fetch_sub_chapter(email):
    return frappe.db.get_value(
        "Robin Chapter Mapping", {"user": email}, ["sub_chapter"]
    )
