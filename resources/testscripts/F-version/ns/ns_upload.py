import requests

requests.packages.urllib3.disable_warnings()
url = 'https://192.168.235.89:30283/api/nsd/v1/ns_descriptors/84090010-6e67-4536-81cc-61ae7b0b4ecd/nsd_content'
resp = requests.put(url, files={'file': open(r"C:\Users\86187\Desktop\vfc-tests\ns\ns-new\ns_vgw.csar", 'rb')}, verify=False)
print(resp.status_code)