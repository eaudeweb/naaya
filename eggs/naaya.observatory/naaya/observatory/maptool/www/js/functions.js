function submit_rate() {
    $.ajax({
        type: "POST",
        url: "@@observatory_pin_add/add_pin_to_observatory",
        data: "lat=" + $('#lat-val').val() +
             "&lon=" + $('#lon-val').val() +
             "&address=" + $('#address-val').val() +
             "&country=" + $('#country-val').val() +
             "&rating=" + $('#vote-val').val() +
             "&type=" + $('#rate-val').val() +
             "&comment=" + $('#comment-val').val(),
        success: function(data) {
            if (console) console.log("success adding pin");
            map_engine.refresh_points();
            return false;
        },
        error: function(req) {
            if(console) console.error("error adding pin:", req);
        }
    });

    return false;
}

