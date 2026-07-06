(function($) {
	/*
	 * Usage:
	 * 
	 * $('#spin').spin();
	 */
	$.fn.spin = function(opts) {
		if (Spinner) {
			return this.each(function() {
				var $this = $(this)
				var data = $this.data();
				if (data.spinner) {
					$this.hide();
					data.spinner.stop();
					delete data.spinner;
				} else {
					data.spinner = new Spinner($.extend({
						color : $this.css('color'),
						lines : 8,
						length : 4,
						width : 3,
						radius : 5,
						top : 4,
						left : 4
					}, opts)).spin(this);
					$this.show();
				}
			});
		} else {
			throw 'spin.js not available.';
		}
	};
	/*
	 * Usage:
	 * 
	 * $('<p>message</p>').showAsDialog();
	 */
	$.fn.showAsDialog = function(opts) {
		$(this).dialog($.extend({
			modal : true,
			closeOnEscape : true,
			buttons : {
				OK : function() {
					$(this).dialog('close');
				}
			}
		}, opts));
	};
})(jQuery);
