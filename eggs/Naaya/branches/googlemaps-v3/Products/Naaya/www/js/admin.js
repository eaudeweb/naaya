/**
 * All the utility functions used in the admin sections
*/
$(document).ready(function(){

	set_up_info_boxes();
	jQuery("a.suggest_translation").click(add_suggestion);
        if ($('#comments-list').length){
            $('#comments-list').dataTable({
                'aaSorting': [[2, "desc"]],
                'sPaginationType': 'full_numbers',
                "aLengthMenu": [[10, 25, 50, -1], [10, 25, 50, "All"]],
                'aoColumnDefs': [{
                    'bVisible': false,
                    'aTargets': [ 1, 2, 3, 4 ]
                }]
            });
        }

        $('.toggle-spam-status').live('click', function(e){
            e.preventDefault();
            e.stopPropagation();
            var $this = $(this);
            var href = $this.attr('href');
            var comment = $this.attr('id').replace('c-', '');
            var comment_holder = $this.closest('tr');
            var loading = $('.akismet-loading', $this.parent());

            if( $this.hasClass('spam-status') ){
                status = 'True';
            }else {
                status = 'False';
            }

            $.ajax({
                type: "GET",
                url: href,
                dataType: 'json',
                beforeSend: function(){
                    comment_holder.animate({
                        opacity: 0.55
                    }, 300, function(){
                        loading.fadeIn('fast');
                    });
                },
                success: function(response){
                    if( response.status ==  'error' ){
                        alert(response.message);
                    }

                    if( response.status == 'success' ){
                        if( status == 'True' ) {
                            comment_holder.removeClass('ham-comment').addClass('spam-comment');
                        }else {
                            comment_holder.removeClass('spam-comment').addClass('ham-comment');
                        }
                    }

                    return false;
                },
                complete: function(){
                    comment_holder.animate({
                        opacity: 1
                    }, 300, function(){
                        loading.fadeOut('fast');
                    });
                }
            });
        });

        $('.delete-comment').live('click', function(e){
            e.preventDefault();
            e.stopPropagation();
            var $this = $(this);
            var href = $this.attr('href');

            $.ajax({
                type: "GET",
                url: href,
                dataType: 'json',
                success: function(response){
                    if( response.status == 'success' ){
                        comment_holder = $this.closest('tr');
                        comment_holder.animate({
                            opacity: 0
                        }, 300, function(){
                            comment_holder.remove();
                        });
                    }
                }
            });
        });
});

/**
 * Select all checkboxes from a datatable
*/

function selectAll(name){
	$('.datatable td.checkbox input[@name="' + name + '"][type="checkbox"]').attr('checked', $('.select-all').attr('checked') || false);
	return false;
}

function set_up_info_boxes() {
	$('a.info-link').click(toggle_info);

	function toggle_info(evt) {
		evt.preventDefault();
		var info_div = $(this).closest('tr').next();
		info_div.toggle();
	}
}

/**
 * Translate Messages: add an external translate suggestion
*/

function add_suggestion(){
	var jthis = jQuery(this);
	var lang = jthis.attr("name");
	var suggestion = jthis.attr("name");
	jQuery("form[name='translate_" + lang
	       + "'] textarea[name='translation:utf8:ustring']").val(jthis.text());
}
