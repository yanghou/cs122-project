### CS122, Winter 2017: Course search engine: search
###
### Huanye Liu

from math import radians, cos, sin, asin, sqrt
import sqlite3
import json
import re
import os
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from mpl_toolkits.basemap import Basemap
# Use this filename for the database
DATA_DIR = os.path.dirname(__file__)
DATABASE_FILENAME = os.path.join(DATA_DIR, 'pres16results.db')

# a dictionary translating the abbrieviation to full name of the state
abbr_to_name = {
        'AK': 'Alaska',
        'AL': 'Alabama',
        'AR': 'Arkansas',
        'AS': 'American Samoa',
        'AZ': 'Arizona',
        'CA': 'California',
        'CO': 'Colorado',
        'CT': 'Connecticut',
        'DC': 'District of Columbia',
        'DE': 'Delaware',
        'FL': 'Florida',
        'GA': 'Georgia',
        'GU': 'Guam',
        'HI': 'Hawaii',
        'IA': 'Iowa',
        'ID': 'Idaho',
        'IL': 'Illinois',
        'IN': 'Indiana',
        'KS': 'Kansas',
        'KY': 'Kentucky',
        'LA': 'Louisiana',
        'MA': 'Massachusetts',
        'MD': 'Maryland',
        'ME': 'Maine',
        'MI': 'Michigan',
        'MN': 'Minnesota',
        'MO': 'Missouri',
        'MP': 'Northern Mariana Islands',
        'MS': 'Mississippi',
        'MT': 'Montana',
        'NA': 'National',
        'NC': 'North Carolina',
        'ND': 'North Dakota',
        'NE': 'Nebraska',
        'NH': 'New Hampshire',
        'NJ': 'New Jersey',
        'NM': 'New Mexico',
        'NV': 'Nevada',
        'NY': 'New York',
        'OH': 'Ohio',
        'OK': 'Oklahoma',
        'OR': 'Oregon',
        'PA': 'Pennsylvania',
        'PR': 'Puerto Rico',
        'RI': 'Rhode Island',
        'SC': 'South Carolina',
        'SD': 'South Dakota',
        'TN': 'Tennessee',
        'TX': 'Texas',
        'UT': 'Utah',
        'VA': 'Virginia',
        'VI': 'Virgin Islands',
        'VT': 'Vermont',
        'WA': 'Washington',
        'WI': 'Wisconsin',
        'WV': 'West Virginia',
        'WY': 'Wyoming'
}




def search(args_from_ui):
    '''

    Takes a dictionary containing state name abbreviation for 
    plotting the winning party on a map and returns the number
    of votes for each candidate of the state.

    example {'state':'TX'}

    Return: a list of tuples containing the number of votes for
    each candidate of the state.
    '''
    if args_from_ui =={}:
        return None
  
    db = sqlite3.connect(DATABASE_FILENAME)
    c = db.cursor()
    if 'state' in args_from_ui:
        query='select cand,votes from t where fips=?'
        arg = args_from_ui['state']

    r = c.execute(query,[arg])
    # result is a list of tuples
    result = r.fetchall()
    c.close()
    
    # translate the abbrieviation to full name of the state
    state_name = abbr_to_name[arg]
    # the name of leading candidate of the state
    lead = result[0][0]
    
     
    # plotting on the map
    m = Basemap(llcrnrlon=-119,llcrnrlat=22,urcrnrlon=-64,urcrnrlat=49,
                             projection='lcc',lat_1=33,lat_2=45,lon_0=-95)
    m.readshapefile('statesp020', name='states', drawbounds=True)
    # collect the state names from the shapefile attributes so we can
        # look up the shape obect for a state by it's name
    state_names = []
    for shape_dict in m.states_info:
        state_names.append(shape_dict['STATE'])
            


    # fill corresponding color in the map based on who wins 
    ax = plt.gca()   
    if state_name != 'US':
        seg = m.states[state_names.index(state_name)]
        if lead =='Donald Trump':
            poly = Polygon(seg,facecolor = 'red', edgecolor='red')
        elif lead == 'Hillary Clinton':
            poly = Polygon(seg,facecolor = 'blue', edgecolor='blue')
        ax.add_patch(poly)
    plt.title("Red or Blue?",fontsize=20)    
    graph_path = os.path.join(DATA_DIR,'static')
    plt.savefig(os.path.join(graph_path,'map.png')) 
    plt.clf()    

    return result


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

