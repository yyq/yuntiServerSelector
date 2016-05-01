import subprocess
import re
import string
import threading

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
      print "Command FAILED and we'll try it again : " + self.command
      result = subprocess.check_output(self.command, shell=True)
      
    resultarray = result.split("\n")
    packet_loss_rate = re.findall(r'\b\d+\.\d+\b', resultarray[-3])[0]
    average_latency = re.findall(r'\b\d+\.\d+\b', resultarray[-2])[1]
    final.append([self.command, string.atof(packet_loss_rate), string.atof(average_latency)])

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
