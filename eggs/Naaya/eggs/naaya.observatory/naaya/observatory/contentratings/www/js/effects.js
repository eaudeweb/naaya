$(document).ready(function () {
    /**
     * Rate Water, Soil, Vegetation, Citizens (images and checkboxes click functions)
    */
    //$('#rate-form img[class="rate-img"]').each(function(){
    //    $(this).click(function(){
    //        _class = $(this).attr('class').split(' ');
    //        selected = false;
    //        if(_class.length){
    //            for(index = 0; index < _class.length; index ++){
    //                if(_class[index] == 'selected'){
    //                    selected = true;
    //                }
    //            }
    //        }
    //
    //        if(selected == false){
    //            $(this).attr('class', 'rate-img selected');
    //            $(this).css({'border': '1px solid white'});
    //        }else{
    //            $(this).attr('class', 'rate-img');
    //            $(this).css({'border': 'none'});
    //        }
    //    });
    //});

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
