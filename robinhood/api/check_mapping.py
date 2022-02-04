import frappe


@frappe.whitelist(allow_guest=True)
def mapping():
    """Robin mapping."""
    if frappe.session.user == 'Guest':
        return False
    if frappe.db.sql(
        "SELECT name from `tabRobin Chapter Mapping` where user = %(user)s limit 1",
        {"user": frappe.session.user}
    ):
        return False

    return True
