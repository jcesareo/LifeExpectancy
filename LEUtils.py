#!/usr/bin/env python
import datetime
from dateutil.relativedelta import relativedelta as relativedelta

class LifeExpectancyException( Exception ):
   pass


def isDate( d ):
   '''
   Verifies d can be turned into a date,
   returns tuple with verification boolean + date/string
   '''
   
   # d has to be a datetime or a string in ISO format
   if isinstance( d, str ):
      try:
         d = datetime.datetime.strptime( d, '%Y-%m-%d' )
         d = datetime.date( d.year, d.month, d.day )
      except Exception:
         return ( False, "date has to be in format "
            "YYYY-MM-DD" )
   elif not isinstance( d, datetime.date ):
      return ( False, "date %s is incorrect type %s"
               % ( d, d.__class__ ) )

   return ( True, d )

   
class LifeExpectancy( object ):

   def __init__( self, country, dob, sex ):

      # country is just a string, no verificaiton
      if not isinstance( country, str ):
         raise LifeExpectancyException( "country has to be a string" )

      self.country_ = country
      ( v, date ) = isDate( dob )
      
      if not v:
         raise LifeExpectancyException( date )
      self.dob_ = date

      if not isinstance( sex, str ):
         raise LifeExpectancyException( "sex has to be the string 'male|female' " )
      sex = sex.lower()
      if sex not in [ 'male', 'female' ]:
         raise LifeExpectancyException( "sex has to be 'male|female' " )
      self.sex_ = sex
      # date of death, calculated when lifeExp is retrieved
      self.dod_ = None
      
   def country( self ):
      return self.country_

   def dob( self ):
      return self.dob_

   def sex( self ):
      return self.sex_

   def dod( self ):
      return self.dod_

   def setExpectedDod( self, lifeExp ):
      '''
      Calculates the expected date of death
      based on lifeExp, a float of the number of years
      expected for a person with these life expectancy traits
      '''
      # calculate roughly how many daysare expected
      lifeExpDays = int( lifeExp * 365.25 )
      lifeDelta = relativedelta()
      lifeDelta.days = lifeExpDays
      self.dod_ = self.dob_ + lifeDelta

   def setDod( self, dod ):
      '''
      Set date of death for lifeExpectancy directly
      '''

      ( v, date ) = isDate( dod )
      if not v:
         raise LifeExpectancyException( date )
      self.dod_ = date
      
   def lifeExpectancy( self ):
      '''
      Returns the relative delta
      between today's date and the date of death
      '''

      if not self.dod_:
         # can't calculate the life expectancy if we don't know date of death
         return None
      today = datetime.date.today()
      return relativedelta( self.dod_, today )

   def __eq__( self, other ):
      '''
      Two life expectancies are the same if the country, dob and sex is the same
      '''

      if not isinstance( other, self.__class__ ):
         return False
      return ( other.country() == self.country_ and other.dob() == self.dob_
               and other.sex() == self.sex() )


   def __str__( self ):
      return ( "country: %s, dob: %s, sex: %s" %
               ( self.country_, self.dob_.isoformat(),
                 self.sex_ ) )


class LECache( object ):

   def __init__( self, maxsize ):
      self.maxsize_ = maxsize
      self.cache_ = [ None ] * maxsize

   def put( self, lifeExpectancy ):
      if lifeExpectancy in self.cache_:
         self.cache_.remove( lifeExpectancy )
      # add the lifeExpectancy to front of the list
      self.cache_.insert( 0, lifeExpectancy )
      # if the length of the cache exceeds the max size
      # remove the last lifeExpectancy
      if len( self.cache_ ) > self.maxsize_:
         self.cache_.pop()

   def get( self, lifeExpectancy ):
      '''
      Returns the cached value if
      there is one equal to lifeExpectancy,
      None otherwise
      '''
      result = None
      for le in self.cache_:
         if lifeExpectancy == le:
            result = le
            # update the priority on the result
            self.put( result )
            break
      return result
