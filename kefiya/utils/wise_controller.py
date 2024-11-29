import frappe
import requests
from frappe import _

from frappe.utils import now_datetime
from .import_wise_transaction import ImportWiseTransaction

class WiseController:
    def __init__(self, kefiya_login_docname):
        self.kefiya_login = frappe.get_doc("Kefiya Login", kefiya_login_docname)
        self.name = self.kefiya_login.name
        self.profile = self.kefiya_login.profile
        self.url = self.kefiya_login.api_url
        self.profile_id = self.kefiya_login.profile_id
        self.account_id = self.kefiya_login.account_list
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


    def get_wise_transactions(self, start_date=None, end_date=None):
        """Get Wise transactions.

        The code is not allowing to fetch transaction which are older
        than 90 days. Also only transaction from atleast one day ago can be
        fetched

        :param start_date: Date to start the fetch
        :param end_date: Date to end the fetch
        :type start_date: date
        :type end_date: date
        :return: Transaction as json object list
        """
        # if start_date is None:
        #     start_date = now_datetime().date() - relativedelta(days=90)

        # if end_date is None:
        #     end_date = now_datetime().date() - relativedelta(days=1)

        # if (now_datetime().date() - start_date).days >= 90:
        #     raise NotImplementedError(
        #         _("Start date more then 90 days in the past")
        #     )

        # with self.fints_connection:
        #     account = self.get_fints_account_by_iban(
        #         self.kefiya_login.account_iban)
        #     return json.loads(
        #         json.dumps(
        #             self.fints_connection.get_transactions(
        #                 account,
        #                 start_date,
        #                 end_date
        #             ),
        #             cls=mt940.JSONEncoder
        #         )
        #     )
    
        response = requests.get(self.url + f"/v1/profiles/{self.profile_id}/balance-statements/{self.account_id}/statement.json?intervalStart={start_date}T00:00:00.000Z&intervalEnd={end_date}T23:59:59.999Z&type=COMPACT", headers=self.headers)
        transactions = response.json()
        return transactions['transactions']


    def import_wise_transactions(self, kefiya_import):
        """Create bank transactions based on Wise transactions.

        :param kefiya_import: kefiya_import doc name
        :type kefiya_import: str
        :return: List of transactions
        """
        try:
            # self.interactive.show_progress_realtime(
            #     _("Start transaction import"), 40, reload=False
            # )
            curr_doc = frappe.get_doc("Kefiya Import", kefiya_import)
            new_bank_transactions = None
            transactions = self.get_wise_transactions(
                curr_doc.from_date,
                curr_doc.to_date
            )

            if(len(transactions) == 0):
                frappe.msgprint(_("No transaction found"))
            else:
                # try:
                #     save_file(
                #         kefiya_import + ".json",
                #         json.dumps(
                #             tansactions, ensure_ascii=False
                #         ).replace(",", ",\n").encode('utf8'),
                #         'Kefiya Import',
                #         kefiya_import,
                #         folder='Home/Attachments/FinTS',
                #         decode=False,
                #         is_private=1,
                #         df=None
                #     )
                # except Exception as e:
                #     frappe.throw(_("Failed to attach file"), e)

                # curr_doc.start_date = tansactions[0]["date"]
                # curr_doc.end_date = tansactions[-1]["date"]

                importer = ImportWiseTransaction(self.kefiya_login)
                importer.kefiya_import(transactions)

                if len(importer.bank_transactions) == 0:
                    frappe.msgprint(_("No new transactions found"))
                # else:
                #     # Save payment entries
                #     frappe.db.commit()

                #     frappe.msgprint(_(
                #         "Found a total of '{0}' payments"
                #     ).format(
                #         len(importer.bank_transactions)
                #     ))
                # new_bank_transactions = importer.bank_transactions

            # curr_doc.submit()
            # self.interactive.show_progress_realtime(
            #     _("Bank Transaction import completed"), 100, reload=False
            # )

            # return {
            #     "transactions": tansactions[:10],
            #     "payments": new_bank_transactions,
            # }

        except Exception as e:
            frappe.throw(_(
                "Error parsing transactions<br>{0}"
            ).format(str(e)), frappe.get_traceback())