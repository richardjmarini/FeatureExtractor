#!/usr/bin//env python

from optparse import OptionParser, make_option
from sys import stdin, argv
from re import match, sub
from itertools import izip, chain
from inspect import currentframe
from nltk import word_tokenize, pos_tag
from math import log


from featurebase import Feature, Token
      
class AddressClassifier(object):

   def __init__(self):
      self.handlers= {}

   @Feature("INITCAP")
   def initcap(self, token):
      if match("^[A-Z][a-z]+.*", token.word):
         return True

   @Feature("ALLCAPS")
   def allcaps(self, token):
      if match("^[A-Z]+$", token.word):
         return True

   @Feature("CONTAINSDIGITS")
   def containsdigits(self, token):
      if match("\d", token.word):
         return True

   @Feature("ALLDIGITS")
   def alldigits(self, token):
      if match("^\d+$", token.word):
         return True

   @Feature("ACRONYM")
   def acronym(self, token):
      if match("(([A-z]\.){2})+", token.word):
         return True

   @Feature("WORD")
   def word(self, token):
      if match("[A-z]+", token.word):
         return True

   @Feature("PUNCUATION")
   def puncuation(self, token):
      if match("[\.,!?;+'\(\)\"\[\]=_\-:#@]", token.word):
         return True

   @Feature("SINGLEINITIAL")
   def singleinitial(self, token):
      if match("^[A-z]\.$", token.word):
         return True

   @Feature("UPPERCASECHAR")
   def uppsercasechar(self, token):
      if match("^[A-Z]$", token.word):
         return True

   @Feature("LOWERCASECHAR")
   def lowercasechar(self, token):
      if match("^[a-z]$", token.word):
         return True

   @Feature("CONTAINSDASH")
   def containsdash(self, token):
      if match("\-", token.word):
         return True

   @Feature("PHONE")
   def phone(self, token):
      if match("^(\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}$", token.word):
         return True

   @Feature("EMAIL")
   def email(self, token):
      if match("\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}\b", token.word):
         return True

   @Feature("USSTATENAME")
   def usstatename(self, token):

      states= {u'WA': u'Washington', u'DE': u'Delaware', u'WI': u'Wisconsin', u'WV': u'West Virginia', u'HI': u'Hawaii', u'FL': u'Florida', u'WY': u'Wyoming', u'NH': u'New Hampshire', u'NJ': u'New Jersey', u'NM': u'New Mexico', u'TX': u'Texas', u'LA': u'Louisiana', u'NC': u'North Carolina', u'ND': u'North Dakota', u'NE': u'Nebraska', u'TN': u'Tennessee', u'NY': u'New York', u'PA': u'Pennsylvania', u'CA': u'California', u'NV': u'Nevada', u'VA': u'Virginia', u'CO': u'Colorado', u'AK': u'Alaska', u'AL': u'Alabama', u'AR': u'Arkansas', u'VT': u'Vermont', u'IL': u'Illinois', u'GA': u'Georgia', u'IN': u'Indiana', u'IA': u'Iowa', u'OK': u'Oklahoma', u'AZ': u'Arizona', u'ID': u'Idaho', u'CT': u'Connecticut', u'ME': u'Maine', u'MD': u'Maryland', u'MA': u'Massachusetts', u'OH': u'Ohio', u'UT': u'Utah', u'MO': u'Missouri', u'MN': u'Minnesota', u'MI': u'Michigan', u'RI': u'Rhode Island', u'KS': u'Kansas', u'MT': u'Montana', u'MS': u'Mississippi', u'SC': u'South Carolina', u'KY': u'Kentucky', u'OR': u'Oregon', u'SD': u'South Dakota'}

      if sub("[^A-z]", "", token.word.lower()) in chain(*[(abbr.lower(), name.lower()) for abbr, name in states.iteritems()]):
         return True

   @Feature("STREETSUFFIX")
   def streetsuffix(self, token):

      suffixes= {"ave": "avenue", "st": "street", "str": "street", "rd": "road", "blvd": "boulevard", "cir": "circle", "ct": "court", "pl": "place", "hwy": "highway", "terr": "terrace", "dr": "drive", "ctr": "center", "brk": "brook", "brg": "bridge", "br": "branch", "bnd": "bend", "bch": "beach", "aly": "alley", "xing": "crossing", "cyn": "canyon", "terr": "terrace", "plz": "plaza", "ln": "lane", "crk": "creek", "crse": "course", "crst": "crest", "cswy": "causeway", "pkwy": "parkway"}
      if sub("[^A-z]", "", token.word.lower()) in chain(*[(abbr.lower(), name.lower()) for abbr, name in suffixes.iteritems()]):
         return True

   @Feature("SECONDARYUNIT")
   def secondaryunit(self, token):

      designators= {"Apt": "Appartment", "Bld": "Building", "Ste": "Suite", "Rm": "Room", "Fl": "Floor", "Un": "Unit", "Flr": "Floor"}

      if sub("[^A-z]", "", token.word.lower()) in chain(*[(abbr.lower(), name.lower()) for abbr, name in designators.iteritems()]):
         return True

   @Feature("STREETDIRECTION")
   def streetdirection(self, token):

      directions= {"N": "North", "NE": "North East", "E": "East", "SE": "South East", "S": "South", "SW": "south West", "W": "West", "NW": "North West"}

      if sub("[^A-z]", "", token.word.lower()) in chain(*[(abbr.lower(), name.lower()) for abbr, name in directions.iteritems()]):
         return True

   @Feature("POBOX")
   def pobox(self, token):

      postalboxes= {"PO": "P.O.", "PO BOX": "P.O. BOX"}

      if sub("[^A-z]", "", token.word.lower()) in chain(*[(abbr.lower(), name.lower()) for abbr, name in postalboxes.iteritems()]):
         return True

   @Feature("ZIPCODE")
   def zipcode(self, token):

      if len(sub("[^0-9]", "", token.word)) in (5, 9):
         return True

   def index(self, tokens):

      features= [handler.feature for handler in Feature.handlers]
      total_features= float(len(features))
      token_features= list(chain(*[token.features for token in tokens]))
      self.probability_matrix= dict([(feature, token_features.count(feature) / total_features) for feature in features])

      print "Probability Matrix:", self.probability_matrix

      self.entropy= sum([probability * log(probability, 2) for probability in self.probability_matrix.values() if probability > 0])
 

   def probability(self, feature):

      return self.probability_matrix.get(feature, 0)

   def classify(self, token):

      for handler in Feature.handlers:
         handler(self, token)

      return token.features

class Address(AddressClassifier):

   def __init__(self, text):

      super(Address, self).__init__()

      self.text= text
      self.tokens= [Token(*word) for word in pos_tag(word_tokenize(self.text))]
      map(self.classify, self.tokens)

      print "Tokens:", [(token.word, token.length, token.features) for token in self.tokens]

      self.index(self.tokens)

   def parse(self):
      pass

def parse_args(argv):

   optParser= OptionParser()

   [optParser.add_option(opt) for opt in [
      make_option("-f", "--file", default= stdin, help= "input file"),
   ]]

   optParser.set_usage("%prog --query")

   opts, args= optParser.parse_args()
   if opts.file == stdin:
      setattr(opts, "file", stdin.read())
   else:
      fh= open(opts.file, "r")
      setattr(opts, "file", fh.read())
      fh.close()
      
   return opts


if __name__ == '__main__':

   opts= parse_args(argv)

   address= Address(opts.file)
   address.parse()
  
