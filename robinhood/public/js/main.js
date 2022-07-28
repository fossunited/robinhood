(function() {
    if (frappe.session.user != "Guest") {
        document
            .querySelector(".nav-link[href*=checkin]")
            .setAttribute("href", "/checkin");
    }
})();

function checkMapping() {
    if(
        window.location.pathname.split('/')[1] !== "profile-update"
    ){
        frappe.call({
            method: "robinhood.api.check_mapping.mapping",
            callback: function(r) {
                if (r.message === true) {
                    window.location = "/profile-update";
                }
            },
        });
    }
}

window.onload = function() {
    checkMapping();
};
