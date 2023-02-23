#!/bin/bash

#rasa run -m models --enable-api --cors "*" -p 5006 &
#sleep 20s
#rasa run actions -p 5056 &> /dev/null

#Start the execution
rasaPID=`sudo lsof -t -i tcp:5008`
if [ -z "$rasaPID" ]
then
echo "No process is running"
else
sudo su -c "sudo kill -9 $rasaPID" -s /bin/sh devops_admin
fi

rasaActionPID=`sudo lsof -t -i tcp:5058`
if [ -z "$rasaActionPID" ]
then
echo "No process is running"
else
sudo su -c "sudo kill -9 $rasaActionPID" -s /bin/sh devops_admin
fi

cd /home/devops_admin/vivifyChatbots/envohb/open_health
git pull

rasa run -m models --enable-api --cors "*" -p 5008 &
sleep 20s
rasa run actions -p 5058 &> /dev/null
sleep 30s

exit


