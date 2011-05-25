$(document).ready(function(){
	$('.js-enabled').remove();
	
	if( $('.highlights-content').length ){
		$('.highlights-content').scrollCarousel({
			selector: '.highlights'
		});
	}
	
	$('#global-search-input').focus(function(){
		$(this).addClass('focus');
		
		if( $(this).val() === 'Search' ){
			$(this).val('');
			
			$(this).css({
				'color': '#252525',
				'font-style': 'normal'
			});
		}
	});
	
	$('#global-search-input').blur(function(){
		$(this).removeClass('focus');
		
		if( $(this).val() === '' ){
			$(this).val('Search');
			
			$(this).css({
				'color': '#AFAFAF',
				'font-style': 'italic'
			});
		}
	});
	
	if($('.scroll-item').length){
		var sCurrentPage = 1,
			sTotalPages = parseInt($('.scroll-item').length),
			hideDelay = 200,
			hideDelayTimer = null,
			beingShown = false,
			shown = false;
			
		$('.pagination-pages-link').append('1 / ' + sTotalPages + '');
		
		for (index = 1; index <= sTotalPages; index ++){
			element = '<a href="#scroll-page-' + index + '" rel="scroll-page">' + index + '</a>';
			$('.pagination-pages-content').append(element);
		}
		
		if(sTotalPages === 1){
			$('a[rel=scroll-page]').addClass('disabled');
		}else {
			$('.pagination-pages-link, .pagination-pages').mouseover(function (e) {
				if (hideDelayTimer) {
					clearTimeout(hideDelayTimer);
				}
				
				if (beingShown || shown) {
					return;
				} else {
					beingShown = true;
					
					$('.pagination-pages').stop(true, true)
															.animate({
																opacity: "show",
																top: "-45"
															}, "fast", "swing", function(){
																beingShown = false;
																shown = true;
															});
				}
				
				return false;
			}).mouseout(function () {
				if (hideDelayTimer) {
					clearTimeout(hideDelayTimer);
				}
				hideDelayTimer = setTimeout(function () {
					hideDelayTimer = null;
					
					$('.pagination-pages').animate({
																opacity: "hide",
																top: "-55"
															}, "fast", "swing", function(){
																shown = false;
																$('.pagination-pages').css('display', 'none');
															});
				}, hideDelay);
				
				return false;
			});
			
			//Get the height of the first item
			$('.scroll-mask').css({
				'height': $('#scroll-page-1').height() - 27
			});
			//Calculate the total width - sum of all sub-panels width
			//Width is generated according to the width of #mask * total of sub-panels
			$('.scroll-panel').width(parseInt($('.scroll-mask').width() * $('.scroll-panel .scroll-item').length));
			//Set the sub-panel width according to the #mask width (width of #mask and sub-panel must be same)
			$('.scroll-panel .scroll-item').width($('.scroll-mask').width());
		}
		
		$('a[rel=scroll-page]').click(function (e) {
			e.preventDefault();
			
			if($(this).hasClass('disabled')){
				return false;
			}
			
			if( $(this).hasClass('next-link') ){
				sGoToPage = parseInt(sCurrentPage + 1);
			}else if( $(this).hasClass('prev-link') ) {
				sGoToPage = parseInt(sCurrentPage - 1);
			}else {
				href = $(this).attr('href');
				var matches = href.match(/\#(scroll)\-(page)\-[0-9]+/g);
				if( matches.length ){
					parts = href.split('-');
					sGoToPage = parseInt(parts[2]);
				}else {
					return false;
				}
			}
			
			if( ( sGoToPage > 0 ) && ( sGoToPage <= sTotalPages ) ){
				if( $(this).hasClass('next-link') ){
					sCurrentPage += 1;
					$('.prev-link').removeClass('disabled');
				}else if( $(this).hasClass('prev-link') ) {
					sCurrentPage -= 1;
					$('.next-link').removeClass('disabled');
				}else {
					href = $(this).attr('href');
					var matches = href.match(/\#(scroll)\-(page)\-[0-9]+/g);
					if( matches.length == 0 ){
						return false;
					}else {
						sCurrentPage = sGoToPage;
					}
				}
			
				if( sGoToPage == sTotalPages ){
					$('.next-link').addClass('disabled');
					$('.prev-link').removeClass('disabled');
				}else if( sGoToPage == 1 ){
					$('.prev-link').addClass('disabled');
					$('.next-link').removeClass('disabled');
				}else {
					$('.next-link').removeClass('disabled');
					$('.prev-link').removeClass('disabled');
				}
			
				scrollToPage = '#scroll-page-' + sGoToPage;
				var panelheight = $(scrollToPage).height();
				$('.scroll-mask').animate({
						'height': panelheight - 27
					},{
						queue: false,
						duration:500
					}
				);
				$('.scroll-mask').scrollTo(scrollToPage, 800);
				
				$('.pagination-pages-link').text('' + sCurrentPage + ' / ' +  sTotalPages + '');
			}
			
			return false;
		});
	}
	
	if( $('#calendar-box').length ){
		todayIndicator = $('#calendar-days-today');
		dayWidth = $('li:first', '#calendar-days').outerWidth(),
		days = $('li', '#calendar-days'); //Total Items
		showable_days_count = 7;
		animating = false;
	
		active_day = $('li.active', '#calendar-days');
		active_index = days.index(active_day);
	
		left_index = initial_left_index();
		left_day = $(days.get(left_index));
		left_day.addClass('left-day');
	
		$('.calendar-mask').scrollTo('li.left-day');
		animateTodayIndicator(active_index, left_index);
	
		days.click(function(e){
			e.preventDefault();
			dayClicked($(this));
			return false;
		});
	
		button_back = $('a.button-back', '#calendar-content');
		if (left_index == 0) {
			button_back.addClass('disabled');
		}
		button_back.click(function(e) {
			e.preventDefault();
			animateDays(true);
			return false;
		});
	
		button_forward = $('a.button-forward', '#calendar-content');
		if (days.length - left_index == showable_days_count) {
			button_forward.addClass('disabled');
		}
		button_forward.click(function(e) {
			e.preventDefault();
			animateDays(false);
			return false;
		});
	}
	
	/**
	 * Main Categories Slideshow
	 * 
	 * Main Categories Slideshow Tooltips
	*/
	if($('#categories-slideshow').length){
		$('#categories-slideshow').infiniteCarousel('.button-categories-slideshow-previous', '.button-categories-slideshow-next');
		
		topHeight = 9;
		bottomHeight = 8;
		holderHeight = 29;
		contentTotalPadding = 30;
		hideOnScroll = false;
		orientation = 'horizontal';
		
		$(function () {
			$('.categories-list>li').each(function () {
				var distance = 10;
				var time = 250;
				var hideDelay = 200;
				var hideDelayTimer = null;
				var beingShown = false;
				var shown = false;
				var trigger = $('.category-submenu-trigger', this);
				var info = $('.toolTip', this).css('opacity', 0);
				
				var content_height = $('.content', this).height();
				
				$([trigger.get(0), info.get(0)]).mouseover(function (e) {
					offsetLeft = info.parent('.categories-list>li').offset().left;
					
					info.removeClass('toolTipLeftArrow toolTipRightArrow');
					
					if( (offsetLeft > 900) ){
						info.addClass('toolTipRightArrow');
					}else {
						info.addClass('toolTipLeftArrow');
					}
					
					arrowMarginTop = ((content_height + contentTotalPadding) / 2) - (holderHeight / 2) + topHeight;
					leftAboveHeight = ((content_height + contentTotalPadding) / 2) - (holderHeight / 2);
					left_shadow_below_height = content_height - leftAboveHeight - topHeight - holderHeight + contentTotalPadding;
					
					$('.left>.repeat.above', info).css('height', leftAboveHeight);
					
					left_shadow_below_height = content_height - leftAboveHeight - topHeight - holderHeight + contentTotalPadding;
					right_shadow_below_height = content_height - topHeight + contentTotalPadding;
					
					shadowMarginTop = content_height + contentTotalPadding + 1;
					
					$('.left>.repeat.below', info).css('height', left_shadow_below_height);
					$('.right>.repeat', info).css('height', right_shadow_below_height);
					$('.shadow.left, .shadow.right', info).css('top', shadowMarginTop);
					
					$('.arrow', info).css('top', arrowMarginTop);
					
					if (hideDelayTimer) {
						clearTimeout(hideDelayTimer);
					}
					
					if (beingShown || shown) {
						// don't trigger the animation again
						return;
					} else {
						// reset position of info box
						beingShown = true;
						info.css({
							top: info.offset.top,
							left: info.offset.left,
							display: 'block'
						}).animate({
							top: '-=' + distance + 'px',
							opacity: 1
						},
						time, 'swing', function() {
							beingShown = false;
							shown = true;
						});
					}
					
					return false;
				}).mouseout(function () {
					if (hideDelayTimer) {
						clearTimeout(hideDelayTimer);
					}
					
					hideDelayTimer = setTimeout(function () {
						hideDelayTimer = null;
						info.animate({
							top: '50px',
							opacity: 0
						},
						time, 'swing', function () {
							shown = false;
							info.css('display', 'none');
						});
					}, hideDelay);
					
					return false;
				});
			});
		});
	}
	
	/**
	 * Multimedia
	 */
	if( $('#multimedia-files-tiled').length || $('#multimedia-files-full').length ){
	
		$("a.mfile-link").click(function(e) {
			e.preventDefault();
			var mfile_id = parseInt($(this).attr("id").split("-")[2]);
			select_mfile(this);
			currentFile = mfile_id;
			multimedia_full_show_buttons(currentFile, totalFiles);
			multimedia_show_view('full');
			return false;
		});
	
		/**
		 * Multimedia Toggle View (Full/Tiled)
		*/
	
		$("a[rel=multimedia-toggle-view]").click(function(e){
			e.preventDefault();
			elementToShow = $(this).attr("id").split("-")[2];
	
			// if no video selected just show the first one
			if (elementToShow === 'full' &&
				$('.file-title', '#multimedia-files-full').html() === 'File title') {
				var mfile_link = $("a.mfile-link", '#multimedia-files-tiled');
				var mfile_id = parseInt($(mfile_link).attr("id").split("-")[2]);
				select_mfile(mfile_link);
				currentFile = mfile_id;
			}
	
			multimedia_show_view(elementToShow);
			return false;
		});
		
		/**
		 * Multimedia Tiled Pagination by page numbers (icon)
		*/
		var totalPages = parseInt($('#multimedia-files-tiled .multimedia-group').length);
		var currentPage = 1, index, current = '', element = '';
		controller = $('#multimedia-files-tiled .multimedia-pagination .multimedia-page-numbers');
	
		/**
		 * Disable buttons
		 */
		if (currentPage == 1) {
			$('#multimedia-files-tiled .multimedia-pagination a.button-back').addClass('disabled');
		}
		if (currentPage == totalPages) {
			$('#multimedia-files-tiled .multimedia-pagination a.button-forward').addClass('disabled');
		}
	
		/**
		 * Create pages
		*/
		for (index = 1; index <= totalPages; index++) {
			if (index === currentPage) {
				current = ' class="current"';
			} else {
				current = '';
			}
			
			element += '<a href="javascript:void(0);"' + current + ' title="Go to page ' + index + '"><span>' + (index) + '</span></a>';
		}
		$('#multimedia-files-tiled .multimedia-pagination .multimedia-page-numbers').append(element);
		
		/**
		 * Bind click event
		*/
		$('#multimedia-files-tiled .multimedia-page-numbers a').click(function(e){
			e.preventDefault();
			goToPage = parseInt($(this).children('span').text());
			if(goToPage !== currentPage){
				/**
				 * Go to desired page
				*/
				$('#multimedia-files-tiled .multimedia-files #multimedia-group-' + currentPage + '').fadeOut("fast", function(){
					$('#multimedia-files-tiled .multimedia-files #multimedia-group-' + goToPage + '').fadeIn("fast");
				});
				
				/**
				 * Set current page
				*/
				$('#multimedia-files-tiled .multimedia-page-numbers a').removeClass('current');
				$(this).addClass('current');
				
				currentPage = goToPage;
			}
		});
		
		/**
		 * Multimedia Tiled Pagination by back/forward (arrows)
		 *
		 * Bind click event
		*/
		$('#multimedia-files-tiled .multimedia-pagination a.button-back, #multimedia-files-tiled .multimedia-pagination a.button-forward').click(function(e){
			e.preventDefault();
	
			/**
			 * Disable button if already "out of pages"
			*/
			if( ($(this).hasClass('button-back') && (currentPage == 1)) || ($(this).hasClass('button-forward') && (currentPage == totalPages)) ){
				$(this).addClass('disabled');
				return false;
			}
			
			/**
			 * Set desired page
			*/
			if( $(this).hasClass('button-back') ){
				goToPage = currentPage - 1;
			}else if( $(this).hasClass('button-forward') ) {
				goToPage = currentPage + 1;
			}
			
			/**
			 * Go to desired page
			*/
			$('#multimedia-files-tiled .multimedia-files #multimedia-group-' + currentPage + '').fadeOut("fast", function(){
				$('#multimedia-files-tiled .multimedia-files #multimedia-group-' + goToPage + '').fadeIn("fast");
			});
			
			/**
			 * Set current page
			*/
			$('#multimedia-files-tiled .multimedia-page-numbers a').removeClass('current');
			$('#multimedia-files-tiled .multimedia-page-numbers a:eq(' + parseInt(goToPage - 1) + ')').addClass('current');
			
			currentPage = goToPage;
	
			/**
			 * Enable/Disable buttons
			 */
			if (currentPage == 1) {
				$('#multimedia-files-tiled .multimedia-pagination a.button-back').addClass('disabled');
			} else {
				$('#multimedia-files-tiled .multimedia-pagination a.button-back').removeClass('disabled');
			}
			if (currentPage == totalPages) {
				$('#multimedia-files-tiled .multimedia-pagination a.button-forward').addClass('disabled');
			} else {
				$('#multimedia-files-tiled .multimedia-pagination a.button-forward').removeClass('disabled');
			}
		});
	
		/**
		 * Multimedia Full Pagination
		*/
		var totalFiles = parseInt($('#multimedia-files-tiled .mfile-link').length);
		var currentFile = 1;
		$('#multimedia-files-full a.button-back').addClass('disabled');
	
		/**
		 * Multimedia Full Pagination by back/forward (arrows)
		 *
		 * Bind click event
		*/
		$('#multimedia-files-full .multimedia-pagination a.button-back, #multimedia-files-full .multimedia-pagination a.button-forward').click(function(e){
			e.preventDefault();
	
			/**
			 * Disable button if already "out of pages"
			*/
			if( ($(this).hasClass('button-back') && (currentFile == 1)) || ($(this).hasClass('button-forward') && (currentFile == totalFiles)) ){
				$(this).addClass('disabled');
				return false;
			}
	
			/**
			 * Set desired page
			*/
			if( $(this).hasClass('button-back') ){
				goToFile = currentFile - 1;
			}else if( $(this).hasClass('button-forward') ) {
				goToFile = currentFile + 1;
			}
	
			var mfile_link = $("#m-file-" + goToFile);
			select_mfile(mfile_link);
			currentFile = goToFile;
			multimedia_full_show_buttons(currentFile, totalFiles);
		});
	}
});

/**
 * Main JS Functions
*/

function contentScrollbar(contents){
	var options = {
		scroll: 										'vertical',
		scrollEasingAmount : 				400,
		scrollEasingType: 					'easeOutCirc',
		extraBottomScrollingSpace: 	1.05,
		scrollbarHW: 								'fixed',
		mouseWheelSupport: 					'yes',
		buttonsSupport: 						'no',
		buttonsScrollingSpeed: 			10
	};
	
	for( selector in contents ) {
		var options = $.extend({}, options, contents[selector]);
		$(selector).customScrollbar(options.scroll,
																options.scrollEasingAmount,
																options.scrollEasingType,
																options.extraBottomScrollingSpace,
																options.scrollbarHW,
																options.mouseWheelSupport,
																options.buttonsSupport,
																options.buttonsScrollingSpeed);
	}
	
	return false;
}

(function (jQuery) {
  jQuery('a.external-link').click(function () {
		window.open(this.href);
		return false;
	});
})(jQuery);

/**
 * Dropwdown menu
*/
(function ($) {
	$.fn.dropdownMenu = function (customOptions) {
		$.fn.dropdownMenu.defaults = {
			selector: 				'ul.menu-list li',
			subSelector:			'ul.menu-item-content',
			label:						'a.menu-item-label',
			defaultOpen: 			false,
			closeAllOther:		false
		};
		
		var options = $.extend({}, $.fn.dropdownMenu.defaults, customOptions);
		
		this.each(function () {
			var menu = $(options.selector, this);
			
			menu.mouseover(function(){
				if( $(this).hasClass('separator') ){
					return false;
				}
				
				$(this).addClass('selected');
				$(options.subSelector, this).show();
				
			}).mouseout(function(){
				$(this).removeClass('selected');
				$(options.subSelector, this).hide();
			});
			
			function initialize(menu) {
				if( $(options.subSelector, menu) ){
					$(options.label).addClass('subitems');
					/* $(options.subSelector).hide(); */
				}
				
				return false;
			}
			
			initialize();
		});
		
		return this;
	};
})(jQuery);

/**
 * Dropdown links
*/
(function ($) {
	$.fn.dropdown = function (customOptions) {
		$.fn.dropdown.defaults = {
			selector: 				'ul.dropdown-menu',
			label:						'span.dropdown-label img',
			submenuSelector: 	'ul.dropdown-submenu',
			defaultOpen: 			false,
			closeAllOther:		false
		};
		
		var options = $.extend({}, $.fn.dropdown.defaults, customOptions);
		
		this.each(function () {
			var menu = this;
			
			/**
			 * Show/Hide Menu on window.ready
			*/
			function initialize(menu) {
				( options.defaultOpen ) ? $(options.submenuSelector, menu).slideDown() : $(options.submenuSelector, menu).slideUp();
			}
			
			/**
			 * Bind click event for submenu label
			*/
			$(options.label).click(function(event){
				event.preventDefault();
				label = $(this);
				
				var submenu = $(options.submenuSelector, label.parent().parent());
				
				if( submenu.is(':visible') ){
					submenu.slideUp();
					label.attr({
						'src': img_expand,
						'title': 'Expand',
						'alt': 'Expand'
					});
				}else if( !submenu.is(':visible') ){
					/**
					 * Close all expanded submenus if needed
					*/
					if( options.closeAllOther ){
						$(options.submenuSelector, menu).slideUp();
					}
					
					submenu.slideDown();
					label.attr({
						'src': img_collapse,
						'title': 'Collapse',
						'alt': 'Collapse'
					});
				}
				
				return false;
			});
			
			initialize();
		});
		
		return this;
	};
})(jQuery);

/**
 * Multimedia functions
*/
function select_mfile(mfile_link) {
	var mfile_url = $(mfile_link).attr('href');
	var media_id = $('img', mfile_link).attr('alt');
	var video_src = mfile_url + '/' + media_id;
	var video_title = $(mfile_link).attr('title');
	flowplayer_config(site_url, "multimedia-show",
		video_src, "", "", true);
	$('.file-title', '#multimedia-files-full').html(video_title);
	$('.file-more', '#multimedia-files-full').attr('href', mfile_url);
}

function multimedia_show_view(elementToShow) {
	var elementToHide = '';
	if( elementToShow === 'full' ){
		elementToHide = 'tiled';
	}else if( elementToShow === 'tiled' ){
		elementToHide = 'full';
	}else {
		return;
	}

	if ($('#multimedia-files-' + elementToShow).is(':visible')) {
		return;
	}

	$("#multimedia-files-" + elementToHide + "").fadeOut("fast", function() {
		$("#multimedia-files-" + elementToShow + "").fadeIn("fast");
	});

	$("#button-toggle-" + elementToShow + "").addClass('selected');
	$("#button-toggle-" + elementToHide + "").removeClass('selected');
}

function multimedia_full_show_buttons(currentFile, totalFiles) {
	$('#multimedia-files-full .multimedia-pagination a').removeClass('disabled');

	if (currentFile == 1) {
		$('#multimedia-files-full .multimedia-pagination a.button-back').addClass('disabled');
	}
	if (currentFile == totalFiles) {
		$('#multimedia-files-full .multimedia-pagination a.button-forward').addClass('disabled');
	}
}

/**
 * Scrollbar
*/
(function ($) {
$.fn.customScrollbar = function (scrollType,animSpeed,easeType,bottomSpace,draggerDimType,mouseWheelSupport,scrollBtnsSupport,scrollBtnsSpeed){
	var id = $(this).attr("id");
	var $customScrollBox=$("#"+id+" .customScrollBox");
	var $customScrollBox_container=$("#"+id+" .customScrollBox .container");
	var $customScrollBox_content=$("#"+id+" .customScrollBox .content");
	var $dragger_container=$("#"+id+" .dragger_container");
	var $dragger=$("#"+id+" .dragger");
	var $scrollUpBtn=$("#"+id+" .scrollUpBtn");
	var $scrollDownBtn=$("#"+id+" .scrollDownBtn");
	var $customScrollBox_horWrapper=$("#"+id+" .customScrollBox .horWrapper");
	
	//get & store minimum dragger height & width (defined in css)
	if(!$customScrollBox.data("minDraggerHeight")){
		$customScrollBox.data("minDraggerHeight",$dragger.height());
	}
	if(!$customScrollBox.data("minDraggerWidth")){
		$customScrollBox.data("minDraggerWidth",$dragger.width());
	}
	
	//get & store original content height & width
	if(!$customScrollBox.data("contentHeight")){
		$customScrollBox.data("contentHeight",$customScrollBox_container.height());
	}
	if(!$customScrollBox.data("contentWidth")){
		$customScrollBox.data("contentWidth",$customScrollBox_container.width());
	}
	
	CustomScroller();
	
	function CustomScroller(reloadType){
		//horizontal scrolling ------------------------------
		if(scrollType=="horizontal"){
			var visibleWidth=$customScrollBox.width();
			//set content width automatically
			$customScrollBox_horWrapper.css("width",999999); //set a rediculously high width value ;)
			$customScrollBox.data("totalContent",$customScrollBox_container.width()); //get inline div width
			$customScrollBox_horWrapper.css("width",$customScrollBox.data("totalContent")); //set back the proper content width value
			
			if($customScrollBox_container.width()>visibleWidth){ //enable scrollbar if content is long
				$dragger.css("display","block");
				if(reloadType!="resize" && $customScrollBox_container.width()!=$customScrollBox.data("contentWidth")){
					$dragger.css("left",0);
					$customScrollBox_container.css("left",0);
					$customScrollBox.data("contentWidth",$customScrollBox_container.width());
				}
				$dragger_container.css("display","block");
				$scrollDownBtn.css("display","inline-block");
				$scrollUpBtn.css("display","inline-block");
				var totalContent=$customScrollBox_content.width();
				var minDraggerWidth=$customScrollBox.data("minDraggerWidth");
				var draggerContainerWidth=$dragger_container.width();
		
				function AdjustDraggerWidth(){
					if(draggerDimType=="auto"){
						var adjDraggerWidth=Math.round(totalContent-((totalContent-visibleWidth)*1.3)); //adjust dragger width analogous to content
						if(adjDraggerWidth<=minDraggerWidth){ //minimum dragger width
							$dragger.css("width",minDraggerWidth+"px");
						} else if(adjDraggerWidth>=draggerContainerWidth){
							$dragger.css("width",draggerContainerWidth-10+"px");
						} else {
							$dragger.css("width",adjDraggerWidth+"px");
						}
					}
				}
				AdjustDraggerWidth();
		
				var targX=0;
				var draggerWidth=$dragger.width();
				$dragger.draggable({ 
					axis: "x", 
					containment: "parent", 
					drag: function(event, ui) {
						ScrollX();
					}, 
					stop: function(event, ui) {
						DraggerRelease();
					}
				});
			
				$dragger_container.click(function(e) {
					var $this=$(this);
					var mouseCoord=(e.pageX - $this.offset().left);
					if(mouseCoord<$dragger.position().left || mouseCoord>($dragger.position().left+$dragger.width())){
						var targetPos=mouseCoord+$dragger.width();
						if(targetPos<$dragger_container.width()){
							$dragger.css("left",mouseCoord);
							ScrollX();
						} else {
							$dragger.css("left",$dragger_container.width()-$dragger.width());
							ScrollX();
						}
					}
				});

				//mousewheel
				$(function($) {
					if(mouseWheelSupport=="yes"){
						$customScrollBox.unbind("mousewheel");
						$customScrollBox.bind("mousewheel", function(event, delta) {
							var vel = Math.abs(delta*10);
							$dragger.css("left", $dragger.position().left-(delta*vel));
							ScrollX();
							if($dragger.position().left<0){
								$dragger.css("left", 0);
								$customScrollBox_container.stop();
								ScrollX();
							}
							if($dragger.position().left>$dragger_container.width()-$dragger.width()){
								$dragger.css("left", $dragger_container.width()-$dragger.width());
								$customScrollBox_container.stop();
								ScrollX();
							}
							return false;
						});
					}
				});
				
				//scroll buttons
				if(scrollBtnsSupport=="yes"){
					$scrollDownBtn.mouseup(function(){
						BtnsScrollXStop();
					}).mousedown(function(){
						BtnsScrollX("down");
					});
				
					$scrollUpBtn.mouseup(function(){
						BtnsScrollXStop();
					}).mousedown(function(){
						BtnsScrollX("up");
					});
				
					$scrollDownBtn.click(function(e) {
						e.preventDefault();
					});
					$scrollUpBtn.click(function(e) {
						e.preventDefault();
					});
				
					btnsScrollTimerX=0;
				
					function BtnsScrollX(dir){
						if(dir=="down"){
							var btnsScrollTo=$dragger_container.width()-$dragger.width();
							var scrollSpeed=Math.abs($dragger.position().left-btnsScrollTo)*(100/scrollBtnsSpeed);
							$dragger.stop().animate({left: btnsScrollTo}, scrollSpeed,"linear");
						} else {
							var btnsScrollTo=0;
							var scrollSpeed=Math.abs($dragger.position().left-btnsScrollTo)*(100/scrollBtnsSpeed);
							$dragger.stop().animate({left: -btnsScrollTo}, scrollSpeed,"linear");
						}
						clearInterval(btnsScrollTimerX);
						btnsScrollTimerX = setInterval( ScrollX, 20);
					}
				
					function BtnsScrollXStop(){
						clearInterval(btnsScrollTimerX);
						$dragger.stop();
					}
				}

				//scroll
				var scrollAmount=(totalContent-visibleWidth)/(draggerContainerWidth-draggerWidth);
				function ScrollX(){
					var draggerX=$dragger.position().left;
					var targX=-draggerX*scrollAmount;
					var thePos=$customScrollBox_container.position().left-targX;
					$customScrollBox_container.stop().animate({left: "-="+thePos}, animSpeed, easeType);
				}
			} else { //disable scrollbar if content is short
				$dragger.css("left",0).css("display","none"); //reset content scroll
				$customScrollBox_container.css("left",0);
				$dragger_container.css("display","none");
				$scrollDownBtn.css("display","none");
				$scrollUpBtn.css("display","none");
			}
		//vertical scrolling ------------------------------
		} else {
			var visibleHeight=$customScrollBox.height();
			if($customScrollBox_container.height()>visibleHeight){ //enable scrollbar if content is long
				$dragger.css("display","block");
				if(reloadType!="resize" && $customScrollBox_container.height()!=$customScrollBox.data("contentHeight")){
					$dragger.css("top",0);
					$customScrollBox_container.css("top",0);
					$customScrollBox.data("contentHeight",$customScrollBox_container.height());
				}
				$dragger_container.css("display","block");
				$scrollDownBtn.css("display","inline-block");
				$scrollUpBtn.css("display","inline-block");
				var totalContent=$customScrollBox_content.height();
				var minDraggerHeight=$customScrollBox.data("minDraggerHeight");
				var draggerContainerHeight=$dragger_container.height();
		
				function AdjustDraggerHeight(){
					if(draggerDimType=="auto"){
						var adjDraggerHeight=Math.round(totalContent-((totalContent-visibleHeight)*1.3)); //adjust dragger height analogous to content
						if(adjDraggerHeight<=minDraggerHeight){ //minimum dragger height
							$dragger.css("height",minDraggerHeight+"px").css("line-height",minDraggerHeight+"px");
						} else if(adjDraggerHeight>=draggerContainerHeight){
							$dragger.css("height",draggerContainerHeight-10+"px").css("line-height",draggerContainerHeight-10+"px");
						} else {
							$dragger.css("height",adjDraggerHeight+"px").css("line-height",adjDraggerHeight+"px");
						}
					}
				}
				AdjustDraggerHeight();
		
				var targY=0;
				var draggerHeight=$dragger.height();
				$dragger.draggable({ 
					axis: "y", 
					containment: "parent", 
					drag: function(event, ui) {
						Scroll();
					}, 
					stop: function(event, ui) {
						DraggerRelease();
					}
				});
				
				$dragger_container.click(function(e) {
					var $this=$(this);
					var mouseCoord=(e.pageY - $this.offset().top);
					if(mouseCoord<$dragger.position().top || mouseCoord>($dragger.position().top+$dragger.height())){
						var targetPos=mouseCoord+$dragger.height();
						if(targetPos<$dragger_container.height()){
							$dragger.css("top",mouseCoord);
							Scroll();
						} else {
							$dragger.css("top",$dragger_container.height()-$dragger.height());
							Scroll();
						}
					}
				});

				//mousewheel
				$(function($) {
					if(mouseWheelSupport=="yes"){
						$customScrollBox.unbind("mousewheel");
						$customScrollBox.bind("mousewheel", function(event, delta) {
							var vel = Math.abs(delta*10);
							$dragger.css("top", $dragger.position().top-(delta*vel));
							Scroll();
							if($dragger.position().top<0){
								$dragger.css("top", 0);
								$customScrollBox_container.stop();
								Scroll();
							}
							if($dragger.position().top>$dragger_container.height()-$dragger.height()){
								$dragger.css("top", $dragger_container.height()-$dragger.height());
								$customScrollBox_container.stop();
								Scroll();
							}
							return false;
						});
					}
				});

				//scroll buttons
				if(scrollBtnsSupport=="yes"){
					$scrollDownBtn.mouseup(function(){
						BtnsScrollStop();
					}).mousedown(function(){
						BtnsScroll("down");
					});
				
					$scrollUpBtn.mouseup(function(){
						BtnsScrollStop();
					}).mousedown(function(){
						BtnsScroll("up");
					});
				
					$scrollDownBtn.click(function(e) {
						e.preventDefault();
					});
					$scrollUpBtn.click(function(e) {
						e.preventDefault();
					});
				
					btnsScrollTimer=0;
				
					function BtnsScroll(dir){
						if(dir=="down"){
							var btnsScrollTo=$dragger_container.height()-$dragger.height();
							var scrollSpeed=Math.abs($dragger.position().top-btnsScrollTo)*(100/scrollBtnsSpeed);
							$dragger.stop().animate({top: btnsScrollTo}, scrollSpeed,"linear");
						} else {
							var btnsScrollTo=0;
							var scrollSpeed=Math.abs($dragger.position().top-btnsScrollTo)*(100/scrollBtnsSpeed);
							$dragger.stop().animate({top: -btnsScrollTo}, scrollSpeed,"linear");
						}
						clearInterval(btnsScrollTimer);
						btnsScrollTimer = setInterval( Scroll, 20);
					}
				
					function BtnsScrollStop(){
						clearInterval(btnsScrollTimer);
						$dragger.stop();
					}
				}
				
				//scroll
				if(bottomSpace<1){
					bottomSpace=1; //minimum bottomSpace value is 1
				}
				var scrollAmount=(totalContent-(visibleHeight/bottomSpace))/(draggerContainerHeight-draggerHeight);
				function Scroll(){
					var draggerY=$dragger.position().top;
					var targY=-draggerY*scrollAmount;
					var thePos=$customScrollBox_container.position().top-targY;
					$customScrollBox_container.stop().animate({top: "-="+thePos}, animSpeed, easeType);
				}
			} else { //disable scrollbar if content is short
				$dragger.css("top",0).css("display","none"); //reset content scroll
				$customScrollBox_container.css("top",0);
				$dragger_container.css("display","none");
				$scrollDownBtn.css("display","none");
				$scrollUpBtn.css("display","none");
				/**
				 * Added
				*/
				$('#mcs_container .customScrollBox .container').css('width', '100%');
			}
		}
		
		$dragger.mouseup(function(){
			DraggerRelease();
		}).mousedown(function(){
			DraggerPress();
		}).mouseover(function(){
			DraggerHover();
		}).mouseout(function(){
			DraggerOut();
		});

		function DraggerPress(){
			$dragger.addClass("dragger_pressed").removeClass('dragger_hover');
		}

		function DraggerRelease(){
			$dragger.removeClass("dragger_pressed").addClass('dragger_hover');
		}

		function DraggerHover(){
			$dragger.addClass("dragger_hover").removeClass('dragger_pressed');
		}

		function DraggerOut(){
			$dragger.removeClass("dragger_hover");
		}
	}
	
	$(window).resize(function() {
		if(scrollType=="horizontal"){
			if($dragger.position().left>$dragger_container.width()-$dragger.width()){
				$dragger.css("left", $dragger_container.width()-$dragger.width());
			}
		} else {
			if($dragger.position().top>$dragger_container.height()-$dragger.height()){
				$dragger.css("top", $dragger_container.height()-$dragger.height());
			}
		}
		CustomScroller("resize");
	});
};  
})(jQuery);

/**
 * Scroll Carousel
*/
(function ($) {
	$.fn.scrollCarousel = function (customOptions) {
		/**
		 * Set default options
		*/
		$.fn.scrollCarousel.defaults = {
			selector: 				'.related',
			resizeHeight: 		false,
			hideDelay:				200,
			hideDelayTimer:		null
		};
		
		/**
		 * Merge default options with user specified options
		*/
		var options = $.extend({}, $.fn.scrollCarousel.defaults, customOptions);
		
		this.each(function () {
			/**
			 * Declare variables/selector for panel, groups, content and buttons
			 *
			 * All variables are build with plugin`s option 'selector'
			*/
			var carouselCurrentPage = 1,
					goToPage = 1,
					panel = $(options.selector + '-panel'),
					groups = $(options.selector + '-group'),
					group = options.selector.replace(/\./, "") + '-group',
					content = $(options.selector + '-content'),
					button = options.selector.replace(/\./, "") + '-button',
					totalPages = parseInt(groups.length);
			
			if(totalPages === 1){
				/**
				 * Disabled buttons if there is just one page
				*/
				$('a[rel=' + button + ']').addClass('disabled');
			}else if( (totalPages > 1) && (carouselCurrentPage === 1) ) {
				$('a[rel=' +  button + '].button-back').addClass('disabled');
			}else if( (totalPages > 1) && (carouselCurrentPage === totalPages) ){
				$('a[rel=' +  button + '].button-forward').addClass('disabled');
			}
			
			/**
			 * Set panel and groups width
			*/
			panel.width(parseInt(content.width() * totalPages));
			groups.width(content.width());
			
			/**
			 * Bind click event for Forward/Back buttons
			 *
			 * Do nothing if buttons are disabled
			*/
			$('a[rel=' + button + ']').click(function (e) {
				e.preventDefault();
				
				if($(this).hasClass('disabled')){
					return false;
				}
				
				/**
				 * Get number of the page to go to
				*/
				if( $(this).hasClass('button-forward') ){
					goToPage = parseInt(carouselCurrentPage + 1);
				}else if( $(this).hasClass('button-back') ) {
					goToPage = parseInt(carouselCurrentPage - 1);
				}else {
					return false;
				}
				
				/**
				 * Do nothing if it is not a valid page number
				*/
				if( ( goToPage > 0 ) && ( goToPage <= totalPages ) ){
					if( $(this).hasClass('button-forward') ){
						carouselCurrentPage += 1;
						$('.button-back').removeClass('disabled');
					}else if( $(this).hasClass('button-back') ) {
						carouselCurrentPage -= 1;
						$('.button-forward').removeClass('disabled');
					}else {
						return false;
					}
					
					/**
					 * Disable button (Back/Forward) if we are on the first/last page
					*/
					if( goToPage == totalPages ){
						$('.button-forward').addClass('disabled');
					}else if( goToPage == 1 ){
						$('.button-back').addClass('disabled');
					}
					
					scrollToPage = '#' + group + '-' + goToPage;
					
					/**
					 * Animate content height if needed
					*/
					if( options.resizeHeight ){
						panelheight = $(scrollToPage).height();
						
						content.animate({
								'height': panelheight
							},{
								queue: false,
								duration:500
							}
						);
					}
					
					/**
					 * Go to required page
					*/
					content.scrollTo(scrollToPage, 800);
				}
				
				return false;
			});
		});
		
		return this;
	};
})(jQuery);

/**
 * Calendar Functions
*/
function initial_left_index() {
	var active_day_index = days.index(active_day);
	if (active_day_index > 3) {
		return active_day_index - 3;
	}
	return 0;
}

function animateDays(day_direction) {
	if (day_direction) {
		if (left_index <= 0) {
			return false;
		}
	} else {
		if (left_index >= days.length - showable_days_count) {
			return false;
		}
	}

	if (day_direction) {
		left_index--;
	} else {
		left_index++;
	}

	left_day.removeClass('left-day');
	left_day = $(days.get(left_index));
	left_day.addClass('left-day');

	$('.calendar-mask').scrollTo('li.left-day');
	animateTodayIndicator(active_index, left_index);

	if (left_index == 0) {
		button_back.addClass('disabled');
	} else {
		button_back.removeClass('disabled');
	}

	if (days.length - left_index == showable_days_count) {
		button_forward.addClass('disabled');
	} else {
		button_forward.removeClass('disabled');
	}
}

function dayClicked(selected_day){
	if( selected_day.hasClass('active') || animating ){
		return false;
	}

	animating = true;
	selected_index = days.index(selected_day);
	select_direction = selected_index < active_index;

	active_day.removeClass('active');
	active_day = selected_day;
	active_index = selected_index;
	active_day.addClass('active');

	animateTodayIndicator(active_index, left_index);
	animateCalendar(active_index, select_direction);
}

function animateTodayIndicator(active_index, left_index) {
	if (active_index - left_index >= showable_days_count) {
		todayIndicator.animate({
			left: (showable_days_count + 100) * dayWidth
		}, 250);
	} else if (active_index < left_index) {
		todayIndicator.animate({
			left: -100 * dayWidth
		}, 250);
	} else {
		todayIndicator.animate({
			left: (active_index - left_index) * dayWidth
		}, 150);
	}
}

function animateCalendar(active_index, select_direction) {
	var selectedStartLeft, activeLeft;

	var selectedDay = $('div.items-group:eq(' + active_index + ')', '#calendar-items');
	var activeDay = $('div.items-group.active', '#calendar-items');

	if (!select_direction) {
			selectedStartLeft = 350;
			activeLeft = -350;
	} else {
			selectedStartLeft = -350;
			activeLeft = 350;
	}

	activeDay.removeClass('active');
	selectedDay.addClass('active');

	selectedDay.css('left', selectedStartLeft);
	activeDay.css('left', 0);
	activeDay.animate({
		left: activeLeft
	}, 250);
	selectedDay.animate({
		left: 0
	}, 250, function () {
		animating = false;
	});
}

/**
 * End calendar functions
*/

jQuery.fn.infiniteCarousel = function(previous, next, options){
	var sliderList = jQuery(this).children()[0];
	
	if (sliderList) {
		var increment = jQuery(sliderList).children().outerWidth("true"),
		elmnts = jQuery(sliderList).children(),
		numElmts = elmnts.length,
		sizeFirstElmnt = increment,
		shownInViewport = Math.round(jQuery(this).width() / sizeFirstElmnt),
		firstElementOnViewPort = 1,
		isAnimating = false;
		
		for (i = 0; i < shownInViewport; i++) {
			jQuery(sliderList).css('width',(numElmts+shownInViewport)*increment + increment + "px");
			jQuery(sliderList).append(jQuery(elmnts[i]).clone());
		}
		
		jQuery(previous).click(function(event){
			if (!isAnimating) {
				if (firstElementOnViewPort == 1) {
					jQuery(sliderList).css('left', "-" + numElmts * sizeFirstElmnt + "px");
					firstElementOnViewPort = numElmts;
				}
				else {
					firstElementOnViewPort--;
				}
				
				jQuery(sliderList).animate({
					left: "+=" + increment,
					y: 0,
					queue: true
				}, "swing", function(){isAnimating = false;});
				isAnimating = true;
			}
			
		});
		
		jQuery(next).click(function(event){
			if (!isAnimating) {
				if (firstElementOnViewPort > numElmts) {
					firstElementOnViewPort = 2;
					jQuery(sliderList).css('left', "0px");
				}
				else {
					firstElementOnViewPort++;
				}
				jQuery(sliderList).animate({
					left: "-=" + increment,
					y: 0,
					queue: true
				}, "swing", function(){isAnimating = false;});
				isAnimating = true;
			}
		});
	}
};
