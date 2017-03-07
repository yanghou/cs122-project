create table  geocodes (
    fips integer,
    state integer,
    county integer,
    full_name text,
    state_name text,
    county_name text,
    primary key (fips));

.separator ","
.import geocodes.csv geocodes

create table data (
    fips integer,
    state integer,
    county integer,
    pct_clinton numeric,
    pct_trump numeric,
    lead text,
    percent_female numeric,
    percent_white numeric,
    percent_black numeric,
    percent_latino numeric,
    percent_white_male numeric,
    Gini_Coefficient numeric,
    per_capita_income numeric,
    per_capita_income_amongst_whites numeric,
    unemployment_rate numeric,
    no_highschool_diploma numeric,
    unemployment_rate_no_highschool numeric,
    labor_force_particiipation_rate numeric,
    white_men_with_highschool_diploma numeric,
    foreign key (fips) references geocodes(fips));

.import data.csv data