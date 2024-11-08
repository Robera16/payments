import frappe
import requests

class WiseController:
    def __init__(self, kefiya_login_docname):
        self.kefiya_login = frappe.get_doc("Kefiya Login", kefiya_login_docname)
        self.name = self.kefiya_login.name
        self.profile = self.kefiya_login.profile
        self.url = self.kefiya_login.api_url
        self.headers = {
            "Authorization": f"Bearer {self.kefiya_login.get_password('api_key')}",
            "Content-Type": "application/json"
        }

    def get_wise_accounts(self):
        """Get Wise Accounts.
        :return: List of WISEAccount objects.
        """
        
        frappe.publish_progress(25, title="Loading Wise Accounts", description="Fetching Profile ID...")

        profile_id = self.get_profile_id()

        frappe.publish_progress(75, title="Loading Wise Accounts", description="Fetching Account Balances ID...")

        response = requests.get(self.url + f"/v4/profiles/{profile_id}/balances?types=STANDARD", headers=self.headers)
        balances = response.json()
        ids = [balance['id'] for balance in balances]

        frappe.publish_progress(100, title="Loading Wise Accounts", description="Completed")

        return {
            'profile_id': profile_id,
            'ids': ids
        }

    def get_profile_id(self):
        response = requests.get(self.url + "/v2/profiles", headers=self.headers)
        profiles = response.json()
        for profile in profiles:
            if self.profile == profile['type']:
                return profile['id']