#!/usr/bin/env python
# This script used for doing annotations internal to the team.
# These were the short-form annotation instructions:
"""
Short version: For each CaringBridge site, do the following:
1. Read the site
2. Enter the site ID in the first question
3. Answer the 3 Yes/No questions for this site
4. Add a note if you have questions or uncertainty
5. Submit and start a new form for the next site

---

Thank you for volunteering to help us annotate CaringBridge blog sites for our analysis of the CaringBridge social network. This Google form is to be submitted based on the sites you were emailed.

A typical CaringBridge site is a blog-like website created by a patient or a caregiver with some kind of medical situation; common examples include cancer, surgery, or chronic pain.  However, because CaringBridge is a popular site, it attracts the attention of spammers attempting to market products and make use of CaringBridge's link authority.  We need help identifying and removing these spam sites.

In your email, you have 10 HTML attachments, which can be opened in any modern web browser.  Each attachment depicts the description and first three "journal" updates of a CaringBridge site.  Read the description and the first three updates to get a sense of if the blog is non-spam, in English, and is otherwise a typical CaringBridge site.

Note: Some of the posts you read may be upsetting or medically graphic; do not feel compelled to keep reading a site that is making you uncomfortable.  These sites are personal and private; you shouldn't share any details from these sites with anyone outside of this lab. You should delete the email with the site data when you are finished annotating the set of attachments.

We appreciate your help!  Questions/comments, talk to Zach or Marco, or contact levon003@umn.edu.
"""

import sys
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

BATCH_SIZE = 10
ANNOTATION_DIR = '/home/srivbane/shared/caringbridge/data/projects/sna-social-support/data_selection/human_site_annotation/'

def send_email(x500, site_ids):
    dir = ANNOTATION_DIR
    gmail_user = 'caringbridgeannotation@gmail.com'
    gmail_password = 'caringbridge'

    sent_from = gmail_user
    to = f'{x500}@umn.edu'
    subject = 'Spam Identification'

    email_text = f"""\
    From: UMN CaringBridge research team <{sent_from}>
    To: {to}
    Subject: {subject}
    10 HTML sites are attached. Please fill out the following form to review them: https://docs.google.com/forms/d/e/1FAIpQLScUdRjOQbo1Iw6T02AmIqML3_dMEJVnRED1Xihs7-gquIOVig/viewform?usp=sf_link
    Thank you for your participation.
    ---
    This message is automated. Contact levon003@umn.edu with any questions.
    """
    # set up email message
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = sent_from
    msg['To'] = to
    msg.attach(MIMEText(email_text, 'plain'))

    # attach sites
    html_dir = dir + '/html_random'
    filenames = [f'site_{id}.html' for id in site_ids]
    for filename in filenames:
        filepath = os.path.join(html_dir, filename)
        with open(filepath, 'rb') as f:
            part = MIMEApplication(f.read(), Name=filename)
        part['Content-Disposition'] = f'attachment; filename="{filename}"'
        msg.attach(part)
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com')
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.send_message(msg)
        server.close()
        print('Message sent and connection to server closed.')
        print(f'Sites sent: {filenames}')
    except:
        print('Login failed. Aborting...')
        sys.exit(1)
    # record which sites were sent
    with open(os.path.join(dir,'sent_random_site_ids.txt'), 'a+') as f:
        f.write(f'# Sent to {x500}\n')
        for id in site_ids:
            f.write(id + '\n')

def main():
    dir = ANNOTATION_DIR
    x500 = sys.argv[1]
    with open(os.path.join(dir,'random_site_ids_201910.txt'), 'r') as f:
        ids = f.readlines()
        ids = [x.strip() for x in ids]
    try:
        with open(os.path.join(dir, 'sent_random_site_ids.txt'), 'r') as f:
            sent_ids = f.readlines()
            sent_ids = [x.strip() for x in sent_ids]
            # check which site was the last one sent out
            # to determine where to start next batch
            if sent_ids != []:
                start = ids.index(sent_ids[-1]) + 1
            else:
                start = 0
    except FileNotFoundError:
        start = 0
    batch = ids[start:start+BATCH_SIZE]
    if batch == []:
        print('All sites have been sent out!')
        return
    send_email(x500, batch)

if __name__ == "__main__":
    main()
