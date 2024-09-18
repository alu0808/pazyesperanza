--
-- PostgreSQL database dump
--

-- Dumped from database version 16.4
-- Dumped by pg_dump version 16.4

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;


--
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- Name: avance_caso_emblematico; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.avance_caso_emblematico (
    id integer NOT NULL,
    nombre_caso character varying(255) NOT NULL,
    ocurrencias_periodo text,
    actividades_realizadas text,
    presencia_participacion text,
    estado_actual text,
    recomendaciones text,
    otro_asunto text,
    responsable_registro character varying(255),
    fecha_registro timestamp without time zone
);


ALTER TABLE public.avance_caso_emblematico OWNER TO postgres;

--
-- Name: avance_caso_emblematico_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.avance_caso_emblematico_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.avance_caso_emblematico_id_seq OWNER TO postgres;

--
-- Name: avance_caso_emblematico_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.avance_caso_emblematico_id_seq OWNED BY public.avance_caso_emblematico.id;


--
-- Name: avance_politica_memoria; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.avance_politica_memoria (
    id integer NOT NULL,
    nombre_politica_memoria character varying(255) NOT NULL,
    ocurrencias_periodo text,
    actividades_realizadas text,
    estado_actual_gestion text,
    recomendaciones text,
    otro_asunto text,
    responsable_registro character varying(255),
    fecha_registro timestamp without time zone
);


ALTER TABLE public.avance_politica_memoria OWNER TO postgres;

--
-- Name: avance_politica_memoria_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.avance_politica_memoria_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.avance_politica_memoria_id_seq OWNER TO postgres;

--
-- Name: avance_politica_memoria_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.avance_politica_memoria_id_seq OWNED BY public.avance_politica_memoria.id;


--
-- Name: caso_emblematico; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.caso_emblematico (
    nombre_caso character varying(255) NOT NULL,
    numero_expediente character varying(255) NOT NULL,
    sala character varying(255),
    antecedentes text,
    descripcion_caso text,
    numero_afectados integer,
    objetivo_defensa text,
    situacion_caso text,
    otro_dato text,
    fecha_registro timestamp without time zone
);


ALTER TABLE public.caso_emblematico OWNER TO postgres;

--
-- Name: iniciativa; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.iniciativa (
    nombre_iniciativa character varying(255) NOT NULL,
    derecho_generico character varying(255),
    otro_derecho_detalle character varying(255),
    colectivo_organizacion character varying(255),
    poblacion text,
    total_hombres_ninos integer,
    total_mujeres_ninos integer,
    total_hombres_adolescentes integer,
    total_mujeres_adolescentes integer,
    total_hombres_jovenes integer,
    total_mujeres_jovenes integer,
    total_hombres_mujeres integer,
    total_mujeres_mujeres integer,
    total_hombres_discapacidad integer,
    total_mujeres_discapacidad integer,
    total_hombres_migrantes integer,
    total_mujeres_migrantes integer,
    total_hombres_amazonicas integer,
    total_mujeres_amazonicas integer,
    total_hombres_periurbanas integer,
    total_mujeres_periurbanas integer,
    total_hombres_conflicto integer,
    total_mujeres_conflicto integer,
    otra_poblacion_detalle character varying(255),
    total_hombres_otra integer,
    total_mujeres_otra integer,
    tipo_naturaleza text,
    cambio_politica_detalle character varying(255),
    cambio_marcos_detalle character varying(255),
    cambio_practicas_detalle character varying(255),
    cambio_sensibilidad_detalle character varying(255),
    otro_naturaleza_detalle character varying(255),
    otro_naturaleza_particular character varying(255),
    sector_publico_competente_1 character varying(255),
    dependencia_instancia_1 character varying(255),
    alcance_escala_1 character varying(50),
    sector_publico_competente_2 character varying(255),
    dependencia_instancia_2 character varying(255),
    alcance_escala_2 character varying(50),
    localidad_1 character varying(255),
    localidad_2 character varying(255),
    localidad_3 character varying(255),
    descripcion_situacion text,
    objetivo_especifico text,
    campos text,
    campo_otro_detalle character varying(255),
    componente_1 text,
    componente_2 text,
    componente_3 text,
    contenido_1 integer,
    contenido_2 integer,
    contenido_3 integer,
    contenido_4 integer,
    contenido_5 integer,
    contenido_6 integer,
    contenido_7 integer,
    contenido_otro character varying(255),
    calificacion_otro_contenido integer,
    fase_implementacion text,
    fase_normas_detalle character varying(255),
    fase_institucionalizacion_detalle character varying(255),
    fase_otro_detalle character varying(255),
    actividad_1 character varying(255),
    actividad_2 character varying(255),
    actividad_3 character varying(255),
    actividad_4 character varying(255),
    actividad_5 character varying(255),
    proyecto_1 character varying(255),
    fuente_financiamiento_1 character varying(255),
    financiamiento_1 character varying(255),
    periodo_financiamiento_1 character varying(255),
    proyecto_2 character varying(255),
    fuente_financiamiento_2 character varying(255),
    financiamiento_2 character varying(255),
    periodo_financiamiento_2 character varying(255),
    observaciones text,
    responsable_registro character varying(255),
    fecha_registro timestamp without time zone
);


ALTER TABLE public.iniciativa OWNER TO postgres;

--
-- Name: politica_nacional_memoria; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.politica_nacional_memoria (
    nombre_politica_memoria character varying(255) NOT NULL,
    localizacion character varying(255),
    descripcion_propuesta text,
    institucion_1 character varying(255),
    asunto_1 character varying(255),
    institucion_2 character varying(255),
    asunto_2 character varying(255),
    institucion_3 character varying(255),
    asunto_3 character varying(255),
    organizaciones_aliadas text,
    otro_dato text,
    fecha_registro timestamp without time zone
);


ALTER TABLE public.politica_nacional_memoria OWNER TO postgres;

--
-- Name: proceso_iniciativa; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.proceso_iniciativa (
    id integer NOT NULL,
    nombre_iniciativa character varying(255) NOT NULL,
    objetivo_especifico text NOT NULL,
    logros text,
    sustento_logros text,
    contenido_1 integer,
    contenido_2 integer,
    contenido_3 integer,
    contenido_4 integer,
    contenido_5 integer,
    contenido_6 integer,
    contenido_7 integer,
    contenido_otro text,
    calificacion_otro_contenido integer,
    fase_implementacion text,
    fase_normas_detalle text,
    fase_institucionalizacion_detalle text,
    fase_otro_detalle text,
    nivel_avance_comentarios text,
    componente_1 text,
    calificacion_componente_1 integer,
    componente_2 text,
    calificacion_componente_2 integer,
    componente_3 text,
    calificacion_componente_3 integer,
    sustento_valoracion text,
    capacidad_1 integer,
    capacidad_2 integer,
    capacidad_3 integer,
    capacidad_4 integer,
    capacidad_5 integer,
    otra_capacidad character varying(255),
    calificacion_otra_capacidad integer,
    reforzar_competencias text,
    participacion_comportamiento integer,
    comentario_valoracion text,
    factores_favorecido text,
    factores_obstaculizado text,
    actividad_1 text,
    aporte_1 text,
    actividad_2 text,
    aporte_2 text,
    actividad_3 text,
    aporte_3 text,
    actividad_4 text,
    aporte_4 text,
    actividad_5 text,
    aporte_5 text,
    cambios_estrategia text,
    comentario_relevante text,
    responsable_registro character varying(255),
    fecha_registro timestamp without time zone
);


ALTER TABLE public.proceso_iniciativa OWNER TO postgres;

--
-- Name: proceso_iniciativa_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.proceso_iniciativa_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.proceso_iniciativa_id_seq OWNER TO postgres;

--
-- Name: proceso_iniciativa_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.proceso_iniciativa_id_seq OWNED BY public.proceso_iniciativa.id;


--
-- Name: registro; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.registro (
    dni character varying(20) NOT NULL,
    nombre character varying(100) NOT NULL,
    edad integer,
    sexo character varying(10),
    lugar_nacimiento character varying(100),
    calle character varying(100),
    comunidad character varying(100),
    distrito character varying(100),
    provincia character varying(100),
    departamento character varying(100),
    poblacion_titular text,
    otro_poblacion character varying(100),
    derecho_prioritario text,
    otro_derecho character varying(100),
    oficina_regional character varying(100),
    proyectos character varying(255),
    tipo_servicios text,
    servicio_actividad character varying(255),
    fecha_participacion date,
    propuesta_agenda character varying(255),
    agenda_detalle character varying(255),
    red_colectivo character varying(255),
    red_detalle character varying(255),
    comunidad_fe character varying(255),
    fe_detalle character varying(255),
    tipo_participacion_fe character varying(255),
    capacidad_1 integer,
    capacidad_2 integer,
    capacidad_3 integer,
    capacidad_4 integer,
    capacidad_5 integer,
    otra_capacidad character varying(255),
    calificacion_otra_capacidad integer,
    fecha_registro timestamp without time zone
);


ALTER TABLE public.registro OWNER TO postgres;

--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying(100) NOT NULL,
    password_hash character varying(255) NOT NULL,
    role character varying(50) NOT NULL
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: avance_caso_emblematico id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.avance_caso_emblematico ALTER COLUMN id SET DEFAULT nextval('public.avance_caso_emblematico_id_seq'::regclass);


--
-- Name: avance_politica_memoria id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.avance_politica_memoria ALTER COLUMN id SET DEFAULT nextval('public.avance_politica_memoria_id_seq'::regclass);


--
-- Name: proceso_iniciativa id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.proceso_iniciativa ALTER COLUMN id SET DEFAULT nextval('public.proceso_iniciativa_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
02ca1165e154
\.


--
-- Data for Name: avance_caso_emblematico; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.avance_caso_emblematico (id, nombre_caso, ocurrencias_periodo, actividades_realizadas, presencia_participacion, estado_actual, recomendaciones, otro_asunto, responsable_registro, fecha_registro) FROM stdin;
\.


--
-- Data for Name: avance_politica_memoria; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.avance_politica_memoria (id, nombre_politica_memoria, ocurrencias_periodo, actividades_realizadas, estado_actual_gestion, recomendaciones, otro_asunto, responsable_registro, fecha_registro) FROM stdin;
\.


--
-- Data for Name: caso_emblematico; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.caso_emblematico (nombre_caso, numero_expediente, sala, antecedentes, descripcion_caso, numero_afectados, objetivo_defensa, situacion_caso, otro_dato, fecha_registro) FROM stdin;
\.


--
-- Data for Name: iniciativa; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.iniciativa (nombre_iniciativa, derecho_generico, otro_derecho_detalle, colectivo_organizacion, poblacion, total_hombres_ninos, total_mujeres_ninos, total_hombres_adolescentes, total_mujeres_adolescentes, total_hombres_jovenes, total_mujeres_jovenes, total_hombres_mujeres, total_mujeres_mujeres, total_hombres_discapacidad, total_mujeres_discapacidad, total_hombres_migrantes, total_mujeres_migrantes, total_hombres_amazonicas, total_mujeres_amazonicas, total_hombres_periurbanas, total_mujeres_periurbanas, total_hombres_conflicto, total_mujeres_conflicto, otra_poblacion_detalle, total_hombres_otra, total_mujeres_otra, tipo_naturaleza, cambio_politica_detalle, cambio_marcos_detalle, cambio_practicas_detalle, cambio_sensibilidad_detalle, otro_naturaleza_detalle, otro_naturaleza_particular, sector_publico_competente_1, dependencia_instancia_1, alcance_escala_1, sector_publico_competente_2, dependencia_instancia_2, alcance_escala_2, localidad_1, localidad_2, localidad_3, descripcion_situacion, objetivo_especifico, campos, campo_otro_detalle, componente_1, componente_2, componente_3, contenido_1, contenido_2, contenido_3, contenido_4, contenido_5, contenido_6, contenido_7, contenido_otro, calificacion_otro_contenido, fase_implementacion, fase_normas_detalle, fase_institucionalizacion_detalle, fase_otro_detalle, actividad_1, actividad_2, actividad_3, actividad_4, actividad_5, proyecto_1, fuente_financiamiento_1, financiamiento_1, periodo_financiamiento_1, proyecto_2, fuente_financiamiento_2, financiamiento_2, periodo_financiamiento_2, observaciones, responsable_registro, fecha_registro) FROM stdin;
\.


--
-- Data for Name: politica_nacional_memoria; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.politica_nacional_memoria (nombre_politica_memoria, localizacion, descripcion_propuesta, institucion_1, asunto_1, institucion_2, asunto_2, institucion_3, asunto_3, organizaciones_aliadas, otro_dato, fecha_registro) FROM stdin;
\.


--
-- Data for Name: proceso_iniciativa; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.proceso_iniciativa (id, nombre_iniciativa, objetivo_especifico, logros, sustento_logros, contenido_1, contenido_2, contenido_3, contenido_4, contenido_5, contenido_6, contenido_7, contenido_otro, calificacion_otro_contenido, fase_implementacion, fase_normas_detalle, fase_institucionalizacion_detalle, fase_otro_detalle, nivel_avance_comentarios, componente_1, calificacion_componente_1, componente_2, calificacion_componente_2, componente_3, calificacion_componente_3, sustento_valoracion, capacidad_1, capacidad_2, capacidad_3, capacidad_4, capacidad_5, otra_capacidad, calificacion_otra_capacidad, reforzar_competencias, participacion_comportamiento, comentario_valoracion, factores_favorecido, factores_obstaculizado, actividad_1, aporte_1, actividad_2, aporte_2, actividad_3, aporte_3, actividad_4, aporte_4, actividad_5, aporte_5, cambios_estrategia, comentario_relevante, responsable_registro, fecha_registro) FROM stdin;
\.


--
-- Data for Name: registro; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.registro (dni, nombre, edad, sexo, lugar_nacimiento, calle, comunidad, distrito, provincia, departamento, poblacion_titular, otro_poblacion, derecho_prioritario, otro_derecho, oficina_regional, proyectos, tipo_servicios, servicio_actividad, fecha_participacion, propuesta_agenda, agenda_detalle, red_colectivo, red_detalle, comunidad_fe, fe_detalle, tipo_participacion_fe, capacidad_1, capacidad_2, capacidad_3, capacidad_4, capacidad_5, otra_capacidad, calificacion_otra_capacidad, fecha_registro) FROM stdin;
73879198	fdffdfdwwwwwwwwwwwwwwwwwwwwwwwwww	\N																\N								\N	\N	\N	\N	\N		\N	2024-09-16 21:02:22.443457
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, username, password_hash, role) FROM stdin;
3	admin	scrypt:32768:8:1$jPf9dJC3hwe45eY9$9ee7104c544e91ee8371ec26b3739cc5c3d6a9d95250f7e55e4c081d8495c5024a87ca38c470d7b47bf62e3686c66c30e8c1ac44c365ab0c3b95c3cbddd941e9	admin
5	lucia	scrypt:32768:8:1$ipMAHCPpyVNfxCQn$54a23cfbb53c2d85d8e0185fefa245a04b095e4786e69defd068d95513a0db3df8c9f611f88256d157473c3a6ae6ec4e3d2638d395e1f04c0aa2408c418c4be1	viewer
6	brunito	scrypt:32768:8:1$asQ01DMjmsgtwjGw$d6f8872082a2eddd6772fe5ebbf9137f673a6724155a381a44407844d5ef4457ea0035142a25608f9c48adf3bccf45dbe83ff2b2b882cd7af65b622a3859b8d8	admin
\.


--
-- Name: avance_caso_emblematico_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.avance_caso_emblematico_id_seq', 1, false);


--
-- Name: avance_politica_memoria_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.avance_politica_memoria_id_seq', 1, false);


--
-- Name: proceso_iniciativa_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.proceso_iniciativa_id_seq', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 6, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: avance_caso_emblematico avance_caso_emblematico_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.avance_caso_emblematico
    ADD CONSTRAINT avance_caso_emblematico_pkey PRIMARY KEY (id);


--
-- Name: avance_politica_memoria avance_politica_memoria_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.avance_politica_memoria
    ADD CONSTRAINT avance_politica_memoria_pkey PRIMARY KEY (id);


--
-- Name: caso_emblematico caso_emblematico_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.caso_emblematico
    ADD CONSTRAINT caso_emblematico_pkey PRIMARY KEY (nombre_caso);


--
-- Name: iniciativa iniciativa_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.iniciativa
    ADD CONSTRAINT iniciativa_pkey PRIMARY KEY (nombre_iniciativa);


--
-- Name: politica_nacional_memoria politica_nacional_memoria_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.politica_nacional_memoria
    ADD CONSTRAINT politica_nacional_memoria_pkey PRIMARY KEY (nombre_politica_memoria);


--
-- Name: proceso_iniciativa proceso_iniciativa_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.proceso_iniciativa
    ADD CONSTRAINT proceso_iniciativa_pkey PRIMARY KEY (id);


--
-- Name: registro registro_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.registro
    ADD CONSTRAINT registro_pkey PRIMARY KEY (dni);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: avance_caso_emblematico avance_caso_emblematico_nombre_caso_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.avance_caso_emblematico
    ADD CONSTRAINT avance_caso_emblematico_nombre_caso_fkey FOREIGN KEY (nombre_caso) REFERENCES public.caso_emblematico(nombre_caso);


--
-- Name: avance_politica_memoria avance_politica_memoria_nombre_politica_memoria_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.avance_politica_memoria
    ADD CONSTRAINT avance_politica_memoria_nombre_politica_memoria_fkey FOREIGN KEY (nombre_politica_memoria) REFERENCES public.politica_nacional_memoria(nombre_politica_memoria);


--
-- Name: proceso_iniciativa proceso_iniciativa_nombre_iniciativa_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.proceso_iniciativa
    ADD CONSTRAINT proceso_iniciativa_nombre_iniciativa_fkey FOREIGN KEY (nombre_iniciativa) REFERENCES public.iniciativa(nombre_iniciativa);


--
-- PostgreSQL database dump complete
--

