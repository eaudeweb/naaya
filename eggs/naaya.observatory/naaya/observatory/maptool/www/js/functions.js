function submit_rate() {
    if(($('#rate-val').val() == 'cit') && ($('#comment-val').val() == '')){
        alert('You must enter a comment for citizens rate!');
        return false;
    }

    if(($('#rate-val').val() !== 'cit') && ($('#rate-val').val() !== 'wat') && ($('#rate-val').val() !== 'veg') && ($('#rate-val').val() !== 'soil')){
        alert('Please select rate type!');
        return false;
    }

    if($('#vote-val').val() == ''){
        alert('Please select vote value!');
        return false;
    }

    $.ajax({
        type: "POST",
        url: "@@pin_add/submit_pin",
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
