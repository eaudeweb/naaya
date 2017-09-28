$(document).ready(function () {
    $('#pin').draggable({revert: 'valid'});
    $('#map').droppable({
        drop: function(event, ui) {
            /**
             * Retrieve XY coordinates
            */
            x = $('#pin').offset().left - $('#center_content').offset().left +  11;
            y = $('#pin').offset().top - $('#center_content').offset().top - 70;
            add_point_to_xy(x, y);
        }
    });

    /**
     * Reset all on #cancel.click
    */
    $('#reset').click(function(){
        $('#rate-form img[class="rate-img selected"]').each(function(){
            $(this).css({'border': 'none'});
        });

        $('#rate-form img[class="vote-img selected"]').each(function(){
            $(this).css({'border': 'none'});
        });
    });
});

function SelectRate(i){
    $('#rate-form img[class="rate-img"]').each(function(){
        if($(this).attr('id') != (i + '-img')){
            $(this).attr('class', 'rate-img');
            $(this).css('border', 'none');
        }
    });

    $('#' + i + '-img').attr('class', 'rate-img');
    $('#' + i + '-img').css({'border': '1px solid white'});
    $('#rate-val').val(i);
    console.log(i);
    return false;
}

function SelectVote(el, i){
    $('#rate-form img[class="vote-img"]').each(function(e){
        if($(this).attr('id') != ('_v' + i)){
            $(this).attr('class', 'vote-img');
            $(this).css('border', 'none');
            $(this).val('0');
        }
    });

    $('#_v' + i).attr('class', 'vote-img');
    $('#_v' + i).css({'border': '1px solid white'});
    $('#vote-val').val(i);

    return false;
}
