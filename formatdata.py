# CS 122 Project
#
# Christopher Summers

import numpy as np
import pandas as pd
import urllib3
import json

SUMMARY_FILE_URL = "http://api.census.gov/data/2015/acs5?"
SUBJECT_TABLE_URL = "http://api.census.gov/data/2015/acs5/subject?"
ELECTION_FILE = "./pres16results.csv"

SUMMARY_FILE_VARS = {'male': '002', 'female': '026', 'female_alt': '017',
                     'whitelatino': 'A', 'black': 'B', 'native': 'C', 
                     'asian': 'D', 'islander': 'E', 'other': 'F',
                     'multiracial': 'G', 'white': 'H', 'latino': 'I'}


def get_election_results():
    '''
    Reads in the election csv file, cleans and munges the data, and returns a 
    pandas DataFrame with the following columns:
        county_name: (string)
        fips: (string) 5 digit unique code for each county (note: many of 
            these start with 0)
        state: 2 digit code for the state; the first 2 digits of the fips code
        county: (string) 3 digit code; last 3 digits of the fips code
        st: (string) 2 letter state code
        votes_clinton: number of clinton votes
        votes_trump: number of trump votes
        total_votes: total votes in that county
        pct_clinton: percent of clinton votes for that county
        pct_trump: percent of trump votes for that county
        lead: (string) the name of the leading candidate in that county
    '''
    results = pd.read_csv(ELECTION_FILE, dtype=str)
    columns = list(results.columns.values)
    columns = ['county_name'] + columns[1:]
    results.columns = columns

    results = results[results.fips.str.len() != 2]
    results = results.dropna()
    results.fips = results.fips.str.pad(5, fillchar="0")
    results.sort_values('fips', inplace=True)

    results_clinton = results[results.cand == "Hillary Clinton"]
    results_trump = results[results.cand == "Donald Trump"]
    results_trump = results_trump.loc[:,['fips','votes', 'pct']]
    results = pd.merge(results_clinton, results_trump, on=['fips'], 
        suffixes = ("_clinton", "_trump"))

    results.insert(2, 'state', results.fips.str.slice(0,2))
    results.insert(3, 'county', results.fips.str.slice(2))
    results = results.iloc[:,[0,1,2,3,5,7,11,8,9,12,10]]

    results[results.columns[5:10]] = results[results.columns[5:10]].astype(np.float32)
    mgn = (results.votes_trump - results.votes_clinton) / results.total_votes
    results.insert(10,"margin", mgn)

    results.to_csv("election_results.csv")
    return results


def create_pandas_from_url(url):
    '''
    Takes a census ACS API url string and returns that string as a DataFrame
    '''
    pm = urllib3.PoolManager()
    print("url:", url)
    r = pm.request('GET', url)
    table = json.loads(r.data.decode('utf-8'))
    array = np.array(table[1:])
    df = pd.DataFrame(array[1:], columns=table[0])
    print("HELLO!!")

    return df


def get_summary_file_table(var_dict, state="*", county="*"):
    '''
    Input:
        var_dict: an ACS variable dictionary with 'id' and 'name'
        state: 2 digit state code, use default value "*" to include all states
        county: 3 digit county code

    Returns:
        a pandas DataFrame
    '''
    # Get the total population (B01001_001E) and all other variables chosen
    var_id = var_dict['id']
    divisor = var_dict['divisor']
    if divisor is None:
        divisor = ''
        normalize = False
    else:
        divisor = "," + divisor
        normalize = True

    get_string = "get={}{}".format(var_id, divisor)
    for_string = "&for=county:{}&in=state:{}".format(county, state)
    url = SUMMARY_FILE_URL + get_string + for_string
    df = create_pandas_from_url(url)

    # Normalize values
    df[df.columns[:-2]] = df[df.columns[:-2]].astype(np.float32)
    if normalize:
        columns = [var_id, divisor[1:]]
        df[var_id] = df[var_id] / df[divisor[1:]]

    # Formatting
    df = df.loc[:,['state','county',var_id]]
    df.columns = ['state','county',var_dict.get('name', var_id)]

    return df


def merge_acs_election(acs):
    '''
    Combines an acs table with the election results
    '''
    if not 'state' in acs.columns:
        raise ValueError('acs data missing state column')
    if not 'county' in acs.columns:
        raise ValueError('acs data missing county column')

    election_results = get_election_results()
    election_results = election_results.loc[:,
        ['fips','state','county','margin','lead']]
    df = pd.merge(election_results, acs, on=['state','county'])

    return df


def create_single_variable_table(var_dict, state="*", county="*"):
    '''
    Creates a table with the election results of each county, along with the
    the values of the chosen variable.
    '''
    acs = get_summary_file_table(var_dict, state, county)
    df = merge_acs_election(acs)

    return df


def create_acs_multitable(variable_dicts, state="*", county="*"):
    '''
    Takes a list of Census API variable names, and retrieves the data on that 
    variable for the state and county specified. A value of '*' for state or 
    county will return data for all states or counties.
    '''
    acs = get_summary_file_table(variable_dicts[0], state, county)
    for var_dict in variable_dicts[1:]:
        df = get_summary_file_table(var_dict, state, county)
        acs = pd.merge(acs, df, on=['state','county'])

    return acs


def create_multi_variable_table(var_dicts, state='*', county='*'):
    '''
    Takes a list of variable dictionaries and returns the merged data.
    '''
    acs = create_acs_multitable(var_dicts, state=state, county=county)
    df = merge_acs_election(acs)

    return df