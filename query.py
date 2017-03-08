import sqlite3
import pandas as pd

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

def query_database(d):
    db=sqlite3.connect('data.db')
    c=db.cursor()
    command1='select fips,'
    command2='select fips,'
    command3='select fips,margin from data;'
    if len(d['independent'])==1:
        command1=command1+d['independent'][0]+' from data;'
    else:
        for item in d['independent']:
            command1=command1+item+', '
        command1=command1[:-2]+' from data;'
    c.execute(command1)
    names1=get_header(c)
    independent1=c.fetchall()
    if 'control' not in d:
        control=None
    else:
        if len(d['control'])==1:
            command2=command2+d['control'][0][0]+' from data;'
        else:
            for item in d['control']:
                command2=command2+item[0]+', '
            command2=command2[:-2]+' from data;'
        c.execute(command2)
        names2=get_header(c)
        control1=c.fetchall()
        control=pd.DataFrame(control1)
        control.columns=names2
    c.execute(command3)
    names3=get_header(c)
    margin1=c.fetchall()
    independent=pd.DataFrame(independent1)
    independent.columns=names1
    margin=pd.DataFrame(margin1)
    margin.columns=names3
    return independent,control,margin