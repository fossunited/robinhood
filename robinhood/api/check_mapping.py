import frappe


@frappe.whitelist()
def mapping():
    """Robin mapping."""
    return frappe.db.sql(
        "SELECT name from `tabRobin Chapter Mapping` where user = %(user)s limit 1",
        {"user": frappe.session.user}
    )
