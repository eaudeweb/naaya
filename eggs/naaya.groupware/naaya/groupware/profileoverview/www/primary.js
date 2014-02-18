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


$(document).ready(function(){
    ldap_roles.init();
    var user = $("#user").val();
    var all_igs = $.ajax({
            url: '/profile_overview',
            dataType: 'json',
            async: false,
            data:{user: user, ajax: 'igs'},
            success: function(data){
                if (data.length > 0){
                    $.each(data, function(index, value){
                        $.ajax({
                            url: '/profile_overview',
                            async: false,
                            data: {user: user, ajax: 'memberships', ig_id: value},
                            success: function(data){
                                $('#ig_access').append(data);
                                igs.init();
                            },
                        });
                    });
                    $('#ig_access_loader').hide();
                    $.each(data, function(index, value){
                        $.ajax({
                            url: '/profile_overview',
                            async: false,
                            data: {user: user, ajax: 'subscriptions', ig_id: value},
                            success: function(data){
                                $('#ig_subscriptions').append(data);
                                igs.init();
                            },
                        });
                    });
                    $('#ig_subscriptions_loader').hide();
                    if ($('#ig_subscriptions').html().replace(/\s+/g, '').length == 0){
                        $('#ig_subscriptions').html("User " + user +
                            " has no subscriptions configured in Interest Groups.");
                    }
                } else {
                    $('#ig_access').html('You are not a member of any Interest Group');
                }
            },
        });
    var ajax_calls = function(){
        jQuery.ajax({url: '/profile_overview',
                     data: {user: user, ajax: 'memberships'},
                     success: function(data){
                                jQuery('#ig_access').html(data);
                                igs.init();
                        },
                     complete: function(jqXHR, textStatus){
                           jQuery.get('/profile_overview', {user: user, ajax: 'subscriptions'},
                                function(data){
                                 jQuery('#ig_subscriptions').html(data);
                                });
                        }
        });
    };
    //window.setTimeout(ajax_calls, 1000);
    });

})();
