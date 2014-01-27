$(function() {
    $('li.customized').each(function() {
        var name = $('a.template', $(this)).text();
        var button = make_delete_button(name, "Delete custom template?");
        $(this).append(" ", button.text("revert"));
    });

    $('li.local').each(function() {
        var name = $('a.template', $(this)).text();
        var button = make_delete_button(name, "Delete local template?");
        $(this).append(" ", button.text("delete"));
    });

    function make_delete_button(name, question) {
        var button = $('<a href="#" class="button-for-custom">');
        button.click(function(evt) {
            evt.preventDefault();
            button.hide();
            var no_button = $('<a>').text('cancel').click(function(evt) {
                confirm_message.remove();
                button.show();
            }).addClass('button-for-custom');
            var yes_button = $('<a>').text('yes').click(function(evt) {
                $.post('./manage_delObjects', {'ids:list': name},
                       function() {
                    window.location.reload(true);
                });
            }).addClass('button-for-custom').css('color', 'red');
            var confirm_message = $('<span>').append(
                    question, " ", no_button, " ", yes_button);
            button.after(confirm_message);
        });
        return button;
    }
});

