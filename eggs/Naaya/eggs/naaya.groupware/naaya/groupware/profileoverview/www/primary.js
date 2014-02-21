$(document).ready(function(){
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

    function get_data(portals, igs_count, index, ajax, div_id, left_id, loader_id){
        var igs_left = igs_count - index;
        var value = portals[index];
        $.ajax({
            url: '/profile_overview',
            data: {user: user, ajax: ajax, ig_id: value},
            success: function(data){
                $('#'+div_id).append(data);
                index += 1;
                if (index < igs_count){
                    get_data(portals, igs_count, index, ajax, div_id,
                                left_id, loader_id);
                }
                else{
                    $('#'+left_id).hide();
                    $('#'+loader_id).hide();
                    if (ajax == 'subscriptions'){
                        if ($('#ig_subscriptions').html().replace(/\s+/g, '').length == 0){
                            $('#ig_subscriptions').html("User " + user +
                                " has no subscriptions configured in Interest Groups.");
                        }
                    }
                }
            },
        });
        $('#'+left_id).text(igs_left + ' Interest Groups left to check.');
    }

    ldap_roles.init();
    var user = $("#user").val();
    var all_igs = $.ajax({
            url: '/profile_overview',
            dataType: 'json',
            data:{user: user, ajax: 'igs'},
            success: function(data){
                var igs_count = data.length;
                if (igs_count > 0){
                    $('#igs_access_left').text(igs_count + ' Interest Groups left to check.');
                    get_data(data, igs_count, 0, 'memberships', 'ig_access',
                                'igs_access_left', 'ig_access_loader');
                    get_data(data, igs_count, 0, 'subscriptions', 'ig_subscriptions',
                                'igs_subscriptions_left', 'ig_subscriptions_loader');
                } else {
                    $('#ig_access').html('You are not a member of any Interest Group');
                }
            },
        });
    });

