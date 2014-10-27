function Linkify(inputText) {
    //URLs starting with http://, https://, or ftp://
    var replacePattern1 = /(\b(https?|ftp):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/gim;
    var replacedText = inputText.replace(replacePattern1, '<a href="$1">$1</a>');

    //URLs starting with www. (without // before it, or it'd re-link the ones done above)
    var replacePattern2 = /(^|[^\/])(www\.[\S]+(\b|$))/gim;
    var replacedText = replacedText.replace(replacePattern2, '$1<a href="http://$2">$2</a>');

    //Change email addresses to mailto:: links
    var replacePattern3 = /(^[a-zA-Z0-9_\-\.]+@[a-zA-Z0-9\-\.]+?\.[a-zA-Z]{2,6}$)/gim;
    var replacedText = replacedText.replace(replacePattern3, '<a href="mailto:$1">$1</a>');

    return replacedText
}

$(document).ready(function(){
    $('.stringWidget span').each(function(){
        $(this).html(Linkify($(this).html()));
    });
})

$(function () {
	if( $('.survey-box').is(':visible') == true ){
		var top = parseFloat($('.survey-box').css('margin-top').replace(/auto/, 0));
		$(window).scroll(function (event) {
		  var y = $(this).scrollTop();

		  if (y >= (top - 20)) {
			$('.survey-box').addClass('fixed');
		  } else {
			$('.survey-box').removeClass('fixed');
		  }
		}); 
	}
    
});
