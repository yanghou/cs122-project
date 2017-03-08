import pandas as pd

data=pd.read_csv('data.csv',dtype={'fips':object,'state':object,'county':object},skiprows=[0],names=['id','fips','state','county','margin','lead','p_female','p_white','median_age','p_no_highschool','p_unemployed','p_labor_force','median_income','gini','p_poverty','median_mfr_income','p_foreign_born','p_american'])
geo=pd.read_csv('geocodes.csv',dtype={'fips':object,'state':object,'county':object},skiprows=[0],names=['id','fips','state','county','full_name','state_name','county_name'])
data=data.drop('id',axis=1)
data.to_csv('data_new.csv',index=False,header=False)
geo=geo.drop('id',axis=1)
geo.to_csv('geo_new.csv',index=False,header=False)