# ConjuctiveGramRank Homework 2
Find rank proximity for given query in each document and show top results.

## Test Data
Given a folder with text file containing

1) The quick or the brown fox
2) jumped over sally
3) and the brilliant bob fox
4) but not the brown peter bunny

## Run the Script
usage: ConjunctiveGramRank.py [-h] folder mgram nresults query

positional arguments:
  folder      get documents from folder
  mgram       get m-gram count
  nresults    get result count
  query       get query

options:
  -h, --help  show this help message and exit

Example: python .\ConjunctiveGramRank.py hw1 4 5 "the_brown"
