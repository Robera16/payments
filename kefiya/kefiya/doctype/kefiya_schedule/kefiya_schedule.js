// Copyright (c) 2019, jHetzer and contributors
// For license information, please see license.txt

{% include "kefiya/public/js/controllers/fints_interactive.js" %}

frappe.ui.form.on('Kefiya Schedule', {
	onload: function(frm) {
		kefiya.interactive.progressbar(frm);
	},
	refresh: function(frm) {
		frm.clear_custom_buttons();
		frm.events.import_transactions(frm);
	},
	import_transactions: function(frm) {
		frm.add_custom_button(__("Import Transaction"), function(){
			frm.save().then(() => {
				frappe.call({
					method: "kefiya.kefiya.doctype.kefiya_schedule.kefiya_schedule.scheduled_import_fints_payments",
					args: {
						'manual': true
					}
				});
			});
		}).addClass("btn-primary");
	}
});


frappe.ui.form.on('Kefiya Schedule Item', {
    kefiya_login: function (frm, cdt, cdn) {
		
		const row = frappe.get_doc(cdt, cdn);
		if(row.kefiya_login){
			frappe.db.get_value("Kefiya Login",{'name': row.kefiya_login},['connection_type'], function(value){			
				frappe.model.set_value(cdt, cdn, 'connection_type', value.connection_type)
			});
		}
    }
});
