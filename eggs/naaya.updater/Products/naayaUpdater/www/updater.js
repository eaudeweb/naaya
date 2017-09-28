$(document).ready(function(){
    /**
     * Display some details
    */
    $('.show-details').click(function(e){
        e.preventDefault();
        $(this).siblings('.details').toggle();
    });

    /**
     * Select/deselect all checkboxes
    */
    var selectall_default = $('.select-all').val()?$('.select-all').val():$('.select-all').text();
    var selectall_toggle = "Deselect all"
    $('.select-all').click(function(e){
        e.preventDefault();
        var is_value = $(this).val()?true:false;
        var current_value = is_value?$(this).val():$(this).text()
        var select_all = current_value == selectall_default?true:false
        $('input[type=checkbox]').attr('checked', select_all);
        if(is_value){
            $(this).val(select_all?selectall_toggle:selectall_default);
        }else{
            $(this).text(select_all?selectall_toggle:selectall_default);
        }
        localStorage.form = '';
    });

    $('.select-file-type').click(function(e){
        e.preventDefault();
        $this = $(this);
        type = $this.attr('id');
        items = $('#portals-files-list input[type=radio]');
        items.each(function(){
            name = $(this).attr('value');
            var re = new RegExp('.*(' + type + ').*');
            if( name.match(re) ){
                $(this).attr('checked', 'checked');
            }
        });
    });
    /**
    This is not good enough to work
    $(':input').change(function(){
        localStorage.form = $(this).parents('form').serialize();
    });
    if (localStorage.form){
        unserialize(localStorage.form);
    }
    **/
    //Create links
    if ($('body pre').length){
        $('body pre').html(Linkify($('body pre').html()));
    }
});

/**
*
*  URL encode / decode
*  http://www.webtoolkit.info/
*
**/
function url_decode(utftext) {
    utftext = unescape(utftext)
    var string = "";
    var i = 0;
    var c = c1 = c2 = 0;
    while ( i < utftext.length ) {
        c = utftext.charCodeAt(i);
        if (c < 128) {
            string += String.fromCharCode(c);
            i++;
        }
        else if((c > 191) && (c < 224)) {
            c2 = utftext.charCodeAt(i+1);
            string += String.fromCharCode(((c & 31) << 6) | (c2 & 63));
            i += 2;
        }
        else {
            c2 = utftext.charCodeAt(i+1);
            c3 = utftext.charCodeAt(i+2);
            string += String.fromCharCode(((c & 15) << 12) | ((c2 & 63) << 6) | (c3 & 63));
            i += 3;
        }
    }
    return string;
}

function unserialize(data){
    var rows = data.split('&');
    $.each(rows, function(i, row){
        var field = url_decode(row).split('=');
        var field_el = $(':input[name='+ field[0] +']');
        if(field_el.attr('type') == 'checkbox'){
            field_el.attr('checked', field[1]);
        }else{
            field_el.val(field[1]);
        }
    })
}
