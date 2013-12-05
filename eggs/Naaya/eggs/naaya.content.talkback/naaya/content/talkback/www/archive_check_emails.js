$(function () {
    var recipients = [];
    invalid_email_text = gettext("cannot be reached!");
    $("td#recipients-cell>a").each(function () {recipients.push($(this))});
    $.each(recipients, function (i, recipient) {
        var recipientValue = $.trim(recipient.text());
        function alterDom(data, textStatus, jqXHR) {
            if (data[recipientValue] === false) {
                recipient.removeAttr("href");
                recipient[0].style.color = "red";
                recipient.attr("title", recipientValue + " " + invalid_email_text);
            }
        }
        $.get("check_email", {'email': recipientValue}, alterDom, "json");
    });
});
