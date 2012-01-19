(function(){

    function init_userinfo(){
        jQuery(".userinfo_item h3").click(
                function(){
                    var h3 = jQuery(this);
                    jQuery(".items", this.parentNode).toggle('blind',
                                                             function(){
                                                              if(jQuery(this).is(":visible")){
                                                                h3.removeClass("close").addClass("open");
                                                              } else h3.removeClass("open").addClass("close");
                                                             }
                                                             , 800);
                });
        jQuery(".more_link").click(function(){
           var jthis = jQuery(this);
           jQuery(".more_list_item", this.parentNode).show('blind', {}, 800);
           jthis.hide();
        });
    }

    jQuery(document).ready(function(){
        init_userinfo();
    });

})();
