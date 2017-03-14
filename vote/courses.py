### CS122, Winter 2017: Course search engine: search
###
### Huanye Liu

from math import radians, cos, sin, asin, sqrt
import sqlite3
import json
import re
import os


# Use this filename for the database
DATA_DIR = os.path.dirname(__file__)
DATABASE_FILENAME = os.path.join(DATA_DIR, 'course-info.db')

  


def catalog_tables(keywords):
    '''
    The function takes a string of key terms that the user enters, 
    and returns a tuple of two strings the first of which containing 
    the 'JOIN' tables to be use in the FROM clause and the second of 
    which to be used in the WHERE clause.
    Inputs:
        keywords: a string of key terms entered by the  user
    Return:
         a tuple of strings representing the number of catalog_index 
         tables needed in the FROM clause and the corresponding modification 
         in the WHERE clause.  
    '''
    key_list = keywords.split()
    num = len(key_list)
    if num==1:
        return (['catalog_index','courses'],'word= ?')
    result1list=[]
    result2list=[]
    for i in range(1,num+1):
        result1list.append('catalog_index AS catalog'+str(i))
        result2list.append('catalog'+str(i)+'.word = ?')
    result1list.append('courses')
    return (result1list, result2list)

def day_where(daylist):
    '''
    The function returns a sql where clause based on the number of 
    strings in the input.
    Input:
        a list of strings representing day in a week
    Returns:
        a string connecting separate clause using OR 
    '''
    num = len(daylist)
    if num==1:
        return 'day = ?'
    resultlist=[]
    for i in range(num):
        resultlist.append('day = ?')
    tmp= ' OR '.join(resultlist)
    return '('+tmp+')'

def merge_list(args_from_ui,dictionary,S_F):
    '''
    The function contructs the sql select clause list or from
    clause list based on the value of S_F.
    Inputs:
       args_from_ui: a dictionary containing search criteria.
       dictionary: one of the first two dictionaries defined in 
                   the find_courses function: select_dict or 
                   from_dict
       S_F: specify whether we want to construct the select clause
            list or the from clause list.
     
    Returns:
       a list of attributes for the select clause or a list of table
       names for the from clause.
    '''
    # collecting all attribute names or all table names in tmp_list
    tmp_list=[]
    for key in args_from_ui:
        tmp_list+=(dictionary[key])
    tmp_set=set(tmp_list)
    rv_list = list(tmp_set)
    # if try to figure out the select clause, we follow the required 
    # order
    if S_F == 'S':
        # specify the order
        SORT_ORDER ={'dept':0,'course_num':1,'section_num':2,'day':3,\
                     'time_start':4,'time_end':5,'building':6,\
                     'walking_time':7,'enrollment':8,'title':9}
        rv_list.sort(key=lambda val: SORT_ORDER[val])
    # if try to figure out the from clause, we don't care the order
    return rv_list




def construct_sql(args_from_ui, select_dict, from_dict, where_dict):
    '''
    The function contructs a complete sql query and an argument list based on 
    the args_from_ui and the three dictionaries specifying the select, from 
    and where clauses.
    Inputs:
       args_from_ui:a dictionary containing search criteria from user input
       select_dict: a dictionary used to construct the select clause from user input 
       from_dict: a dictionary used to construct the from clause from user input
       where_dict: a dictionary used to construct the where clause from user input
    Returns:
       a string of a complete sql query and a list of arguments
    '''
    select_list = merge_list(args_from_ui, select_dict, 'S')
    select_clause = ', '.join(select_list)
    from_list = merge_list(args_from_ui,from_dict,'F')
    from_clause = ' JOIN '.join(from_list)
    # the following code fragment constructs the where clause and the argument list
    tmp_list = []
    arg_list = []
    for key in args_from_ui:
        tmp_list += where_dict[key]
        # two special cases:
        if key=='terms':
            for word in args_from_ui[key].split():
                arg_list.append(word)
        elif key == 'day':
            for day in args_from_ui[key]:
                arg_list.append(day)
        else:
            arg_list.append(args_from_ui[key])
    where_clause = ' AND '.join(tmp_list)
    sql='SELECT '+select_clause+' FROM '+from_clause+' WHERE '+where_clause
    print(sql)
    print(arg_list)
    return (sql,arg_list)


def find_courses(args_from_ui):
    '''
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

    select_dict={'terms':['dept','course_num','title'],
                 'dept':['dept','course_num','title'],
                 'day':['dept','course_num','section_num','day','time_start','time_end'],
                 'time_start':['dept','course_num','section_num','day','time_start','time_end'],
                 'time_end':['dept','course_num','section_num','day','time_start','time_end'],
                 'walking_time':['dept','course_num','section_num','day','time_start','time_end','buildilng','walking_time'],
                 'building':['dept','course_num','section_num','day','time_start','time_end','buildilng','walking_time'],
                 'enroll_lower':['dept','course_num','section_num','day','time_start','time_end','enrollment'],
                 'enroll_upper':['dept','course_num','section_num','day','time_start','time_end','enrollment']}
    terms_value_from= []
    terms_value_where = []
    if 'terms' in args_from_ui:
        terms_value = catalog_tables(args_from_ui['terms'])
        terms_value_from = terms_value[0]
        terms_value_where = terms_value[1]
    from_dict={'terms':terms_value_from,
               'dept':['courses'],
               'day':['courses','sections','meeting_patterns'],
               'time_start':['courses','sections','meeting_patterns'],
               'time_end':['courses','sections','meeting_patterns'],
               'walking_time':['courses','sections','meeting_patterns','gps AS a','gps AS b'],
               'building':['courses','sections','meeting_patterns','gps AS a','gpa AS b'],
               'enroll_lower':['courses','sections','meeting_patterns'],
               'enroll_upper':['courses','sections','meeting_patterns']}
    
    where_dict = {'terms':terms_value_where,
                  'dept':['dept = ?'],
                  'day':[day_where(args_from_ui['day'])],
                  'time_start':['time_start >= ?'],
                  'time_end':['time_end <= ?'],
                  'enroll_lower':['enroll_lower >= ?'],
                  'enroll_upper':['enroll_upper <= ?'],
                  'building':[],
                  'walking_time':[]}
    sql,args = construct_sql(args_from_ui, select_dict, from_dict, where_dict)
    db = sqlite3.connect('course-info.db')
    c = db.cursor()
    r = c.execute(sql,args)
    return (get_header(c), r.fetchall())


########### auxiliary functions #################
########### do not change this code #############

def compute_time_between(lon1, lat1, lon2, lat2):
    '''
    Converts the output of the haversine formula to walking time in minutes
    '''
    meters = haversine(lon1, lat1, lon2, lat2)

    #adjusted downwards to account for manhattan distance
    walk_speed_m_per_sec = 1.1 
    mins = meters / (walk_speed_m_per_sec * 60)

    return mins


def haversine(lon1, lat1, lon2, lat2):
    '''
    Calculate the circle distance between two points 
    on the earth (specified in decimal degrees)
    '''
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 

    # 6367 km is the radius of the Earth
    km = 6367 * c
    m = km * 1000
    return m 



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

