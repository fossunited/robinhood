import frappe


def update(doc, method=None):
    if not frappe.db.sql("SELECT name from `tabRobin Chapter Mapping` where chapter = %(city)s", {"city": doc.city}):
        frappe.get_doc({
            "doctype": "Robin Chapter Mapping",
            "user": frappe.session.user,
            "chapter": doc.city
        }).save(ignore_permissions=True)