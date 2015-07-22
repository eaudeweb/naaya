$(document).ready(function() {
	$('#slideshow_link').click(function(e) {
		e.preventDefault();
		//create slideshow container if it doesn't exist
		if ($('#slideshow_container')[0] == null) {
			var container = document.createElement('div');
			container.id = 'slideshow_container';
			$('body').append(container);
			container = $('#slideshow_container');
		}
		else {
			var container = $('#slideshow_container');
		}
		//get current picture id from the a.href (blank when not on photo page)
		var pic_id = this.href.split('/');
		pic_id = pic_id[pic_id.length-1];
		//get the slideshow page
		container.load('./slideshow', {startpic: pic_id}, function(){
			var winH = $(window).height();
			var winW = $(window).width();

			$(container).css('top',  winH/2-$(container).height()/2);
			$(container).css('left', winW/2-$(container).width()/2);

			//create mask if it doesn't exist;
			if ($('#mask')[0] == null) {
				var mask = document.createElement('div');
				mask.id = 'mask';
				$('body').append(mask);
				// stop slideshow when clicking on the dark background mask
				$('#mask').click(function() {
					$(this).hide();
					$('#slideshow_container').hide();
					$('#slideshow_container').unbind();
					$('#slideshow_container').remove();
				});
			}
			var maskHeight = $(document).height();
			var maskWidth = $(document).width();
			$('#mask').css({'height':maskHeight});
			$('#mask').fadeIn(1000);
			$('#mask').fadeTo("slow",0.9);
			container.show();
		});
		// stop slideshow when clicking on the picture
		container.click(function() {
			$(this).hide();
			$('#mask').hide();
			$(this).unbind();
			$(this).remove();
		});
	});
})