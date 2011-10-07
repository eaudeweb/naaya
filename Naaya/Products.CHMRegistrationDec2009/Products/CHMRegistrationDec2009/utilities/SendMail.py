def send_mail(msg_from, msg_to, msg_subject, msg_body, msg_body_text, smtp_host, smtp_port):
    import smtplib
    from email.MIMEMultipart import MIMEMultipart
    from email.MIMEText import MIMEText

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = msg_subject
    msg['From'] = msg_from
    msg['To'] = ', '.join(msg_to)

    # Create the body of the message (a plain-text and an HTML version).
    text = msg_body_text
    html = msg_body

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain', _charset='utf-8')
    part2 = MIMEText(html, 'html', _charset='utf-8')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)

    # Send the message via local SMTP server.
    s = smtplib.SMTP(smtp_host, smtp_port)
    # sendmail function takes 3 arguments: sender's address, recipient's address
    # and message to send - here it is sent as one string.
    s.sendmail(msg_from, msg_to, msg.as_string())
    s.quit()