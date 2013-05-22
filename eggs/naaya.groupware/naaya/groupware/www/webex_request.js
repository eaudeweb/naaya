$(function() {
    var start_pack = $("#start_time_pack");
    var end_pack = $("#end_time_pack");

    $("#all_day").change(function() {
        if (this.checked) {
            start_pack.hide();
            end_pack.hide();
        }
        else {
            start_pack.show();
            end_pack.show();
        }
    });
});
