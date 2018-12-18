#!/usr/bin/python
import sys
import argparse
import optparse
import requests
import logging
import os
import commands
import json
import time
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

string_join = sys.argv[1] + " " + sys.argv[2]
del sys.argv[1]
del sys.argv[1]

parser = argparse.ArgumentParser()

parser.add_argument('-n', '--nome', help='nome que sera criado o objeto no tower')
parser.add_argument('-o', '--org', help='organization que existe no tower')
parser.add_argument('-u', '--user', help='username para execucao no tower')
parser.add_argument('-p', '--password', help='password para autenticacao')
parser.add_argument('-t', '--tower', help='url para acesso ao tower')
parser.add_argument('-i', '--inventory', help='nome do inventario')
parser.add_argument('-e', '--extra', type=str, nargs='+', help='extra vars')

args = parser.parse_args()

Vnome = args.nome
Vorg = args.org
Vuser = args.user
Vpassword = args.password
Vhost = args.tower
Vinventory = args.inventory
Vextra = args.extra

if Vextra is not None:
    i = iter(Vextra)
    Vextra = dict(zip(i, i))

auth=(Vuser, Vpassword)
url_base = "https://" + Vhost + "/api/v2/"

def call(url):
    url = url_base + url
    return requests.get(url, verify=False, auth=auth)

def call_post(url, data):
    headers = {'Content-Type': 'application/json'}
    url = url_base + url
    ret = requests.post(url, data = json.dumps(data), verify=False, headers=headers, auth=auth)
    return ret

def call_job(url):
    headers = {'Content-Type': 'application/json'}
    url = url_base + url
    ret = requests.post(url, verify=False, headers=headers, auth=auth)
    return ret

def call_delete(url):
    headers = {'Content-Type': 'application/json'}
    url = url_base + url
    ret = requests.delete(url, verify=False, headers=headers, auth=auth)
    return ret

def getinventory(nome):
    ret = call("inventories/?search=" + nome)
    ret_json = json.loads(ret.text)
    return ret_json.get("results")[0].get("id")

def gettemplate(nome):
    ret = call("job_templates/?search=" + nome)
    ret_json = json.loads(ret.text)
    return ret_json.get("results")[0].get("id")

def createinventory(nome):
    data = {"name": nome, "organization": 2}
    return call_post("inventories/",data)

def deleteinventory(nome):
    ret = getinventory(nome)
    return call_delete("inventories/{}/".format(ret))

def createhost(nome,inventario):
    ret = getinventory(inventario)
    data = {"name": nome}
    return call_post("inventories/{}/hosts/".format(ret), data)

def joblaunch(nome,inventario,extravars):
    ret = gettemplate(nome)
    retinv = getinventory(inventario)
    data = {"inventory": retinv, "extra_vars": extravars}
    ret = call_post("job_templates/{}/launch/".format(ret),data)
    ret_json = json.loads(ret.text)
    job = ret_json.get("job")
    print (job)

def jobmonitor(job):
    ret = call('jobs/{}/activity_stream/'.format(job))
    ret_json = json.loads(ret.text)
    job_status = ret_json.get("results")[0].get("summary_fields").get("job")[0].get("status")
    monitor(job_status,job)


def monitor(jobstatus,job):
    cont = True
    while cont:
        ret = call('jobs/{}/activity_stream/'.format(job))
        ret_json = json.loads(ret.text)
        job_status = ret_json.get("results")[0].get("summary_fields").get("job")[0].get("status")
        print job_status
        if job_status == 'successful':
            print "job concluido"
            cont = False
        if job_status == 'failed':
            print "job falhou"
            cont = False
        if job_status == 'canceled':
            print "job cancelado"
            cont = False
        if job_status == 'running':
            print "job executando"
            time.sleep(10)

if string_join == 'create inventory':
   createinventory(Vnome)

if string_join == 'delete inventory':
    deleteinventory(Vnome)

if string_join == 'create host':
    createhost(Vnome,Vinventory)

if string_join == 'job launch':
    joblaunch(Vnome,Vinventory,Vextra)

if string_join == 'job monitor':
    jobmonitor(Vnome)
