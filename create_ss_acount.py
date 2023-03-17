import pexpect
import sys, os
import logging
import time,datetime
import json
import random,uuid
import send_to_article

USER_LIST_FILE='user.json'
USERNAME_PREV='user'
ACCOUNT_NUM=10
SERVER_ADDR='ss.miao7.cn'

def add_user(user_info):
  success = []
  process = pexpect.spawn("bash ssrmu.sh", logfile=sys.stdout, encoding='utf-8')
  process.expect("管理脚本")
  process.sendline("7")
  process.expect("用户配置")
  process.sendline("1")

  for user in user_info:
    add_one_user(process, user['username'], user['port'],user['password'],user['encryption'],user['device_num'],user['one_thread_limit'],user['all_thread_limit'],user['total_limit'])
    try:
      success.append(user)
      process.expect("是否继续")
      process.sendline("Y")
    except:
      # process.expect("错误")
      process = pexpect.spawn("bash ssrmu.sh", logfile=sys.stdout)
      process.expect("管理脚本")
      process.sendline("7")
      process.expect("用户配置")
      process.sendline("1")

  json.dump(success, open(USER_LIST_FILE, 'w'))
  return success

def add_one_user(process, username, port, password, encryption, device_num, one_thread_limit, all_thread_limit, total_limit):
  process.expect("要设置的用户")
  process.sendline(username)
  process.expect("端口")
  process.sendline(port)
  process.expect("密码")
  process.sendline(password)
  process.expect("加密方式")
  process.sendline(encryption)
  process.expect("协议插件")
  process.sendline('1')
  process.expect("混淆插件")
  process.sendline('1')
  process.expect("限制的设备数")
  process.sendline(device_num)
  process.expect("单线程 限速上限")
  process.sendline(one_thread_limit)
  process.expect("总速度 限速上限")
  process.sendline(all_thread_limit)
  process.expect("总流量上限")
  process.sendline(total_limit)
  process.expect("禁止访问的端口")
  process.sendline('')

def delete_user():
  if not (os.path.exists(USER_LIST_FILE)):
    return True
  user_info = json.load(open(USER_LIST_FILE, 'r'))
  for i in range(0,len(user_info)):
    user = user_info[i]
    delete_one_user(user['port'])
  return True

def delete_one_user(port):
  process = pexpect.spawn("bash ssrmu.sh", logfile=sys.stdout, encoding='utf-8')
  process.expect("管理脚本")
  process.sendline("7")
  process.expect("用户配置")
  process.sendline("2")
  process.expect("要删除的用户")
  process.sendline(port)
  time.sleep(0.5)

def create_ten_user_info():
  port_list = []
  while True:
    rand = random.randint(10000, 20000)
    if not rand in port_list:
      port_list.append(rand)

    if (len(port_list) >= ACCOUNT_NUM):
      break
  # user['username'], user['port'],user['password'],user['encryption'],user['device_num'],user['one_thread_limit'],user['all_thread_limit'],user['total_limit']
  user_info = []
  for i in range(0, len(port_list)):
    user_info.append({
      'username': USERNAME_PREV + str(port_list[i]),
      'port': str(port_list[i]),
      'password': str(uuid.uuid4()).split('-')[0],
      'encryption': encryption(i),
      'device_num': '2',
      'one_thread_limit': '100',
      'all_thread_limit': '100',
      'total_limit': '1'
    })

  return user_info

def encryption(i):
  if (i <= 3):
    return "1"
  elif(i <= 6):
    return "3"
  else:
    return "5"

def encryption2Str(i):
  if (i == '1'):
    return 'none'
  elif(i == '3'):
    return 'rc4-md5'
  else:
    return 'aes-128-ctr'

def create_md(success):
  title = datetime.datetime.now().strftime('%Y年%m月%d日——SS测试账号分享')
  dateStr = datetime.datetime.now().strftime('%Y年%m月%d日')
  content = ''
  for i in range(0, len(success)):
    user = success[i]
    content = (content + '+ 服务器地址：{0}   端口：{1}  密码：{2} 加密：{3} 混淆：plain \n').format(SERVER_ADDR, user['port'], user['password'], encryption2Str(user['encryption']))

  template = '''---
title: {0}
tag:
category: 
  - SS账号分享
  - 技术分享
url: 
---

{1}

分享SS帐号，仅用当天可用，不能保证网速。


![banner](https://blog.miao7.cn/wp-content/uploads/2023/03/Pasted-28.png)

## SS帐号分享

{2}



SS客户端配置参考链接：
[科学上网SS/SSR——Windows和安卓客户端配置](https://blog.miao7.cn/index.php/2023/03/17/%e7%a7%91%e5%ad%a6%e4%b8%8a%e7%bd%91ss-ssr-windows%e5%92%8c%e5%ae%89%e5%8d%93%e5%ae%a2%e6%88%b7%e7%ab%af%e9%85%8d%e7%bd%ae/)


  '''
  md = dateStr + '.md'
  with open(md, 'w', encoding='utf-8') as f:
    f.write(template.format(title, dateStr, content))
  return md

if __name__ == '__main__':
  # 先删除
  delete_user()
  print('删除成功')
  user_info = create_ten_user_info()
  print(user_info)
  success = add_user(user_info)
  
  name = sys.argv[1]
  password = sys.argv[2]

  md = create_md(success)
  send_to_article.send_to_wordpress(send_to_article.load_markdown_info(md), 'https://blog.miao7.cn', name, password)







