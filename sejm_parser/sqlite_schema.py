def create_tables(c):
    c.cursor().execute(
        '''CREATE TABLE IF NOT EXISTS summary(ID INTEGER PRIMARY KEY AUTOINCREMENT, summary VARCHAR(4000), project_id VARCHAR(4000), date DATETIME, project_url VARCHAR(2000), title VARCHAR(4000), hashtags VARCHAR(4000), long_summary VARCHAR(4000),process_id VARCHAR(4000), document_date VARCHAR(30), process_url VARCHAR(4000))''')

    c.commit()
    c.close()
