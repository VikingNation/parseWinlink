# parseWinlinkLog.py
#
# Author: Jason Johnson
# Contact: k3jsj@arrl.net
import sys
import re
import csv

def parseWinlink():
    
    if len(sys.argv) != 3:
        print("Usage: parseWinlinkLog input.log output.csv")
        print("       Parse WINLINK connection logfile for Vara HF connections and write output to output.csv")
        print("       Credits:  Jason Johnson (k3jsj@arrl.net)")
        print("")      
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    with open(input_file,'r') as file:
      data = file.read().replace('\\n', '')
      
    find_specific_lines(data, output_file)
    file.close()




def parse_connection_info_HF(log_record):
    # Regular expression pattern to extract relevant information
    # pattern = r"\*\*\* Winlink Vara Connection to (\w+) @ (\d{4}/\d{2}/\d{2}) (\d{2}:\d{2}:\d{2})  USB Dial: (\d+\.\d+)"
    pattern = r"\*\*\* Winlink Vara Connection to (\w+) @ (\d{4}/\d{2}/\d{2}) (\d{2}:\d{2}:\d{2})  USB Dial: (\d+\.\d+)"
    
    # Match the pattern in the log record
    match = re.match(pattern, log_record)
    
    if match:
        gateway = match.group(1)
        date = match.group(2)
        time = match.group(3)
        usb_dial_frequency = float(match.group(4))
        return gateway, date, time, usb_dial_frequency
    else:
        return None

def parse_bearing_info(log_record):
	# Regular expression pattern to extract relevant information
	# *** Station Bearing: 160,  Range: 20 km
	pattern =  r"\*\*\* Station Bearing: (\d+),\s+Range: (\d+) (km|mi)"
		
	#Match the pattern in the log record
	match = re.match(pattern, log_record)
	
	if match:
		bearing = match.group(1)
		range = match.group(2)
		units = match.group(3)
		return bearing, range, units
	else:
		return None

def parse_message_sent_info(log_record):
    #Messages sent: 1.  Total bytes sent: 894,  Time: 09:31,  bytes/minute: 94
    pattern = r"\*\*\* Messages sent: (\d+).\s+Total bytes sent: (\d+),\s+Time: (\d+):(\d+),\s+bytes/minute: (\d+)"
    
    match = re.match(pattern, log_record)
    
    if match:
        msg_sent = match.group(1)
        bytes_sent = match.group(2)
        time_sent_in_seconds = int(match.group(3)) * 60 + int(match.group(4))
        sent_bytes_per_minute = match.group(5)
        return msg_sent, bytes_sent, time_sent_in_seconds, sent_bytes_per_minute
    else:
        return None
        
 
def parse_message_received_info(log_record):
    #*** Messages Received: 1.  Total bytes received: 456,  Total session time: 09:31,  bytes/minute: 48
    pattern = r"\*\*\* Messages Received: (\d+).\s+Total bytes received: (\d+),\s+Total session time: (\d+):(\d+),\s+bytes/minute: (\d+)"
    
    match = re.match(pattern, log_record)
    
    if match:
        msg_received = match.group(1)
        bytes_received = match.group(2)
        time_received_in_seconds = int(match.group(3)) * 60 + int(match.group(4))
        received_bytes_per_minute = match.group(5)
        return msg_received, bytes_received, time_received_in_seconds, received_bytes_per_minute
    else:
        return None 

def parse_session_complete_info(log_record):
    #*** Session: 9.7 min;  Avg Throughput: 147 Bytes/min;   1 Min Peak Throughput: 147 Bytes/min
    pattern = r"\*\*\* Session:\s+(\d+).(\d+) min;\s+Avg Throughput:\s+(\d+) Bytes/min;\s+1 Min Peak Throughput:\s+(\d+) Bytes/min"
    
    match = re.match(pattern, log_record)
    
    if match:
        session_avg_throughput = match.group(3)
        session_min_throughput = match.group(4)
        
        session_duration_seconds = int(match.group(1))*60 + int((int(match.group(2))/10*60))
        return session_duration_seconds, session_avg_throughput, session_min_throughput
    else:
        return None 


    
def find_specific_lines(log_text, output_file):
    lines = log_text.split('\n')
    keywords = ["Connection to", "*** Messages sent", "*** Messages Received", "*** Session", "Station Bearing"]

    with open(output_file, 'w', newline='') as file:
       writer =csv.writer(file)
       writer.writerow(['Gateway','Date', 'Time', 'DialFrequency', 'Bearing', 'Range', 'Units', \
                        'MsgSent', 'BytesSent', 'TimeSentSec', 'SentBytesPerMinute', \
                        'MsgRecv', 'BytesRx', 'TimeRecSec', 'RecBytesPerMinute', \
                        'DurationSec', 'SesAvgThruPut', 'SecMinThruPut'])
       
    
       for i, line in enumerate(lines):
           for keyword in keywords:
              if keyword in line:
                  print(f"{keyword} found in line {i + 1}: {line}")
                  if ( keyword == "Connection to"):
                      result = parse_connection_info_HF(line)
                      if result:
                          gateway, date, time, usb_dial_frequency = result
                          print(gateway, date, time, usb_dial_frequency)
                        
                  if ( keyword == "Station Bearing"):
                    result = parse_bearing_info(line)
                    if result:
                       bearing, range, units = result
                       print(bearing, range, units)
                  if ( keyword == "*** Messages sent"):
                    result = parse_message_sent_info(line)
                    if result:
                       msg_sent, bytes_sent, time_sent_in_seconds, sent_bytes_per_minute  = result
                       print(msg_sent, bytes_sent, time_sent_in_seconds, sent_bytes_per_minute)
                       
                  if ( keyword == "*** Messages Received"):                    
                      result = parse_message_received_info(line)
                      if result:
                         msg_received, bytes_received, time_received_in_seconds, received_bytes_per_minute = result
                         print(msg_received, bytes_received, time_received_in_seconds, received_bytes_per_minute)
                       
                  if ( keyword == "*** Session"):
                      result = parse_session_complete_info(line)
                    
                      if result:
                          session_duration_seconds, session_avg_throughput, session_min_throughput = result
                          print(session_duration_seconds, session_avg_throughput, session_min_throughput)
                          writer.writerow([gateway, date, time, usb_dial_frequency, bearing, range, units, msg_sent, bytes_sent, time_sent_in_seconds, \
                            sent_bytes_per_minute, msg_received, bytes_received, time_received_in_seconds, received_bytes_per_minute, \
                            session_duration_seconds, session_avg_throughput, session_min_throughput])
                          
                       
		
		
    file.close()
    
# Example usage:
log_text = """*** Winlink Vara Connection to W6IDS @ 2021/12/11 16:50:28  USB Dial: 7083.000
*** Station Bearing: 281,  Range: 708 km
RMS Trimode 1.3.41.0 ***  Welcome To W6IDS RMS HYBRID Gateway - Richmond, IN  ***
K3JSJ has 198 daily minutes remaining with W6IDS (EM79NV)
[WL2K-5.0-B2FWIHJM$]
;PQ: 28991504
CMS via W6IDS >
   ;FW: K3JSJ
   [RMS Express-1.5.43.0-B2FHM$]

   ;PR: 90305052
   ; W6IDS DE K3JSJ (FM18PX)
   FF
;PM: K3JSJ 78JMEP8L0LZL 427 SERVICE@winlink.org Undelivered Message
FC EM 78JMEP8L0LZL 563 427 0
F> 8C
   FS Y
*** Receiving 78JMEP8L0LZL
*** 78JMEP8L0LZL - 578/438 bytes received
*** Bytes: 457,  Time: 00:28,  bytes/minute: 973
   FF
FQ
*** --- End of session at 2021/12/11 16:51:46 ---
*** Messages sent: 0.  Total bytes sent: 0,  Time: 01:18,  bytes/minute: 0
*** Messages Received: 1.  Total bytes received: 457,  Total session time: 01:18,  bytes/minute: 350
*** Disconnected from Winlink RMS: W6IDS @ 2021/12/11 16:51:54
*** Session: 1.4 min;  Avg Throughput: 255 Bytes/min;   1 Min Peak Throughput: 255 Bytes/min"""



if __name__ == "__main__":
    parseWinlink()
