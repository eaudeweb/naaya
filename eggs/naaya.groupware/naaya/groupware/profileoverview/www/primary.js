(function(){

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
                var igs_count = data.length;
                if (igs_count > 0){
                    $('#igs_access_left').text(igs_count + ' Interest Groups left to check.');
                    $.each(data, function(index, value){
                        var igs_left = igs_count - index - 1;
                        $.ajax({
                            url: '/profile_overview',
                            async: false,
                            data: {user: user, ajax: 'memberships', ig_id: value},
                            success: function(data){
                                $('#ig_access').append(data);
                            },
                        });
                        $('#igs_access_left').text(igs_left + ' Interest Groups left to check.');
                    });
                    $('#igs_access_left').hide();
                    $('#ig_access_loader').hide();
                    $('#igs_subscriptions_left').text(igs_count + ' Interest Groups left to check.');
                    $.each(data, function(index, value){
                        var igs_left = igs_count - index - 1;
                        $.ajax({
                            url: '/profile_overview',
                            async: false,
                            data: {user: user, ajax: 'subscriptions', ig_id: value},
                            success: function(data){
                                $('#ig_subscriptions').append(data);
                            },
                        });
                        $('#igs_subscriptions_left').text(igs_left + ' Interest Groups left to check.');
                    });
                    $('#igs_subscriptions_left').hide();
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
    });

})();
