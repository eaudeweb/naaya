    var window_status = undefined;
    var doctitle = $(document).attr("title");
    $(document).ready(function(){
        var msgbox = $("#msg");
        msgbox[0].value = "";
        msgbox.focus();
        msgbox.keyup(function (e) {
            if (e.which == 13) sendMessage();
        });
        $("#sendbtn").click(function() { sendMessage(); });
        ajaxCall();
        getUsers();
        getInvites();
        getPendingInvites();
        $(window).bind("blur", function(){window_status = 'blured'});
        $(window).bind("focus", function(){handleFocus()});
        $("#private").css({display: "none"});
    });

    function getMessages(data){
        if (data.indexOf('chtmsg') != -1) populateMessages(data);
        var lastid = $("#messages div:last").attr("id");
        setTimeout(function(){ajaxCall(lastid)}, 1000);
        }

    function ajaxCall(lastid){
        if (lastid == undefined) { lastid = '' }
        $.post("messages_html", { lastid : lastid }, function(data){ getMessages(data) });
    }

    function getUsers() {
        $("#userlist").load("online_users_html");
        setTimeout("getUsers()", 5000);
    }

    function sendMessage(){
        var msg = $("#msg")[0].value;
        $.post("submitMessage", { msg : msg } );
        $("#msg")[0].value = "";}

    function populateMessages(data) {
        if ($("#messages")[0].innerHTML.length > 1) {
            $("#messages div:last").after(data);
            var newmsg = $("#messages div:last").attr("id");
            scrollMessages(newmsg);
            if (window_status == "blured") handleBlur();
        }
        else {
            $("#messages").html(data);
            var lastmsg = $("#messages div:last").attr("id");
            scrollMessages(lastmsg);
            if (window_status == "blured") handleBlur();
        }
    }

    function scrollMessages(id) {
        if ( id ) {
            var id = "#" + id;
            $(id)[0].scrollIntoView();
        }
    }

    var tInterval = undefined;
    function handleBlur(){
        playSound();
        clearInterval(tInterval);
        tInterval = setInterval("switchTitle()", 1000);
    }

    function handleFocus(){
        window_status = 'focused';
        $(document).attr("title", doctitle);
        clearInterval(tInterval);
    }

    function switchTitle(){
        if (window_status == "blured") {
            if ( $(document).attr("title") == doctitle ) { $(document).attr("title", "NEW MESSAGE")}
            else $(document).attr("title", doctitle);
        }
    }

    function pmInvite(elem){
        var user = elem.id;
        $.post("pm_invite", {"from_user": this_user, "to_user": user});
    }

    function getInvites(){
        $.post("get_user_invites", {"user" : this_user}, handleInvites, "json");
        setTimeout('getInvites()', 5000);
    }

    var il = '';
    function handleInvites(data){
        il = '';
        if (data){
            $.each(data, write_invites);
            $("#invites").html(il);
            $("#invites a").bind("click", acceptInvite);
        }
        if (!data){
            $("#invites").html = '';
        }
    }

    function getPendingInvites(){
        $.post("get_pending_invites", {"user" : this_user}, handlePendingInvites, "json");
        setTimeout('getPendingInvites()', 5000);
    }

    var pl = '';
    function handlePendingInvites(data) {
        pl = '';
        if (data){
            $("#private").css({display: "block"})
            $("#private_label").html('<p>You have invited people in the following chat rooms:</p>');
            $.each(data, write_pending);
            $("#private_rooms").html(pl);
        }
        if (!data){
            $("#private_label").html = '';
            $("#private_rooms").html = '';
        }
    }

    function write_pending(user, values){
        var url = values[0];
        var accepted = values[1];
        item = '<li><a href="' + url + '" target="_blank" id="'+ user +'">Private chat with ' + user + '</a>';
        if (accepted == 0) {
            item = item + ' <span class="unaccepted_invite">[PENDING]</span></li>'
        }

        if (accepted == 1) {
            item = item + ' <span class="accepted_invite">[ACCEPTED]</span></li>'
        }
        pl = pl + item;
    }

    function write_invites(user, url){
        il = il + '<li><a href="' + url + '" target="_blank" id="'+ user +'">Accept chat invitation form ' + user + '</a></li>';
    }

    function acceptInvite() {
        $.post("accept_invite", {"this_user" : this_user, "from_user" : this.id});
        li = this.parentNode
        li.parentNode.removeChild(li);
    }

    function playSound() {
        $.sound.enabled = true;
        $.sound.play('alert_wav')
    }
