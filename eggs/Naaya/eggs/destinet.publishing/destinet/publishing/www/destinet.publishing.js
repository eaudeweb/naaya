(function(){
    
    function init_userinfo(){
        jQuery(".userinfo_item h3").click(
                function(){
                    jQuery(".items", this.parentNode).toggle('blind', {}, 800);
                });
    }

    
    jQuery(document).ready(function(){
        init_userinfo();
    });


})();
