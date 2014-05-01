#!/usr/bin/env python

from json import loads
from os import path, pardir, curdir
from sys import stdin, stderr, stdout, argv
from optparse import OptionParser, make_option

class Parser:

   def __init__(self, input= stdin, output= stdout):

      self.input= input
      self.output= output

   def parse(self, feature_tree):

      for document in self.input:
          p
      print feature_tree


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
      setattr(opts, "input", stdin.read())
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




