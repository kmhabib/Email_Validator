#!/usr/bin/python
import csv
import dns.resolver
import re
import socket
import smtplib
import sys
import os
import time


def open_emails(fname):

	email_list = []
	with open(fname, 'rb') as csvfile:
		emailreader = csv.reader(csvfile)
		for row in emailreader:
			if any("@" in s for s in row):
				if re.match(r'.*(gmail|yahoo|msn).*',row[0]):
					pass
				else:
					email_list.append(', '.join(row)) 
	return email_list

def find_mx_host(records):
	current = records[0].preference
	mx = records[0].exchange
	#print("current", current)
	for rdata in records:
		#print 'host', rdata.exchange, 'has preference', rdata.preference
		if rdata.preference < current:
			current = rdata.preference
			mx = rdata.exchange
	return str(mx)

def connect_validate(email_list):

	validated_emails = []
	interesting_emails = []
	for email in email_list:
		print(email)
		match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', email)

		if match == None:
			print('Bad Syntax')
			#raise ValueError('Bad Syntax')
			continue
		username,domain = email.split('@')
		print("user,domain", username,domain)
		try:
			records = dns.resolver.query(domain, 'MX')
		except:
			print("Domain", domain, " is not correct")
			continue			
		#min_pref = records[0].preference
		mxRecord = find_mx_host(records)
		print("mxRecord", mxRecord)
		# Get local server hostname
		host = socket.gethostname()

		# SMTP lib setup (use debug level for full output)
		server = smtplib.SMTP()
		server.set_debuglevel(0)

		# SMTP Conversation
		try:
			server.connect(mxRecord)
			server.helo(host)
			server.mail('verify@verified.com')
			code, message = server.rcpt(str(email))
			server.quit()
		except:
			print("MX error", mxRecord)
			continue
		#server.helo(host)
		#server.mail('verify@verified.com')
		#code, message = server.rcpt(str(email))
		#server.quit()
		# Assume 250 as Success
		if code == 250:
			print('Success')
			validated_emails.append(email)
		else:
			#interesting_emails = numpy.array([[email,code,message]])
			interesting_emails.append(email+" "+ str(code) + " " +message)
	return validated_emails, interesting_emails

#print interesting_emails
#write to verified_emails file
def write_verified( validated_emails):
	timestr = time.strftime("%Y%m%d-%H%M%S")
	fname = "verified_emails_" + timestr + ".csv"
	with open(os.path.join("output_files",fname), 'wb') as csvfile:
		emailwriter = csv.writer(csvfile, dialect='excel')
		for row in validated_emails:
			emailwriter.writerow([row])
	
#write to interesting_emails file
def write_interesting(interesting_emails):
	timestr = time.strftime("%Y%m%d-%H%M%S")
        fname = "interesting_emails_" + timestr + ".csv"
	with open(os.path.join("output_files",fname), 'wb') as csvfile:
		emailwriter = csv.writer(csvfile, dialect='excel')
		for row in interesting_emails:
			emailwriter.writerow([row])
	
def main(fname1):
	email_list = open_emails(fname1) 	
	validated_emails,interesting_emails = connect_validate(email_list)
        #write_verified(fname2, validated_emails)
        write_verified( validated_emails)
        #write_interesting(fname3, interesting_emails)
        write_interesting(interesting_emails)

if __name__ == '__main__':
	main(sys.argv[1])
