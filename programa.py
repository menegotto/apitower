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
    return requests.get(url, verify=False, auth=auth)

def call_post(url, data):
    headers = {'Content-Type': 'application/json'}
    url = url_base + url
    logger.debug(url)
    ret = requests.post(url, data = json.dumps(data), verify=False, headers=headers, auth=auth)
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

def createinventory(nome):
    print "create inventory"
    data = {"name": nome, "organization": 2}
    return call_post("inventories/",data)

def deleteinventory(nome):
    ret getinventory(nome)
    return call_delete("inventories/{}/".format(ret))
    
# OK
def createhost(nome,inventario):
    print "create host"
    data = {"nome": host}
    return call_post("inventories/{}/hosts/".format(inventario), data)
# OK
def joblaunch(nome):
    print "job launch"
    return call_post("job_templates/" + nome + "/launch/")
# OK
def jobmonitor(job):
    print "job monitor"
    ret = call('jobs/{}/activity_stream/'.format(job))
    ret_json = json.loads(ret.text)
    return ret_json.get("results")[0].get("summary_fields").get("job")[0].get("status")


#print sys.argv[1]
#string_join = sys.argv[1] + " " + sys.argv[2]
#print string_join

if string_join == 'create inventory':
   createinventory(Vnome,Vorg)

if string_join == 'delete inventory':
    deleteinventory(Vnome)

if string_join == 'create host':
    createhost(Vnome,Vinventory)

if string_join == 'job launch':
    joblaunch(Vnome)

if string_join == 'job monitor':
    jobmonitor()
