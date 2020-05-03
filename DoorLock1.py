#!/usr/bin/env python

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import array as arr
import time
from pyfingerprint.pyfingerprint import PyFingerprint
from string import Template
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import threading
from datetime import datetime

"""
PyFingerprint
Copyright (C) 2015 Bastian Raschke <bastian.raschke@posteo.de>
All rights reserved.

"""
savedTag = arr.array('d', [150090968736, 96344208387])
reader = SimpleMFRC522()

print(savedTag[1])
print(savedTag[0])
entrance = 0
selected=0
push=0
sus=0
# LCD Pins
LCD_RS = 40
LCD_E  = 38
LCD_D4 = 37
LCD_D5 = 35
LCD_D6 = 33
LCD_D7 = 31
 
LCD_WIDTH = 16
LCD_CHR = True
LCD_CMD = False
 
LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0
 
# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

file=open("storedDta.txt","a+")
def initial():
  GPIO.setwarnings(False)
  GPIO.setmode(GPIO.BOARD)
  GPIO.setup(32,GPIO.OUT)
  GPIO.setup(29,GPIO.OUT)
  GPIO.setup(3,GPIO.OUT)
  GPIO.setup(36,GPIO.OUT)
  GPIO.setup(5,GPIO.IN,pull_up_down=GPIO.PUD_UP)
  GPIO.setup(7,GPIO.IN,pull_up_down=GPIO.PUD_UP)
  GPIO.output(36,0)
  GPIO.output(32,0)
  GPIO.output(29,0)
  GPIO.output(3,0)

def lcd_byte(bits, mode):
  # ??Send byte to data pins
  # bits = data
  # mode = True  for character
  #        False for command
 
  GPIO.output(LCD_RS, mode) # RS
 
  # High bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x10==0x10:
    GPIO.output(LCD_D4, True)
  if bits&0x20==0x20:
    GPIO.output(LCD_D5, True)
  if bits&0x40==0x40:
    GPIO.output(LCD_D6, True)
  if bits&0x80==0x80:
    GPIO.output(LCD_D7, True)
 
  # Toggle 'Enable' pin
  lcd_toggle_enable()
 
  # Low bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x01==0x01:
    GPIO.output(LCD_D4, True)
  if bits&0x02==0x02:
    GPIO.output(LCD_D5, True)
  if bits&0x04==0x04:
    GPIO.output(LCD_D6, True)
  if bits&0x08==0x08:
    GPIO.output(LCD_D7, True)
 
  # Toggle 'Enable' pin
  lcd_toggle_enable()
 
def lcd_toggle_enable():
  # Toggle enable
  time.sleep(E_DELAY)
  GPIO.output(LCD_E, True)
  time.sleep(E_PULSE)
  GPIO.output(LCD_E, False)
  time.sleep(E_DELAY)


def lcd_init():
	
  GPIO.setwarnings(False)
  GPIO.setmode(GPIO.BOARD)
  GPIO.setup(LCD_E, GPIO.OUT)  # E
  GPIO.setup(LCD_RS, GPIO.OUT) # RS
  GPIO.setup(LCD_D4, GPIO.OUT) # DB4
  GPIO.setup(LCD_D5, GPIO.OUT) # DB5
  GPIO.setup(LCD_D6, GPIO.OUT) # DB6
  GPIO.setup(LCD_D7, GPIO.OUT) # DB7
  # Initialise display
  lcd_byte(0x33,LCD_CMD) # 110011 Initialise
  lcd_byte(0x32,LCD_CMD) # 110010 Initialise
  lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
  lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off
  lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
  lcd_byte(0x01,LCD_CMD) # 000001 Clear display
  time.sleep(E_DELAY)
 
def lcd_string(message,line):
  # Send string to display
 
  message = message.ljust(LCD_WIDTH," ")
 
  lcd_byte(line, LCD_CMD)
 
  for i in range(LCD_WIDTH):
    lcd_byte(ord(message[i]),LCD_CHR)

try:
    f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)

    if ( f.verifyPassword() == False ):
        raise ValueError('The given fingerprint sensor password is wrong!')

except Exception as e:
    print('The fingerprint sensor could not be initialized!')
    print('Exception message: ' + str(e))
    exit(1)


def invalidate():
    global entrance
    print ("invalid")
    lcd_byte(0x01,LCD_CMD)
    lcd_string("ACCESS DENIED",LCD_LINE_1)
    if(entrance==3):
        lcd_string("system lock",LCD_LINE_2)
        GPIO.output(32,1)
        GPIO.output(3,1)
        time.sleep(3)
        GPIO.output(3,0)
        GPIO.output(32,0)
        if(entrance==3):
            sendMail()
            print("email sent")
            suspendMode()
            entrance=0
            print("end of suspend mode")
            lcd_string("place your tag",LCD_LINE_1)
            lcd_string("finger:press OK",LCD_LINE_2)
            time.sleep(1)

    else:
        GPIO.output(32,1)
        GPIO.output(3,1)
        time.sleep(.5)
        GPIO.output(3,0)
        time.sleep(.2)
        GPIO.output(3,1)
        time.sleep(.5)
        GPIO.output(3,0)
        time.sleep(.2)
        GPIO.output(3,1)
        time.sleep(.5)
        GPIO.output(3,0)
        GPIO.output(32,0)
    print(entrance)
        
def validate():
    global entrance
    print ("valid")
    lcd_byte(0x01,LCD_CMD)
    lcd_string("Welcome",LCD_LINE_1)
    lcd_string("ACCEPT",LCD_LINE_2)
    entrance=0
    GPIO.output(29,1)
    GPIO.output(36,1)
    GPIO.output(3,1)
    time.sleep(.1)
    GPIO.output(3,0)
    time.sleep(1)
    GPIO.output(3,1)
    time.sleep(.1)
    GPIO.output(3,0)
    GPIO.output(29,0)
    GPIO.output(36,0)
def readRFID():
  global entrance
  try:

      id, text = reader.read()
      if(sus==1):
          print("action not allowed")
      elif(entrance==3):
          print("action not allowed")
          lcd_string("ACCESS DENIED",LCD_LINE_1)
          lcd_string("system lock",LCD_LINE_2)
      elif int(id == savedTag[0]) | int(id == savedTag[1]):
          print ("valid")
          validate()
          now= datetime.now()
          file.write("tag id = %d  "" Time = %s valid\n"%(id ,now))
          lcd_byte(0x01,LCD_CMD)
          lcd_string("place your tag",LCD_LINE_1)
          lcd_string("finger:press OK",LCD_LINE_2)
      else:
          entrance=entrance+1
          print ("invalid")
          invalidate()
          now= datetime.now()
          file.write("tag id = %d  "" Time = %s invalid\n"%(id ,now))
          lcd_byte(0x01,LCD_CMD)
          lcd_string("place your tag",LCD_LINE_1)
          lcd_string("finger:press OK",LCD_LINE_2)
      print(id)
  finally:
      print('off')


def enrollFinger():
  try:
      print('Plce Ur Finger')
      lcd_byte(0x01,LCD_CMD)
      lcd_string("place valid",LCD_LINE_1)
      lcd_string("finger",LCD_LINE_2)
      while ( f.readImage() == False ):
          pass
      lcd_byte(0x01,LCD_CMD)
      f.convertImage(0x01)
      number = f.searchTemplate()
      position = number[0]
      accuracy = number[1]
      if ( position == -1 ):
          print('No match')
          lcd_string("ACCESS DENIED",LCD_LINE_1)
          lcd_string("try again",LCD_LINE_2)
          time.sleep(1)
      else:
          print('Position# ' + str(position))
          print('Accuracy: ' + str(accuracy))
          lcd_string("enroll mode",LCD_LINE_1)
          lcd_string("Start!",LCD_LINE_2)
          time.sleep(2)
          print('Place Ur Finger')
          lcd_byte(0x01,LCD_CMD)
          lcd_string("Place Ur Finger",LCD_LINE_1)
          while ( f.readImage() == False ):
              pass
          f.convertImage(0x01)
          print('convert')
          number = f.searchTemplate()
          position = number[0]
          lcd_byte(0x01,LCD_CMD)
          if ( position >= 0 ):
              print('position#' + str(position))

          else:
              print('Remove finger')
              time.sleep(2)

              print('Place the same finger again...')
              lcd_byte(0x01,LCD_CMD)
              lcd_string("place the same",LCD_LINE_1)
              lcd_string("finger",LCD_LINE_2)
              while ( f.readImage() == False ):
                  pass
              lcd_byte(0x01,LCD_CMD)
              f.convertImage(0x02)
              if ( f.compareCharacteristics() == 0 ):
                  print('not match')
                  lcd_byte(0x01,LCD_CMD)
                  lcd_string("Not match!",LCD_LINE_1)
                  lcd_string("Try again",LCD_LINE_2)
                  time.sleep(3)
                  lcd_byte(0x01,LCD_CMD)
              else: 
                  f.createTemplate()
                  position = f.storeTemplate()
                  print('Finger enrolled successfully!')
                  print('New template position#' + str(position))
                  lcd_byte(0x01,LCD_CMD)
                  lcd_string("new finger added",LCD_LINE_1)
                  time.sleep(3)
      lcd_byte(0x01,LCD_CMD)
      lcd_string("place your tag",LCD_LINE_1)
      lcd_string("finger:press OK",LCD_LINE_2)

  except Exception as e:
      print('Operation failed!')
      print('Exception message: ' + str(e))
      exit(1)

def deleteFinger():
  try:
      print('Waiting for finger...')
      lcd_byte(0x01,LCD_CMD)
      lcd_string("place finger",LCD_LINE_1)
      while ( f.readImage() == False ):
          pass
      lcd_byte(0x01,LCD_CMD)
      f.convertImage(0x01)
      number = f.searchTemplate()
      position = number[0]
      accuracy = number[1]

      if ( position == -1 ):
          print('No match')
          lcd_string("No Match!",LCD_LINE_1)
          time.sleep(1)
      else:
          print('position#' + str(position))
          print('accuracy' + str(accuracy))
          position = int(position)

          if ( f.deleteTemplate(position) == True ):
              print('Template deleted!')
              lcd_byte(0x01,LCD_CMD)
              lcd_string("Founded",LCD_LINE_1)
              lcd_string("Deleted",LCD_LINE_2)

      lcd_byte(0x01,LCD_CMD)
      lcd_string("place your tag",LCD_LINE_1)
      lcd_string("finger:press OK",LCD_LINE_2)

  except Exception as e:
      print('Operation failed!')
      print('Exception message: ' + str(e))
      exit(1)

def searchFinger():
  global entrance
  try:
      print('place finger')
      lcd_byte(0x01,LCD_CMD)
      lcd_string("Place Ur Finger",LCD_LINE_1)
      while ( f.readImage() == False ):
          pass
      lcd_byte(0x01,LCD_CMD)
      f.convertImage(0x01)
      number = f.searchTemplate()
      position = number[0]
      accuracy = number[1]
      if ( position == -1 ):
          print('No match')
          entrance=entrance+1
          invalidate()
          now= datetime.now()
          file.write(" finger request"" Time = %s invalid \n" %now)
      else:
          print('Position#' + str(position))
          print('Accuracy: ' + str(accuracy))
          validate()
          now= datetime.now()
          file.write("finger char place = %d  "" Time = %s valid\n"%(position ,now))
      lcd_byte(0x01,LCD_CMD)
      lcd_string("place your tag",LCD_LINE_1)
      lcd_string("finger:press OK",LCD_LINE_2)

  except Exception as e:
      print('Operation failed!')
      print('Exception message: ' + str(e))
      exit(1)

def switch2(Channel):
  print('switch2')
  global selected
  global sus
  print(sus)
  if(sus==1):
      print("action not allowed")
  elif(entrance==3):
      print("action not allowed")
  elif(selected == 0):
      lcd_string("finger:enroll",LCD_LINE_2)
      selected=1
  elif(selected == 1):
      lcd_string("finger:delete",LCD_LINE_2)
      selected=2
  elif(selected ==2):
      lcd_string("finger:press ok",LCD_LINE_2)
      selected=0

def switch1(channel):
  global selected
  global sus
  print('switch1')
  print(sus)
  if(sus==1):
      print("action not allowed")
  elif(entrance==3):
      print("action not allowed")
      lcd_string("ACCESS DENIED",LCD_LINE_1)
      lcd_string("system lock",LCD_LINE_2)
  elif(selected == 0):
      print('search')
      selected=0
      searchFinger()
  elif(selected == 1):
      print('enroll')
      selected=0
      enrollFinger()
  elif(selected == 2):
      selected=0
      print('delete')
      selected=0
      deleteFinger()

def getContacts(file):
    
    names = []
    emails = []
    with open(file, mode='r', encoding='utf-8') as contacts:
        for each in contacts:
            names.append(each.split()[0])
            emails.append(each.split()[1])
    return names, emails

def readMessage(file):
    
    with open(file, mode='r', encoding='utf-8') as template:
        content = template.read()
    return Template(content)

def sendMail():
    names, emails = getContacts('informations.txt')
    message = readMessage('message.txt')

    s = smtplib.SMTP(host='smtp.gmail.com', port=587)
    s.starttls()
    s.login('***','***')
    for name, email in zip(names, emails):
        msg = MIMEMultipart()
        message = message.substitute(PERSON_NAME=name.title())
        msg['From']='doorlockproject34@gmail.com'
        msg['To']=email
        msg['Subject']="DoorLock Security Syastem"
        msg.attach(MIMEText(message, 'plain'))
        s.send_message(msg)
        del msg
        print(message)
    s.quit()

GPIO.setup(5,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(7,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(5,GPIO.FALLING,callback=switch1,bouncetime=500)
GPIO.add_event_detect(7,GPIO.FALLING,callback=switch2,bouncetime=500)

def suspendMode():
  global sus
  sus=1
  print("sus start")
  time.sleep(60)
  print("sus end")
  sus=0

def updateTime():
    global entrance
    entrance=0
    print(entrance)

lcd_init()
initial()

def every(delay,task):
  global sus
  while True:
      time.sleep(delay)
      if(entrance==1):
          time.sleep(delay)
      if(entrance==2):
          time.sleep(delay)
      if(entrance==3):
          time.sleep(delay)
      else:
          pass
      try:
          if(entrance!=0 & sus==0):
              task()
      except Exception:
          traceback.print_exc()

t=threading.Thread(target=lambda: every(500,updateTime))
t.start()

lcd_init()
initial()
lcd_byte(0x01,LCD_CMD)
lcd_string("place your tag",LCD_LINE_1)
lcd_string("finger:press OK",LCD_LINE_2)

try:
    while True:
        if(sus==0):
            readRFID()
            lcd_init()
            initial()
            lcd_byte(0x01,LCD_CMD)
            lcd_string("place your tag",LCD_LINE_1)
            lcd_string("finger:press OK",LCD_LINE_2)
        else:
            lcd_string("ACCESS DENIED",LCD_LINE_1)
            lcd_string("system lock",LCD_LINE_2)

except KeyboardInterrupt:
  lcd_byte(0x01,LCD_CMD)
  GPIO.cleanup()
  file.close()
GPIO.cleanup()
