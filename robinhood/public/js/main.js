(function () {
  if (frappe.session.user != "Guest") {
    document
      .querySelector(".nav-link[href*=checkin]")
      .setAttribute("href", "/checkin?new=1");
  }
})();

function checkMapping() {
    frappe.call({
      method: "robinhood.api.check_mapping.mapping",
      callback: function (r) {
        console.log(r.message);
        if (r.message === 0) {
          window.location = "/profile-update";
        }
      },
    });

}
window.onload = function () {
  checkMapping();
};
