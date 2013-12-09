// make this a global object to be used later
var check_emails = {
	names: [],
    validate_names: [],
    invalid_email_text: gettext("cannot be reached!"),

	setupWorkingData: function (cssSelection) {
		that = this;
		$(cssSelection).each(function () {
			that.names.push($(this));
			that.validate_names.push($(this).text());
			console.log(that.validate_names[that.validate_names.length - 1]);
		})
	},

    findInvalidDomItems: function (invalidItems, callback) {
		that = this;
        for (i=0; i < that.names.length; ++i) {
            if (jQuery.inArray(that.names[i].text(), invalidItems) >= 0) {
				callback(that.names[i], that.validate_names[i]);
            }
        }
    },

	resolveTheRest: function (i, stop, items, callback, th) {
		that = this;
		console.log(" + send from: " + th + "; mail: " + that.validate_names[i]);
        $.ajax({url: "check_email",
                data: {"email": items[i]},
                dataType: "json",
                type: "GET"}).done(function(data, textStatus, jqXHR) {
                    if (data[items[i]] === false) {
                        domIdx = jQuery.inArray(items[i], that.validate_names);
                        if (domIdx >= 0) {
							callback(that.names[domIdx], that.validate_names[domIdx]);
                        }
                    }
                }).always(function() {
                    ++i;
                    if (i < stop) {
                        that.resolveTheRest(i, stop, items, callback, th);
                    }
				});
    },

	resolve: function(cssSelection, domModifierCallback, multiplexFactor) {
		this.setupWorkingData(cssSelection);
		that = this;

		$.ajax({url: "check_emails",
		data: {"emails[]": this.validate_names},
		dataType: "json",
		type: "POST"}).done(function(data, textStatus, jqXHR) {
			if ( ! $.isEmptyObject(data.invalid)) {
				//console.log(data.invalid);
				that.findInvalidDomItems(data.invalid, domModifierCallback);
			}
			if ( ! $.isEmptyObject(data.notResolved)) {
				if (multiplexFactor <= data.notResolved.length) {
					chunkSize = Math.ceil(data.notResolved.length / multiplexFactor);
					start = 0;
					stop = chunkSize;
					stop = stop <= data.notResolved.length ? stop : data.notResolved.length;
					for (i=0; i < multiplexFactor; ++i) {
						that.resolveTheRest(start, stop, data.notResolved, domModifierCallback, i);
						start = stop;
						stop += chunkSize;
						stop = stop <= data.notResolved.length ? stop : data.notResolved.length;
					}
				} else {
					that.resolveTheRest(0, data.notResolved.length, data.notResolved, domModifierCallback, 0);
				}
			}
		});
	}
}
