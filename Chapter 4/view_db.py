import pandas as pd
import sqlite3

connection = sqlite3.connect('planets.db')
planets = pd.read_sql_query("SELECT * FROM planets", connection)
users   = pd.read_sql_query("SELECT * FROM users", connection)

print(planets)
print(users)

connection.close()