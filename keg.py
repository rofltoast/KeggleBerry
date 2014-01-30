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
from adabot import *
from seekrits import *

t = Twitter( auth=OAuth(OAUTH_TOKEN, OAUTH_SECRET, CONSUMER_KEY, CONSUMER_SECRET) )

boardRevision = GPIO.RPI_REVISION
GPIO.setmode(GPIO.BCM) # use real GPIO numbering
GPIO.setup(22,GPIO.IN, pull_up_down=GPIO.PUD_UP)#Set software pullup on pin 22
GPIO.setup(23,GPIO.IN, pull_up_down=GPIO.PUD_UP)#Set software pullup on pin 23

# set up pygame
pygame.init()

# set up the window
VIEW_WIDTH = 1248
VIEW_HEIGHT = 688
BEER1 = 'Pale Ale'
BEER2 = 'Stout'
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

# set up the background
# bg = pygame.image.load('beer-bg.png')

# set up the adabots
back_bot = adabot(361, 151, 361, 725)
middle_bot = adabot(310, 339, 310, 825)
front_bot = adabot(220, 527, 220, 888)

def renderThings(flowMeter, flowMeter2, tweet, windowSurface, basicFont):
  # Clear the screen
  windowSurface.fill(BLACK)#No background image; black fill
  
  # draw the adabots
  back_bot.update()
  windowSurface.blit(back_bot.image,(back_bot.x, back_bot.y))
  middle_bot.update()
  windowSurface.blit(middle_bot.image,(middle_bot.x, middle_bot.y))
  front_bot.update()
  windowSurface.blit(front_bot.image,(front_bot.x, front_bot.y))

  # Draw Beer Name Left Keg
  text = beerFont.render("Stout", True, WHITE, BLACK)
  textRect = text.get_rect()
  windowSurface.blit(text, (windowInfo.current_w - textRect.width - 80, 0))

  # Draw Beer Name Right Keg
  text = beerFont.render("Pale Ale", True, WHITE, BLACK)
  textRect = text.get_rect()
  windowSurface.blit(text, (80,0))

  # Draw Ammt Poured
  text = basicFont.render("CURRENT:", True, WHITE, BLACK)
  textRect = text.get_rect()
  windowSurface.blit(text, (80,220))
  text = basicFont.render(flowMeter2.getFormattedThisPour(), True, WHITE, BLACK)
  textRect = text.get_rect()
  windowSurface.blit(text, (80,220+LINEHEIGHT))
  text = basicFont.render(flowMeter2.getFormattedTotalPour(), True, WHITE, BLACK)
  textRect = text.get_rect()
  windowSurface.blit(text, (80, 220+(2*(LINEHEIGHT+5))))

  # Draw Ammt Poured Total
  text = basicFont.render("TOTAL:", True, WHITE, BLACK)
  textRect = text.get_rect()
  windowSurface.blit(text, (windowInfo.current_w - textRect.width - 80, 220))
  text = basicFont.render(flowMeter.getFormattedThisPour(), True, WHITE, BLACK)
  textRect = text.get_rect()
  windowSurface.blit(text, (windowInfo.current_w - textRect.width - 80, 220 + LINEHEIGHT))
  text = basicFont.render(flowMeter.getFormattedTotalPour(), True, WHITE, BLACK)
  textRect = text.get_rect()
  windowSurface.blit(text, (windowInfo.current_w - textRect.width - 80, 220 + (2 * (LINEHEIGHT+5))))

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
    tweet = "Someone just poured " + fm.getFormattedThisPour() + " of " + BEER1 + " from the keg!" 
    ######insert SQL push here(thisPour)
    fm.thisPour = 0.0
    tweetPour(tweet)
 
  if (fm2.thisPour > 0.05 and currentTime - fm2.lastClick > 2000): # 2 seconds of inactivity causes a tweet
    tweet = "Someone just poured " + fm2.getFormattedThisPour() + " of " + BEER2 + " from the keg!"
    ######insert SQL push here(thisPour)
    fm2.thisPour = 0.0
    tweetPour(tweet)

  # Update the screen
  renderThings(fm, fm2, tweet, windowSurface, basicFont)
