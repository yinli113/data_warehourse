#!/usr/bin/env python
# coding: utf-8

# ensure that the data has been successfully transformed and loaded into the target tables, we will do the fianl test
# 
# 
# 
# 

# In[1]:


import configparser
import psycopg2

# CONFIG
config = configparser.ConfigParser()
config.read('dwh.cfg')

def main():
    config = configparser.ConfigParser()
    config.read('dwh.cfg')

    host = config.get('CLUSTER', 'host')
    dbname = config.get('CLUSTER', 'dbname')
    user = config.get('CLUSTER', 'user')
    password = config.get('CLUSTER', 'password')
    port = config.getint('CLUSTER', 'port')  

    conn = psycopg2.connect(
        host=host,
        dbname=dbname,
        user=user,
        password=password,
        port=port
    )
    cur = conn.cursor()

    # Run SELECT COUNT(*) queries to check the data in  Redshift tables
    queries = [
        "SELECT COUNT(*) FROM staging_events;",
        "SELECT COUNT(*) FROM staging_songs;",
        "SELECT COUNT(*) FROM songplays;",
        "SELECT COUNT(*) FROM users;",
        "SELECT COUNT(*) FROM songs;",
        "SELECT COUNT(*) FROM artists;",
        "SELECT COUNT(*) FROM times;"
    ]

    for query in queries:
        cur.execute(query)
        result = cur.fetchone()
        print(f"Result of {query}: {result[0]}")

    conn.close()

if __name__ == "__main__":
    main()


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:



 


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




