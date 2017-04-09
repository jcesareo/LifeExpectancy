#!/usr/bin/env python
import datetime
from dateutil.relativedelta import relativedelta as relativedelta

class LifeExpectancyException( Exception ):
   pass


def isDate( d ):
   '''
   Helper method. Verifies d can be turned into a date,
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


class Person( object ):
   def __init__( self, name, lifeExp ):
      self.name_ = name
      self.lifeExp_ = lifeExp

   def name( self ):
      return self.name_
   
   def lifeExp( self ):
      return self.lifeExp_

class Age( object ):
   def __init__( self, years, months, days ):
      self.y_ = years if years > 0 else 0
      self.m_ = months if months > 0 else 0
      self.d_ = days if days > 0 else 0

   def __str__( self ):
      return "%sy%sm%sd" % ( self.y_, self.m_, self.d_ )

class LifeExpectancy( object ):

   def __init__( self, country, dob, gender, date=None ):
      # country is just a string, no verificaiton
      if not isinstance( country, str ):
         raise LifeExpectancyException( "country has to be a string" )

      self.country_ = country
      ( v, dob ) = isDate( dob )
      if not v:
         raise LifeExpectancyException( dob )
      self.dob_ = dob
      if not isinstance( gender, str ):
         raise LifeExpectancyException( "gender has to be a string of value 'male|female'' " )
      gender = gender.lower()
      if gender not in [ 'male', 'female' ]:
         raise LifeExpectancyException( "gender has to be male or female " )
      self.gender_ = gender
      self.lifeExp_ = None
      if date:
         self.setDate( date )


   def country( self ):
      return self.country_

   def dob( self ):
      return self.dob_

   def gender( self ):
      return self.gender_

   def setDate( self, date ):
      if self.lifeExp_:
         raise LifeExpectancyException( "Changing date when "
            "life expectancy has already been calculated isn't allowed" )

      ( v, date ) = isDate( date )
      if not v:
         raise LifeExpectancyException( date )
      self.date_ = date
      delta = relativedelta( self.date_, self.dob_ )
      self.age_ = Age( delta.years, delta.months, delta.days )
      
   def date( self ):
      return self.date_

   def age( self ):
      return self.age_

   def calculateLifeExp( self, lifeExp ):
      '''
      Calculates the expected life exepctancy
      based on lifeExp, a float of the number of years
      expected for a person to live based on her age at a certain date
      lifeExp_ is a relativedelta
      '''

      dod = self.date_ + relativedelta( days=( lifeExp * 365.25 ) )
      # do this so that we have days, months, and years
      self.lifeExp_ = relativedelta( dod, self.date_ )

   def setLifeExp( self, delta ):
      self.lifeExp_ = delta
      
   def lifeExpectancy( self ):
      return self.lifeExp_

   def lifeExpectancyJson( self ):

      return { 'years': self.lifeExp_.years,
               'months': self.lifeExp_.months,
               'days': self.lifeExp_.days }

   def __eq__( self, other ):
      '''
      Two life expectancies are the same if the country, dob and gender is the same
      '''

      if not isinstance( other, self.__class__ ):
         return False
      return ( other.country() == self.country_ and other.dob() == self.dob_
               and other.gender() == self.gender() and self.date() == other.date() )


   def __str__( self ):
      return ( "country: %s, dob: %s, gender: %s, date: %s" %
               ( self.country_, self.dob_.isoformat(),
                 self.gender_, self.date_ ) )



