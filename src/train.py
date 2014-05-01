#!/usr/bin/env python

from os import path, pardir, curdir
from sys import stdout, stdin, stderr, exit, argv
from optparse import OptionParser, make_option
from nltk import word_tokenize, pos_tag
from json import loads, dumps
from glob import glob
from math import log
from operator import itemgetter
from itertools import chain, izip

from featurebase import Token
from address import AddressClassifier

class Trainer(AddressClassifier):

   default_classification= ["OTHER"]

   def __init__(self):

      super(Trainer, self).__init__()

   def generate(self, input, output= stdout):

      tokens= [Token(*word) for word in map(lambda word: list(word) + self.default_classification, pos_tag(word_tokenize(''.join(input))))]
      map(self.add_features, tokens)

      feature_list= list(chain(*[token.features for token in tokens]))

      document= []
      for token in tokens:
         feature_dict= dict([(feature, False) for feature in feature_list])
         feature_dict.update([(feature, True) for feature in token.features])
         feature_dict.update([('POS', token.pos), ('CLASS', token.classification)])
         document.append((token.word, feature_dict))

      output.write(dumps(document))
      output.flush()

   def gain(self, attribute, data, target= 'CLASS'):
 
      freq= {}
      h_subset= 0.0

      for (word, feature_dict) in data:
         try:
            freq[feature_dict[attribute]]+= 1
         except KeyError:
            freq[feature_dict[attribute]]= 1

      for v, f in freq.iteritems():
         p= f / float(sum(freq.values()))
         data_subset= [(word, feature_dict) for (word, feature_dict) in data if feature_dict[attribute] == v]
         h_subset+= p * self.entropy(data_subset)

      g= self.entropy(data) - h_subset

      return g

   def frequency(self, data, target= 'CLASS'):

      freq= {}
      for (word, feature_dict) in data:
         cls= feature_dict.get(target)
         try:
            freq[cls]+= 1
         except KeyError:
            freq[cls]= 1

      return freq

   def entropy(self, data, target= 'CLASS'):

      freq= self.frequency(data, target)
      s= float(len(data))
      h= sum([-(f / s) * log(f / s, 2) for (cls, f) in freq.iteritems()])

      return h

   def majority(self, data, target= 'CLASS'):

      freq= self.frequency(data, target)
      m= sorted(freq.iteritems(), key= itemgetter(1), reverse= True)[0][0]

      return m

   def build_tree(self, feature_list, data):

      h= self.entropy(data)

      if len(feature_list) - 1 == 0 or h == 0.0: 
         return self.majority(data)

      feature= sorted([(f, self.gain(f, data)) for f in feature_list if f != 'CLASS'], key= itemgetter(1), reverse= True)[0][0]

      feature_list.pop(feature_list.index(feature))

      tree= {feature: {}}
      for value in self.frequency(data, feature).keys():

         data_subset= filter(lambda (word, feature_dict): feature_dict.get(feature) == value,  data)
         branch= self.build_tree(feature_list, data_subset)

         tree[feature][value]= branch

      return tree
 
   def train(self, input, output):
 
      for document in input:

         data= loads(document)
          
         (word, feature_dict)= data[0]
         feature_list= feature_dict.keys()

         tree= self.build_tree(feature_list, data)

         output.write(dumps(tree))
         output.flush()
 
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

