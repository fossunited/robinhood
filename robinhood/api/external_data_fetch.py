import frappe
import requests

@frappe.whitelist(allow_guest=True)
def fetch_food_stats():
    headers = {"Accept":"applicaiton/json", "Content-type": "application/json"}
    response = requests.get(url="https://robinhoodarmy.com/joinnowmail/getStats", headers=headers).json()
    return response['food']['meals']
