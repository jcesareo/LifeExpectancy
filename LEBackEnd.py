#!/usr/bin/env python
import os
from LEUtils import isDate
import tempfile

class LEDataStorageException( Exception ):
   pass

class LEDataStorage( object ):
   '''
   Builds a hierarchy of files starting from root + dir
   Each country has its own subfolder in rootdir/
   Each year has a subfolder in rootdir/country/
   Each month has a folder in folder in rootdir/country/year/
   Each day has a folder in folder rootdir/country/year/month/
   Each sex has a file in folder rootdir/country/year/month/day/
   The file has the life expectancy float number
   '''

   def __init__( self, root=tempfile.gettempdir(), directory='lifeExpectancy',
                 countries=list() ):

      if not os.path.exists( root ):
         raise LEDataStorageException( "Directory %s does not exist, "
            " pick an existing root directory" )
      self.root_ = os.path.abspath( root )
      self.dir_ = ( root + directory ) 
      if not os.path.exists( self.dir_ ):
         os.mkdir( self.dir_ )

      for country in countries:
         countryPath = os.path.join( self.dir_, country )
         if not os.path.exists( countryPath ):
            os.mkdir( countryPath )


   def root( self ):
      return self.root_

   def directory( self ):
      return self.dir_

   def fetchLifeExpectancy( self, lifeExpectancy ):
      '''
      Given a life expectancy object, use the country, dob, and sex
      to retrieve the dod
      '''
      lifeExpPath = "%s/%s/%s/%s/%s" % ( lifeExpectancy.country(),
                                         lifeExpectancy.dob().year,
                                         lifeExpectancy.dob().month,
                                         lifeExpectancy.dob().day,
                                         lifeExpectancy.sex() )


      lifeExpFile = os.path.join( self.dir_, lifeExpPath )
      if not os.path.exists( lifeExpFile ):
         return None

      with open( lifeExpFile, 'r' ) as fd:         
         ( v, dod ) = isDate( fd.read().strip() )
         if not v:
            return None
      return dod
      
   def setLifeExpectancy( self, lifeExpectancy ):

      # if the dod is not seath for this lifeExpectancy then do not add
      # to the storage
      if not lifeExpectancy.dod():
         raise LEDataStorageException( "life expectancy %s doesn't have a dod set, "
                                       "can't add to data storage" )
      
      lifeExpDir = "%s/%s/%s/%s" % ( lifeExpectancy.country(),
                                     lifeExpectancy.dob().year,
                                     lifeExpectancy.dob().month,
                                     lifeExpectancy.dob().day )

      lifeExpPath = os.path.join( self.dir_, lifeExpDir )
      
      if not os.path.exists( lifeExpPath ):
         os.makedirs( lifeExpPath )

      lifeExpFile = os.path.join( lifeExpPath, lifeExpectancy.sex() )
      if not os.path.exists( lifeExpFile ):
         with open( lifeExpFile, 'w' ) as fd:
            fd.write( lifeExpectancy.dod().isoformat() )
      

