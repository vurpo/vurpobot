#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import telegram
import subprocess
import re
import requests,json
import traceback
import sys


"""
Changelog:
version 1: /vurpobot command
version 2: /fortune command and sed-style text replacement
version 3: /hacklab status command
version 4: error handling
"""

VERSION = "4"

print("Connecting to Telegram...")
bot = telegram.Bot(token="175897430:AAG_qwLc_vr_-Y8R7wNvXFc5HQpG2xvHB0g")
print("Connected.")

LAST_UPDATE_ID = None
receivedUpdates = []

commandSuccessful = True

try:
  #print([repl(i) for i in bot.getUpdates()])
  LAST_UPDATE_ID = bot.getUpdates()[-1].update_id
except IndexError:
  LAST_UPDATE_ID = None

def getChatName(update):
  updateDict = update.to_dict()
  print(updateDict)
  if updateDict['message']['chat']['type'] == "group":
    return updateDict['message']['chat']['title']
  elif updateDict['message']['chat']['type'] == "private":
    return "{0}{1}{2}".format(updateDict['message']['chat']['first_name'], (" " if (len(updateDict['message']['chat']['last_name']) > 0) else ""), updateDict['message']['chat']['last_name'])
  return ""

print("Starting main loop")
while True:
  try:
    for update in bot.getUpdates(offset=LAST_UPDATE_ID, timeout=10):
      #print update
      lastUpdate = update
      chat_id = update.message.chat_id
      message = update.message.text#.encode('utf-8') 
      if message == "/vurpobot":
        commandSuccessful = false
        print("Sending intro message")
        bot.sendMessage(chat_id=chat_id, text="I am but a simple bot, tending to my scripts. v{}".format(VERSION))
        commandSuccessful = true
      elif message == "/camera 1" and chat_id == 49506617:
        commandSuccessful = false
        print("Sending camera 1 picture")
        bot.sendChatAction(chat_id=49506617, action=telegram.ChatAction.UPLOAD_PHOTO)
        #subprocess.Popen(["fswebcam", "--no-banner", "-r", "320x240", "--jpeg", "100", "-D", "1", "-S", "9", "latest.jpg"]).wait()
        subprocess.Popen(["ffmpeg", "-y", "-f", "video4linux2", "-s", "640x480", "-i", "/dev/video0", "-ss", "0:0:2", "-frames", "1", "latest1.jpg"]).wait()
        pic = open("latest1.jpg", "rb")
        bot.sendPhoto(chat_id=49506617, photo=pic)
        pic.close()
        commandSuccessful = true
      elif message == "/camera 2" and chat_id == 49506617:
        commandSuccessful = false
        print("Sending camera 2 picture")
        bot.sendChatAction(chat_id=49506617, action=telegram.ChatAction.UPLOAD_PHOTO)
        #subprocess.Popen(["fswebcam", "--no-banner", "-r", "320x240", "--jpeg", "100", "-D", "1", "-S", "9", "latest.jpg"]).wait()
        subprocess.Popen(["ffmpeg", "-y", "-f", "video4linux2", "-s", "640x480", "-i", "/dev/video1", "-ss", "0:0:2", "-frames", "1", "latest2.jpg"]).wait()
        pic = open("latest2.jpg", "rb")
        bot.sendPhoto(chat_id=49506617, photo=pic)
        pic.close()
        commandSuccessful = true
      elif re.search("^/speak .+$", message) != None:
        commandSuccessful = false
        match = re.search("^/speak (.+)$", message)
        subprocess.Popen(["./speak_to_opus.sh", match.groups()[0]]).wait()
        speak = open("output.ogg", "rb")
        bot.sendVoice(chat_id=chat_id, voice=speak)
        speak.close()
        commandSuccessful = true
      else:
        receivedUpdates.append(update)
        print(update)
        #print receivedUpdates
     
      LAST_UPDATE_ID = update.update_id+1
  except KeyboardInterrupt:
    print("Caught KeyboardInterrupt, exiting")
    sys.exit(0)
  except:
    err = traceback.format_exc()
    print("Caught exception, reporting\n***\n{}***".format(err))  
    try:
      if not commandSuccessful:
        bot.sendMessage(chat_id=49506617, text="*Error in chat \"{0}\":*\n```\n{1}\n```".format(getChatName(lastUpdate), err), parse_mode=telegram.ParseMode.MARKDOWN) #Hardcoded chat id
        bot.sendMessage(chat_id=chat_id, text="Error processing command! Reported to vurpo.")
      else:
        bot.sendMessage(chat_id=49506617, text="*Error in mainloop:*\n```\n{1}\n```".format( err), parse_mode=telegram.ParseMode.MARKDOWN) #Hardcoded chat id
    except:
      print("Exception caught while reporting exception")
      print(traceback.format_exc())
  finally:
    LAST_UPDATE_ID = update.update_id+1
