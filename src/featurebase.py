#!/usr/bin/env python

class Token(object):

   def __init__(self, word, pos= None):

      self.word= word
      self.pos= pos
      self.features= [pos]
      self.length= len(word)

   def add_feature(self, feature):
      if feature not in self.features:
         self.features.append(feature)

   def remove_feature(self, feature):
      if feature in self.features:
         self.features.pop(feature)

class Feature(object):

   handlers= []

   def __init__(self, feature):
      self.feature= feature

   def __call__(self, fn):

      def decorated(cls, token):
         if fn(cls, token) == True:
            token.add_feature(self.feature)

      decorated.feature= self.feature
      self.handlers.append(decorated)
      return decorated

