import frappe


def update(doc, method=None):
    if not frappe.db.sql(
        "SELECT name from `tabRobin Chapter Mapping` where chapter = %(city)s",
        {"city": doc.city},
    ):
        frappe.get_doc(
            {
                "doctype": "Robin Chapter Mapping",
                "user": frappe.session.user,
                "chapter": doc.city,
            }
        ).save(ignore_permissions=True)


@frappe.whitelist()
def fetch_profile_details():
    res = frappe.db.sql(
        """
    SELECT first_name, last_name, mobile_no, city, profile_picture
    FROM `tabUser profile update`
    WHERE owner=%s
    """,
        [frappe.session.user],
    )
    if res:
        return res
    return []
