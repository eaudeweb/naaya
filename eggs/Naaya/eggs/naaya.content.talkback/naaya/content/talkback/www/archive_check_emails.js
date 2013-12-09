$(function () {
	function markDomElement(e, text) {
		e.removeAttr("href");
		e[0].style.color = "red";
		e.attr("title", text + " " + check_emails.invalid_email_text);
	}
	check_emails.resolve("td#recipients-cell>a", markDomElement, 2);
});
