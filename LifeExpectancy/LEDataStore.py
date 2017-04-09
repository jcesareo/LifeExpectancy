#!/usr/bin/env python
from dateutil.relativedelta import relativedelta as relativedelta
import json
import os
import tempfile

from LEUtils import isDate

class LEDataStoreException( Exception ):
   pass

class LEDataStore( object ):
   '''
   Builds a hierarchy of files starting from root + dir
   These LifeExpectancy members are used for hierarchy:
   - date
   - country
   - date of birth
   Lastly the gender stores the life expectancy in json format

   The hierarchy for a a path to a file is:
   /rootdir/date.year/date.month/date.day/country/dob.year/dob.month/dob.day/
   '''

   def __init__( self, root=tempfile.gettempdir(), directory='lifeExpectancy' ):

      if not os.path.exists( root ):
         raise LEDataStoreException( "Directory %s does not exist, "
            " pick an existing root directory" )
      self.root_ = os.path.abspath( root )
      self.dir_ = os.path.join( root, directory ) 
      if not os.path.exists( self.dir_ ):
         os.mkdir( self.dir_ )

   def root( self ):
      return self.root_

   def directory( self ):
      return self.dir_


   def _lifeExpPath( self, lifeExp ):

      dateDir = "%s/%s/%s" % ( lifeExp.date().year,
                               lifeExp.date().month,
                               lifeExp.date().day )
      dob = lifeExp.dob()
      dobDir = "%s/%s/%s/%s" % ( lifeExp.country(), dob.year, dob.month,
                                 dob.day )

      datePath = os.path.join( self.dir_, dateDir )
      lifeExpPath = os.path.join( datePath, dobDir )

      return lifeExpPath
      
   def fetchLifeExpectancy( self, lifeExp ):
      '''
      Given a life expectancy object, use the country, dob, and gender
      to retrieve the dod
      '''

      lifeExpFile = os.path.join( self._lifeExpPath( lifeExp ), lifeExp.gender() )
      if not os.path.exists( lifeExpFile ):
         return None

      with open( lifeExpFile, 'r' ) as fd:
         lifeExpJson = json.load( fd )
         return relativedelta( **lifeExpJson )
      
   def addLifeExpectancy( self, lifeExp ):

      # if life expectancy isnt set in lifeExp,
      # do not store anything
      if not lifeExp.lifeExpectancy():
         raise LEDataStoreException( "life expectancy in %s is not set" % lifeExp )

      lifeExpPath = self._lifeExpPath( lifeExp )
      if not os.path.exists( lifeExpPath ):
         os.makedirs( lifeExpPath )

      lifeExpFile = os.path.join( lifeExpPath, lifeExp.gender() )
      if not os.path.exists( lifeExpFile ):
         with open( lifeExpFile, 'w' ) as fd:
            json.dump( lifeExp.lifeExpectancyJson(), fd )

