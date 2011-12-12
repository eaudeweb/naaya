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
    }

    
    jQuery(document).ready(function(){
        init_userinfo();
    });


})();
