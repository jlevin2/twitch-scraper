# Twitch Scrapper

## Overview 
This application will scrape twitch for current streamers streaming a list of games. It will record all streamers above a certain threshold, and then will log them in a CSV. Futher, the service will send an email alert to a set of recipients if the stream has not already been alerted on.

This is a version of an ETL I wrote for work purposes. This script could be extended to send the file to a data storage center such as Amazon S3 and eventually into a relational database.

## Dependecies
1. Python3
2. Python requests module (for HTTP requests)
3. Gmail account with perms enabled for application

## Setup
1. Fill in config file, setup accounts etc. 
2. Enable to run at scheduled interval with crontab

## Process Steps
1. Load info from config file
2. Queries Twitch for top 50 streams accross every game listed (not whitespace in titles is defined as %%)
3. Writes the data to a local CSV
4. Opens local registry (mini DB)
5. Checks any stream ID that hasn't been alerted on
6. If any streams to alert on, sends email to distro list
7. Terminates

## Future improvments
1. Add data storage for files
2. Turn registry into DB system
3. Add logging
4. Hookup to error handling alert service