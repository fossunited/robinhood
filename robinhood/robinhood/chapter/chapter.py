from datetime import date

import frappe
from frappe.utils.data import get_first_day_of_week, get_last_day_of_week


@frappe.whitelist(allow_guest=True)
def fetch_chapter_checkins():
    """
    Show chapters and their checkin count.
    """
    return frappe.db.sql(
        """
        SELECT sc.parent_chapter, c.sub_chapter, COUNT(*) AS checkin_count
        FROM `tabCheckin` c
        JOIN `tabSub Chapter` sc ON c.sub_chapter=sc.name
        GROUP BY sc.parent_chapter, c.sub_chapter
    """,
        as_dict=True,
    )


@frappe.whitelist(allow_guest=True)
def fetch_top_chapter_checkins():
    """
    Show checkin count of chapters in this week
    """
    re = frappe.db.sql(
        """
        SELECT sc.parent_chapter, c.sub_chapter, COUNT(*) AS checkin_count
        FROM `tabCheckin` c
        JOIN `tabSub Chapter` sc ON c.sub_chapter=sc.name
        WHERE c.creation BETWEEN %s AND %s
        GROUP BY sc.parent_chapter, c.sub_chapter
    """,
        [
            str(get_first_day_of_week(date.today())),
            str(get_last_day_of_week(date.today())),
        ],
        as_dict=True,
    )
    return re
