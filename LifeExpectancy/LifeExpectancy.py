#!/usr/bin/env python
from LEUtils import LifeExpectancy, Person
from LECache import LECache
from LEDataStore import LEDataStore

import requests
import sys
import time
import datetime

banner = """
********************************************
*****      Life Expectancy App         *****
The Life Expectancy App calculates your life 
expectancy according to the World Population 
API: http://api.population.io
based on date of birth, country of origin
and gender.
********************************************
"""

def lifeExpectancyInput():
   name = raw_input( "Name: " )
   country = raw_input( "Country: " )
   dob = raw_input( "Date of Birth: (YYYY-MM-DD) " )
   gender = raw_input( "Gender: (Male|Female) " )

   try:
      le = LifeExpectancy( country, dob, gender, datetime.date.today() )
   except Exception as e:
      return( False, " Couldn't process your request because %s" % e.message )

   return ( True, Person( name, le ) )

def lifeExpectancyOutput( name, delta ):

   print ( "\n%s's life expectancy is: %s years, %s months, %s weeks and %s days" % 
           ( name, delta.years, delta.months, delta.days / 7, delta.days % 7 ) )


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
      return ( False, resp.json()[ 'detail' ] )

   import pdb
   pdb.set_trace()
   return ( True, resp.json()[ 'remaining_life_expectancy' ] )

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
      return ( False, resp.json()[ 'detail' ] )

   return ( True, resp.json()[ 'total_life_expectancy' ] )

def getCountriesFromWPA():

   url = "http://api.population.io/1.0/countries"
   try:
      resp = requests.get( url=url )
   except Exception as e:
      # no connection to the internet
      return []
   if not resp.ok:
      return []
   return resp.json()[ 'countries' ]

def checkCountry( country, countries ):
   '''
   Helper method checks if country is in the cached list of countries.
   Prompts user to print the list of countries if the country passed
   doesn't exist.
   '''
   
   if country in countries:
      return True

   print "Country %s is invalid" % country
   showCountries = raw_input( "Do you want to see a list "
                              "of valid countries? [yes|No] " )
   if showCountries.lower().startswith( 'y' ):
      print ",".join( countries )
   return False

def exit():
   '''
   Helper method. Asks user to continue using the App 
   after having retrieved information for a single user
   '''

   exit = raw_input( "\nExit? [yes|No] " )
   if exit.lower().startswith( 'y' ):
      return True
   return False

def lifeExpectancy():

   global banner
   print banner

   # preemptively get countries from WPA
   countries = getCountriesFromWPA()
   # create a cache of 10 elements
   cache = LECache( 10 )
   # create a backend data storage system
   dataStorage = LEDataStore()

   while True:
      # parse user input
      ( v, p ) = lifeExpectancyInput()
      if not v:
         print p
         if exit():
            sys.exit( 0 )
         continue

      # check the country, if invalid allow user to print list of countries
      if not checkCountry( p.lifeExp().country(), countries ):
         if exit():
            sys.exit( 0 )
         continue

      # input is valid, fulfill request

      # first check in the cache
      cached = cache.get( p.lifeExp() )
      if cached:
         lifeExpectancyOutput( p.name(), cached.lifeExpectancy() )
         if exit():
            sys.exit( 0 )
         continue

      # check the data storage
      delta = dataStorage.fetchLifeExpectancy( p.lifeExp() )
      if delta:
         p.lifeExp().setLifeExp( delta )
         lifeExpectancyOutput( p.name(), p.lifeExp().lifeExpectancy() )
         if exit():
            sys.exit( 0 )
         # store the latest query in the cache
         cache.put( p.lifeExp() )
         continue

      # if we don't have the life expectancy query locally
      # get the life expectancy from the web
      # there are 2 cases:
      # 1) the dob is in the future, calculate an expected life expectancy
      #    using the total life expectancy API
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
         if exit():
            sys.exit( 0 )
         continue

      # takes the float value retrieved from WPA and
      # calculates the life expectancy
      p.lifeExp().calculateLifeExp( lifeExpFloat )
      # prints the life expectancy to the user
      lifeExpectancyOutput( p.name(), p.lifeExp().lifeExpectancy() )
      if exit():
         sys.exit( 0 )
      # add the life expectancy calculation to both the cache and the dataStorage
      cache.put( p.lifeExp() )
      dataStorage.addLifeExpectancy( p.lifeExp() )

if __name__ == "__main__":
   lifeExpectancy()
