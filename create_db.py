import psycopg2

dbname = "news_articles"
dbhost = "localhost"
dbuser = "postgres"
dbpass = "postgres"
conn = psycopg2.connect("dbname='" + dbname +
                        "' user='" + dbuser +
                        "' host='" + dbhost +
                        "' password='" + dbpass + "'")
cur = conn.cursor()
cur.execute("""

CREATE TABLE news(
    id INTEGER PRIMARY KEY,
    title VARCHAR(200),
    subtitle VARCHAR(300),
    date_time TIMESTAMP WITHOUT TIME ZONE,
    text TEXT,
    authors VARCHAR(200),
    tags VARCHAR(300),
    subject VARCHAR(100),
    portal VARCHAR(100)
)
""")
conn.commit()
conn.close()
