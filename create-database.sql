create table  geocodes (
    fips text,
    state text,
    county text,
    full_name text,
    state_name text,
    county_name text,
    primary key (fips));

.separator ","
.import geo_new.csv geocodes

create table data (
    fips text,
    state text,
    county text,
    margin numeric,
    lead text,
    p_female numeric,
    p_white numeric,
    median_age numeric,
    p_no_highschool numeric,
    p_unemployed numeric,
    p_labor_force numeric,
    median_income numeric,
    gini numeric,
    p_poverty numeric,
    median_mfr_income numeric,
    p_foreign_born numeric,
    p_american numeric,
    foreign key (fips) references geocodes (fips));

.import data_new.csv data