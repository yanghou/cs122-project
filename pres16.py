### CS122, Winter 2017: Course search engine: search
###
### Huanye Liu

from math import radians, cos, sin, asin, sqrt
import sqlite3
import json
import re
import os
import matplotlib.pyplot as plt

# Use this filename for the database
DATA_DIR = os.path.dirname(__file__)
DATABASE_FILENAME = os.path.join(DATA_DIR, 'pres16results.db')

  




def graph_test(args_from_ui):
    '''
    {'colname':''}    

    Takes a dictionary containing search criteria and returns courses
    that match the criteria.  The dictionary will contain some of the
    following fields:

      - dept a string
      - day is array with variable number of elements  
           -> ["'MWF'", "'TR'", etc.]
      - time_start is an integer in the range 0-2359
      - time_end is an integer an integer in the range 0-2359
      - enroll is an integer
      - walking_time is an integer
      - building ia string
      - terms is a string: "quantum plato"]

    Returns a pair: list of attribute names in order and a list
    containing query results.
    '''
    # the following three dictionaries record all information from the inpur-output table
    # as specified in the assignment description.  Keys of all dictionaries are the
    # row names of the table, and for each key, the corresponding value in the first dictionary
    # is the related attribute names we need to select out, the value in the second 
    # dictionary is the related table we need to join, and the value in the last dictionary
    # is the where clause we need to add constraints on.
    if args_from_ui =={}:
        return None
    fb=False
    db = sqlite3.connect(DATABASE_FILENAME)
    c = db.cursor()
    if 'state' in args_from_ui:
        query='select cand,votes,pct from t where fips=?'
        arg = args_from_ui['state']
    if 'county' in args_from_ui:
        query = 'select cand,votes,pct from t where county=?'
        arg = args_from_ui['county']
    if 'cand_name' in args_from_ui:
        fb = True
        if args_from_ui['S_C'] == 'STATE':
            query = "select fips, max(votes) from t where lead = ? and length(fips)=2 and fips!='US' group by fips"
        elif args_from_ui['S_C'] == 'COUNTY':
            query = "select county, max(votes) from t where lead = ? and length(county)>2 group by county"
    
        arg = args_from_ui['cand_name']

    r = c.execute(query,[arg])
    # result is a list of tuples
    result = r.fetchall()
    c.close()
    
    if fb:
         return result
    labels=[]
    votes=[]
    freq = []
     
    for e in result:
        labels.append(e[0])
        votes.append(e[1])
        freq.append(e[2])
    votes[0]+=' '+labels[0]+' Wins'
    explode = [0.1]+[0]*(len(labels)-1)
    patches,text=plt.pie(freq,labels=votes,explode = explode, shadow=True)
    plt.legend(patches,labels, loc="best",prop={'size':8})
    graph_path = os.path.join(DATA_DIR,'static')
    plt.savefig(os.path.join(graph_path,'test.png')) 
    plt.clf()    
    return 'graph'


########### auxiliary functions #################
########### do not change this code #############



def get_header(cursor):
    '''
    Given a cursor object, returns the appropriate header (column names)
    '''
    desc = cursor.description
    header = ()

    for i in desc:
        header = header + (clean_header(i[0]),)

    return list(header)


def clean_header(s):
    '''
    Removes table name from header
    '''
    for i in range(len(s)):
        if s[i] == ".":
            s = s[i+1:]
            break

    return s



########### some sample inputs #################

example_0 = {"time_start":930,
             "time_end":1500,
             "day":["MWF"]}

example_1 = {"building":"RY",
             "dept":"CMSC",
             "day":["MWF", "TR"],
             "time_start":1030,
             "time_end":1500,
             "enroll_lower":20,
             "terms":"computer science"}

