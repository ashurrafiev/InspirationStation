from psycopg2 import connect
from psycopg2 import Error as PostgresError

import cherrypy


def db_connect(cfg):
    db = cfg['database']
    return connect(
        host=db['host'],
        port=db.get('port', 5432),
        user=db.get('user', 'root'),
        password=db.get('pwd', ''),
        database=db['name']
    )

def post_story(cfg, data):
    try:
        with db_connect(cfg) as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO "stories" ("uid", "obj", "q1", "q2", "q3", "time")
                    VALUES (gen_random_uuid(), %(obj)s, %(q1)s, %(q2)s, %(q3)s, now())
                    RETURNING "uid"
                """, data)
                row = cursor.fetchone()
                connection.commit()
                return row[0] if row else None
    except PostgresError as e:
        cherrypy.log.error(f"Database error: {str(e)}")
        raise cherrypy.HTTPError(500)

def get_story(cfg, uid):
    try:
        with db_connect(cfg) as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT "obj", "q1", "q2", "q3",
                        extract(epoch from "time")::integer
                    FROM "stories"
                    WHERE "uid"=%s
                """, (uid,))
                row = cursor.fetchone()
                if row:
                    return dict(zip(['obj', 'q1', 'q2', 'q3', 'time'], row))
                else:
                    return None
    except PostgresError as e:
        cherrypy.log.error(f"Database error: {str(e)}")
        raise cherrypy.HTTPError(500)

def list_stories(cfg, p=0, lim=100):
    try:
        with db_connect(cfg) as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT "uid", "obj", "q1", "q2", "q3", "time", "mod"
                    FROM "stories"
                    ORDER BY "time" DESC
                    LIMIT %s OFFSET %s
                """, (lim, p*lim))
                rows = cursor.fetchall()
                return rows
    except PostgresError as e:
        cherrypy.log.error(f"Database error: {str(e)}")
        raise cherrypy.HTTPError(500)
