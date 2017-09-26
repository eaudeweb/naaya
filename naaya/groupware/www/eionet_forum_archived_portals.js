$(document).ready(function(){
    loadArchivedPortals();
});

function loadArchivedPortals(){
    var portals;

    $.ajax({
        url: "https://archives.eionet.europa.eu/archived_portals_json?jsonp=parseData",
        type: "GET",
        dataType: "jsonp",
        async: true,
        beforeSend: function(){
            $('#loading').fadeIn();
        }
    });
}

function parseData(portals){
    $('#loading').fadeOut();
    if( $('#archived_portals').length ){
        ul = $('#archived_portals');
        if ( portals.length > 0 ) {
            $.each(portals, function(index, portal){
                li = $('<li><a class="ig_title" href="' + portal.url + '">' + portal.title + '</a><div class="ig_subtitle">' + portal.subtitle + '</div></li>');
                ul.append(li);
            });
        }else {
            li = $('<li><p>No archived portals!</p></li>');
            ul.append(li);
        }
    }
}
