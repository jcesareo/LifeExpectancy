#!/usr/bin/env python
import os
from LEUtils import isDate
import tempfile
import json
from dateutil.relativedelta import relativedelta as relativedelta

class LEDataStorageException( Exception ):
   pass

class LEDataStorage( object ):
   '''
   Builds a hierarchy of files starting from root + dir
   Each country has its own subfolder in rootdir/
   Each year has a subfolder in rootdir/country/
   Each month has a folder in folder in rootdir/country/year/
   Each day has a folder in folder rootdir/country/year/month/
   Each gender has a file in folder rootdir/country/year/month/day/
   The file has the life expectancy float number
   '''

   def __init__( self, root=tempfile.gettempdir(), directory='lifeExpectancy' ):

      if not os.path.exists( root ):
         raise LEDataStorageException( "Directory %s does not exist, "
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
         raise LEDataStorageException( "life expectancy in %s is not set" % lifeExp )

      lifeExpPath = self._lifeExpPath( lifeExp )
      if not os.path.exists( lifeExpPath ):
         os.makedirs( lifeExpPath )

      lifeExpFile = os.path.join( lifeExpPath, lifeExp.gender() )
      if not os.path.exists( lifeExpFile ):
         with open( lifeExpFile, 'w' ) as fd:
            json.dump( lifeExp.lifeExpectancyJson(), fd )

