# coding=utf-8
from __future__ import unicode_literals

import hashlib
import frappe
import datetime
from frappe import _

class ImportWiseTransaction:
    def __init__(self, kefiya_login):
        self.bank_transactions = []
        self.kefiya_login = kefiya_login

    def kefiya_import(self, wise_transactions):
        total_transactions = len(wise_transactions)

        for idx, t in enumerate(wise_transactions):

            progress = ((idx + 1) / total_transactions) * 100
            frappe.publish_progress(
                    progress,
                    title=_("Importing Transactions"),
                    description=_("Processing transaction {}/{}").format(idx + 1, total_transactions)
                )

            try:
                # Convert to positive value if required
                amount = abs(float(t['amount']['value']))
                status = t['type'].lower()

                if amount == 0:
                    continue
                
                if status not in ['credit', 'debit']:
                    frappe.log_error(
                        _('Payment type not handled'),
                        'Kefiya Import Error'
                    )
                    continue

                date = self.format_api_date(t['date'])
                applicant_name = 'applicant_name'
                purpose = t['details']['description']
                # applicant_iban = t['applicant_iban']
                # applicant_bin = t['applicant_bin']

                transaction_id = t['referenceNumber']
                if frappe.db.exists(
                    'Bank Transaction', {
                        'reference_number': transaction_id
                    }
                ):
                    continue

                if status == 'credit':
                    payment_type = 'Receive'
                    party_type = 'Customer'
                    deposit = amount
                    withdrawal = 0
                elif status == 'debit':
                    payment_type = 'Pay'
                    party_type = 'Supplier'
                    deposit = 0
                    withdrawal = amount

                party, party_type, iban, bank_account_no = self.get_bank_account_data(self.kefiya_login.bank_account)          

                bank_transaction = frappe.get_doc({
                    'doctype': 'Bank Transaction',
                    'date': date,
                    'status': 'Unreconciled',
                    'bank_account': self.kefiya_login.bank_account,
                    'company': self.kefiya_login.company,
                    'deposit': deposit,
                    'withdrawal': withdrawal,
                    'description': purpose,
                    'reference_number': transaction_id,
                    'allocated_amount': 0,
                    'unallocated_amount': amount,
                    'party_type': party_type,
                    'party': party,
                    'bank_party_name': applicant_name,
                    'bank_party_account_number': bank_account_no,
                    'bank_party_iban': iban,
                    'docstatus': 1
                })
                bank_transaction.insert()
                self.bank_transactions.append(bank_transaction)
            except Exception as e:
                frappe.log_error("Error importing bank transaction", "{}\n\n{}".format(t, frappe.get_traceback()))
                frappe.msgprint("There were some transactions with error. Please, have a look on Error Log.")



    def format_api_date(self, api_date):
        datetime_obj = datetime.datetime.fromisoformat(api_date.replace("Z", "+00:00"))
        return datetime_obj.strftime("%Y-%m-%d")


    def get_bank_account_data(self, bank_account):
        party, party_type = '', ''
       
        bank_account_doc = frappe.get_doc('Bank Account', {'name': bank_account})
        party = bank_account_doc.party
        party_type = bank_account_doc.party_type
        iban = bank_account_doc.iban
        bank_account_no = bank_account_doc.bank_account_no

        return [party, party_type, iban, bank_account_no]