import time
from info import *

#Init flowmeter class
class FlowMeter():
  PINTS_IN_A_LITER = 2.11338
  SECONDS_IN_A_MINUTE = 60
  MS_IN_A_SECOND = 1000.0
  beerConf = ''
  enabled = True
  clicks = 0
  lastClick = 0
  clickDelta = 0
  hertz = 0.0
  flow = 0 # in Liters per second
  thisPour = 0.0 # in Liters
  totalPour = 0.0 # in Liters
  bLevel = 40.0
  beerCal = 0
  beer = ''

  def __init__(self, beerConf):
    self.beerConf = beerConf #Receive beer parameter (to delineate the correct beer/keg)
    self.clicks = 0
    self.lastClick = int(time.time() * FlowMeter.MS_IN_A_SECOND)
    self.clickDelta = 0
    self.hertz = 0.0
    self.flow = 0.0
    self.thisPour = 0.0
    self.totalPour = 0.0
    self.enabled = True
    
    #Grab the correct keg/beer properties
    if beerConf == 'left':
      self.beer = 'left'
      self.bLevel = Info.beerTotalL
      self.beerCal = Info.beerCalL
    else:
      self.beer = 'right'
      self.bLevel = Info.beerTotalR
      self.beerCal = Info.beerCalR
      
  def update(self, currentTime):
    self.clicks += 1
    # get the time delta
    self.clickDelta = max((currentTime - self.lastClick), 1)
    # calculate the instantaneous speed
    if (self.enabled == True and self.clickDelta < 1000):
      self.hertz = FlowMeter.MS_IN_A_SECOND / self.clickDelta
      self.flow = self.hertz / (FlowMeter.SECONDS_IN_A_MINUTE * 7.5)  # In Liters per second
      instPour = self.flow * (self.clickDelta / FlowMeter.MS_IN_A_SECOND)  
      self.thisPour += instPour
      self.totalPour += instPour
    # Update the last click
    self.lastClick = currentTime

  def getFormattedClickDelta(self):
     return str(self.clickDelta) + ' ms'
  
  def getFormattedHertz(self):
     return str(round(self.hertz,3)) + ' Hz'
  
  #Get flow per second
  def getFormattedFlow(self):
    return str(round(self.flow * FlowMeter.PINTS_IN_A_LITER, 3)) + ' pints/s'
      
  #Get current flow reading
  def getFormattedThisPour(self):
    return str(round(self.thisPour * FlowMeter.PINTS_IN_A_LITER, 3)) + ' pints'
      
  #Get/Update overall total pour of keg
  def getFormattedTotalPour(self):
    return str(round(self.totalPour * FlowMeter.PINTS_IN_A_LITER, 3)) + ' pints'
      
  #Get/Update remaining beer
  def getFormattedRemaining(self):
    return str(round(self.bLevel - self.totalPour * FlowMeter.PINTS_IN_A_LITER, 2)) + ' pints remaining'
    
  #Display calories for current pour
  def getFormattedCal(self):
    return str(round((self.thisPour * FlowMeter.PINTS_IN_A_LITER) * self.beerCal, 2)) + ' Calories'
