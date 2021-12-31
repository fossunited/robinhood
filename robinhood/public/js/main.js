(function() {
	if (frappe.session.user != 'Guest') {
		document.querySelector('.nav-link[href*=checkin]').setAttribute('href', '/checkin?new=1');
	}
})();

function checkMapping(){
	if(window.location.href.split('/').at(-1) != 'profile-update'){
		frappe.call({
			method: "robinhood.robinhood.doctype.robin_chapter_mapping.robin_chapter_mapping.get_mapped_city",
			callback: function (r) {
			    console.log(r.message)
				if (!r.message) {
				    window.location = '/profile-update'
				}
			}
		})
	}

}
window.onload = function() {
  checkMapping();
};
