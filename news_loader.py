import psycopg2

dbname = "news_articles"
dbhost = "localhost"
dbuser = "postgres"
dbpass = "postgres"


def load_news(fields=['id', 'title', 'text', 'portal']):
    conn = psycopg2.connect("dbname='" + dbname +
                            "' user='" + dbuser +
                            "' host='" + dbhost +
                            "' password='" + dbpass + "'")

    cur = conn.cursor()
    field_names = str(fields).replace("'", "") \
                             .replace("[", "") \
                             .replace("]", "")

    query = "SELECT " + field_names + " FROM news"
    news = []

    cur.execute(query)
    for values in cur.fetchall():
        data = dict(zip(fields, values))
        news.append(data)

    return news
