// make this a global object to be used later
var check_emails = {
	toBeResolvedText: [],
    invalid_email_text: gettext("cannot be reached!"),

	setupWorkingData: function (cssSelection, callback) {
		that = this;
		that.callback = callback;
		that.cssSelection = cssSelection;
		$(cssSelection).each(function () {
			that.toBeResolvedText.push($(this).text());
		})
	},

    findInvalidDomItems: function (invalidItems) {
		that = this;
        for (i=0; i < invalidItems.length; ++i) {
			// FIXME: if an email name contains the other then this method will match both
			specificSelection = that.cssSelection + ":contains('"+ invalidItems[i]+"')";
			$(specificSelection).each(
					function () {
						that.callback($(this), $(this).text());
					});
        }
    },

	resolveTheRest: function () {
		$.ajax({url: "check_emails",
			data: {"emails[]": that.toBeResolvedText},
			dataType: "json",
			type: "POST"}).done(
			function(data, textStatus, jqXHR) {
				if ( ! $.isEmptyObject(data.invalid)) {
					that.findInvalidDomItems(data.invalid);
				}
				if ( ! $.isEmptyObject(data.notResolved)) {
					that.toBeResolvedText = data.notResolved;
					setTimeout(that.resolveTheRest, 3000);
				}
			});
    },

	resolve: function(cssSelection, domModifierCallback) {
		this.setupWorkingData(cssSelection, domModifierCallback);
		that = this;

		that.resolveTheRest();
	}
}
