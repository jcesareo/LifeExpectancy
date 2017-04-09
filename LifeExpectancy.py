#!/usr/bin/env python
from LEUtils import LifeExpectancy, Person
from LECache import LECache
from LEBackEnd import LEDataStorage

import requests
import sys
import time
import datetime

banner = """
********************************************
*****      Life Expectancy App         *****
Given your date of birth, country and gender
it calculates your life expectancy using
data from the World Population API:
http://api.population.io
********************************************
"""

def lifeExpectancyInput():
   name = raw_input( "Enter your name: " )
   country = raw_input( "What country are you from? " )
   dob = raw_input( "What is your date of birth? (YYYY-MM-DD) " )
   gender = raw_input( "What is your gender? [Male|Female] " )

   try:
      le = LifeExpectancy( country, dob, gender, datetime.date.today() )
   except Exception as e:
      return( False, " Couldn't process your request because %s" % e.message )

   return ( True, Person( name, le ) )

def lifeExpectancyOutput( name, delta ):

   print ( "\n%s's Life Expectancy:\nDays remaining: %s\nWeeks remaining: %s\n"
           "Months remaining: %s\nYears remaining: %s" %
           ( name, delta.days % 7, delta.days / 7, delta.months,
             delta.years ) )


def getRemainingLifeExpectancyFromWPA( lifeExp ):
   '''
   Returns the total life expectancy give an object of class LifeExpectancy
   Assumes the lifeExp has an age that is not zero
   '''

   remLifeExpUrl = "http://api.population.io/1.0/life-expectancy/remaining"
   paramsUrl = "/%s/%s/%s/%s" % ( lifeExp.gender(), lifeExp.country(),
                                  lifeExp.date().isoformat(),
                                  lifeExp.age() )
   try:
      resp = requests.get( url=remLifeExpUrl + paramsUrl )
   except Exception as e:
      # no connection to the internet
      return ( False, "Can't connect to the Internet" )

   if not resp.ok:
      return ( False, resp.json[ 'detail' ] )

   return ( True, resp.json[ 'remaining_life_expectancy' ] )

def getTotalLifeExpectancyFromWPA( lifeExp ):
   '''
   Get an estimated life expectancy based solely on date of birth
   Assumes the date of birth is in the future
   '''

   totalLifeExpUrl = "http://api.population.io/1.0/life-expectancy/total"
   paramsUrl = "/%s/%s/%s" % ( lifeExp.gender(), lifeExp.country(),
                                  lifeExp.dob().isoformat() )
   try:
      resp = requests.get( url= totalLifeExpUrl + paramsUrl )
   except Exception as e:
      # no connection to the internet
      return ( False, "Can't connect to the Internet" )
   if not resp.ok:
      return ( False, resp.json[ 'detail' ] )

   return ( True, resp.json[ 'total_life_expectancy' ] )

def getCountriesFromWPA():

   url = "http://api.population.io/1.0/countries"
   try:
      resp = requests.get( url=url )
   except Exception as e:
      # no connection to the internet
      return []
   if not resp.ok:
      return []
   return resp.json[ 'countries' ]

def checkCountry( country, countries ):

   if country in countries:
      return True

   print "Country %s is invalid" % country
   showCountries = raw_input( "Do you want to see a list "
                              "of valid countries? [yes|No] " )
   if showCountries.lower().startswith( 'y' ):
      print ",".join( countries )
   return False

def askContinue():
   cont = raw_input( "\nTry again? [yes|No] " )
   if not cont.lower().startswith( 'y' ):
      return False
   return True

def lifeExpectancy():

   print banner
   countries = getCountriesFromWPA()
   cache = LECache( 10 )
   dataStorage = LEDataStorage()

   while True:
      ( v, p ) = lifeExpectancyInput()
      if not v:
         print p
         if not askContinue():
            sys.exit( 0 )
         continue

      # check the country, allow user to print list of countries
      if not checkCountry( p.lifeExp().country(), countries ):
         if not askContinue():
            sys.exit( 0 )
         continue

      # input is valid, let's fulfill the request

      # first check in the cache
      cached = cache.get( p.lifeExp() )
      if cached:
         lifeExpectancyOutput( p.name(), cached.lifeExpectancy() )
         if not askContinue():
            sys.exit( 0 )
         continue

      # otherwise check in the data storage for the lifeExp
      delta = dataStorage.fetchLifeExpectancy( p.lifeExp() )
      if delta:
         p.lifeExp().setLifeExp( delta )
         lifeExpectancyOutput( p.name(), p.lifeExp().lifeExpectancy() )
         if not askContinue():
            sys.exit( 0 )
         # store the latest query in the cache
         cache.put( p.lifeExp() )
         continue

      # if we don't have it anywhere, get the life expectancy from the web
      # there are 2 cases:
      # 1) the dob is in the future, calculate an expected life expectancy
      #    using total life expectancy API
      # 2) the dob is in the past, calculate the expected life expectancy
      #    using the remaining life expectancy API

      if p.lifeExp().dob() > datetime.date.today():
         # set the date as the date of birth so that we will not recalculate
         # it until the dob has passed
         p.lifeExp().setDate( p.lifeExp().dob() )
         ( v, lifeExpFloat ) = getTotalLifeExpectancyFromWPA( p.lifeExp() )
      else:
         ( v, lifeExpFloat ) = getRemainingLifeExpectancyFromWPA( p.lifeExp() )
         
      if not v:
         print lifeExpFloat
         if not askContinue():
            sys.exit( 0 )
         continue

      p.lifeExp().calculateLifeExp( lifeExpFloat )
      lifeExpectancyOutput( p.name(), p.lifeExp().lifeExpectancy() )
      if not askContinue():
         sys.exit( 0 )
      # add the lifeExp we calculated to both the cache and the dataStorage
      cache.put( p.lifeExp() )
      dataStorage.addLifeExpectancy( p.lifeExp() )

if __name__ == "__main__":
   lifeExpectancy()