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
    query = """
        INSERT INTO "stories" ("uid", "obj", "q1", "q2", "q3", "mod", "time")
        VALUES (gen_random_uuid(), %(obj)s, %(q1)s, %(q2)s, %(q3)s, %(mod)s, now())
        RETURNING "uid"
    """
    try:
        with db_connect(cfg) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, data)
                row = cursor.fetchone()
                connection.commit()
                return row[0] if row else None
    except PostgresError as e:
        cherrypy.log.error(f"Database error: {str(e)}")
        raise cherrypy.HTTPError(500)

def update_story(cfg, uid, data):
    query = """
        UPDATE "stories"
        SET "obj" = %(obj)s, "q1" = %(q1)s, "q2" = %(q2)s, "q3" = %(q3)s, "mod" = %(mod)s 
        WHERE "uid" = %(uid)s
    """
    try:
        data['uid'] = uid
        with db_connect(cfg) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, data)
                connection.commit()
    except PostgresError as e:
        cherrypy.log.error(f"Database error: {str(e)}")
        raise cherrypy.HTTPError(500)

def get_story(cfg, uid):
    query = """
        SELECT "obj", "q1", "q2", "q3",
            extract(epoch from "time")::integer
        FROM "stories"
        WHERE "uid"=%s
    """
    try:
        with db_connect(cfg) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (uid,))
                row = cursor.fetchone()
                if row:
                    return dict(zip(['obj', 'q1', 'q2', 'q3', 'time'], row))
                else:
                    return None
    except PostgresError as e:
        cherrypy.log.error(f"Database error: {str(e)}")
        raise cherrypy.HTTPError(500)

def get_story_raw(cfg, uid):
    query = """
        SELECT "uid", "obj", "q1", "q2", "q3", "time", "mod"
        FROM "stories"
        WHERE "uid"=%s
    """
    try:
        with db_connect(cfg) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (uid,))
                row = cursor.fetchone()
                return row
    except PostgresError as e:
        cherrypy.log.error(f"Database error: {str(e)}")
        raise cherrypy.HTTPError(500)

def mod_options():
    return ['new','ok','block','star']

def list_stories(cfg, sel, p=0, lim=100):
    query = """
        SELECT "uid", "obj", "q1", "q2", "q3", "time", "mod"
        FROM "stories"
        WHERE "mod" IN %(sel)s
        ORDER BY "time" DESC
        LIMIT %(lim)s OFFSET %(offs)s
    """
    query_total = """
        SELECT COUNT(*)
        FROM "stories"
        WHERE "mod" IN %(sel)s
    """
    try:
        sel = tuple(sel)
        with db_connect(cfg) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, {'sel':sel, 'lim':lim, 'offs':p*lim})
                rows = cursor.fetchall()
                cursor.execute(query_total, {'sel': sel})
                total = cursor.fetchone()
                return total[0], rows
    except PostgresError as e:
        cherrypy.log.error(f"Database error: {str(e)}")
        raise cherrypy.HTTPError(500)

def set_mod(cfg, sel, mod):
    query = """
        UPDATE "stories"
        SET "mod"=%(mod)s
        WHERE "uid" IN %(sel)s
    """
    query_returning = """
        RETURNING "uid", "obj", "q1", "q2", "q3", "time", "mod"
    """
    try:
        fetch = False
        if len(sel)==1:
            query = query + query_returning
            fetch = True
        sel = tuple(sel)
        with db_connect(cfg) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, {'sel':sel, 'mod':mod})
                row = cursor.fetchone() if fetch else None
                connection.commit()
                return row
    except PostgresError as e:
        cherrypy.log.error(f"Database error: {str(e)}")
        raise cherrypy.HTTPError(500)
