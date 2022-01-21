# Copyright (c) 2021, zerodha and contributors
# For license information, please see license.txt


import os
import time

import frappe
import pdfkit
from frappe.model.document import Document
from frappe.utils import get_url
from frappe.utils.background_jobs import enqueue
from jinja2 import Template
from pdf_text_overlay import pdf_from_template


def image_resize(doc, method):
    """
    Resize uploaded selfies to a smaller size.
    """
    from PIL import Image

    filepath = frappe.utils.get_site_path() + "/public" + doc.file_url
    image = Image.open(filepath)
    MAX_SIZE = (220, 220)

    image.thumbnail(MAX_SIZE)
    image.save(filepath)

    return image


class Checkin(Document):
    def generate_certificate(self, checkin_count):
        """
        Generate a certificate after every 10 and 100 checkins to be sent to the respective robin.
        """
        jinja_data = {
            "robin_name": frappe.db.get_value(
                "User", {"email": self.owner}, ["first_name"]
            ),
            "base_url": get_url(),
            # "base_url": "http://0.0.0.0:8010",
            "robin_location": frappe.db.get_value(
                "Robin Chapter Mapping", {"user": self.owner}, ["chapter"]
            ),
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
            filename = f"{self.owner}_certificate.pdf"
            certificate_pdf = {
                "fname": filename,
                "fcontent": filecontent,
            }
            frappe.sendmail(
                recipients=[self.owner],
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
        WHERE owner=%s
        GROUP BY owner
        """,
            [self.owner],
            as_dict=True,
        )
        if res and res[0]["count"] in [10, 100]:
            enqueue(self.generate_certificate, checkin_count=res[0]["count"])


@frappe.whitelist()
def fetch_chapter(email):
    return frappe.db.get_value("Robin Chapter Mapping", {"user": email}, ["chapter"])


@frappe.whitelist(allow_guest=True)
def checkins(city):
    """Checkins."""
    if city:
        query = """SELECT sum(c.meals_served), date(c.creation)
            from `tabCheckin` c

            WHERE c.creation >= now() - INTERVAL 60 day
                and c.city = %(city)s
            group by date(c.creation)  order by date(c.creation)

        """
    else:
        query = """SELECT sum(meals_served), date(creation)
            from `tabCheckin`
            WHERE creation >= now() - INTERVAL 60 day
            group by date(creation) order by date(creation)"""

    data = frappe.db.sql(query, {"city": city}, as_list=True)
    labels = []
    values = []
    for row in data:
        values.append(row[0])
        labels.append(row[1])

    return {"labels": labels, "values": values}


@frappe.whitelist(allow_guest=True)
def top_robins(city):
    """Top ronins."""
    return frappe.db.sql(
        """SELECT c.name,
        c.selfie, c.creation, c.location, c.meals_served
        from `tabCheckin` c
        WHERE c.creation >= now() - INTERVAL 60 DAY
            and c.city = %(city)s
        order by date(c.creation)""",
        {"city": city},
    )
