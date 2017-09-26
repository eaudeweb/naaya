$(document).ready(function(){
	$('.js-enabled').remove();
	
	$('.menu-bar').each(function() {
		var top_items = $('> li', this);
		top_items.mouseenter(function(evt) {
			$(this).addClass('menu-bar-hover');
		});
		top_items.mouseleave(function(evt) {
			$(this).removeClass('menu-bar-hover');
		});
	});
});
