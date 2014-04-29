#!/usr/bin/env python

from os import path, pardir, curdir
from sys import stdout, stdin, stderr, exit, argv
from optparse import OptionParser, make_option
from nltk import word_tokenize, pos_tag
from json import loads, dumps

from featurebase import Token
from address import AddressClassifier

class Trainer(AddressClassifier):

   default_classification= ["OTHER"]

   def __init__(self, text, output= stdout):

      super(Trainer, self).__init__()

      self.text= text
      self.output= output
      self.tokens= [Token(*word) for word in map(lambda word: list(word) + self.default_classification, pos_tag(word_tokenize(self.text)))]
      map(self.add_features, self.tokens)

      #print "Tokens:"
      #pprint([(token.word, token.length, token.features) for token in self.tokens])

   def generate(self):

      document= {
         'probabilities': self.probabilities(self.tokens),
         'entropy': self.entropy(),
         'classificiations': [(token.word, token.features, token.classification) for token in trainer.tokens]
      }

      self.output.write(dumps(document))
      self.output.flush()


def parse_args(argv):

   optParser= OptionParser()

   [optParser.add_option(opt) for opt in [
      make_option("-i", "--input", default= stdin, help= "input file"),
      make_option("-o", "--output", default= stdout, help= "output file"),
      make_option("-g", "--generate", action= "store_true", default= False, help= "generate training document"),
      make_option("-d", "--documents", default= path.join(pardir, "documents", "*.train"), help= "training documents")
   ]]

   optParser.set_usage("%prog --query")

   opts, args= optParser.parse_args()
   if opts.input == stdin:
      setattr(opts, "input", stdin.read())
   else:
      fh= open(opts.input, "r")
      setattr(opts, "input", fh.read())
      fh.close()

   if opts.output != stdout:
      setattr(opts, "output", open(opts.output, "w"))

   return opts


if __name__ == '__main__':

   opts= parse_args(argv)

   trainer= Trainer(opts.input, opts.output)

   if opts.generate:
      trainer.generate()

