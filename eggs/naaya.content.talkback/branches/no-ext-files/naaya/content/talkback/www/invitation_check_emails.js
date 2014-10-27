$(function () {
	function markDomElement(e, text) {
		e[0].style.color = "red";
		e.attr("title", text + " " + check_emails.invalid_email_text);
	}
	check_emails.resolve(".tb-invitations code", markDomElement, 2);
});
