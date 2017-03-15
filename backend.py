# CS 122 Project
#
# Chris Summers

import pandas as pd
import numpy as np
import model
import query


def analyze(query_dict):
    '''
    Takes in a query dictionary with a list of variable names for 'independent'
    and a list of tuples for 'control'. Creates a model based on these 
    variables and runs the analysis of the model.

    Returns: the beta values for the independnet and control variables
    '''
    i_var = query_dict.get('independent', None)
    c_var = [x for (x,y) in query_dict.get('control', [])]
    c_values = [y for (x,y) in query_dict.get('control', [])]
    d_var = ['margin']

    if i_var is None:
        return [(None, None)]

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
    '''
    Returns a full pandas DataFrame of all the data
    '''
    data = pd.read_csv('data_without_nans.csv',
        dtype={'fips': str, 'state': str, 'county': str})
    data = data.iloc[:,1:]
    return data


def get_variable_names():
    '''
    Retrieves the variable name assignments from the variables.csv fil.
    Also creates a dictionary relating database names to axes names.
    '''
    variable_display_names = pd.read_csv('variables.csv')
    name_dict = {}
    for i, row in variable_display_names.iterrows():
        name_dict[row['Name in Database']] = row['Axes Name']
    return variable_display_names, name_dict


if __name__ == "__main__":
    d = {"independent":['p_labor_force', 'p_white'], 
        'control':[('median_income', None), 
                  ('p_unemployed',0.05), 
                  ('p_no_highschool',None)]
        }
    result = analyze(d)
