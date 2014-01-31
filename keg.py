#!/usr/bin/python
import os
import time
import math
import logging
import pygame, sys
from pygame.locals import *
import RPi.GPIO as GPIO
from twitter import *
from flowmeter import *
from seekrits import *

t = Twitter( auth=OAuth(OAUTH_TOKEN, OAUTH_SECRET, CONSUMER_KEY, CONSUMER_SECRET) )

boardRevision = GPIO.RPI_REVISION
GPIO.setmode(GPIO.BCM) # use real GPIO numbering
GPIO.setup(22,GPIO.IN, pull_up_down=GPIO.PUD_UP)#Set software pullup on pin 22
GPIO.setup(23,GPIO.IN, pull_up_down=GPIO.PUD_UP)#Set software pullup on pin 23

# set up pygame
pygame.init()

# set up the window
VIEW_WIDTH = 1280
VIEW_HEIGHT = 800
LEFTBEER = 'Stout'
RIGHTBEER = 'Pale Ale'
pygame.display.set_caption('KeggleBerry')

# hide the mouse
pygame.mouse.set_visible(False)

# set up the flow meters
fm = FlowMeter('Pints')#Default measurement is pints, swtich to 'metric' for L
fm2 = FlowMeter('Pints')#Default measurement is pints, swtich to 'metric' for L
tweet = ''

# set up the colors
BLACK = (0,0,0)
WHITE = (255,255,255)

# set up the window surface
windowSurface = pygame.display.set_mode((VIEW_WIDTH,VIEW_HEIGHT), FULLSCREEN, 32) 
windowInfo = pygame.display.Info()
FONTSIZE = 35
LINEHEIGHT = 28
beerFONTSIZE = 98
basicFont = pygame.font.SysFont(None, FONTSIZE)
beerFont = pygame.font.SysFont(None, beerFONTSIZE)

def renderThings(flowMeter, flowMeter2, tweet, windowSurface, basicFont):
  # Clear the screen
  windowSurface.fill(BLACK)#No background image; black fill
  
  mug = pygame.image.load('Mug.png')
  windowSurface.blit(mug, (397,200))
  
  leftkeg = pygame.image.load('corny.png')
  windowSurface.blit(leftkeg, (0,70))
  
  rightkeg = pygame.image.load('corny.png')
  windowSurface.blit(rightkeg, (946,70))
  
  # Draw Beer Name Left Keg
  text = beerFont.render(LEFTBEER, True, WHITE, BLACK)
  textRect = text.get_rect()
  windowSurface.blit(text, (windowInfo.current_w - textRect.width - 80, 0))

  # Draw Beer Name Right Keg
  text = beerFont.render(RIGHTBEER, True, WHITE, BLACK)
  textRect = text.get_rect()
  windowSurface.blit(text, (80,0))
  
  if (fm.enabled == True):
    text = basicFont.render(flowMeter.getFormattedThisPour(), True, WHITE, BLACK)
    textRect = text.get_rect()
    windowSurface.blit(text, (550,200+LINEHEIGHT))
  if (fm2.enabled == True):
    text = basicFont.render(flowMeter2.getFormattedThisPour(), True, WHITE, BLACK)
    textRect = text.get_rect()
    windowSurface.blit(text, (550,200+LINEHEIGHT))
  
  
  #########LEFT KEG#########
  ## Draw Ammt Poured 
  #text = basicFont.render("CURRENT:", True, WHITE, BLACK)
  #textRect = text.get_rect()
  #windowSurface.blit(text, (80,220))
  #text = basicFont.render(flowMeter2.getFormattedThisPour(), True, WHITE, BLACK)
  #textRect = text.get_rect()
  #windowSurface.blit(text, (80,220+LINEHEIGHT))
  ## Draw price
  #text = basicFont.render(flowMeter2.getFormattedPrice(), True, WHITE, BLACK)
  #textRect = text.get_rect()
  #windowSurface.blit(text, (80,250+LINEHEIGHT))
  ## Draw calories
  #text = basicFont.render(flowMeter2.getFormattedCal(), True, WHITE, BLACK)
  #textRect = text.get_rect()
  #windowSurface.blit(text, (80,280+LINEHEIGHT))
  # Draw remaining
  text = basicFont.render(flowMeter2.getFormattedRemaining(), True, WHITE, BLACK)
  textRect = text.get_rect()
  windowSurface.blit(text, (50, 765))

  #########RIGHT KEG#########
  # Draw Ammt Poured Total
  #text = basicFont.render("CURRENT:", True, WHITE, BLACK)
  #textRect = text.get_rect()
  #windowSurface.blit(text, (windowInfo.current_w - textRect.width - 80, 220))
  #text = basicFont.render(flowMeter.getFormattedThisPour(), True, WHITE, BLACK)
  #textRect = text.get_rect()
  #windowSurface.blit(text, (windowInfo.current_w - textRect.width - 80, 220 + LINEHEIGHT))
  ## Draw price
  #text = basicFont.render(flowMeter.getFormattedPrice(), True, WHITE, BLACK)
  #textRect = text.get_rect()
  #windowSurface.blit(text, (windowInfo.current_w - textRect.width - 80, 250 + LINEHEIGHT))
  ## Draw calories
  #text = basicFont.render(flowMeter.getFormattedCal(), True, WHITE, BLACK)
  #textRect = text.get_rect()
  #windowSurface.blit(text, (windowInfo.current_w - textRect.width - 80, 280 + LINEHEIGHT))
  # Draw remaining
  text = basicFont.render(flowMeter.getFormattedRemaining(), True, WHITE, BLACK)
  textRect = text.get_rect()
  windowSurface.blit(text, (windowInfo.current_w - textRect.width - 55, 765))

  # Display everything
  pygame.display.flip()

# Beer, on Pin 22.
def doAClick(channel):
  currentTime = int(time.time() * FlowMeter.MS_IN_A_SECOND)
  if fm.enabled == True:
    fm.update(currentTime)

# Beer, on Pin 23.
def doAClick2(channel):
  currentTime = int(time.time() * FlowMeter.MS_IN_A_SECOND)
  if fm2.enabled == True:
    fm2.update(currentTime)

def tweetPour(theTweet):
  try:
    t.statuses.update(status=theTweet)
  except:
    logging.warning('Error tweeting: ' + theTweet + "\n")

GPIO.add_event_detect(22, GPIO.RISING, callback=doAClick, bouncetime=20)#Set 'rising edge' detection on pin 22
GPIO.add_event_detect(23, GPIO.RISING, callback=doAClick2, bouncetime=20)#Set 'rising edge' detection on pin 23

# main loop
while True:
  # Handle keyboard events
  for event in pygame.event.get():
    if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
      GPIO.cleanup()
      pygame.quit()
      sys.exit()
  
  currentTime = int(time.time() * FlowMeter.MS_IN_A_SECOND)
  
  if (fm.thisPour > 0.05 and currentTime - fm.lastClick > 2000): # 2 seconds of inactivity causes a tweet
    tweet = "Someone just poured " + fm.getFormattedThisPour() + " of " + LEFTBEER + " from the keg! ($" + fm.getFormattedPrice()
    ######insert SQL push here(thisPour)
    fm.thisPour = 0.0
    tweetPour(tweet)
 
  if (fm2.thisPour > 0.05 and currentTime - fm2.lastClick > 2000): # 2 seconds of inactivity causes a tweet
    tweet = "Someone just poured " + fm2.getFormattedThisPour() + " of " + RIGHTBEER + " from the keg! ($" + fm2.getFormattedPrice() + ")"
    ######insert SQL push here(thisPour)
    fm2.thisPour = 0.0
    tweetPour(tweet)

  # Update the screen
  renderThings(fm, fm2, tweet, windowSurface, basicFont)
