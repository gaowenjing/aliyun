#!/usr/bin/python
from datetime import datetime, timedelta
import json, sys, base64, os

import accessid
#Access Key ID
akid = accessid.akid
#Access Key Secret
aks = accessid.aks

userdata = '''#include
https://raw.githubusercontent.com/gaowenjing/aliyun/master/aliyun.txt
#https://code.aliyun.com/jmgwj/aliyun/raw/master/aliyun.txt'''

maxbandwidth = '3'
chargetype = 'PayByBandwidth'
#chargetype = 'PayByTraffic'

try:
  f = file('inst.log', 'r')
  inst_id = json.loads(f.read())['InstanceId']
except:
  inst_id = ''

def r(request):
  exec('from aliyunsdkecs.request.v20140526 import ' + request)
  req = getattr(eval(request), request)()
  return req

def releasetime(i):
  rt = datetime.utcnow() + timedelta(hours = int(i))
  return rt.replace( minute = 59, second = 0, microsecond = 0).isoformat() + 'Z'

if __name__ == '__main__':

  try:
    sys.argv[1]
  except:
    print('no command.')
    exit(1)

  if sys.argv[1] == 'showip':
    with open('inst.ip', 'r') as fd:
      print(json.loads(fd.read())['IpAddress'])
    exit(0)

  from aliyunsdkcore import client
  clt = client.AcsClient(akid ,aks, 'cn-hongkong')

  # parse arguments
  if sys.argv[1] == 'add':
    req = r('CreateInstanceRequest')
    req.set_ImageId('centos_7_3_64_40G_base_20170322.vhd')
    req.set_InstanceType('ecs.t5-lc2m1.nano')
#    req.set_InstanceType('ecs.n1.tiny')
    req.set_InternetChargeType(chargetype)
    req.set_InternetMaxBandwidthOut(maxbandwidth)
    req.set_UserData(base64.encodestring(userdata))

  elif sys.argv[1] == 'del':
    req = r('DeleteInstanceRequest')
    req.set_InstanceId(inst_id)

  elif sys.argv[1] == 'addip':
    req = r('AllocatePublicIpAddressRequest')
    req.set_InstanceId(inst_id)

  elif sys.argv[1] == 'start':
    req = r('StartInstanceRequest')
    req.set_InstanceId(inst_id)

  elif sys.argv[1] == 'stop':
    req = r('StopInstanceRequest')
    req.set_InstanceId(inst_id)

  elif sys.argv[1] == 'rt':
    req = r('ModifyInstanceAutoReleaseTimeRequest')
    req.set_InstanceId(inst_id)
    req.set_AutoReleaseTime(releasetime(sys.argv[2]))
    print(releasetime(sys.argv[2]))

  elif sys.argv[1] == 'passwd':
    req = r('ModifyInstanceAttributeRequest')
    req.set_InstanceId(inst_id)
    req.set_Password('dadfdadf1F')

  elif sys.argv[1] == 'key':
    req = r('AttachKeyPairRequest')
    inst_ids = []
    inst_ids.append(str(inst_id))
    req.set_InstanceIds(inst_ids)
    req.set_KeyPairName('hp')

  elif sys.argv[1] == 'ssh':
    ip_file = file('inst.ip', 'r')
#    print('ssh ' + json.loads(ip_file.read())['IpAddress'])
    os.system('ssh ' + json.loads(ip_file.read())['IpAddress'])
    exit(2)

  elif sys.argv[1] == 'show':
    req = r('DescribeInstancesRequest')

  elif sys.argv[1] == 'status':
    req = r('DescribeInstanceStatusRequest')

  elif sys.argv[1] == 'attr':
    req = r('DescribeInstanceAttributeRequest')
    req.set_InstanceId(inst_id)

  else:
    req = r(sys.argv[1])

  try:
    eval(sys.argv[2])
  except:
    pass

  # process request
  req.set_accept_format('json')
  result = clt.do_action_with_exception(req)
  print(result)

  # log instance id
  if sys.argv[1] == 'add':
    result_file = file('inst.log', 'w')
    result_file.write(result)

  if sys.argv[1] == 'addip':
    result_file = file('inst.ip', 'w')
    result_file.write(result)
    os.system('sed -i "s/remote [0-9.]\+$/remote "' + json.loads(result)['IpAddress'] + '/ /etc/openvpn/ali.conf')
    os.system('systemctl restart openvpn@ali')

  log_file = file('aliyun.log', 'a')
  log_file.write(str(datetime.now()) + ' ' + result + '\n')
