import smtplib
import os
import ckan.plugins as p
import pylons.config as config

from ckan.common import request
from ckan.lib.base import BaseController
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders
import ckan.lib.mailer as mailer

class DdugController(BaseController):
    def _get_context(self):
        return {'model': model, 'session': model.Session,
                'user': c.user, 'auth_user_obj': c.userobj}    

    def feedbackProv1(self):
        # assert type(['maulik.kamdar@insight-centre.org'])==list
         requestHandler = config.get('ckan.feedback.request_email', "dmulindwa@gmail.com") # this should read from config file or send email to default
         senderEmail = config.get('ckan.feedback.sender_email', "admin@data.ug") # this should read from config file or send email from default
         
         msg = MIMEMultipart()
         msg['From'] = senderEmail
         msg['To'] = requestHandler
         msg['Date'] = formatdate(localtime=True)
         msg['Subject'] = "Dataset Request for " + request.params['datasetName']
         
         dataRequest = "User Name: " + request.params['name'] + "\nUser Email: " + request.params['email'] + "\nOrganization Name: " + request.params['organization'] + "\nDataset Name: " + request.params['datasetName'] + "\nDataset Description: " + request.params['description']
         msg.attach( MIMEText(dataRequest) )
        
        
         email_subject = "Dataset Request for " + request.params['datasetName']
         email_name = request.params['name']
         email_body = msg.as_string() 
         
         try:
             mailer.mail_recipient(email_name, requestHandler, email_subject, email_body)
         except mailer.MailerException:
             raise
        
         return p.toolkit.render('feedbackProv.html')

