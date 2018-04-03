# -*- coding: utf-8 -*-
import subprocess
import re
import threading
import time

serverCountry = ["mo", "jp", "hk", "tw", "sg", "us"]
serverNumber = [2, 9, 13, 2, 3, 3]
serverSuffix = 'hello, moto'

address_n = 0
final = []
threads = []


class PingThread (threading.Thread):
    def __init__(self, thread, command):
        threading.Thread.__init__(self)
        self.threadID = thread
        self.command = command

    def run(self):
        print(self.command)
        global final
        try:
            result = subprocess.check_output(self.command, shell=True)

        except subprocess.CalledProcessError:
            print("Command FAILED and we'll try it again : " + self.command + "\n")
            time.sleep(5)
            try:
                result = subprocess.check_output(self.command, shell=True)
            except subprocess.CalledProcessError:
                print("Failed again")
        if not result:
            resultarray = result.decode("utf-8") .split("\n")
            packet_loss_rate = re.findall(r'\b\d+\.\d+\b', resultarray[-3])[0]
            average_latency = re.findall(r'\b\d+\.\d+\b', resultarray[-2])[1]
            final.append([self.command, float(packet_loss_rate), float(average_latency)])


commandx = ''
for country_s in serverCountry:
    maxNumber = serverNumber[serverCountry.index(country_s)]
    for number in range(maxNumber):
        commandx = "ping -c 30 " + country_s + str(number+1) + serverSuffix

t = PingThread(address_n, commandx)
t.start()
threads.append(t)

address_n += 1

for t in threads:
    t.join()

final = sorted(final, key=lambda x:(x[1], x[2]))

for x in range(len(final)):
    print(final[x])

print("BEST server is: " + final[0][0].split(" ")[-1])
print("Packet Loss is: " + str(final[0][1]) + "%")
print("Latency     is: " + str(final[0][2]) + "ms")
time.sleep(1)
bestServer = final[0][0].split(" ")[-1]
print(bestServer)
