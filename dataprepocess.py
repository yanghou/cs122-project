import pandas as pd
import copy

data=pd.read_csv('data.csv',skiprows=[0],names=['id','fips','state','county','pct_clinton','pct_trump','lead','percent_female','percent_white','percent_black','percent_latino','percent_white_male','Gini_Coefficient','per_capita_income','per_capita_income_amongst_whites','unemployment_rate','no_highschool_diploma','unemployment_rate_no_highschool','labor_force_participation_rate','white_men_with_highschool_diploma'])
geo=pd.read_csv('geocodes.csv',skiprows=[0],names=['id','fips','state','county','full_name','state_name','county_name'])
data=data.drop('id',axis=1)
data.to_csv('data_new.csv',index=False)
geo=geo.drop('id',axis=1)
geo.to_csv('geo_new.csv',index=False)