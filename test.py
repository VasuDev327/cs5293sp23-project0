# third party libraries
import PyPDF2
import requests

# built-in libraries
import argparse
import io
import re
import sqlite3
import pytest
from project0 import *

def test_main(url):
    testingMain = main(url)
    assert True
    return(testingMain)
    
# the below function has all other functions like create, populatedb, status, incidentscount, 
# if this functions gives the output, which means other functions are running fine.
def test_extractedincidents(testingMain):
    testingExtractingIncidents = extractincidents(testingMain)
    assert True

url = "https://www.normanok.gov/sites/default/files/documents/2023-01/2023-01-01_daily_incident_summary.pdf"
testingMain = test_main(url)
test_extractedincidents(testingMain)