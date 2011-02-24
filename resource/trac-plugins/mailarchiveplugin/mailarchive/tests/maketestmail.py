# -*- coding: utf-8 -*-
# MailArchive plugin

from datetime import datetime,timedelta
import uuid


now = datetime.now()
today = datetime.today()

_mail_num = 1000
i = 0

mail_address="testmail@example.com"
dt = datetime.now()
message_id = ''

for i in range(0,_mail_num):
	last_message_id = message_id
	if i % 5 == 0:
		last_message_id = ''
	message_id = '%s%s'%(uuid.uuid4() , mail_address)
	dt = dt + timedelta(0,60)
	print "From - %s"%(dt.strftime('%a %b %d %H:%M:%S %Y')) #Mon Jun 30 14:29:49 2008
	print "Received: by 192.168.0.1 with HTTP; Sun, 29 Jun 2008 22:26:59 -0700 (PDT)"
	print "Message-ID: <%s>" %( message_id )
	print "Date: %s +0900"%(dt.strftime('%a, %d %b %Y %H:%M:%S')) #Mon, 30 Jun 2008 14:26:59 +0900
	print "From: %s"%(mail_address)
	print "To: %s"%(mail_address)
	print "Subject: TestII%s "%(str(i))
	if last_message_id != '':
		print "In-Reply-To: <%s>" %( last_message_id )
	print "MIME-Version: 1.0"
	print "Content-Type: text/plain; charset=ISO-8859-1"
	print "Content-Transfer-Encoding: 7bit"
	print "Content-Disposition: inline"
	print "Delivered-To: mailarchivetest@example.com"
	print ""
	print "This is Test Mail ."
	print ""
	print ""


