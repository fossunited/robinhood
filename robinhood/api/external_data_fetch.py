import frappe
import requests

@frappe.whitelist(allow_guest=True)
def fetch_food_stats():
    headers = {"Accept":"applicaiton/json", "Content-type": "application/json"}
    response = requests.get(url="https://robinhoodarmy.com/joinnowmail/getStats", headers=headers).json()
    
    return response['food']['meals']

@frappe.whitelist(allow_guest=True)
def fetch_weekly_food_stats():
    headers = {"Accept":"applicaiton/json,text/html", "Content-type": "application/json"}
    response = requests.get(url="https://robinhoodarmy.com/joinnowmail/getMealStats", headers=headers).text
    
    return response
