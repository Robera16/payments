// Copyright (c) 2019, jHetzer and contributors
// For license information, please see license.txt

{% include "kefiya/public/js/controllers/fints_interactive.js" %}

frappe.ui.form.on('Kefiya Login', {
	onload: function(frm) {
		kefiya.interactive.progressbar(frm);
		if(frm.doc.account_iban){
			frm.toggle_display("transaction_settings_section",true);
		}else{
			frm.toggle_display("transaction_settings_section",false);
		}
	},
	setup: function(frm) {
		frm.set_query("erpnext_account", function() {
			return {
				filters: {
					'account_type': 'Bank',
					'company': frm.doc.company,
					'is_group': 0
				}
			};
		});
	},
	refresh: function(frm) {
		// frm.set_df_property("account_nr","options",frm.fields_dict.account_nr.value)
		// if(frm.fields_dict.account_nr.df.reqd && )
		// frm.toggle_reqd("account_nr",true);
		if(frm.doc.iban_list){
			frm.set_df_property("account_iban","options",JSON.parse(frm.doc.iban_list));
		}
		if(!frm.doc.account_iban){
			frm.toggle_display("account_iban",false);
		}
		if(!frm.doc.account_list){
			frm.toggle_display("account_list",false);
		}
		if(!frm.doc.profile_id){
			frm.toggle_display("profile_id",false);
		}
		/*
		if(!frm.doc.__unsaved && frm.doc.account_nr){
			frm.toggle_display("transaction_settings_section",true)
		}else{
			frm.toggle_display("transaction_settings_section",false)
		}
		*/
	},
	/* account_nr: function(frm) {
		if(frm.doc.account_nr){
			frm.save();
		}
	},*/
	get_accounts: function(frm) {
		if (frm.doc.__unsaved){
			frm.save().then(() => {
				frm.events.call_get_login_accounts(frm);
			});
		}else{
			frm.events.call_get_login_accounts(frm);
			frappe.hide_progress();
		}
	},
	load_accounts: function(frm) {
		if (frm.doc.__unsaved){
			frm.save().then(() => {
				frm.events.get_wise_accounts(frm);
			});
		}else{
			frm.events.get_wise_accounts(frm);
			frappe.hide_progress();
		}
	},
	get_wise_accounts: function(frm){

		frappe.call({
			method:"kefiya.utils.client.get_wise_accounts",
			args: {
				'kefiya_login_docname': frm.doc.name,
			},
			callback: function(r) {

				frm.toggle_display("profile_id",true);
				frm.set_value("profile_id", r.message.profile_id);
				frm.toggle_display("account_list",true);
				frm.set_df_property('account_list', 'options', r.message.ids);

				frm.toggle_reqd("profile_id",true);
				frm.toggle_reqd("account_list",true);
			},
			error: function(/* r */) {
				// frappe.hide_progress();
				// frm.set_df_property("account_iban","options","");
				// frm.toggle_display("account_iban",false);

				// frappe.run_serially([
				// 	() => frm.set_value("account_iban",""),
				// 	() => frm.set_value("iban_list",""),
				// 	() => frm.set_value("failed_connection",frm.doc.failed_connection + 1),
				// 	() => frm.save(),
				// ]);
			}
		});
	},
	call_get_login_accounts: function(frm){
		frappe.call({
			method:"kefiya.utils.client.get_accounts",
			args: {
				'kefiya_login': frm.doc.name,
				'user_scope': frm.doc.name
			},
			callback: function(r) {
				// console.log(r)
				frm.toggle_display("account_iban",true);
				frm.set_value("account_iban","");
				frm.set_value("failed_connection",0);

				var ibanList = r.message.accounts.map(x => x[0]);
				frm.set_df_property("account_iban","options",ibanList);
				// frm.toggle_reqd("account_nr",true);
				// console.log(JSON.stringify(ibanList));
				frm.set_value("iban_list", JSON.stringify(ibanList));
				frm.toggle_reqd("account_iban",true);
			},
			error: function(/* r */) {
				// console.log(r);
				frappe.hide_progress();
				frm.set_df_property("account_iban","options","");
				frm.toggle_display("account_iban",false);

				frappe.run_serially([
					() => frm.set_value("account_iban",""),
					() => frm.set_value("iban_list",""),
					() => frm.set_value("failed_connection",frm.doc.failed_connection + 1),
					() => frm.save(),
				]);
			}
		});
	},
});
