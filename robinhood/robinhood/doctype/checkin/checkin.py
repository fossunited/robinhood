# Copyright (c) 2021, zerodha and contributors
# For license information, please see license.txt


import frappe
from frappe.model.document import Document
from frappe.utils.background_jobs import enqueue
# from pdf_text_overlay import pdf_from_template


class Checkin(Document):
    def generate_certificate(self):
        """
        Generate a certificate after every N checkins to be sent to the respective robin.
        """
        jinja_data = {
            "robin_name": frappe.db.get_value(
                "User", {"email": self.user}, ["first_name"]
            ),
            "checkins_milestone": 50,
        }

        with open(
            frappe.get_app_path(
                "robinhood",
                "robinhood",
                "doctype",
                "checkin",
                "certificate",
                "certificate.html",
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
                subject="Congratulations! You won a certificate in recognition to your \
                    work",
                message="Enjoy",
                attachments=[certificate_pdf],
                delayed=False,
            )

    def before_insert(self):
        self.user = frappe.session.user

    def after_insert(self):
        res = frappe.db.sql(
            """
        SELECT COUNT(*) AS count
        FROM `tabCheckin`
        WHERE user=%s
        GROUP BY user
        HAVING COUNT(*)>%s
        """,
            [self.user, 20],
            as_dict=True,
        )
        if res and res[0]["count"]:
            enqueue(self.generate_certificate)


@frappe.whitelist()
def fetch_sub_chapter(email):
    return frappe.db.get_value(
        "Robin Chapter Mapping", {"user": email}, ["sub_chapter"]
    )


@frappe.whitelist(allow_guest=True)
def checkins(city):
    """Checkins."""
    if city:
        query = """SELECT sum(c.meals_served), date(c.creation)
            from `tabCheckin` c
            INNER JOIN `tabRobin Chapter Mapping` as r
                ON c.chapter = r.name
            INNER JOIN `tabChapter` as cp
                ON r.chapter = cp.name
            WHERE c.creation >= now() - INTERVAL 60 day
                and cp.city = %(city)s
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
    return frappe.db.sql("""SELECT c.name,
        c.selfie, c.creation, c.location, c.meals_served
        from `tabCheckin` c
        INNER JOIN `tabRobin Chapter Mapping` as r
            ON c.chapter = r.name
        INNER JOIN `tabChapter` as cp
            ON r.chapter = cp.name
        WHERE c.creation >= now() - INTERVAL 60 DAY
            and cp.city = %(city)s
        order by date(c.creation)""", {"city": city})
