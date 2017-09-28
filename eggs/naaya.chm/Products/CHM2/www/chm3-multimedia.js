$(document).ready(function(){

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

$('.multimedia-pagination').css({'margin-left': $('.multimedia-box-top h3').width() + 'px'});

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


function select_mfile(mfile_link) {
    var mfile_url = $(mfile_link).attr('href');
    var media_id = $('img', mfile_link).attr('alt');
    var video_src = mfile_url + '/' + media_id;
    var video_title = $(mfile_link).attr('title').split(':')[1];
    flowplayer_config(site_url, "multimedia-show",
        video_src, "", "", true);
    $('.file-title', '#multimedia-files-full').html("<span class='multimedia-file-label'>FILM</span><span class='multimedia-file-title-holder'>" + video_title + "</span>");
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

});
