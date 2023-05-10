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

def post_story(cfg, user, ip, data):
    data['ip'] = ip
    if user:
        data['user'] = user
        query = """
            INSERT INTO "stories" ("uid", "obj", "q1", "q2", "q3", "mod", "ip", "time", "editor", "upd_time")
            VALUES (gen_random_uuid(), %(obj)s, %(q1)s, %(q2)s, %(q3)s, %(mod)s, %(ip)s, now(), %(user)s, now())
            RETURNING "uid"
        """
    else:
        query = """
            INSERT INTO "stories" ("uid", "obj", "q1", "q2", "q3", "ip", "time")
            VALUES (gen_random_uuid(), %(obj)s, %(q1)s, %(q2)s, %(q3)s, %(ip)s, now())
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

def update_story(cfg, uid, user, data):
    query = """
        UPDATE "stories"
        SET "obj" = %(obj)s, "q1" = %(q1)s, "q2" = %(q2)s, "q3" = %(q3)s,
            "mod" = %(mod)s, "editor" = %(user)s, "upd_time" = now()
        WHERE "uid" = %(uid)s
    """
    try:
        data['uid'] = uid
        data['user'] = user
        with db_connect(cfg) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, data)
                connection.commit()
    except PostgresError as e:
        cherrypy.log.error(f"Database error: {str(e)}")
        raise cherrypy.HTTPError(500)

def get_story(cfg, uid):
    query = """
        SELECT "obj", "q1", "q2", "q3", "mod",
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
                    return dict(zip(['obj', 'q1', 'q2', 'q3', 'mod', 'time'], row))
                else:
                    return None
    except PostgresError as e:
        cherrypy.log.error(f"Database error: {str(e)}")
        raise cherrypy.HTTPError(500)

def get_story_raw(cfg, uid):
    query = """
        SELECT "uid", "obj", "q1", "q2", "q3", "time", "mod", "ip", "editor", "upd_time"
        FROM "stories"
        WHERE "uid" = %s
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

def list_stories(cfg, sel, p=0, lim=100, count_only=False, random_order=False):
    order_by = 'random()' if random_order else '"time"'
    query = f"""
        SELECT "uid", "obj", "q1", "q2", "q3", "time", "mod", "ip", "editor", "upd_time"
        FROM "stories"
        WHERE "mod" IN %(sel)s
        ORDER BY {order_by} DESC
        LIMIT %(lim)s OFFSET %(offs)s
    """
    query_total = """
        SELECT
            COALESCE(SUM(CASE WHEN "mod" = 'new' THEN 1 ELSE 0 END), 0) AS "new",
            COALESCE(SUM(CASE WHEN "mod" IN %(sel)s THEN 1 ELSE 0 END), 0) AS "sel",
            COUNT(*) AS "total"
        FROM "stories"
    """
    try:
        sel = tuple(sel)
        with db_connect(cfg) as connection:
            with connection.cursor() as cursor:
                if count_only:
                    rows = []
                else:
                    cursor.execute(query, {'sel':sel, 'lim':lim, 'offs':p*lim})
                    rows = cursor.fetchall()
                cursor.execute(query_total, {'sel': sel})
                counts = dict(zip(['new','sel','total'], cursor.fetchone()))
                return counts, rows
    except PostgresError as e:
        cherrypy.log.error(f"Database error: {str(e)}")
        raise cherrypy.HTTPError(500)

def set_mod(cfg, sel, user, mod):
    query = """
        UPDATE "stories"
        SET "mod" = %(mod)s, "editor" = %(user)s, "upd_time" = now()
        WHERE "uid" IN %(sel)s
    """
    query_returning = """
        RETURNING "uid", "obj", "q1", "q2", "q3", "time", "mod", "ip", "editor", "upd_time"
    """
    try:
        fetch = False
        if len(sel)==1:
            query = query + query_returning
            fetch = True
        sel = tuple(sel)
        with db_connect(cfg) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, {'sel':sel, 'mod':mod, 'user':user})
                row = cursor.fetchone() if fetch else None
                connection.commit()
                return row
    except PostgresError as e:
        cherrypy.log.error(f"Database error: {str(e)}")
        raise cherrypy.HTTPError(500)
