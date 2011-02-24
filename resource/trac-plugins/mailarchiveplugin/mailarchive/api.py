# -*- coding: utf-8 -*-

from trac.core import Interface

class EmailException(Exception):
    """error exception when processing email messages"""
    
class IEmailHandler(Interface):

    def match(mail):
        """
        whether this handler can be used on this message
        """

    def invoke(mail, warnings):
        """
        what to do on receiving an email;
        returns the message if it is availble to other 
        IEmailHandler plugins or None
        if the message is consumed
        warnings is a list of warnings to append to
        """

    def order():
        """
        what order to process the IEmailHandler in.
        higher order == higher precedence;
        None = no precedence
        """
