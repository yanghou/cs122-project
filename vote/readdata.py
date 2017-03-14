import csv, sqlite3

con = sqlite3.connect("pres16results.db")
cur = con.cursor()
cur.execute("CREATE TABLE t (county, fips,cand,st,pct_report,votes,total_votes,pct,lead);") # use your column names here

with open('pres16results.csv') as fin: # `with` statement available in 2.5+
    # csv.DictReader uses first line in file for column headings by default
    dr = csv.DictReader(fin) # comma is default delimiter
    to_db = [(i['county'], i['fips'],i['cand'],i['st'],i['pct_report'],i['votes'],i['total_votes'],i['pct'],i['lead']) for i in dr]

cur.executemany("INSERT INTO t (county, fips,cand,st,pct_report,votes,total_votes,pct,lead) VALUES (?,?,?,?,?,?,?,?,?);", to_db)
con.commit()
con.close()


