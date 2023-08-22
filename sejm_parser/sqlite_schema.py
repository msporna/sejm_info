def create_tables(c):
    c.cursor().execute(
        '''CREATE TABLE IF NOT EXISTS summary(ID INTEGER PRIMARY KEY AUTOINCREMENT, summary VARCHAR(4000), project_id VARCHAR(4000), date DATETIME, project_url VARCHAR(2000), title VARCHAR(4000), hashtags VARCHAR(4000), long_summary VARCHAR(4000),process_id VARCHAR(4000), document_date VARCHAR(30), process_url VARCHAR(4000))''')
    c.cursor().execute(
        '''CREATE TABLE IF NOT EXISTS poslowie(ID INTEGER PRIMARY KEY AUTOINCREMENT, first_name_last_name VARCHAR(100), club VARCHAR(100), dob VARCHAR(100),education VARCHAR(100),district_name VARCHAR(100),number_of_votes VARCHAR(100), place_of_birth VARCHAR(100), photo VARCHAR(4000), posel_id VARCHAR(20))''')

    c.commit()
    c.close()
