CREATE TYPE public.mod_status AS ENUM (
    'new',
    'block',
    'ok',
    'star'
);

ALTER TYPE public.mod_status OWNER TO local;

SET default_tablespace = '';

SET default_table_access_method = heap;

CREATE TABLE public.stories (
    uid uuid NOT NULL,
    obj character varying(32) NOT NULL,
    q1 text,
    q2 text,
    q3 text,
    "time" timestamp without time zone NOT NULL,
    mod public.mod_status DEFAULT 'new'::public.mod_status NOT NULL,
    ip inet NOT NULL,
    editor text,
    upd_time timestamp without time zone
);

ALTER TABLE public.stories OWNER TO local;

ALTER TABLE ONLY public.stories
    ADD CONSTRAINT stories_pkey PRIMARY KEY (uid);

