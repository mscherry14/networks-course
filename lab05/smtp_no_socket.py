import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import email.utils as utils

def send_email(frm, to, subj, text, html, password):
    msg = MIMEMultipart('alternative')
    msg['Message-ID'] = utils.make_msgid(domain='spbu.hw.com')
    msg['Subject'] = subj
    msg['From'] = frm
    msg['To'] = to

    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    msg.attach(part1)
    ##msg.attach(part2)

    server = smtplib.SMTP('smtp-mail.outlook.com:587')
    server.starttls()
    print(server.login(frm, password))
    server.mail("<" + frm + ">")
    server.rcpt("<" + to + ">")
    print(server.data(msg.as_string()))
    server.quit()


if __name__ == "__main__":
    frm = sys.argv[1]
    password = sys.argv[3]
    to = sys.argv[2]
    text = "Hello!"
    html = """\
<html>
  <head></head>
  <body>
    <p> Meme:
    <br><img
src="https://cs7.pikabu.ru/post_img/2019/09/07/6/1567846374110558367.jpg">
    </p>
  </body>
</html>
"""
    send_email(frm, to, 'Subject', text, html, password)
