#!/usr/bin/env python

from itertools import izip, chain
from json import loads
from os import path, pardir, curdir
from sys import stdin, stderr, stdout, argv
from optparse import OptionParser, make_option
from nltk import word_tokenize, pos_tag

from address import AddressClassifier
from featurebase import Token

class Parser(AddressClassifier):

   default_classification= ["OTHER"]
   tfdict= {True: 'true', False: 'false'}

   def __init__(self, input= stdin, output= stdout):

      self.input= input
      self.output= output

   def classify(self, token, feature_dict, feature_tree):

      for feature in feature_tree:
         feature_value= feature_dict[feature]
         node= feature_tree[feature]
         
         branch= node[self.tfdict.get(feature_value, feature_value)]
         if type(branch) == dict:
            return self.classify(token, feature_dict, branch)
       
      return branch

   def parse(self, feature_tree):

      for document in self.input:

         print "======================================================================"
         address= []
         tokens= [Token(*word) for word in pos_tag(word_tokenize(''.join(document)))]
         map(self.add_features, tokens)

         feature_list= list(chain(*[token.features for token in tokens]))
         for token in tokens:

            feature_dict= dict([(feature, False) for feature in feature_list])
            feature_dict.update([(feature, True) for feature in token.features])
            feature_dict.update([('POS', token.pos), ('CLASS', token.classification)])

            token.classification=  self.classify(token, feature_dict, feature_tree)
            if token.classification in ('START', 'MIDDLE', 'END'):
               print "%20s %20s" % (token.word, token.classification)

               address.append(token)

         if [token.classification for token in address].count('MIDDLE') <= 20:
            print ' '.join([token.word for token in address])
         else:
            print 'ERROR: could not determine address'
         print "----------------------------------------------------------------------"




def parse_args(argv):

   optParser= OptionParser()

   [optParser.add_option(opt) for opt in [
      make_option("-i", "--input", default= stdin, help= "input file(s)"),
      make_option("-o", "--output", default= stdout, help= "output file"),
      make_option("-f", "--feature", default= path.join(pardir, 'trees', 'address.tree'), help= "feature tree")
   ]]

   optParser.set_usage("%prog --query")

   opts, args= optParser.parse_args()
   if opts.input == stdin:
      setattr(opts, "input", [stdin.read()])
   else:
      filenames= glob(opts.input) if '*' in opts.input else [opts.input]
      setattr(opts, 'input', [open(filename, 'r').read() for filename in filenames])

   if opts.output != stdout:
      setattr(opts, "output", open(opts.output, "w"))

   setattr(opts, "feature", loads(open(opts.feature, 'r').read()))

   return opts


if __name__ == '__main__':

   opts= parse_args(argv)

   parser= Parser(opts.input, opts.output)
   parser.parse(opts.feature)




