# -*- coding: utf-8 -*-

import os.path
import datetime
import smtplib

from email import Encoders
from email.Utils import formatdate
from email.MIMEBase import MIMEBase
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.Header import Header
from email.MIMEImage import *

def create_message(from_addr, to_addr, subject, body, encoding, attach_file, body2='', body3=''):
    """
    Mailのメッセージを構築する
    """
    msg = MIMEMultipart('alternative')
    msg["Subject"] = Header(subject, encoding)

    msg["From"] = from_addr
    msg["To"] = to_addr
    msg["Date"] = formatdate()

    body = MIMEText(body, 'plain', encoding)
    msg.attach(body)
    
    body2 = MIMEText(body2, 'html', encoding)
    msg.attach(body2)
    
    body3 = MIMEText(body3, 'plain', encoding)
    msg.attach(body3)

    # 添付ファイルのデータをセットする
    file = open(attach_file)
    attachment = MIMEImage(file.read(), 'png', name='mail.png')
    msg.attach(attachment)
    attachment.add_header("Content-Disposition","attachment", filename='mail.png')

    return msg

if __name__ == '__main__':
    from_addr = "xxx@xx.xx"
    to_addr = "yyy@yy.yy"
    subject = "sample" 
    body = "test body"
    msg = create_message(from_addr, to_addr, subject, body,
                          'ISO-2022-JP', "../htdocs/png/mail.png",
                          '<strong>aaaa</strong>', 'bbbbbbbbbb')

    print msg