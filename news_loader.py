import psycopg2

dbname = "news_articles"
dbhost = "150.162.58.58"
dbuser = "postgres"
dbpass = "Trajetorias123"


def connect():
    return psycopg2.connect("dbname='" + dbname +
                            "' user='" + dbuser +
                            "' host='" + dbhost +
                            "' password='" + dbpass + "'")

def load_news(fields=['id', 'title', 'text', 'portal']):
    
    conn = connect()
    cur = conn.cursor()
    field_names = str(fields).replace("'", "") \
                             .replace("[", "") \
                             .replace("]", "")

    query = "SELECT " + field_names + " FROM news WHERE date_time <= '22/10/2018' AND date_time >= '22/09/2018' ORDER BY id ASC"
    news = []

    cur.execute(query)
    for values in cur.fetchall():
        data = dict(zip(fields, values))
        news.append(data)

    return news


def load_distinct(field_name):
    
    conn = connect()
    cur = conn.cursor()

    query = "SELECT DISTINCT" + field_name + "FROM news WHERE date_time <= '22/10/2018' AND date_time >= '22/09/2018'"
    
    cur.execute(query)

    fields = []
    for field in cur.fetchall():
        fields.append(field[0])

    return fields


def add_score(ids, field, score):
    conn = connect()
    cur = conn.cursor()

    query = "INSERT INTO similarity (news_id1, news_id2, " + field + ") VALUES (:id1, :id2, :score)"
    query = query.replace(":id1", str(ids[0]))
    query = query.replace(":id2", str(ids[1]))
    query = query.replace(":score", str(score))
    cur.execute(query)
