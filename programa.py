#!/usr/bin/python

import sys
import argparse
import optparse
import requests
import logging
import os
import commands
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

parser = optparse.OptionParser('usage%prog'+'-Vnome <Vnome>'+'-Vorg <Vorg> '+' -Vuser<Vuser>' +'-Vpass <Vpass> '+'-Vhost <Vhost>'+'-Vinventory <Vinventory>')


parser.add_option('-n', dest='Vnome', help='nome que sera criado o objeto no tower')
parser.add_option('-o', dest='Vorg', help='organization que existe no tower')
parser.add_option('-u', dest='Vuser', help='username para execucao no tower')
parser.add_option('-p', dest='Vpass', help='password para autenticacao')
parser.add_option('-t', dest='Vhost', help='url para acesso ao tower')
parser.add_option('-i', dest='Vinventory', help='nome do inventario')


(options,args) = parser.parse_args()
Vnome = options.Vnome
Vorg = options.Vorg
Vuser = options.Vuser
Vpassword = options.Vpass
Vhost = options.Vhost
Vinventory = options.Vinventory

auth=(Vuser, Vpassword)
url_base = "https://" + Vhost + "/api/v2/"

JOB_STATUS = ['pending', 'waiting', 'running', 'failed', 'successful']


def call(url):
    url = url_base + url
    logger.debug(url)
    return requests.get(url, verify=False, auth=auth)

def call_post(url, data):
    headers = {'Content-Type': 'application/json'}
    url = url_base + url
    logger.debug(url)
    ret = requests.post(url, data = json.dumps(data), verify=False, headers=headers, auth=auth)
    logger.debug(ret)
    return ret

def call_job(url):
    headers = {'Content-Type': 'application/json'}
    url = url_base + url
    logger.debug(url)
    ret = requests.post(url, verify=False, headers=headers, auth=auth)
    logger.debug(ret)
    return ret

def call_delete(url):
    headers = {'Content-Type': 'application/json'}
    url = url_base + url
    logger.debug(url)
    ret = requests.delete(url, verify=False, headers=headers, auth=auth)
    logger.debug(ret)
    return ret

def getinventory(nome):
    ret = call("inventories/?search=" + nome)
    ret_json = json.loads(ret.text)
    return ret_json.get("results")[0].get("id")

def gettemplate(nome):
    ret = call("job_templates/?search=" + nome)
    logger.debug(ret)
    ret_json = json.loads(ret.text)
    return ret_json.get("results")[0].get("id")

def createinventory(nome):
    data = {"name": nome, "organization": 2}
    return call_post("inventories/",data)

def deleteinventory(nome):
    ret = getinventory(nome)
    return call_delete("inventories/{}/".format(ret))

# OK
def createhost(nome,inventario):
    ret = getinventory(inventario)
    data = {"name": nome}
    return call_post("inventories/{}/hosts/".format(ret), data)
# OK
def joblaunch(nome,inventario):
    ret = gettemplate(nome)
    retinv = getinventory(inventario)
    data = {"inventory": retinv}
    ret = call_post("job_templates/{}/launch/".format(ret),data)
    ret_json = json.loads(ret.text)
    logger.debug("HTTP {}".format(ret.ok))
    job = ret_json.get("job")
    logger.debug("JOB {}".format(job))

# OK
def jobmonitor(job):
    ret = call('jobs/{}/activity_stream/'.format(job))
    ret_json = json.loads(ret.text)
    return ret_json.get("results")[0].get("summary_fields").get("job")[0].get("status")

string_join = sys.argv[1] + " " + sys.argv[2]

if string_join == 'create inventory':
   createinventory(Vnome)
#sh "/usr/bin/tower-cli inventory create -n nome --organization 2 -u username -p senha -h host

if string_join == 'delete inventory':
    deleteinventory(Vnome)
#/usr/bin/tower-cli inventory delete -n nome -u user -p senha -h host

if string_join == 'create host':
    createhost(Vnome,Vinventory)
#sh "/usr/bin/tower-cli host create -n host -i inventario -u user -p senha -h host"

if string_join == 'job launch':
    joblaunch(Vnome,Vinventory)

if string_join == 'job monitor':
    jobmonitor()
