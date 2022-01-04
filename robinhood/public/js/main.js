(function() {
	if (frappe.session.user != 'Guest') {
		document.querySelector('.nav-link[href*=checkin]').setAttribute('href', '/checkin?new=1');
	}
})();

function checkMapping(){
	if(window.location.href.split('/').at(-1) != 'profile-update' && frappe.session && frappe.session.user != 'Guest'){
		frappe.call({
			method: "robinhood.api.check_mapping.mapping",
			callback: function (r) {
			    console.log(r.message)
				if (r.message.length === 0) {
				    window.location = '/profile-update'
				}
			}
		})
	}

}
window.onload = function() {
  checkMapping();
};
