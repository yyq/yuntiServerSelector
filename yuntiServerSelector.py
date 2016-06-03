# -*- coding: utf-8 -*-

import subprocess
import re
import string
import threading
import time

serverSuffix = "vpncute.com"
serverCountry = ["jp", "us", "sg", "tw", "hk", "uk"]
serverNumber = [4,6,2,1,3,1]
protocolType = ["p1", "p2"]

address_n = 0
final = []
threads = []

class pingThread ( threading.Thread ):
  def __init__(self, threadID, command ):
    threading.Thread.__init__(self)
    self.threadID = threadID
    self.command = command
  def run(self):
    global final
    try:
      result = subprocess.check_output(self.command, shell=True)

    except subprocess.CalledProcessError, e:
      print "Command FAILED and we'll try it again : " + self.command + "\n"
      time.sleep(5)
      result = subprocess.check_output(self.command, shell=True)

    resultarray = result.split("\n")
    packet_loss_rate = re.findall(r'\b\d+\.\d+\b', resultarray[-3])[0]
    average_latency = re.findall(r'\b\d+\.\d+\b', resultarray[-2])[1]
    final.append([self.command, string.atof(packet_loss_rate), string.atof(average_latency)])


# zero, current openned service
command = "scutil --nc list | grep \"(Connected)\" | awk -F \'\"\' \'{print $2}\'"
result = subprocess.check_output( command, shell=True).strip()
if result == "":
    print "Current there is no connected vpn services."
else:
    print "Current connected VPN service is: " + result
    print "We are closing the service: " + result
    result = subprocess.check_output("scutil --nc stop \"" + result + "\"", shell=True)
    time.sleep(15)

for country_s in serverCountry:
  maxNumber = serverNumber[serverCountry.index(country_s)]
  for number in range(maxNumber):
    for type_s in protocolType:
      command = "ping -c 30 " + \
                type_s + "." + \
                country_s + str(number+1) + "." + \
                serverSuffix

      t = pingThread(address_n, command)
      t.start()
      threads.append(t)

      address_n += 1

for t in threads:
  t.join()

final = sorted(final, key = lambda x:(x[1], x[2]))

for x in range(len(final)):
  print final[x]

print "BEST server is: " + final[0][0].split(" ")[-1]
print "Packet Loss is: " + str(final[0][1]) + "%"
print "Latency     is: " + str(final[0][2]) + "ms"
time.sleep(1)
bestServer = final[0][0].split(" ")[-1]
# bestServer = "p1.tw1.vpncute.com"


# first, concat the service name
scountryNameDict = {"jp":"日本", "us":"美国", "sg":"新加坡", "hk":"香港", "uk":"英国", "tw":"台湾" }
sCountryNumberDict = {"1":"1号", "2":"2号", "3":"3号", "4":"4号", "5":"5号", "6":"6号"}
sTypeNumberDict = {"1":" PPTP", "2":" L2TP"}
serviceName = "云梯 "
serviceName += scountryNameDict[bestServer[3:5]]
serviceName += sCountryNumberDict[bestServer[5]]
serviceName += sTypeNumberDict[bestServer[1]]
print bestServer
print serviceName

# check if the service ok
command = "networksetup -getnetworkserviceenabled \"" + serviceName + "\""
try:
    result = subprocess.check_output( command, shell=True).strip()
    if result=="Enabled":
        print "The service " + serviceName + " is available."
        print "We are starting the service " + serviceName
    else:
        print "The service " + serviceName + " is not available."
except subprocess.CalledProcessError, e:
    print "The service " + serviceName + " is not available."


# start the service
subprocess.check_output("networksetup -connectpppoeservice \"" + serviceName + "\"",shell=True)
