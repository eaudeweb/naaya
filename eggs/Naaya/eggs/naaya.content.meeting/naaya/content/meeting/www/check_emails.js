$(function () {
    var recipients = [];
    var recipient_values = [];
    $("td#recipients-cell>a").each(function () {recipients.push($(this))});
    $.each(recipients, function () {recipient_values.push($(this).text())});
    $.get("check_emails", {'emails': recipient_values}, function (data, textStatus, jqXHR) {
        $.each(recipients, function (i, item) {
            if ($.inArray(item.text(), data.invalid_emails) >= 0 ) {
                item.removeAttr("href");
                // alter the style, that is apparently stored in 0
                item[0].style.color = "red";
                item.attr("title", item.text() + " cannot be reached !")
            }
        });
    }, "json");
});
