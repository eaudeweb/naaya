/**
 * All the utility functions used in the admin sections
*/
$(document).ready(function(){
    $('.autocomplete').each(function(){
        var source = $(this).parents('form').attr('href').
        replace(/http:\/\/[^\/]+\//, '');
        var template = $('#template').val();
        var used = false;
        var content;

        $(this).autocomplete({
            minLenght: 0,
            source: function(request, response) {
                toggleLoader();
                data = {
					query: request.term,
                    template: template,
                    skey: 'name',
                    rkey: 1
				};
                if($('#all_users').length){
                    data['all_users'] = $('#all_users').val();
                }
                $.get(source, data, function(data){
                    $('.datatable').replaceWith(data);
                    toggleLoader();
                });
			},
            search: function(event, ui){
                used = true;
            }
        });

        $(this).keyup(function(keyCode){
            if($(this).val() == ''){
                $(this).autocomplete("search", ' ');
            }
        });
    });
});

function toggleLoader(){
    $('.ajax-loader').toggle();
}

function show_ldap_section(id, url) {
    $('#second_tab_set a.current_sub').removeClass('current_sub');
    if (id) {
        $('#'+id).addClass('current_sub');
    }

    $('#section_wating_response').css('display', 'block');
    $('#section_parent').css('display', 'none');

    $.ajax({
        type: 'GET',
        url: url,
        success: function(data) {
            $('#section_parent').html(data);

            $('#section_wating_response').css('display', 'none');
            $('#section_parent').css('display', 'block');
        },
        error: function() {
            $('#section_wating_response').css('display', 'none');
            alert('Error displaying user management section');
        }
    });
}
function show_ldap_users_fieldset(url) {
    $('#users_roles_wating_response').show();

    $.ajax({
        type: 'GET',
        url: url,
        success: function(data) {
            $('#users_field').replaceWith(data);

            $('#users_roles_wating_response').hide();
        },
        error: function() {
            $('#users_roles_wating_response').hide();
            alert('Error displaying users roles');
        }
    });
}
