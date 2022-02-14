(function () {
  if (frappe.session.user != "Guest") {
    document
      .querySelector(".nav-link[href*=checkin]")
      .setAttribute("href", "/checkin?new=1");
  }
})();

function checkMapping() {
  if (
    window.location.href.split("/").at(-1) !== "profile-update" &&
    !["Guest", undefined].includes(frappe.session?.user)
  ) {
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
}
window.onload = function () {
  checkMapping();
};
