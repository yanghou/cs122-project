# CS 122 Project
#
# Chris Summers

import pandas as pd
import numpy as np
import model
import query


def analyze(query_dict):
    
    i_var = query_dict.get('independent', None)
    c_var = [x for (x,y) in query_dict.get('control', [])]
    c_values = [y for (x,y) in query_dict.get('control', [])]
    d_var = ['margin']

    if i_var is None:
        return [(None, None)]

    fuckthis = '''
    independent, control, margin = query.query_database(query_dict)
    data = pd.merge(independent, control, on='fips')
    data = pd.merge(data, margin, on='fips').iloc[:,1:]
    i_data = independent.iloc[:,1:]
    d_data = margin.iloc[:,1:]
    c_data = control.iloc[:,1:]
    '''

    i_var = query_dict['independent']
    c_var = [x for (x,y) in query_dict['control']]
    c_values = [y for (x,y) in query_dict['control']]
    d_var = ['margin']

    data = get_data()    
    analysis_model = model.Model(data, d_var, i_var, c_var, c_values=c_values)
    b_dict = analysis_model.go(values=c_values)
    rv = []
    for key, value in b_dict.items():
        rv.append((key, value))

    return rv



def get_data():
    data = pd.read_csv('data_without_nans.csv',
        dtype={'fips': str, 'state': str, 'county': str})
    data = data.iloc[:,1:]
    return data



if __name__ == "__main__":
    d = {"independent":['p_labor_force', 'p_white'], 
        'control':[('median_income', None), ('p_unemployed',0.9), ('p_no_highschool',None)]}
    result = analyze(d)