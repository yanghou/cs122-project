import sqlite3
import pandas as pd

def query_database(d):
    db=sqlite3.connect('data.db')
    c=db.cursor()
    command1='select '
    command2='select '
    command3='select margin from data;'
    if len(d['independent'])==1:
        command1=command1+d['independent'][0]+' from data;'
    else:
        for item in d['independent']:
            command1=command1+item[0]+', '
        command1=command1[:-2]+' from data;'
    c.excecute(command1)
    names1=get_header(c)
    independent1=c.fetchall()
    if len(d['control'])==1:
        command2=command2+d['control'][0]+' from data;'
    else:
        for item in d['control']:
            command2=command2+item[0]+', '
        command2=command2[:-2]+' from data;'
    c.excecute(command2)
    names2=get_header(c)
    control1=c.fetchall()
    c.excecute(command3)
    names3=get_header(c)
    margin1=c.fetchall()
    independent=pd.DataFrame(independent1)
    independent=independent.transpose()
    independent.columns=names1
    control=pd.DataFrame(control1)
    control=control.transpose()
    control.columns=names2
    margin=pd.DataFrame(margin1)
    margin=margin.transpose()
    margin.columns=names3
    return independent,control,margin