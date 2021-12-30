(function() {
	if (frappe.session.user != 'Guest') {
		document.querySelector('.nav-link[href*=checkin]').setAttribute('href', '/checkin?new=1');
	}
})();