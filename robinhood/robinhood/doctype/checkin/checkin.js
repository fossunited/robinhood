// Copyright (c) 2021, zerodha and contributors
// For license information, please see license.txt

frappe.ui.form.on("Checkin", {
  user: function (frm) {
    if (frm.is_new() == 1) {
      frappe.call({
        // method: "frappe.client.get_value",
        method: "robinhood.robinhood.doctype.checkin.checkin.fetch_sub_chapter",
        args: {
          email: frm.doc.user,
        },
        callback: function (r) {
          console.log("re....", r.message);
          if ("message" in r) {
            frm.set_value("sub_chapter", r.message);
          }
        },
      });
    }
  },
});
