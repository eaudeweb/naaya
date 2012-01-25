(function(){
var igs = {
        init: function(){
            jQuery("div.see_more a").click(function(){
                var ctxt = jQuery("#"+jQuery(this).attr("data-access"));
                jQuery(".see_more, .see_more_dots", ctxt).hide();
                jQuery(".more", ctxt).show('blind', {}, 800);
            });
        }
    };

var ldap_roles = {
        init: function(){
            jQuery(".toggle_role").click(function(){
                var elem = jQuery("a.toggle_role", this.parentNode);
                ldap_roles.toggle_tr_row(elem.attr("id"));
               }
            );
        },

        toggle_tr_row: function(role_id, hide){
            if (typeof(hide) == 'undefined')
                hide = false;
            var tr = jQuery("tr#row_"+role_id);
            var children = jQuery("tr."+role_id, tr.parentNode);
        
            if (tr.hasClass("expanded") || hide){
                tr.removeClass("expanded");
                if (hide)
                    tr.hide();
                children.each(function(){
                    ldap_roles.toggle_tr_row(jQuery(this).attr("id").replace("row_", ""), true);
                 });
            }else{
                tr.addClass("expanded");
                children.show();
            }
        }
    };


jQuery(document).ready(function(){

   ldap_roles.init();
   jQuery.get('/profile_ajax', '', function(data){
                jQuery('#ig_access').html(data);
                igs.init();
        });

});

})();
