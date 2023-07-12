# -*- coding=utf-8 -*-
# functions lib

import sublime
from .config import *
import re, os, hashlib
from .applescript import tell
from urllib.parse import urlparse
import ipaddress

# setting working dir
workdir = os.environ['HOME'] + '/.xtools'
if os.path.exists(workdir):
    pass
else:
    os.mkdir(workdir)


def convert_ipv4_to_C(view):
    rets = {}
    pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}'
    regions = view.find_all(pattern)

    for region in regions:  
        ip = view.substr(region)
        if ip in rets.keys():
            rets[ip] = rets[ip] + 1
        else:
            rets[ip] = 1

    rets = sorted(rets.items(), key=lambda v:v[1], reverse = True)

    text = '[+] 所有 C 段: \n'
    for line in rets:
        text += '{0}.0/24 [{1}]'.format(line[0],line[1]) + "\n"
        
    return text


def convert_C_to_ipv4(text):
    ret = ''
    for line in text.split('\n'):
        try:
            ips = ipaddress.ip_network(line.strip(' '))
            ret += '\n'.join(ips)
        except:
            sublime.message_dialog('[error] IP C is invaild! Please check...')
    return ret


def convert_ipv4_to_B(view):
    rets = {}
    pattern = r'\d{1,3}\.\d{1,3}\.'
    regions = view.find_all(pattern)

    for region in regions:  
        ip = view.substr(region).strip('.')
        if ip in rets.keys():
            rets[ip] = rets[ip] + 1
        else:
            rets[ip] = 1

    rets = sorted(rets.items(), key=lambda v:v[1], reverse = True)

    text = '[+] 所有 B 段: \n'
    for line in rets:
        text += '{0}.0.0/16 [{1}]'.format(line[0],line[1]) + "\n"
        
    return text


def select_ipv4(view):
    pattern = r'(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|[1-9])\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)'
    regions = view.find_all(pattern)

    lan_ips = []
    wan_ips = []
    for region in regions:
        text = view.substr(region)
        if is_lan(text):
            lan_ips.append(text)
        else:
            wan_ips.append(text)
            
    return list(set(lan_ips)),list(set(wan_ips))


def is_lan(ip):
    try:
        return ipaddress.ip_address(ip.strip()).is_private
    except Exception as e:
        return False


def select_domain(view):
    pattern = r'([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+('+top_sufix+'|'+country_sufix+')'
    regions = view.find_all(pattern, sublime.IGNORECASE)

    rootdomains = ''
    domains = ''
    for region in regions:
        text = view.substr(region)
        domains += text + '\n'
        rootdomains += select_rootdomain(text) + '\n'

    return domains,rootdomains


def select_rootdomain(text):
    dms = text.split('.')
    if len(text) == 2:
        return text
    if dms[-2] in top_sufix and dms[-1] in country_sufix:
        root = "{0}.{1}.{2}".format(dms[-3],dms[-2],dms[-1])
        return root
    if dms[-1] in top_sufix or dms[-1] in country_sufix:
        root = "{0}.{1}".format(dms[-2],dms[-1])
        return root


def select_urls(view, path=False):
    pattern = r'https?://\S+'
    regions = view.find_all(pattern, sublime.IGNORECASE)

    array = []
    for region in regions:
        text = view.substr(region)
        if path == False:
            text = delete_url_path(text)
        if text not in array:
            array.append(text)
            
    text = '\n'.join(array)
    return text


def exec_command(cmd):
    tell.app('Terminal','do script"{cmd}"'.format(cmd=cmd),background=True)


def write_file(text):
    file = workdir + '/' + hashlib.md5(text.encode('utf-8')).hexdigest()
    with open(file,'w') as fw:
        fw.write(text)

    return file


def read_file(file):
    with open(file) as fr:
        text = fr.read().strip('\n')
    return text


def delete_url_path(url):
    o = urlparse(url)
    return o.scheme + '://' + o.netloc


def is_url(urls):
    errurls = ''
    for url in urls:
        if re.match(r'^https?:/{2}\w.+$', url):
            pass
        else:
            errurls += url + '\n'
    return errurls