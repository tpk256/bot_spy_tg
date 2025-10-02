import sqlite3


con = sqlite3.connect("../msgs.db")



cur = con.cursor()

with open("scheme.sql", mode='r') as scheme:

    for statement in scheme.read().split(';'):
        cur.execute(statement)
        con.commit()


con.close()