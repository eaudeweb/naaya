// make this a global object to be used later
var check_emails = {
	toBeResolvedText: [],

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
        $.each(invalidItems, function(email, error){
            specificSelection = that.cssSelection + ":contains('" + email +"')";
            $(specificSelection).each(
                function () {
                    that.callback($(this), error);
                });
        });
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
