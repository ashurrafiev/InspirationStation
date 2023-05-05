CREATE TYPE mod_status AS ENUM (
    'new',
    'block',
    'ok',
    'star'
);

-- ALTER TYPE mod_status OWNER TO username;

SET default_tablespace = '';

SET default_table_access_method = heap;

CREATE TABLE stories (
    uid uuid NOT NULL,
    obj character varying(32) NOT NULL,
    q1 text,
    q2 text,
    q3 text,
    "time" timestamp without time zone NOT NULL,
    mod mod_status DEFAULT 'new'::mod_status NOT NULL,
    ip inet NOT NULL,
    editor text,
    upd_time timestamp without time zone
);

-- ALTER TABLE stories OWNER TO username;

ALTER TABLE ONLY stories
    ADD CONSTRAINT stories_pkey PRIMARY KEY (uid);

