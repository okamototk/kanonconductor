# -*- coding: utf-8 -*-

from trac.attachment import Attachment, AttachmentModule, ILegacyAttachmentPolicyDelegate
from trac.core import *
from trac.mimeview.api import Context
from trac.resource import Resource

class MailArchiveAttachment(object):
    
    def __init__(self, env, mail_id):
        self.env = env
        self.id = mail_id
        
    def get_attachments(self, req):
        context = Context.from_request(req, Resource('mailarchive', str(self.id), None))
        #self.log.debug(context)
        return AttachmentModule(self.env).attachment_data(context)
    
    def has_attachments(self, req):
        attachment = self.get_attachments(req)
        if len(attachment['attachments']) > 0:
            return True
        else:
            return False
        
class MailArchiveAttachmentModule(Component):
    implements(ILegacyAttachmentPolicyDelegate)

    # ILegacyAttachmentPolicyDelegate methods
    def check_attachment_permission(self, action, username, resource, perm):
        """ Respond to the various actions into the legacy attachment
        permissions used by the Attachment module. """
        if resource.parent.realm == 'mailarchive':
            if action == 'ATTACHMENT_VIEW':
                return 'MAILARCHIVE_VIEW' in perm(resource.parent)
            if action in ['ATTACHMENT_CREATE', 'ATTACHMENT_DELETE']:
                if 'MAILARCHIVE_ADMIN' in perm(resource.parent):
                    return True
                else:
                    return True # False

