$(function() {
    var auto_chbox = $("#auto_register");

    auto_chbox.parent().hide();

    $("#allow_register").change(function() {
        auto_chbox.prop('checked', false);
        if (this.checked) {
            auto_chbox.parent().show();
        }
        else {
            auto_chbox.parent().hide();
        }
    });
});

