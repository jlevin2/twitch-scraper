import csv
import datetime
import smtplib
import configparser
import requests

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

ENVIRONMENT = 'Prod'
CONFIG_FILE = 'config.ini'

def loadConfig():
	parser = configparser.ConfigParser()
	parser.read(CONFIG_FILE)

	parser.sections()

	conf = {}

	conf['game list'] = parser[ENVIRONMENT]['game list']
	conf['threshold'] = parser[ENVIRONMENT]['threshold']
	conf['smtp host'] = parser[ENVIRONMENT]['smtp host']
	conf['smtp port'] = parser[ENVIRONMENT]['smtp port']
	conf['user'] = parser[ENVIRONMENT]['user']
	conf['pass'] = parser[ENVIRONMENT]['pass']
	conf['to'] = parser[ENVIRONMENT]['to']
	conf['from'] = parser[ENVIRONMENT]['from']

	conf['alert registry'] = parser[ENVIRONMENT]['alert registry']

	conf['filename'] = parser[ENVIRONMENT]['file directory'] + 'twitch_' + str(datetime.datetime.now())[:16] + '.csv'

	conf['client id'] = parser[ENVIRONMENT]['client id'] #

	return conf;

def pullTwitch(conf):
	popular_streamers = []

	for game in conf['game list'].split(','):
		headers = {'Accept' : 'application/vnc.twitchtv.v5+json'}

		url = "https://api.twitch.tv/kraken/streams/?limit=100&stream_type=live&game={0}&client_id={1}".format(
			game, conf['client id'])

		response = requests.get(url, headers=headers)

		if response.status_code != 200:
			logger.error('ERROR')
			raise Exception;

		respj = response.json()

		for stream in respj['streams']:
			viewers = stream['viewers']
			if int(viewers) >= int(conf['threshold']):
				name = stream['channel']['display_name']
				streamer_id = stream['channel']['_id']
				stream_id = stream['_id']
				game = stream['channel']['game']
				stream_start_time = stream['created_at'].replace('Z', '').replace('T', ' ')
				popular_streamers.append((name, viewers, streamer_id, stream_id, game, stream_start_time))

	return popular_streamers

def writeData(conf, streams):
	with open(conf['filename'], 'w', encoding='utf-8', errors='ignore') as f:
		writer = csv.writer(f)
		writer.writerows(streams)

	return 0

def sendEmail(conf, streams):
	file = open(conf['alert registry'], 'r', encoding='utf-8')
	contents = file.read().split('\n')
	toAlert = []
	for st in streams:
		# Check Id
		if str(st[3]) not in contents:
			toAlert.append(st)
	file.close()

	file = open(conf['alert registry'], 'a', encoding='utf-8')
	for alert in toAlert:
		file.write(str(alert[3]) + '\n')
	file.close()
	if toAlert:
		msg = MIMEMultipart('alternative')
		msg.set_charset('UTF-8')
		msg.attach(MIMEText(writeHTML(toAlert).encode('utf-8'), 'html', 'UTF-8'))
		msg['Subject'] = 'Twitch Alert'
		msg['From'] = conf['from']
		msg['To'] = conf['to']
		smtp = smtplib.SMTP_SSL(conf['smtp host'])
		smtp.login(conf['user'], conf['pass'])
		smtp.sendmail(msg['From'], msg['To'].split(','), msg.as_string())
		smtp.quit()

	return 0

def writeHTML(streams):
	# Every report has the same opening
	html = '''<!DOCTYPE html>
	<html> 
	<head> <style> table td {border:solid 1px #000000 ; word-wrap:break-word} </style> </head>
	<body> <p style=\"font-family:'Calibri'\"> We have detected the following streamers are streaming on Twitch: </p> '''
	new_table = '''
	<table border=\"1\" width=\"100%\" style=\"font-family:'Calibri';border-collapse:collapse\">
	<thead> <tr style=\"background-color:#B0C4DE \"> <th> Channel Name </th> 
													<th> Viewers </th> 
													<th> Start Time (UTC) </th> 
			</tr> 
	</thead> '''
	alphabetical = sorted(streams, key=lambda f: f[4])
	sec = alphabetical[0][4]
	html += "<p style=\"font-family:'Calibri';font-weight:bold;font-size:20px\"> " + sec + "</p>"
	html += new_table
	for s in alphabetical:
		if s[4] != sec:
			sec = s[4]
			html += "</table>\n <p style=\"font-family:'Calibri';font-weight:bold;font-size:20px\"> " + sec + "</p>"
			html += new_table

		html += ("<tr style=\"background-color:#D9D9D9 \">  <td align=\"left\">" + s[0] + "</td>" + 
			"<td align=\"center\">" + str(s[1]) + "</td> " + "<td align=\"center\">" + s[5] + "</td> " + " </tr>")

	html += "</table> </body> </html>\n"

	file = open('ex.html', 'w')
	file.write(html)
	file.close()

	# Return the email html text
	return html

def main():
	# Load config file
	conf = loadConfig()
	streams = pullTwitch(conf)
	writeData(conf, streams)
	sendEmail(conf, streams)
	return 0


if __name__ == '__main__':
	main()