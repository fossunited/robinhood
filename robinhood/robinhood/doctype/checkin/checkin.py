# Copyright (c) 2021, zerodha and contributors
# For license information, please see license.txt


import json
import os
import shutil
import time
from datetime import datetime
from hashlib import blake2b
from pathlib import Path

import frappe
import pdfkit
from frappe.model.document import Document
from frappe.utils import get_url, now
from frappe.utils.background_jobs import enqueue
from jinja2 import Template
from PIL import Image


def image_upsize(file_doc, method):
    """
    Upsize the uploaded selfies to a standard size.
    """
    filepath = frappe.utils.get_site_path() + "/public" + file_doc.file_url
    image = Image.open(filepath)

    image.thumbnail((400, 400))
    image.save(filepath, quality=90)
    return image


class Checkin(Document):
    def validate(self):
        if frappe.db.sql(
            """SELECT name
            FROM `tabCheckin`
            WHERE owner = %(owner)s and date(creation) = date(%(_now)s)
            """,
            {"owner": frappe.session.user, "_now": now()},
            as_dict=True,
        ):
            frappe.throw("Not allowed to check-in multiple times during the day")

    def store_certificate_log(self, checkin_count):
        # Store log of the certificate issued.
        doc = frappe.new_doc("Robin Certificate Log")
        doc.date_of_issue = datetime.now()
        doc.robin = self.owner
        doc.type_of_certificate = checkin_count
        doc.certificate_id = self.generate_digital_signature(
            [doc.robin, str(doc.date_of_issue), checkin_count]
        )
        doc.from_checkin = True
        doc.save(ignore_permissions=True)
        frappe.db.commit()
        return doc.certificate_id

    def generate_digital_signature(self, params):
        h = blake2b(
            key="eme+Rw5@Zl@pV2?DX56v89yB5L*#mVP>-Yq*eKK+SRcd0!-&".encode(),
            digest_size=14,
        )
        h.update(json.dumps(params).encode("utf-8"))
        return h.hexdigest()

    def image_downsize(self):
        # Downsize the selfie image for thumbnails.

        basepath = frappe.utils.get_site_path() + "/public"
        old_filepath = basepath + self.selfie

        if not self.selfie:
            return

        # Convert '/files/robin.hood-army.jpg' to '/files/robin.hood-army-small.jpg' by adding '-small'
        file_url = "-small.".join(self.selfie.rsplit(".", 1))
        new_filepath = basepath + file_url

        if Path(old_filepath).exists():
            # Copy existing original uploaded image (selfie) and then downsize it for thumbnail.
            shutil.copy(old_filepath, new_filepath)

            image = Image.open(new_filepath)
            image.thumbnail((210, 210))
            image.save(new_filepath, quality=90)

            self.db_set("selfie_thumbnail", file_url, update_modified=False)

    def generate_certificate(self, checkin_count):
        """
        Generate a certificate after every 10 and 100 checkins to be sent to the respective robin.
        """
        certificate_id = self.store_certificate_log(checkin_count)

        jinja_data = {
            "robin_name": (
                frappe.db.get_value("User", {"email": self.owner}, ["full_name"]) or ""
            ).title(),
            "base_url": get_url(),
            "robin_location": frappe.db.get_value(
                "Robin Chapter Mapping", {"user": self.owner}, ["chapter"]
            ),
            "certificate_date": time.strftime("%d %B %Y"),  # 12 December 2022
            "certificate_id": certificate_id,
        }

        certificate_filename = None
        if checkin_count == 1:
            certificate_filename = "cadet.html"
        elif checkin_count == 10:
            certificate_filename = "ninja.html"
        elif checkin_count == 50:
            certificate_filename = "gladiator.html"            
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
                bcc=['info@robinhoodarmy.com'],
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
        if res and res[0]["count"] in [10, 50, 100]:
            enqueue(self.generate_certificate, checkin_count=res[0]["count"])

    def on_update(self):
        self.image_downsize()


@frappe.whitelist()
def fetch_chapter(email):
    return frappe.db.get_value("Robin Chapter Mapping", {"user": email}, ["chapter"])


@frappe.whitelist(allow_guest=True)
def checkins(city):
    """Checkins."""
    if city:
        query = """SELECT count(c.name), date(c.creation)
            from `tabCheckin` c

            WHERE c.creation >= now() - INTERVAL 60 day
                and c.city = %(city)s
            group by date(c.creation)  order by date(c.creation)

        """
    else:
        query = """SELECT count(name), date(creation)
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
