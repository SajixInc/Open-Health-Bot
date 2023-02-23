#!/bin/bash


ssh -tt devops_admin@vivify-chatbot <<EOF
cd /home/devops_admin/vivifyChatbots
source ./envohb/bin/activate
cd ./envohb/open_health
setsid ./runRasa-ohb.sh > /dev/null 2>&1 < /dev/null &
sleep 60s
rasaPID1=`sudo lsof -t -i tcp:5008`
rasaActionPID1=`sudo lsof -t -i tcp:5058`
if [ -z "$djangoPID1" or "$rasaActionPID1" ]
then
echo "Build was failed for chatbot-ohb-dev"
else
echo "Build was successful on chatbot-ohb-dev"
fi
exit
EOF
