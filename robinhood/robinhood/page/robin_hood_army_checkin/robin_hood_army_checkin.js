frappe.provide("frappe.setup");
frappe.provide("frappe.setup.events");
frappe.provide("frappe.ui");

frappe.setup = {
	slides: [],
	events: {},
	data: {},
	utils: {},
	domains: [],

	on: function (event, fn) {
		if (!frappe.setup.events[event]) {
			frappe.setup.events[event] = [];
		}
		frappe.setup.events[event].push(fn);
	},
	add_slide: function (slide) {
		frappe.setup.slides.push(slide);
	},

	remove_slide: function (slide_name) {
		frappe.setup.slides = frappe.setup.slides.filter((slide) => slide.name !== slide_name);
	},

	run_event: function (event) {
		$.each(frappe.setup.events[event] || [], function (i, fn) {
			fn();
		});
	}
}

frappe.pages['robin-hood-army-checkin'].on_page_load = function (wrapper) {
	let requires = (frappe.boot.setup_wizard_requires || []);
	frappe.require(requires, function () {
		frappe.call({
			method: "frappe.desk.page.setup_wizard.setup_wizard.load_languages",
			freeze: true,
			callback: function (r) {
				frappe.setup.data.lang = r.message;

				frappe.setup.run_event("before_load");
				var wizard_settings = {
					parent: wrapper,
					slides: frappe.setup.slides,
					slide_class: frappe.setup.SetupWizardSlide,
					unidirectional: 1,
					done_state: 1,
				}
				frappe.wizard = new frappe.setup.SetupWizard(wizard_settings);
				frappe.setup.run_event("after_load");
				// frappe.wizard.values = test_values_edu;
				let route = frappe.get_route();
				if (route) {
					frappe.wizard.show_slide(route[1]);
				}
			}
		});
	});
};

frappe.pages['robin-hood-army-checkin'].on_page_show = function () {
	if (frappe.get_route()[1]) {
		frappe.wizard && frappe.wizard.show_slide(frappe.get_route()[1]);
	}
};

frappe.setup.on("before_load", function () {
	// load slides
	frappe.setup.slides_settings.forEach((s) => {
		if (!(s.name === 'user' && frappe.boot.developer_mode)) {
			// if not user slide with developer mode
			frappe.setup.add_slide(s);
		}
	});
});

frappe.setup.SetupWizard = class SetupWizard extends frappe.ui.Slides {
	constructor(args = {}) {
		super(args);
		$.extend(this, args);

		this.page_name = "robin-hood-army-checkin";
		this.welcomed = true;
		frappe.set_route("robin-hood-army-checkin/0");
	}

	make() {
		super.make();
		this.container.addClass("container robin-hood-army-checkin-slide with-form");
		this.$next_btn.addClass('action');
		this.$complete_btn.addClass('action');
		this.setup_keyboard_nav();
	}

	setup_keyboard_nav() {
		$('body').on('keydown', this.handle_enter_press.bind(this));
	}

	disable_keyboard_nav() {
		$('body').off('keydown', this.handle_enter_press.bind(this));
	}

	handle_enter_press(e) {
		if (e.which === frappe.ui.keyCode.ENTER) {
			var $target = $(e.target);
			if ($target.hasClass('prev-btn')) {
				$target.trigger('click');
			} else {
				this.container.find('.next-btn').trigger('click');
				e.preventDefault();
			}
		}
	}

	before_show_slide() {
		if (!this.welcomed) {
			frappe.set_route(this.page_name);
			return false;
		}
		return true;
	}

	show_slide(id) {
		if (id === this.slides.length) {
			// show_slide called on last slide
			this.action_on_complete();
			return;
		}
		super.show_slide(id);
		frappe.set_route(this.page_name, id + "");
	}

	show_hide_prev_next(id) {
		super.show_hide_prev_next(id);
		if (id + 1 === this.slides.length) {
			this.$next_btn.removeClass("btn-primary").hide();
			this.$complete_btn.addClass("btn-primary").show()
				.on('click', () => this.action_on_complete());
		} else {
			this.$next_btn.addClass("btn-primary").show();
			this.$complete_btn.removeClass("btn-primary").hide();
		}
	}

	refresh_slides() {
		// For Translations, etc.
		if (this.in_refresh_slides || !this.current_slide.set_values()) {
			return;
		}
		this.in_refresh_slides = true;

		this.update_values();
		frappe.setup.slides = [];
		frappe.setup.run_event("before_load");

		frappe.setup.slides = this.get_setup_slides_filtered_by_domain();

		this.slides = frappe.setup.slides;
		frappe.setup.run_event("after_load");

		// re-render all slide, only remake made slides
		$.each(this.slide_dict, (id, slide) => {
			if (slide.made) {
				this.made_slide_ids.push(id);
			}
		});
		this.made_slide_ids.push(this.current_id);
		this.setup();

		this.show_slide(this.current_id);
		this.refresh(this.current_id);
		setTimeout(() => {
			this.container.find('.form-control').first().focus();
		}, 200);
		this.in_refresh_slides = false;
	}

	action_on_complete() {
		if (!this.current_slide.set_values()) return;
		this.update_values();
		this.show_working_state();
		this.disable_keyboard_nav();
		this.listen_for_setup_stages();

		return frappe.call({
			method: "frappe.desk.page.setup_wizard.setup_wizard.setup_complete",
			args: { args: this.values },
			callback: (r) => {
				if (r.message.status === 'ok') {
					this.post_setup_success();
				} else if (r.message.status === 'registered') {
					this.update_setup_message(__("starting the setup..."));
				} else if (r.message.fail !== undefined) {
					this.abort_setup(r.message.fail);
				}
			},
			error: () => this.abort_setup("Error in setup")
		});
	}

	post_setup_success() {
		this.set_setup_complete_message(__("Setup Complete"), __("Refreshing..."));
		if (frappe.setup.welcome_page) {
			localStorage.setItem("session_last_route", frappe.setup.welcome_page);
		}
		setTimeout(function () {
			// Reload
			window.location.href = '/app';
		}, 2000);
	}

	abort_setup(fail_msg) {
		this.$working_state.find('.state-icon-container').html('');
		fail_msg = fail_msg ? fail_msg : __("Failed to complete setup");

		this.update_setup_message('Could not start up: ' + fail_msg);

		this.$working_state.find('.title').html('Setup failed');

		this.$abort_btn.show();
	}

	listen_for_setup_stages() {
		frappe.realtime.on("setup_task", (data) => {
			// console.log('data', data);
			if (data.stage_status) {
				// .html('Process '+ data.progress[0] + ' of ' + data.progress[1] + ': ' + data.stage_status);
				this.update_setup_message(data.stage_status);
				this.set_setup_load_percent((data.progress[0] + 1) / data.progress[1] * 100);
			}
			if (data.fail_msg) {
				this.abort_setup(data.fail_msg);
			}
			if (data.status === 'ok') {
				this.post_setup_success();
			}
		})
	}

	update_setup_message(message) {
		this.$working_state.find('.setup-message').html(message);
	}

	get_setup_slides_filtered_by_domain() {
		var filtered_slides = [];
		frappe.setup.slides.forEach(function (slide) {
			if (frappe.setup.domains) {
				let active_domains = frappe.setup.domains;
				if (!slide.domains ||
					slide.domains.filter(d => active_domains.includes(d)).length > 0) {
					filtered_slides.push(slide);
				}
			} else {
				filtered_slides.push(slide);
			}
		})
		return filtered_slides;
	}

	show_working_state() {
		this.container.hide();
		frappe.set_route(this.page_name);

		this.$working_state = this.get_message(
			__("Setting up your system"),
			__("Starting Frappe ...")).appendTo(this.parent);

		this.attach_abort_button();

		this.current_id = this.slides.length;
		this.current_slide = null;
	}

	attach_abort_button() {
		this.$abort_btn = $(`<button class='btn btn-secondary btn-xs btn-abort text-muted'>${__('Retry')}</button>`);
		this.$working_state.find('.content').append(this.$abort_btn);

		this.$abort_btn.on('click', () => {
			$(this.parent).find('.setup-in-progress').remove();
			this.container.show();
			frappe.set_route(this.page_name, this.slides.length - 1);
		});

		this.$abort_btn.hide();
	}

	get_message(title, message = "") {
		const loading_html = `<div class="progress-chart">
			<div class="progress">
				<div class="progress-bar"></div>
			</div>
		</div>`;

		return $(`<div class="slides-wrapper container robin-hood-army-checkin-slide setup-in-progress">
			<div class="content text-center">
				<h1 class="slide-title title">${title}</h1>
				<div class="state-icon-container">${loading_html}</div>
				<p class="setup-message text-muted">${message}</p>
			</div>
		</div>`);
	}

	set_setup_complete_message(title, message) {
		this.$working_state.find('.title').html(title);
		this.$working_state.find('.setup-message').html(message);
	}

	set_setup_load_percent(percent) {
		this.$working_state.find('.progress-bar').css({ "width": percent + "%" });
	}
};

frappe.setup.SetupWizardSlide = class SetupWizardSlide extends frappe.ui.Slide {
	constructor(slide = null) {
		super(slide);
	}

	make() {
		super.make();
		this.set_init_values();
		this.reset_action_button_state();
	}

	set_init_values() {
		var me = this;
		// set values from frappe.setup.values
		if (frappe.wizard.values && this.fields) {
			this.fields.forEach(function (f) {
				var value = frappe.wizard.values[f.fieldname];
				if (value) {
					me.get_field(f.fieldname).set_input(value);
				}
			});
		}
	}

};

// Frappe slides settings
// ======================================================
frappe.setup.slides_settings = [
	{
		// Profile slide
		name: 'user',
		title: __("The First User: You"),
		icon: "fa fa-user",
		fields: [
			{
				"fieldname": "full_name", "label": __("Full Name"), "fieldtype": "Data",
				reqd: 1
			},
			{
				fieldname: "country", label: __("Your Country"), reqd: 1,
				fieldtype: "Autocomplete",
				placeholder: __('Select Country')
			},
			{ "fieldname": "password", "label": __("Password"), "fieldtype": "Password" }
		],
		// help: __('The first user will become the System Manager (you can change this later).'),
		onload: function (slide) {
			if (frappe.session.user !== "Administrator") {
				slide.form.fields_dict.email.$wrapper.toggle(false);
				slide.form.fields_dict.password.$wrapper.toggle(false);

				// remove password field
				delete slide.form.fields_dict.password;

				if (frappe.boot.user.first_name || frappe.boot.user.last_name) {
					slide.form.fields_dict.full_name.set_input(
						[frappe.boot.user.first_name, frappe.boot.user.last_name].join(' ').trim());
				}

				var user_image = frappe.get_cookie("user_image");
				var $attach_user_image = slide.form.fields_dict.attach_user_image.$wrapper;

				if (user_image) {
					$attach_user_image.find(".missing-image").toggle(false);
					$attach_user_image.find("img").attr("src", decodeURIComponent(user_image));
					$attach_user_image.find(".img-container").toggle(true);
				}
				delete slide.form.fields_dict.email;

			} else {
				slide.form.fields_dict.email.df.reqd = 1;
				slide.form.fields_dict.email.refresh();
				slide.form.fields_dict.password.df.reqd = 1;
				slide.form.fields_dict.password.refresh();

				frappe.setup.utils.load_user_details(slide, this.setup_fields);
			}
		},

		setup_fields: function (slide) {
			if (frappe.setup.data.full_name) {
				slide.form.fields_dict.full_name.set_input(frappe.setup.data.full_name);
			}
			if (frappe.setup.data.email) {
				let email = frappe.setup.data.email;
				slide.form.fields_dict.email.set_input(email);
				if (frappe.get_gravatar(email, 200)) {
					var $attach_user_image = slide.form.fields_dict.attach_user_image.$wrapper;
					$attach_user_image.find(".missing-image").toggle(false);
					$attach_user_image.find("img").attr("src", frappe.get_gravatar(email, 200));
					$attach_user_image.find(".img-container").toggle(true);
				}
			}
		},
	}
];

frappe.setup.utils = {
	load_regional_data: function (slide, callback) {
		frappe.call({
			method: "frappe.geo.country_info.get_country_timezone_info",
			callback: function (data) {
				frappe.setup.data.regional_data = data.message;
				callback(slide);
			}
		});
	},

	load_user_details: function (slide, callback) {
		frappe.call({
			method: "frappe.desk.page.setup_wizard.setup_wizard.load_user_details",
			freeze: true,
			callback: function (r) {
				frappe.setup.data.full_name = r.message.full_name;
				frappe.setup.data.email = r.message.email;
				callback(slide);
			}
		});
	},

	setup_language_field: function (slide) {
		var language_field = slide.get_field("language");
		language_field.df.options = frappe.setup.data.lang.languages;
		language_field.refresh();
	},

	setup_region_fields: function (slide) {
		/*
			Set a slide's country, timezone and currency fields
		*/
		let data = frappe.setup.data.regional_data;
		let country_field = slide.get_field('country');
		let translated_countries = [];

		Object.keys(data.country_info).sort().forEach(country => {
			translated_countries.push({
				label: __(country),
				value: country
			});
		});

		country_field.set_data(translated_countries);

		slide.get_input("currency")
			.empty()
			.add_options(
				frappe.utils.unique(
					$.map(data.country_info, opts => opts.currency).sort()
				)
			);

		slide.get_input("timezone").empty()
			.add_options(data.all_timezones);

		// set values if present
		if (frappe.wizard.values.country) {
			country_field.set_input(frappe.wizard.values.country);
		} else if (data.default_country) {
			country_field.set_input(data.default_country);
		}

		slide.get_field("currency").set_input(frappe.wizard.values.currency);

		slide.get_field("timezone").set_input(frappe.wizard.values.timezone);

	},

	bind_language_events: function (slide) {
		slide.get_input("language").unbind("change").on("change", function () {
			clearTimeout(slide.language_call_timeout);
			slide.language_call_timeout = setTimeout(() => {
				var lang = $(this).val() || "English";
				frappe._messages = {};
				frappe.call({
					method: "frappe.desk.page.setup_wizard.setup_wizard.load_messages",
					freeze: true,
					args: {
						language: lang
					},
					callback: function () {
						frappe.setup._from_load_messages = true;
						frappe.wizard.refresh_slides();
					}
				});
			}, 500);
		});
	},

	get_language_name_from_code: function (language_code) {
		return frappe.setup.data.lang.codes_to_names[language_code] || "English";
	},

	bind_region_events: function (slide) {
		/*
			Bind a slide's country, timezone and currency fields
		*/
		slide.get_input("country").on("change", function () {
			var country = slide.get_input("country").val();
			var $timezone = slide.get_input("timezone");
			var data = frappe.setup.data.regional_data;

			$timezone.empty();

			if (!country) return;
			// add country specific timezones first
			const timezone_list = data.country_info[country].timezones || [];
			$timezone.add_options(timezone_list.sort());
			slide.get_field("currency").set_input(data.country_info[country].currency);
			slide.get_field("currency").$input.trigger("change");

			// add all timezones at the end, so that user has the option to change it to any timezone
			$timezone.add_options(data.all_timezones);
			slide.get_field("timezone").set_input($timezone.val());

			// temporarily set date format
			frappe.boot.sysdefaults.date_format = (data.country_info[country].date_format
				|| "dd-mm-yyyy");
		});

		slide.get_input("currency").on("change", function () {
			var currency = slide.get_input("currency").val();
			if (!currency) return;
			frappe.model.with_doc("Currency", currency, function () {
				frappe.provide("locals.:Currency." + currency);
				var currency_doc = frappe.model.get_doc("Currency", currency);
				var number_format = currency_doc.number_format;
				if (number_format === "#.###") {
					number_format = "#.###,##";
				} else if (number_format === "#,###") {
					number_format = "#,###.##";
				}

				frappe.boot.sysdefaults.number_format = number_format;
				locals[":Currency"][currency] = $.extend({}, currency_doc);
			});
		});
	},
};
// frappe.pages['robin-hood-army-chec'].on_page_load = function(wrapper) {
// 	var page = frappe.ui.make_app_page({
// 		parent: wrapper,
// 		title: 'None',
// 		single_column: true
// 	});
// }

