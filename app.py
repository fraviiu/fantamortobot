#!/usr/bin/pytho#!/usr/bin/python3.5

from datetime import datetime, timedelta
import threading
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram import ChatAction
from telegram.ext.dispatcher import run_async
from telegram import ParseMode
import logging
import wptools
import dateutil.parser
import logging
import requests
import requests.packages.urllib3
import io
import shutil
import os
from emoji import emojize
import random
import json
import hashlib
import fileinput
from flask import Flask
import mysql.connector
from newsapi import NewsApiClient
from xml.dom import minidom
import xml.etree.ElementTree as ET
app = Flask(__name__)
apis = ['82a27edd809a4a938dcd84aabe835964','723f76e8b8304a90abd3b7bf77252fc2','7b32c53b7e3542c595f82601627682f6','c89ae5deecbd41f4b938d6357d448124','7cb7d677746b4b9597de82f98ea9bafe','a55367e7d13c4ad2b43e2349ac9b98aa','2accd6d19c3b410294317c2ac8d5ea70','0bda94b5cc3843ec97a730a9671ee1cd','0537de8a2d4141a0ad05091785169138','de25bd2f44d54d9a92718e0ce26b753c']

def add_points(bot, update, args):
    msg = ""
    person_to_add = args[0]
    points_to_add = int(args[1])
    tree = ET.parse('points.xml')  
    root = tree.getroot()
    for elem in root.iter('Player'):
        if elem.attrib['Name'].startswith(args[0]):
            int_element = int(elem.text)
            int_element += points_to_add
            elem.text = str(int_element)
    tree.write('points.xml') 


def list(bot, update):
    msg = ""
    tree = ET.parse('points.xml')  
    root = tree.getroot()
    for elem in root.iter('Player'):
        msg += elem.attrib['Name'] + ": " + elem.text + "\n"
    bot.send_message(chat_id=update.message.chat_id, text=msg)


def news(bot,update,args):
    #api = apis[randint(0, 9)]  de25bd2f44d54d9a92718e0ce26b753c
    #newsapi = NewsApiClient(api_key=random.choice(apis))
    #newsapi = NewsApiClient(api_key='297863bd3e3741c280ed700e294f3ab8')
    print("ricevuto: "+args[0]+"c\n")
    str=""
    flag = False
    with io.open("list_to_check.txt", mode='r', encoding='utf-8') as f:
        #content = f.read().splitlines()
        
       # args[0] = "Barbio"
        for line in f:
            bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
            newsapi = NewsApiClient(api_key=random.choice(apis))
            #line = line.strip('\n')
            line = line.rstrip(' ')
           
            print(line+"\n")
            if line[0] == '-':
            
                line = line.strip('-')
                print(line)
                if flag == True:
                   bot.send_message(chat_id=update.message.chat_id, text=str, parse_mode=ParseMode.HTML)
                   break
                
                if line.startswith(args[0]):
                    flag = True
                    
            if flag == True and not line.startswith(args[0]):    
                if line.startswith('@'):
                    line = line.strip('@')
                    str += '<b>'+line+'</b>\n'
                   
                elif line.startswith('#'):
                    line = line.strip('#')
                    str += '<b>'+line+'</b>\n' 
                else:
                    str += '<b>'+line+'</b>\n'
                     
                try:
                    all_articles_en = newsapi.get_everything(q=line,
                                                      language='en',
                                                      from_parameter=datetime.today()-timedelta(days=7),
                                                      to=datetime.today(),
                                                      sort_by='relevancy',
                                                      page_size = 2,
                                                      page = 1)
                    all_articles_it = newsapi.get_everything(q=line,
                                                      language='it',
                                                      from_parameter=datetime.today()-timedelta(days=7),
                                                      to=datetime.today(),
                                                      sources='ansa',
                                                      sort_by='relevancy',
                                                      page_size = 1,
                                                      page = 1)
                    #print(all_articles+"\n")
                    for x in all_articles_it['articles']:
                       str += "•" + x['title']+"\n"
                    for x in all_articles_en['articles']:
                       str += "•" + x['title']+"\n"
                       #print(x['title'])
                except Exception as e: 
                       print(e)
                
            #print("controllo" +line+"\n")
    f.close()                   
    

last_bot = None
last_update = None
flag_stuck = True
def start(bot, update):
    last_bot = bot
    last_update = update
    morto = emojize(":skull:", use_aliases=True)
    red_flah = emojize(":no_entry_sign:", use_aliases=True)
    vivo = emojize(":unamused_face:", use_aliases=True)
    str = ""

    bot.send_message(chat_id=update.message.chat_id, text="Controllo...\n")
    # bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
    with io.open("list_to_check.txt", mode='r', encoding='utf-8') as f:
        for line in f:
            bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
            try:
                line = line.rstrip('\n')
                line = line.rstrip(' ')
                
                if line[0] == '-':
                    line = line.strip('-')
                    query = ("SELECT Punti FROM points WHERE Nome LIKE %s",(line,))
                    #cursor.execute(query)
                   # print(cursor.fetchone()[0])
                    str += "<b>" + "                                                                                                " + line.strip('-') + "    " + "</b>" + "\n"

                else:
                    if line.startswith('@'):
                        line = line.strip('@')
                        person = wptools.page(line, lang='it').get_wikidata()
                        # person._WIKIPROPS['P570'] = 'death'
                        #  person.get_wikidata()
                        # print(person.wikidata['death'])

                        try:
                            death = person.wikidata['death']
                            str += '<b>(C)</b>    ' + line + "    " + morto + "\n"
                        except:
                            str += '<b>(C)</b>    ' + line + "    " + vivo + "\n"
                        pass

                    elif line.startswith('#'):
                        line = line.strip('#')
                        person = wptools.page(line, lang='it', silent=True).get_wikidata()

                        try:
                            death = person.wikidata['death']

                            str += '<b>(VC)</b>    ' + line + "    " + morto + "\n"
                        except:
                            str += '<b>(VC)</b>    ' + line + "    " + vivo + "\n"
                        pass

                    else:

                        person = wptools.page(line, lang='it', silent=True).get_wikidata()
                        
                           
                        # print(person.wikidata['death'])

                        try:
                            death = person.wikidata['death']
                            str += line + "    " 
                            if line.startswith("Ibrahim al-Asiri"):
                                str += red_flag
                                break 
                            str += morto+"\n"
                        except:
                            str += line + "    " + vivo + "\n"
                        pass


            except:
                try:
                    if line.startswith('@'):
                        line = line.strip('@')
                        person = wptools.page(line, lang='en').get_wikidata()
                        # person._WIKIPROPS['P570'] = 'death'
                        #  person.get_wikidata()
                        # print(person.wikidata['death'])

                        try:
                            death = person.wikidata['death']
                            str += '<b>(C)</b>    ' + line + "    " + morto + "\n"
                        except:
                            str += '<b>(C)</b>    ' + line + "    " + vivo + "\n"
                        pass

                    elif line.startswith('#'):
                        line = line.strip('#')
                        person = wptools.page(line, lang='en', silent=True).get_wikidata()

                        try:
                            death = person.wikidata['death']

                            str += '<b>(VC)</b>    ' + line + "    " + morto + "\n"
                        except:
                            str += '<b>(VC)</b>    ' + line + "    " + vivo + "\n"
                        pass

                    else:

                        person = wptools.page(line, lang='en', silent=True).get_wikidata()

                        # print(person.wikidata['death'])

                        try:
                            death = person.wikidata['death']
                            str += line + "    " + morto + "\n"
                        except:
                            str += line + "    " + vivo + "\n"
                        pass
                except:
                    pass

    f.close()
    flag_stuck = True
    bot.send_message(chat_id=update.message.chat_id, text=str, parse_mode=ParseMode.HTML)
    

def isAlreadyDead(name):
    logfile = open('list_dead.txt', 'r')
    loglist = logfile.readlines()
    logfile.close()
    found = False
    for line in loglist:
        if name in line:
            found = True
    return found


@app.route('/')
def here():
    return "Ok!"


requests.packages.urllib3.disable_warnings()
#logging.getLogger('requests').setLevel(logging.CRITICAL)
today = datetime.today()
updater = Updater(token='370481887:AAGpoWac80QUDJ85otXra_VcaCFBpHVj4Eo')
dispatcher = updater.dispatcher
start_handler = CommandHandler('start', start)
news_handler = CommandHandler('news',news,pass_args=True)
add_points_handler = CommandHandler('add', add_points, pass_args=True)
list_handler = CommandHandler('list', list)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(add_points_handler)
dispatcher.add_handler(list_handler)
dispatcher.add_handler(news_handler)
updater.start_polling()
#updater.idle()
