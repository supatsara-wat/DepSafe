#!/bin/bash 
#set -xeu 
unset http_proxy https_proxy

ERROR_MSG=
ERROR_TITLE="[ERROR] There are some errors in Monitor job of Data Check  API, data cannot be checked"
 # transfer property for e-mail  later

API_DOMAIN=http://data-check-api-prod.jpe2-caas1-prod3.caas.jpe2c.r-local.net
API_PATH=data_checking
HTTP_OK=200

#check data based on inputted data patterns
response=
RETRY_COUNT=1
RETRY_WAIT_SECOND=10


#check whether there is  invalid data 
check_result=`echo "$response" | python3 -c '
import sys,json,re
data = json.loads(sys.stdin.readline())
if data["HTTP_response_status"] != 200:
   print(1)
else:
   msg = []
   for key in data:
      if "report" in key:
         if "no invalid data" not in data[key]:
            m = re.findall(r"\(.*shop id\)",data[key])
            if len(m) > 0 and "Average" in data[key]: 
               tmp_str = m[0].replace("(", "")
               tmp_str = tmp_str.replace(")", "")
               tmp_str = tmp_str.replace("shop id", "")
               tmp_str = tmp_str.replace("and", "")
               tmp_str = re.sub(r"\s+", " ", tmp_str)
               tmp_str = tmp_str.split(" ")
               tmp_str = [x for x in tmp_str if x]
               if len(tmp_str) > 5:
                  msg.append("major")
                #ignore some rare cases 
               else:
                  msg.append("minor")
            else:
               msg.append("major")
	#1 =there is invalid data and the report will send to the email, 0 = no invalid data
   if len(msg) > 0 and "major" in msg:
      print(1)
   elif len(msg) > 0 and msg.count("minor") > 1:
   	  print(1)
   else:
      print(0)
'`
check_result=0
#print error in HTML format
if [  $check_result -ne 0 ] ;  then

   service_name=`echo "$response" | python3 -c '
import sys,json,re
data = json.loads(sys.stdin.readline())
service_name = ""
for key in data:
	if "table_name" == key:
		service_name = service_name + data[key] + " in Data Service API"
	elif "api_url" == key:
		url = data[key].replace("http://shop-karte-api-prod.jpe2-caas1-prod1.caas.jpe2b.r-local.net/", "")
		url = url.replace("http://shop-karte-api-hbase-prod.jpe2-caas1-prod1.caas.jpe2b.r-local.net/", "")
    url = url.replace("http://campaign-api-prod.jpe2-caas1-prod1.caas.jpe2b.r-local.net/", "")
		service_name = service_name + url + " in Shop Karte API"
print(service_name)
'`
   ERROR_TITLE="[ERROR] ${service_name} Has Irregular Data"
fi