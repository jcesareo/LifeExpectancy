#!/usr/bin/env python

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
