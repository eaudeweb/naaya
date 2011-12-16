(function ($) {

$.fn.scrollBox = function () {
    this.each(function () {
        var box = this,
            sCurrentPage = 1,
            sTotalPages = parseInt($('.scroll-item', box).length);

        $('a[rel="scroll-page"]', box).live('click', function(e){
            $link = $(this);

            if($link.hasClass('disabled')){
                return false;
            }

            if( $link.hasClass('next-link') ){
                sGoToPage = parseInt(sCurrentPage + 1);
            }else if( $link.hasClass('prev-link') ) {
                sGoToPage = parseInt(sCurrentPage - 1);
            }else {
                href = $link.attr('href');
                var matches = href.match(/\#(scroll)\-(page)\-[0-9]+/g);
                if( matches.length ){
                    parts = href.split('-');
                    sGoToPage = parseInt(parts[2]);
                }else {
                    return false;
                }
            }

            if( ( sGoToPage > 0 ) && ( sGoToPage <= sTotalPages ) ){

                if( $link.hasClass('next-link') ){
                    sCurrentPage += 1;
                    $('.prev-link', box).removeClass('disabled');
                }else if( $link.hasClass('prev-link') ) {
                    sCurrentPage -= 1;
                    $('.next-link', box).removeClass('disabled');
                }else {
                    href = $link.attr('href');
                    var matches = href.match(/\#(scroll)\-(page)\-[0-9]+/g);
                    if( matches.length == 0 ){
                        return false;
                    }else {
                        sCurrentPage = sGoToPage;
                    }
                }

                if( sGoToPage == sTotalPages ){
                    $('.next-link', box).addClass('disabled');
                    $('.prev-link', box).removeClass('disabled');
                }else if( sGoToPage == 1 ){
                    $('.prev-link', box).addClass('disabled');
                    $('.next-link', box).removeClass('disabled');
                }else {
                    $('.next-link', box).removeClass('disabled');
                    $('.prev-link', box).removeClass('disabled');
                }

                scrollToPage = '#scroll-page-' + sGoToPage;
                panelheight = $(scrollToPage).height();

                $('.scroll-mask', box).animate({
                    'height': panelheight - 27
                },{
                    queue: false,
                    duration:500
                });

                $('.scroll-mask', box).scrollTo(scrollToPage, 800);
            }

            return false;
        });

        function initialize(box) {
            var sTotalPages = parseInt($('.scroll-item', box).length);
    $('.total-pages', box).text(sTotalPages);

            if(sTotalPages == 1){
                $('a[rel="scroll-page"]', box).addClass('disabled');
            }else {
                //Get the height of the first item
                $('.scroll-mask', box).css({
                        'height': $('#scroll-page-1', box).height() - 27
                });
                //Calculate the total width - sum of all sub-panels width
                //Width is generated according to the width of #mask * total of sub-panels
                $('.scroll-panel',box).width(parseInt($('.scroll-mask', box).width() * $('.scroll-panel .scroll-item', box).length));
                //Set the sub-panel width according to the #mask width (width of #mask and sub-panel must be same)
                $('.scroll-panel .scroll-item', box).width($('.scroll-mask', box).width());

                scrollToPage = '#scroll-page-1';
                panelheight = $(scrollToPage, box).height();

                $('.scroll-mask', box).animate({
                    'height': panelheight - 27
                },{
                    queue: false,
                    duration:500
                });

                $('.scroll-mask', box).scrollTo($(scrollToPage, box), 800);
            }
        }

        initialize(box);
    });

    return this;
};

})(jQuery);
