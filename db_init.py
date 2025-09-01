import sqlite3


con = sqlite3.connect("msgs.db")



cur = con.cursor()

with open("scheme.sql", mode='r') as scheme:
    cur.execute(scheme.read())


con.commit()

con.close()