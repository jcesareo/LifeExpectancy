#!/usr/bin/env python
import os
import shutil
import tempfile
import unittest
import datetime
import context
from LifeExpectancy.LEUtils import LifeExpectancy, LifeExpectancyException
from LifeExpectancy.LECache import LECache
from LifeExpectancy.LEDataStore import LEDataStore, LEDataStoreException

import datetime
from dateutil.relativedelta import relativedelta as relativedelta


class LifeExpectancyTest( unittest.TestCase ):

   @classmethod
   def setUpClass( cls ):

      cls.country = "Italy"
      cls.gender = "male"
      cls.dob1 = "1987-03-28"
      cls.dob2 = datetime.date( 1991, 01, 28 )
      cls.today_ = datetime.date.today()
      cls.tomorrow_ = cls.today_ + relativedelta( days=1 )

   def testLifeExpectancyFieldVerifications( self ):
      '''
      Test the __init__ function for LifeExpectancy
      '''

      # invalid country
      with self.assertRaisesRegexp( LifeExpectancyException,
                                    "country has to be a string" ):
         le = LifeExpectancy( 13, "foo", 'male', 'foo' )

      # dob is a string in the wrong format
      with self.assertRaisesRegexp( LifeExpectancyException,
                                    "date is invalid" ):
         le = LifeExpectancy( self.country, "1331-33-33", 'male', 'foo' )

      # dob is a not the right type
      with self.assertRaisesRegexp( LifeExpectancyException,
                                    "date.* is incorrect type" ):
         le = LifeExpectancy( self.country, 1331.33, 'male', 'foo' )

      # gender is not a string
      with self.assertRaisesRegexp( LifeExpectancyException,
                                    "gender has to be a string" ):
         le = LifeExpectancy( self.country, self.dob1, 13, 'foo' )

      # gender is not 'male' or 'female'
      with self.assertRaisesRegexp( LifeExpectancyException,
                                    "gender has to be.*male" ):
         le = LifeExpectancy( self.country, self.dob1, 'foo', 'foo' )


      # date is a string in the wrong format
      with self.assertRaisesRegexp( LifeExpectancyException,
                                    "date is invalid" ):
         le = LifeExpectancy( self.country, self.dob1, 'female', "1331-33-33" )

      le = LifeExpectancy( self.country, self.dob1, self.gender, self.today_ )
      self.assertEqual( le.country(), self.country )
      self.assertEqual( le.dob().isoformat(), self.dob1 )
      self.assertEqual( le.gender(), self.gender )
      self.assertEqual( le.date(), self.today_ )
      le2 = LifeExpectancy( self.country, self.dob1, self.gender, self.tomorrow_ )

      self.assertNotEqual( le, le2 )

   def testLifeExpectancySetLifeExp( self ):
      '''
      tests LifeExpectancy's calculateLifeExp method
      '''

      le = LifeExpectancy( self.country, self.dob2, self.gender, self.today_ )
      lifeExp = float( 80 )
      le.calculateLifeExp( lifeExp )
      delta = le.lifeExpectancy()
      
      # make sure lifeExp was correctly added to the date of death
      self.assertEqual( delta.years, int( lifeExp ) )

      # now add a decimal value to lifeExp, make sure
      # setExpectedDod returns a value more than lifeExp but less than lifeExp + 1
      le.calculateLifeExp( lifeExp + 0.537 )
      delta2 = le.lifeExpectancy()
      self.assertTrue( delta2.months > 0 or delta2.days > 0 )

class LECacheUnitTest( unittest.TestCase ):

   @classmethod
   def setUpClass( cls ):
      cls.maxsize = 10
      cls.les = []
      for x in xrange( 1, cls.maxsize + 1 ):
         le = LifeExpectancy( str( x ),
                              "20%02d-%02d-%02d" %
                              ( x, x, x ), 'male' ,
                              datetime.date.today() )
         le.calculateLifeExp( float( 70 + x ) + float( .09 * x ) )
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
                           self.les[ 0 ].gender(),
                           self.les[ 0 ].date() )
      # get() should return the cached element
      leCached = cache.get( le )
      # the cached element should be equal to the original one
      self.assertEqual( leCached, self.les[ 0 ] )
      # check that the position of the cached element has been updated
      self.assertEqual( cache.cache_.index( leCached ), 0 )

      # now check a non existent element
      le = LifeExpectancy( "Italy", "1987-03-28", "female", datetime.date.today() )
      leCached = cache.get( le )
      self.assertEqual( leCached, None )
      # add this new element to the cache
      le.calculateLifeExp( 90 )
      cache.put( le )
      # assert that the new element is first
      self.assertEqual( cache.cache_[ 0 ], le )
      leCopy = LifeExpectancy( le.country(), le.dob(), le.gender(), le.date() )
      # now try to get the element, it should exist
      leCached = cache.get( leCopy )
      self.assertEqual( leCached, le )

      leCopyDiffDate = LifeExpectancy( le.country(), le.dob(), le.gender(),
                                       le.date() + relativedelta( years=1 ) )

      self.assertEqual( cache.get( leCopyDiffDate ), None )
      
      # with this new LifeExpectancy we should have kicked
      # out self.les[ 1 ] since we moved self.les[ 0 ] previously
      self.assertEqual( cache.get( self.les[ 1 ] ), None )
      # self.les[ 2 ] should be last
      self.assertEqual( cache.cache_[ -1 ], self.les[ 2 ] )


class LEDataStoreUnitTest( unittest.TestCase ):

   @classmethod
   def setUpClass( cls ):
      cls.rootDir_ = tempfile.mkdtemp()
      cls.dir_ = "le"
      cls.today_ = datetime.date.today()
      cls.le1_ = LifeExpectancy( 'Italy', '1987-03-28', 'male', cls.today_ )
      cls.le2_ = LifeExpectancy( 'USA', '1991-01-28', 'female', cls.today_ )

   @classmethod
   def tearDownClass( cls ):
      shutil.rmtree( cls.rootDir_ )

   def testLEDataStoreInit( self ):
      '''
      Test __init__ method for LEDataStore.
      '''

      ds = LEDataStore( root=self.rootDir_, directory=self.dir_ )
      # check that rootDir_ + dirName exists
      self.assertTrue( os.path.exists( ds.directory() ) )

   def testLEDataStoreLifeExpectancy( self ):
      '''
      Test fetch and set lifeExpectancy methods
      '''

      ds = LEDataStore( root=self.rootDir_, directory=self.dir_ )

      lifeExp = 80.123
      self.le1_.calculateLifeExp( lifeExp  )
      ds.addLifeExpectancy( self.le1_ )

      self.assertEqual( self.le1_.lifeExpectancy(), ds.fetchLifeExpectancy( self.le1_ ) )

      # now fetch a non existent lifeExp
      self.assertEqual( ds.fetchLifeExpectancy( self.le2_ ), None )
      # now check that a lifeExp is not added if dod isnt set

      with self.assertRaisesRegexp( LEDataStoreException,
                                    "life expectancy.*is not set" ):
         ds.addLifeExpectancy( self.le2_ )

      self.assertEqual( ds.fetchLifeExpectancy( self.le2_ ), None )
      lifeExp2 = 90.99
      self.le2_.calculateLifeExp( lifeExp2 )
      ds.addLifeExpectancy( self.le2_ )
      self.assertEqual( ds.fetchLifeExpectancy( self.le2_ ), self.le2_.lifeExpectancy() )

      # make sure that if we stat a new data storage with the same
      # directory fetching works
      ds2 = LEDataStore( root=self.rootDir_, directory=self.dir_ )
      
      self.assertEqual( ds2.fetchLifeExpectancy( self.le2_ ), self.le2_.lifeExpectancy() )

if __name__ == '__main__':
   unittest.main()

