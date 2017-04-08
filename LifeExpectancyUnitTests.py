#!/usr/bin/env python
import os
import shutil
import tempfile
import unittest


from LEUtils import LifeExpectancy, LifeExpectancyException
from LECache import LECache
from LEBackEnd import LEDataStorage, LEDataStorageException

import datetime
from dateutil.relativedelta import relativedelta as relativedelta


class LifeExpectancyTest( unittest.TestCase ):

   @classmethod
   def setUpClass( cls ):

      cls.country = "Italy"
      cls.sex = "male"
      cls.dob1 = "1987-03-28"
      cls.dob2 = datetime.date( 1991, 01, 28 )


   def testLifeExpectancyFieldVerifications( self ):
      '''
      Test the __init__ function for LifeExpectancy
      '''

      # invalid country
      with self.assertRaisesRegexp( LifeExpectancyException,
                                    "country has to be a string" ):
         le = LifeExpectancy( 13, "foo", 'male' )

      # dob is a string in the wrong format
      with self.assertRaisesRegexp( LifeExpectancyException,
                                    "date.* has to be in format" ):
         le = LifeExpectancy( self.country, "1331-33-33", 'male' )

      # dob is a not the right type
      with self.assertRaisesRegexp( LifeExpectancyException,
                                    "date.* is incorrect type" ):
         le = LifeExpectancy( self.country, 1331.33, 'male' )

      # sex is not a string
      with self.assertRaisesRegexp( LifeExpectancyException,
                                    "sex has to be the string" ):
         le = LifeExpectancy( self.country, self.dob1, 13 )

      # sex is not 'male' or 'female'
      with self.assertRaisesRegexp( LifeExpectancyException,
                                    "sex has to be.*male" ):
         le = LifeExpectancy( self.country, self.dob1, 'foo' )


      le = LifeExpectancy( self.country, self.dob1, self.sex )
      self.assertEqual( le.country(), self.country )
      self.assertEqual( le.dob().isoformat(), self.dob1 )
      self.assertEqual( le.sex(), self.sex )


   def testLifeExpectancySetExpectedDod( self ):
      '''
      tests LifeExpectancy's setDod method
      '''

      le = LifeExpectancy( self.country, self.dob2, self.sex )
      lifeExp = float( 80 )
      le.setExpectedDod( lifeExp )

      # make sure lifeExp was correctly added to the date of death
      self.assertEqual( self.dob2.year + lifeExp, le.dod().year )

      # now add a decimal value to lifeExp, make sure
      # setExpectedDod returns a value more than lifeExp but less than lifeExp + 1
      le.setExpectedDod( lifeExp + 0.537 )
      rd = relativedelta()
      rd.years += int( lifeExp )
      self.assertLess( self.dob2 + rd, le.dod() )
      rd.years += 1
      self.assertLess( le.dod() , self.dob2 + rd )

   def testLifeExpectancylifeExpectancy( self ):
      '''
      tests LifeExpectancy's lifeExpectancy method
      '''

      le = LifeExpectancy( self.country, self.dob2, self.sex )

      lifeExp = 80.333
      le.setExpectedDod( lifeExp )
      exp = le.lifeExpectancy()
      self.assertEqual( datetime.date.today() + exp, le.dod() )

class LECacheUnitTest( unittest.TestCase ):

   @classmethod
   def setUpClass( cls ):
      cls.maxsize = 10
      cls.les = []
      for x in xrange( 1, cls.maxsize + 1 ):
         le = LifeExpectancy( str( x ),
                              "20%02d-%02d-%02d" %
                              ( x, x, x ), 'male' )
         le.setExpectedDod( float( 70 + x ) + float( .09 * x ) )
         cls.les.append( le )


   def testLECache( self ):
      '''
      test LECache's put and get methods
      '''

      cache = LECache( self.maxsize )
      for le in self.les:
         cache.put( le )

      # pick the first element
      le = LifeExpectancy( self.les[ 0 ].country(),
                           self.les[ 0 ].dob(),
                           self.les[ 0 ].sex() )
      # get() should return the cached element
      leCached = cache.get( le )
      # the cached element should be equal to the original one
      self.assertEqual( leCached, self.les[ 0 ] )
      # check that the position of the cached element has been updated
      self.assertEqual( cache.cache_.index( leCached ), 0 )

      # now check a non existent element
      le = LifeExpectancy( "Italy", "1987-03-28", "female" )
      leCached = cache.get( le )
      self.assertEqual( leCached, None )
      # add this new element to the cache
      le.setExpectedDod( 90 )
      cache.put( le )
      # assert that the new element is first
      self.assertEqual( cache.cache_[ 0 ], le )
      leCopy = LifeExpectancy( le.country(), le.dob(), le.sex() )
      # now try to get the element, it should exist
      leCached = cache.get( leCopy )
      self.assertEqual( leCached, le )

      # with this new LifeExpectancy we should have kicked
      # out self.les[ 1 ] since we moved self.les[ 0 ] previously
      self.assertEqual( cache.get( self.les[ 1 ] ), None )
      # self.les[ 2 ] should be last
      self.assertEqual( cache.cache_[ -1 ], self.les[ 2 ] )


class LEDataStorageUnitTest( unittest.TestCase ):

   @classmethod
   def setUpClass( cls ):
      cls.rootDir_ = tempfile.mkdtemp()
      cls.dir_ = "le" 
      cls.le1_ = LifeExpectancy( 'Italy', '1987-03-28', 'male' )
      cls.le2_ = LifeExpectancy( 'USA', '1991-01-28', 'female' )

   @classmethod
   def tearDownClass( cls ):
      shutil.rmtree( cls.rootDir_ )



   def testLEDataStorageInit( self ):
      '''
      Test __init__ method for LEDataStorage.
      '''


      ds = LEDataStorage( root=self.rootDir_, directory=self.dir_ )
      # check that rootDir_ + dirName exists
      self.assertTrue( os.path.exists( ds.directory() ) )

      countries = [ "italy", "usa" ]
      ds = LEDataStorage( root=self.rootDir_, directory=self.dir_,
                          countries=countries )

      # make sure each country directory exists
      for country in countries:
         self.assertTrue( os.path.exists( os.path.join( ds.directory(), country ) ) )

      countries.append( "spain" )
      ds = LEDataStorage( root=self.rootDir_, directory=self.dir_,
                          countries=countries )

      # make sure each country directory exists
      for country in countries:
         self.assertTrue( os.path.exists( os.path.join( ds.directory(), country ) ) )



   def testLEDataStorageLifeExpectancy( self ):
      '''
      Test fetch and set lifeExpectancy methods
      '''

      ds = LEDataStorage( root=self.rootDir_, directory=self.dir_ )

      self.le1_.setExpectedDod( 80 )
      ds.setLifeExpectancy( self.le1_ )
      dod1 = ds.fetchLifeExpectancy( self.le1_ )
      self.assertEqual( self.le1_.dod(), dod1 )

      # now fetch a non existent lifeExp
      dod2 = ds.fetchLifeExpectancy( self.le2_ )
      self.assertEqual( dod2, None )
      # now check that a lifeExp is not added if dod isnt set

      with self.assertRaisesRegexp( LEDataStorageException,
                                    "life expectancy.*dod set" ):
         ds.setLifeExpectancy( self.le2_ )

      dod2 = ds.fetchLifeExpectancy( self.le2_ )
      self.assertEqual( dod2, None )
      self.le2_.setExpectedDod( 90 )
      ds.setLifeExpectancy( self.le2_ )

      dod2 = ds.fetchLifeExpectancy( self.le2_ )
      self.assertEqual( dod2, self.le2_.dod() )

      # make sure that if we stat a new data storage with the same
      # directory fetching works
      ds2 = LEDataStorage( root=self.rootDir_, directory=self.dir_ )
      dod2 = ds2.fetchLifeExpectancy( self.le2_ )
      self.assertEqual( dod2, self.le2_.dod() )

if __name__ == '__main__':
   unittest.main()
