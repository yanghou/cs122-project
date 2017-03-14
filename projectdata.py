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

SUMMARY_FILE_VARS = {'male': '002', 'female': '026',
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

    return results


def create_pandas_from_url(url):
    '''
    Takes a census ACS API url string and returns that string as a DataFrame
    '''
    pm = urllib3.PoolManager()
    r = pm.request('GET', url)
    table = json.loads(r.data.decode('utf-8'))
    array = np.array(table[1:])
    df = pd.DataFrame(array[1:], columns=table[0])

    return df


def get_summary_file_table(variable, state="*", county="*"):
    '''
    Input:
        variable: (string) a variable code name (B01001_001E, etc.)
        state: 2 digit state code, use default value "*" to include all states
        county: 3 digit county code

    Returns:
        a pandas DataFrame
    '''
    # Get the total population (B01001_001E) and all other variables chosen
    get_string = "get=NAME,B01001_001E,{}".format(variable)
    for_string = "&for=county:{}&in=state:{}".format(county, state)
    url = SUMMARY_FILE_URL + get_string + for_string
    df = create_pandas_from_url(url)

    # Convert population numbers to percentages of total
    columns = ['B01001_001E', variable]
    df[columns] = df[columns].astype(np.float32)
    df[variable] = df[variable] / df['B01001_001E']

    df = df.loc[:,['NAME','state','county',variable]]

    return df


def get_summary_variable_id(var_dict):
    '''
    '''
    race = var_dict.get('race', None)
    sex = var_dict.get('sex', None)

    race_id = SUMMARY_FILE_VARS.get(race, "")
    sex_id = SUMMARY_FILE_VARS.get(sex, "001")
    variable_id = "B01001{}_{}E".format(race_id, sex_id)

    return variable_id


def get_demographic_data(variables, state="*", county="*"):
    '''
    '''
    rv_df = get_summary_file_table(variables[0], state, county)
    rv_df = rv_df.loc[:,['state','county',variables[0]]]
    for var in variables[1:]:
        df = get_summary_file_table(var, state, county)
        df = df.loc[:,['state','county',var]]
        rv_df = pd.merge(rv_df, df, on=['state','county'])

    return rv_df


def get_data_from_variable_dicts(var_dicts, state='*', county='*'):
    '''
    '''
    variables = []
    for d in var_dicts:
        variables.append(get_summary_variable_id(d))

    demographics = get_demographic_data(variables, state=state, county=county)
    election_results = get_election_results()

    df = pd.merge(election_results, demographics, on=['state','county'])
    df = df.loc[:,['fips','state','county','pct_clinton','pct_trump','lead']
        + variables]
    return df


def create_variable_dict(sex=None, race=None, employment=None, income=None):
    d = {'sex': sex, 'race': race, 'employment': employment, 'income': income}
    return d
    

if __name__ == '__main__':
    var_dicts = []
    var_dicts.append(create_variable_dict('male'))
    var_dicts.append(create_variable_dict('female'))
    var_dicts.append(create_variable_dict('male', 'white'))
    var_dicts.append(create_variable_dict(race='black'))

    df = get_data_from_variable_dicts(var_dicts)
    print(df)

    
