#FeatureExtractor

Feature extractor allows the developer to systematically assign feature attributes to tokens via the @Feature decorator.  These feature attributes tokens also have an associated output class which is manually trained..  The entropy of the feature matrix is calculated.  The information gain of each feature is calculated and a decision tree is generated.

## Example
Lets say we wanted the ability to extract a postal address from plain text. First step is to create a classifier.  When methods are decorated with @Feature the user-defined feature passed to the decorator will be added to the token.features list if the method returns True. 

```
class AddressClassifier(FeatureClassifier):

    @Feature("US_STATE") 
    def us_state(self, token):
       if token.word in self.state_names:
          return True
    ...
```

Once you've created your classifier the user can create a "training" document:

```
cat ../documents/sample[0-9].txt | ./train.py --generate --output=../train/address.train
```

By default each token is assigned to the "OTHER" class.  In this example we're going to train the classifier to output one of four classes:

```
START: the start of the address block
MIDDLE: any token in the middle of the address block
END: the end of the address block
OTHER: any token outside of the address block
```

In this example, we'll open the training document and manually train it by manually adjusting the output CLASS parameters for the tokens in question.  Once the training document is completed the user can then generate the decision tree.

```
./train.py --input=../train/address.train --output=../trees/address.tree
```

Once the decision tree is built.  We can now extract the address from a plain text document that had similar features to the training documents.

```
cat ../documents/sample3.txt | ./parse

```






