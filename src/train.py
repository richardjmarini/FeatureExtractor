#!/usr/bin/env python

from os import path, pardir, curdir
from sys import stdout, stdin, stderr, exit, argv
from optparse import OptionParser, make_option
from nltk import word_tokenize, pos_tag
from json import loads, dumps
from glob import glob
from math import log
from operator import itemgetter
from pprint import pprint

from featurebase import Token
from address import AddressClassifier

class Trainer(AddressClassifier):

   default_classification= ["OTHER"]

   def __init__(self):

      super(Trainer, self).__init__()

   def generate(self, input, output= stdout):

      tokens= [Token(*word) for word in map(lambda word: list(word) + self.default_classification, pos_tag(word_tokenize(''.join(input))))]
      map(self.add_features, tokens)

      document= {
         'probabilities': self.probabilities(tokens),
         'entropy': self.entropy(),
         'classifications':  [(token.word, token.features, token.classification) for token in tokens]
      }
      
      output.write(dumps(document))
      output.flush()

   def pnsplit(self, feature, classifications):

      p= 0
      n= 0
      for (word, features, classification) in classifications:
         if feature in features:
            p+= 1
         else:
            n+= 1

      return (p, n)

   def expected_entropy(self, p, n):

      total= p + n
      pos= p / float(total)
      neg= n / float(total)

      if p == 0 or n == 0:
         expected_entropy= 0.0
      else:
         expected_entropy= -pos * log(pos, 2) -  neg * log(neg, 2)
 
      return expected_entropy

   def information_gain(self, features, classifications, entropy):

      igain= {}
      for feature in features:
         (p, n)= self.pnsplit(feature, classifications)
         expected_entropy= self.expected_entropy(p, n)
         igain[feature]= entropy - expected_entropy

         print "%20s %3d %3d    %0.15f %0.15f, %0.15f" % (feature, p, n, entropy, expected_entropy, igain.get(feature))
      return igain

   def train(self, input, output):
 
      for document in input:

         document= loads(document)

         features= document.get("probabilities").keys()
         classifications= document.get("classifications")
         entropy= document.get("entropy")
         igain= self.information_gain(features, classifications, entropy)
        
      print
 
def parse_args(argv):

   optParser= OptionParser()

   [optParser.add_option(opt) for opt in [
      make_option("-i", "--input", default= stdin, help= "input file(s)"),
      make_option("-o", "--output", default= stdout, help= "output file"),
      make_option("-g", "--generate", action= "store_true", default= False, help= "generate training document"),
      make_option("-t", "--train", action= "store_true", default= False, help= "train decession tree")
   ]]

   optParser.set_usage("%prog --query")

   opts, args= optParser.parse_args()
   if opts.input == stdin:
      setattr(opts, "input", stdin.read())
   else:
      filenames= glob(opts.input) if '*' in opts.input else [opts.input]
      setattr(opts, 'input', [open(filename, 'r').read() for filename in filenames])

   if opts.output != stdout:
      setattr(opts, "output", open(opts.output, "w"))

   return opts


if __name__ == '__main__':

   opts= parse_args(argv)

   trainer= Trainer()

   if opts.generate:
      trainer.generate(opts.input, opts.output)

   if opts.train:
      trainer.train(opts.input, opts.output)

