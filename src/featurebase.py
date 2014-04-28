#!/usr/bin/env python

from itertools import chain
from math import log
from pprint import pprint

class Token(object):

   def __init__(self, word, pos= None, classification= None):

      self.word= word
      self.pos= pos
      self.features= [pos]
      self.classification= classification
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

class FeatureClassifier(object):

   def __init__(self):

      super(FeatureClassifier, self).__init__()

   def index(self, tokens):

      # probability= occurences / total
      # entropy(s)= sum( p(i)* log2(p(i)) )

      features= [handler.feature for handler in Feature.handlers]
      total_features= float(len(features))
      token_features= list(chain(*[token.features for token in tokens]))
      self.probability_matrix= dict([(feature, token_features.count(feature) / total_features) for feature in features])

      #print "Probability Matrix:"
      #pprint(self.probability_matrix)

      self.entropy= sum([probability * log(probability, 2) for probability in self.probability_matrix.values() if probability > 0])

      #print "Entropy:", self.entropy


   def probability(self, feature):

      return self.probability_matrix.get(feature, 0)

   def add_features(self, token):

      for handler in Feature.handlers:
         handler(self, token)

      return token.features


