--
-- PostgreSQL database dump
--

\restrict Y8ylmnfLByCW0QNSm7awAmw6bEziZU4HlLwVPvnyIdUi2qGpHDzIfjvDfVI3vHr

-- Dumped from database version 16.11
-- Dumped by pg_dump version 16.11

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
-- Name: to_date_time_safe(text, text); Type: FUNCTION; Schema: public; Owner: nocodb
--

CREATE FUNCTION public.to_date_time_safe(value text, format text) RETURNS timestamp without time zone
    LANGUAGE plpgsql
    AS $$
  BEGIN
    RETURN to_timestamp(value, format);
    EXCEPTION
      WHEN others THEN RETURN NULL;  
  END;
  $$;


ALTER FUNCTION public.to_date_time_safe(value text, format text) OWNER TO nocodb;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: nc_api_tokens; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public.nc_api_tokens (
    id integer NOT NULL,
    base_id character varying(20),
    db_alias character varying(255),
    description character varying(255),
    permissions text,
    token text,
    expiry character varying(255),
    enabled boolean DEFAULT true,
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    fk_user_id character varying(20)
);


ALTER TABLE public.nc_api_tokens OWNER TO nocodb;

--
-- Name: nc_api_tokens_id_seq; Type: SEQUENCE; Schema: public; Owner: nocodb
--

CREATE SEQUENCE public.nc_api_tokens_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.nc_api_tokens_id_seq OWNER TO nocodb;

--
-- Name: nc_api_tokens_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: nocodb
--

ALTER SEQUENCE public.nc_api_tokens_id_seq OWNED BY public.nc_api_tokens.id;


--
-- Name: nc_audit_v2; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public.nc_audit_v2 (
    id character varying(20) NOT NULL,
    "user" character varying(255),
    ip character varying(255),
    source_id character varying(20),
    base_id character varying(20),
    fk_model_id character varying(20),
    row_id character varying(255),
    op_type character varying(255),
    op_sub_type character varying(255),
    status character varying(255),
    description text,
    details text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.nc_audit_v2 OWNER TO nocodb;

--
-- Name: nc_base_users_v2; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public.nc_base_users_v2 (
    base_id character varying(20) NOT NULL,
    fk_user_id character varying(20) NOT NULL,
    roles text,
    starred boolean,
    pinned boolean,
    "group" character varying(255),
    color character varying(255),
    "order" real,
    hidden real,
    opened_date timestamp with time zone,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    invited_by character varying(20)
);


ALTER TABLE public.nc_base_users_v2 OWNER TO nocodb;

--
-- Name: nc_bases_v2; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public.nc_bases_v2 (
    id character varying(128) NOT NULL,
    title character varying(255),
    prefix character varying(255),
    status character varying(255),
    description text,
    meta text,
    color character varying(255),
    uuid character varying(255),
    password character varying(255),
    roles character varying(255),
    deleted boolean DEFAULT false,
    is_meta boolean,
    "order" real,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.nc_bases_v2 OWNER TO nocodb;

--
-- Name: nc_calendar_view_columns_v2; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public.nc_calendar_view_columns_v2 (
    id character varying(20) NOT NULL,
    base_id character varying(20),
    source_id character varying(20),
    fk_view_id character varying(20),
    fk_column_id character varying(20),
    show boolean,
    bold boolean,
    underline boolean,
    italic boolean,
    "order" real,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.nc_calendar_view_columns_v2 OWNER TO nocodb;

--
-- Name: nc_calendar_view_range_v2; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public.nc_calendar_view_range_v2 (
    id character varying(20) NOT NULL,
    fk_view_id character varying(20),
    fk_to_column_id character varying(20),
    label character varying(40),
    fk_from_column_id character varying(20),
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    base_id character varying(20)
);


ALTER TABLE public.nc_calendar_view_range_v2 OWNER TO nocodb;

--
-- Name: nc_calendar_view_v2; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public.nc_calendar_view_v2 (
    fk_view_id character varying(20) NOT NULL,
    base_id character varying(20),
    source_id character varying(20),
    title character varying(255),
    fk_cover_image_col_id character varying(20),
    meta text,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);


ALTER TABLE public.nc_calendar_view_v2 OWNER TO nocodb;

--
-- Name: nc_col_barcode_v2; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public.nc_col_barcode_v2 (
    id character varying(20) NOT NULL,
    fk_column_id character varying(20),
    fk_barcode_value_column_id character varying(20),
    barcode_format character varying(15),
    deleted boolean,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    base_id character varying(20)
);


ALTER TABLE public.nc_col_barcode_v2 OWNER TO nocodb;

--
-- Name: nc_col_button_v2; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public.nc_col_button_v2 (
    id character varying(20),
    base_id character varying(20),
    type character varying(255),
    label text,
    theme character varying(255),
    color character varying(255),
    icon character varying(255),
    formula text,
    formula_raw text,
    error character varying(255),
    parsed_tree text,
    fk_webhook_id character varying(20),
    fk_column_id character varying(20),
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.nc_col_button_v2 OWNER TO nocodb;

--
-- Name: nc_col_formula_v2; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public.nc_col_formula_v2 (
    id character varying(20) NOT NULL,
    fk_column_id character varying(20),
    formula text NOT NULL,
    formula_raw text,
    error text,
    deleted boolean,
    "order" real,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    parsed_tree text,
    base_id character varying(20)
);


ALTER TABLE public.nc_col_formula_v2 OWNER TO nocodb;

--
-- Name: nc_col_lookup_v2; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public.nc_col_lookup_v2 (
    id character varying(20) NOT NULL,
    fk_column_id character varying(20),
    fk_relation_column_id character varying(20),
    fk_lookup_column_id character varying(20),
    deleted boolean,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    base_id character varying(20)
);


ALTER TABLE public.nc_col_lookup_v2 OWNER TO nocodb;

--
-- Name: nc_col_qrcode_v2; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public.nc_col_qrcode_v2 (
    id character varying(20) NOT NULL,
    fk_column_id character varying(20),
    fk_qr_value_column_id character varying(20),
    deleted boolean,
    "order" real,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    base_id character varying(20)
);


ALTER TABLE public.nc_col_qrcode_v2 OWNER TO nocodb;

--
-- Name: nc_col_relations_v2; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public.nc_col_relations_v2 (
    id character varying(20) NOT NULL,
    ref_db_alias character varying(255),
    type character varying(255),
    virtual boolean,
    db_type character varying(255),
    fk_column_id character varying(20),
    fk_related_model_id character varying(20),
    fk_child_column_id character varying(20),
    fk_parent_column_id character varying(20),
    fk_mm_model_id character varying(20),
    fk_mm_child_column_id character varying(20),
    fk_mm_parent_column_id character varying(20),
    ur character varying(255),
    dr character varying(255),
    fk_index_name character varying(255),
    deleted boolean,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    fk_target_view_id character varying(20),
    base_id character varying(20)
);


ALTER TABLE public.nc_col_relations_v2 OWNER TO nocodb;

--
-- Name: nc_col_rollup_v2; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public.nc_col_rollup_v2 (
    id character varying(20) NOT NULL,
    fk_column_id character varying(20),
    fk_relation_column_id character varying(20),
    fk_rollup_column_id character varying(20),
    rollup_function character varying(255),
    deleted boolean,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    base_id character varying(20)
);


ALTER TABLE public.nc_col_rollup_v2 OWNER TO nocodb;

--
-- Name: nc_col_select_options_v2; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public.nc_col_select_options_v2 (
    id character varying(20) NOT NULL,
    fk_column_id character varying(20),
    title character varying(255),
    color character varying(255),
    "order" real,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    base_id character varying(20)
);


ALTER TABLE public.nc_col_select_options_v2 OWNER TO nocodb;

--
-- Name: nc_columns_v2; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public.nc_columns_v2 (
    id character varying(20) NOT NULL,
    source_id character varying(20),
    base_id character varying(20),
    fk_model_id character varying(20),
    title character varying(255),
    column_name character varying(255),
    uidt character varying(255),
    dt character varying(255),
    np character varying(255),
    ns character varying(255),
    clen character varying(255),
    cop character varying(255),
    pk boolean,
    pv boolean,
    rqd boolean,
    un boolean,
    ct text,
    ai boolean,
    "unique" boolean,
    cdf text,
    cc text,
    csn character varying(255),
    dtx character varying(255),
    dtxp text,
    dtxs character varying(255),
    au boolean,
    validate text,
    virtual boolean,
    deleted boolean,
    system boolean DEFAULT false,
    "order" real,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    meta text,
    description character varying(255)
);


ALTER TABLE public.nc_columns_v2 OWNER TO nocodb;

--
-- Name: nc_comment_reactions; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public.nc_comment_reactions (
    id character varying(20) NOT NULL,
    row_id character varying(255),
    comment_id character varying(20),
    source_id character varying(20),
    fk_model_id character varying(20),
    base_id character varying(20),
    reaction character varying(255),
    created_by character varying(255),
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.nc_comment_reactions OWNER TO nocodb;

--
-- Name: nc_comments; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public.nc_comments (
    id character varying(20) NOT NULL,
    row_id character varying(255),
    comment text,
    created_by character varying(20),
    created_by_email character varying(255),
    resolved_by character varying(20),
    resolved_by_email character varying(255),
    parent_comment_id character varying(20),
    source_id character varying(20),
    base_id character varying(20),
    fk_model_id character varying(20),
    is_deleted boolean,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.nc_comments OWNER TO nocodb;

--
-- Name: nc_disabled_models_for_role_v2; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public.nc_disabled_models_for_role_v2 (
    id character varying(20) NOT NULL,
    source_id character varying(20),
    base_id character varying(20),
    fk_view_id character varying(20),
    role character varying(45),
    disabled boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.nc_disabled_models_for_role_v2 OWNER TO nocodb;

--
-- Name: nc_extensions; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public.nc_extensions (
    id character varying(20) NOT NULL,
    base_id character varying(20),
    fk_user_id character varying(20),
    extension_id character varying(255),
    title character varying(255),
    kv_store text,
    meta text,
    "order" real,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.nc_extensions OWNER TO nocodb;

--
-- Name: nc_file_references; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public.nc_file_references (
    id character varying(20) NOT NULL,
    storage character varying(255),
    file_url text,
    file_size integer,
    fk_user_id character varying(20),
    fk_workspace_id character varying(20),
    base_id character varying(20),
    source_id character varying(20),
    fk_model_id character varying(20),
    fk_column_id character varying(20),
    is_external boolean DEFAULT false,
    deleted boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.nc_file_references OWNER TO nocodb;

--
-- Name: nc_filter_exp_v2; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public.nc_filter_exp_v2 (
    id character varying(20) NOT NULL,
    source_id character varying(20),
    base_id character varying(20),
    fk_view_id character varying(20),
    fk_hook_id character varying(20),
    fk_column_id character varying(20),
    fk_parent_id character varying(20),
    logical_op character varying(255),
    comparison_op character varying(255),
    value text,
    is_group boolean,
    "order" real,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    comparison_sub_op character varying(255),
    fk_link_col_id character varying(20),
    fk_value_col_id character varying(20)
);


ALTER TABLE public.nc_filter_exp_v2 OWNER TO nocodb;

--
-- Name: nc_fl6j___LeadAnswers; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public."nc_fl6j___LeadAnswers" (
    id integer NOT NULL,
    free_text_answer text,
    captured_at timestamp without time zone,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    created_by character varying,
    updated_by character varying,
    "nc_fl6j___Leads_id" integer,
    "nc_fl6j___ServiceQuestions_id" integer,
    "nc_fl6j___ServiceQuestionOptions_id" integer
);


ALTER TABLE public."nc_fl6j___LeadAnswers" OWNER TO nocodb;

--
-- Name: nc_fl6j___LeadAnswers_id_seq; Type: SEQUENCE; Schema: public; Owner: nocodb
--

CREATE SEQUENCE public."nc_fl6j___LeadAnswers_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public."nc_fl6j___LeadAnswers_id_seq" OWNER TO nocodb;

--
-- Name: nc_fl6j___LeadAnswers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: nocodb
--

ALTER SEQUENCE public."nc_fl6j___LeadAnswers_id_seq" OWNED BY public."nc_fl6j___LeadAnswers".id;


--
-- Name: nc_fl6j___Leads; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public."nc_fl6j___Leads" (
    id integer NOT NULL,
    nombre text,
    entrada date,
    email character varying,
    telefono character varying,
    tipo_empresa text,
    servicio text,
    extra_informacion text,
    como_nos_conociste text,
    mensaje text,
    origen_lead text DEFAULT 'Formulario web'::text,
    estado text DEFAULT 'Nuevo'::text,
    prioridad text DEFAULT 'Media'::text,
    notas_internas text,
    lead_tag text,
    next_action text DEFAULT 'NO_ACTION'::text,
    next_action_key text,
    owner text,
    last_contact_at date,
    next_followup_at date,
    lost_reason text,
    gdpr_consent boolean DEFAULT false,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    created_by character varying,
    updated_by character varying,
    utm_source text,
    utm_medium text,
    utm_campaign text,
    utm_term text,
    utm_content text,
    landing_url text,
    referrer text,
    bing_click_id_msclkid text,
    google_click_id_gclid text,
    google_click_id_gbraid text,
    google_click_id_wbraid text,
    linkedin_click_id_li_fat_id text,
    entrada_at timestamp without time zone,
    "Ads_Click_ID__unified_" text,
    "Ads_Platform" text,
    "Ads_Click_ID_Type" text
);


ALTER TABLE public."nc_fl6j___Leads" OWNER TO nocodb;

--
-- Name: nc_fl6j___Leads_id_seq; Type: SEQUENCE; Schema: public; Owner: nocodb
--

CREATE SEQUENCE public."nc_fl6j___Leads_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public."nc_fl6j___Leads_id_seq" OWNER TO nocodb;

--
-- Name: nc_fl6j___Leads_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: nocodb
--

ALTER SEQUENCE public."nc_fl6j___Leads_id_seq" OWNED BY public."nc_fl6j___Leads".id;


--
-- Name: nc_fl6j___ServiceQuestionOptions; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public."nc_fl6j___ServiceQuestionOptions" (
    id integer NOT NULL,
    option_label text,
    sort_order bigint,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    created_by character varying,
    updated_by character varying,
    "nc_fl6j___ServiceQuestions_id" integer
);


ALTER TABLE public."nc_fl6j___ServiceQuestionOptions" OWNER TO nocodb;

--
-- Name: nc_fl6j___ServiceQuestionOptions_id_seq; Type: SEQUENCE; Schema: public; Owner: nocodb
--

CREATE SEQUENCE public."nc_fl6j___ServiceQuestionOptions_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public."nc_fl6j___ServiceQuestionOptions_id_seq" OWNER TO nocodb;

--
-- Name: nc_fl6j___ServiceQuestionOptions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: nocodb
--

ALTER SEQUENCE public."nc_fl6j___ServiceQuestionOptions_id_seq" OWNED BY public."nc_fl6j___ServiceQuestionOptions".id;


--
-- Name: nc_fl6j___ServiceQuestions; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public."nc_fl6j___ServiceQuestions" (
    id integer NOT NULL,
    service text,
    question_label text,
    input_type text,
    is_enabled boolean DEFAULT true,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    created_by character varying,
    updated_by character varying
);


ALTER TABLE public."nc_fl6j___ServiceQuestions" OWNER TO nocodb;

--
-- Name: nc_fl6j___ServiceQuestions_id_seq; Type: SEQUENCE; Schema: public; Owner: nocodb
--

CREATE SEQUENCE public."nc_fl6j___ServiceQuestions_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public."nc_fl6j___ServiceQuestions_id_seq" OWNER TO nocodb;

--
-- Name: nc_fl6j___ServiceQuestions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: nocodb
--

ALTER SEQUENCE public."nc_fl6j___ServiceQuestions_id_seq" OWNED BY public."nc_fl6j___ServiceQuestions".id;


--
-- Name: nc_form_view_columns_v2; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public.nc_form_view_columns_v2 (
    id character varying(20) NOT NULL,
    source_id character varying(20),
    base_id character varying(20),
    fk_view_id character varying(20),
    fk_column_id character varying(20),
    uuid character varying(255),
    label text,
    help text,
    description text,
    required boolean,
    show boolean,
    "order" real,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    meta text,
    enable_scanner boolean
);


ALTER TABLE public.nc_form_view_columns_v2 OWNER TO nocodb;

--
-- Name: nc_form_view_v2; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public.nc_form_view_v2 (
    source_id character varying(20),
    base_id character varying(20),
    fk_view_id character varying(20) NOT NULL,
    heading character varying(255),
    subheading text,
    success_msg text,
    redirect_url text,
    redirect_after_secs character varying(255),
    email character varying(255),
    submit_another_form boolean,
    show_blank_form boolean,
    uuid character varying(255),
    banner_image_url text,
    logo_url text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    meta text
);


ALTER TABLE public.nc_form_view_v2 OWNER TO nocodb;

--
-- Name: nc_gallery_view_columns_v2; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public.nc_gallery_view_columns_v2 (
    id character varying(20) NOT NULL,
    source_id character varying(20),
    base_id character varying(20),
    fk_view_id character varying(20),
    fk_column_id character varying(20),
    uuid character varying(255),
    label character varying(255),
    help character varying(255),
    show boolean,
    "order" real,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.nc_gallery_view_columns_v2 OWNER TO nocodb;

--
-- Name: nc_gallery_view_v2; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public.nc_gallery_view_v2 (
    source_id character varying(20),
    base_id character varying(20),
    fk_view_id character varying(20) NOT NULL,
    next_enabled boolean,
    prev_enabled boolean,
    cover_image_idx integer,
    fk_cover_image_col_id character varying(20),
    cover_image character varying(255),
    restrict_types character varying(255),
    restrict_size character varying(255),
    restrict_number character varying(255),
    public boolean,
    dimensions character varying(255),
    responsive_columns character varying(255),
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    meta text
);


ALTER TABLE public.nc_gallery_view_v2 OWNER TO nocodb;

--
-- Name: nc_grid_view_columns_v2; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public.nc_grid_view_columns_v2 (
    id character varying(20) NOT NULL,
    fk_view_id character varying(20),
    fk_column_id character varying(20),
    source_id character varying(20),
    base_id character varying(20),
    uuid character varying(255),
    label character varying(255),
    help character varying(255),
    width character varying(255) DEFAULT '200px'::character varying,
    show boolean,
    "order" real,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    group_by boolean,
    group_by_order real,
    group_by_sort character varying(255),
    aggregation character varying(30) DEFAULT NULL::character varying
);


ALTER TABLE public.nc_grid_view_columns_v2 OWNER TO nocodb;

--
-- Name: nc_grid_view_v2; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public.nc_grid_view_v2 (
    fk_view_id character varying(20) NOT NULL,
    source_id character varying(20),
    base_id character varying(20),
    uuid character varying(255),
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    meta text,
    row_height integer
);


ALTER TABLE public.nc_grid_view_v2 OWNER TO nocodb;

--
-- Name: nc_hook_logs_v2; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public.nc_hook_logs_v2 (
    id character varying(20) NOT NULL,
    source_id character varying(20),
    base_id character varying(20),
    fk_hook_id character varying(20),
    type character varying(255),
    event character varying(255),
    operation character varying(255),
    test_call boolean DEFAULT true,
    payload text,
    conditions text,
    notification text,
    error_code character varying(255),
    error_message character varying(255),
    error text,
    execution_time integer,
    response text,
    triggered_by character varying(255),
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.nc_hook_logs_v2 OWNER TO nocodb;

--
-- Name: nc_hooks_v2; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public.nc_hooks_v2 (
    id character varying(20) NOT NULL,
    source_id character varying(20),
    base_id character varying(20),
    fk_model_id character varying(20),
    title character varying(255),
    description character varying(255),
    env character varying(255) DEFAULT 'all'::character varying,
    type character varying(255),
    event character varying(255),
    operation character varying(255),
    async boolean DEFAULT false,
    payload boolean DEFAULT true,
    url text,
    headers text,
    condition boolean DEFAULT false,
    notification text,
    retries integer DEFAULT 0,
    retry_interval integer DEFAULT 60000,
    timeout integer DEFAULT 60000,
    active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    version character varying(255)
);


ALTER TABLE public.nc_hooks_v2 OWNER TO nocodb;

--
-- Name: nc_integrations_v2; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public.nc_integrations_v2 (
    id character varying(20) NOT NULL,
    title character varying(128),
    config text,
    meta text,
    type character varying(20),
    sub_type character varying(20),
    is_private boolean DEFAULT false,
    deleted boolean DEFAULT false,
    created_by character varying(20),
    "order" real,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.nc_integrations_v2 OWNER TO nocodb;

--
-- Name: nc_jmsd___Approval; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public."nc_jmsd___Approval" (
    "Id" integer NOT NULL,
    lead character varying,
    template character varying,
    phase text,
    draft_message text,
    final_message text,
    rationale text,
    angle_quality text,
    pain_quality text,
    note text,
    approved_by text,
    approved_at timestamp without time zone,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    created_by character varying,
    updated_by character varying
);


ALTER TABLE public."nc_jmsd___Approval" OWNER TO nocodb;

--
-- Name: nc_jmsd___Approval_Id_seq; Type: SEQUENCE; Schema: public; Owner: nocodb
--

CREATE SEQUENCE public."nc_jmsd___Approval_Id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public."nc_jmsd___Approval_Id_seq" OWNER TO nocodb;

--
-- Name: nc_jmsd___Approval_Id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: nocodb
--

ALTER SEQUENCE public."nc_jmsd___Approval_Id_seq" OWNED BY public."nc_jmsd___Approval"."Id";


--
-- Name: nc_jmsd___Attempt; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public."nc_jmsd___Attempt" (
    "Id" integer NOT NULL,
    lead character varying,
    attempt_type text,
    phase text,
    result text,
    reason text,
    metadata text,
    attempt_at timestamp without time zone,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    created_by character varying,
    updated_by character varying
);


ALTER TABLE public."nc_jmsd___Attempt" OWNER TO nocodb;

--
-- Name: nc_jmsd___Attempt_Id_seq; Type: SEQUENCE; Schema: public; Owner: nocodb
--

CREATE SEQUENCE public."nc_jmsd___Attempt_Id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public."nc_jmsd___Attempt_Id_seq" OWNER TO nocodb;

--
-- Name: nc_jmsd___Attempt_Id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: nocodb
--

ALTER SEQUENCE public."nc_jmsd___Attempt_Id_seq" OWNED BY public."nc_jmsd___Attempt"."Id";


--
-- Name: nc_jmsd___Company; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public."nc_jmsd___Company" (
    "Id" integer NOT NULL,
    name text,
    domain text,
    web_url text,
    industry text,
    location_city text,
    location_region text,
    employees_range text DEFAULT 'UNKNOWN'::text,
    revenue_estimate_range text DEFAULT 'UNKNOWN'::text,
    places_place_id text,
    places_rating numeric,
    places_reviews_total bigint,
    places_types text,
    places_website text,
    places_phone text,
    places_address text,
    places_last_checked_at timestamp without time zone,
    places_signal_hash text,
    web_signal_hash text,
    web_last_checked_at timestamp without time zone,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    created_by character varying,
    updated_by character varying
);


ALTER TABLE public."nc_jmsd___Company" OWNER TO nocodb;

--
-- Name: nc_jmsd___Company_Id_seq; Type: SEQUENCE; Schema: public; Owner: nocodb
--

CREATE SEQUENCE public."nc_jmsd___Company_Id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public."nc_jmsd___Company_Id_seq" OWNER TO nocodb;

--
-- Name: nc_jmsd___Company_Id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: nocodb
--

ALTER SEQUENCE public."nc_jmsd___Company_Id_seq" OWNED BY public."nc_jmsd___Company"."Id";


--
-- Name: nc_jmsd___Conversation; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public."nc_jmsd___Conversation" (
    "Id" integer NOT NULL,
    lead character varying,
    state text DEFAULT 'NOT_STARTED'::text,
    last_inbound_at timestamp without time zone,
    last_outbound_at timestamp without time zone,
    interest_level text DEFAULT 'COLD'::text,
    cta_sent_at timestamp without time zone,
    cal_link text,
    notes text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    created_by character varying,
    updated_by character varying
);


ALTER TABLE public."nc_jmsd___Conversation" OWNER TO nocodb;

--
-- Name: nc_jmsd___Conversation_Id_seq; Type: SEQUENCE; Schema: public; Owner: nocodb
--

CREATE SEQUENCE public."nc_jmsd___Conversation_Id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public."nc_jmsd___Conversation_Id_seq" OWNER TO nocodb;

--
-- Name: nc_jmsd___Conversation_Id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: nocodb
--

ALTER SEQUENCE public."nc_jmsd___Conversation_Id_seq" OWNED BY public."nc_jmsd___Conversation"."Id";


--
-- Name: nc_jmsd___Lead; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public."nc_jmsd___Lead" (
    "Id" integer NOT NULL,
    linkedin_url text,
    full_name text,
    title text,
    role_type text DEFAULT 'UNKNOWN'::text,
    location_city text,
    language text DEFAULT 'UNKNOWN'::text,
    source text,
    company character varying,
    pack_candidate character varying,
    segment character varying,
    status text DEFAULT 'NEW'::text,
    priority text DEFAULT 'MEDIUM'::text,
    lead_score bigint DEFAULT 0,
    score_breakdown text,
    scoring_version text,
    created_at timestamp without time zone,
    invite_sent_at timestamp without time zone,
    accepted_at timestamp without time zone,
    next_action_at timestamp without time zone,
    wait_window_days bigint DEFAULT 14,
    last_signal_checked_at timestamp without time zone,
    signal_changed boolean DEFAULT false,
    do_not_contact boolean DEFAULT false,
    do_not_contact_reason text,
    email text,
    phone text,
    created_at1 timestamp without time zone,
    updated_at timestamp without time zone,
    created_by character varying,
    updated_by character varying
);


ALTER TABLE public."nc_jmsd___Lead" OWNER TO nocodb;

--
-- Name: nc_jmsd___Lead_Id_seq; Type: SEQUENCE; Schema: public; Owner: nocodb
--

CREATE SEQUENCE public."nc_jmsd___Lead_Id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public."nc_jmsd___Lead_Id_seq" OWNER TO nocodb;

--
-- Name: nc_jmsd___Lead_Id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: nocodb
--

ALTER SEQUENCE public."nc_jmsd___Lead_Id_seq" OWNED BY public."nc_jmsd___Lead"."Id";


--
-- Name: nc_jmsd___Message_Template; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public."nc_jmsd___Message_Template" (
    "Id" integer NOT NULL,
    template_key text,
    pack character varying,
    segment character varying,
    phase text,
    language text,
    template_text text,
    variables text,
    version bigint DEFAULT 1,
    is_active boolean DEFAULT true,
    notes text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    created_by character varying,
    updated_by character varying
);


ALTER TABLE public."nc_jmsd___Message_Template" OWNER TO nocodb;

--
-- Name: nc_jmsd___Message_Template_Id_seq; Type: SEQUENCE; Schema: public; Owner: nocodb
--

CREATE SEQUENCE public."nc_jmsd___Message_Template_Id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public."nc_jmsd___Message_Template_Id_seq" OWNER TO nocodb;

--
-- Name: nc_jmsd___Message_Template_Id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: nocodb
--

ALTER SEQUENCE public."nc_jmsd___Message_Template_Id_seq" OWNED BY public."nc_jmsd___Message_Template"."Id";


--
-- Name: nc_jmsd___Outcome; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public."nc_jmsd___Outcome" (
    "Id" integer NOT NULL,
    lead character varying,
    call_booked_at timestamp without time zone,
    call_held_at timestamp without time zone,
    outcome text,
    package_recommended character varying,
    value_estimate bigint,
    notes text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    created_by character varying,
    updated_by character varying
);


ALTER TABLE public."nc_jmsd___Outcome" OWNER TO nocodb;

--
-- Name: nc_jmsd___Outcome_Id_seq; Type: SEQUENCE; Schema: public; Owner: nocodb
--

CREATE SEQUENCE public."nc_jmsd___Outcome_Id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public."nc_jmsd___Outcome_Id_seq" OWNER TO nocodb;

--
-- Name: nc_jmsd___Outcome_Id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: nocodb
--

ALTER SEQUENCE public."nc_jmsd___Outcome_Id_seq" OWNED BY public."nc_jmsd___Outcome"."Id";


--
-- Name: nc_jmsd___Pack; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public."nc_jmsd___Pack" (
    "Id" integer NOT NULL,
    pack_key text,
    name text,
    price_min bigint,
    price_max bigint,
    description text,
    is_active boolean DEFAULT true,
    icp_rules text,
    scoring_weights text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    created_at1 timestamp without time zone,
    updated_at1 timestamp without time zone,
    created_by character varying,
    updated_by character varying
);


ALTER TABLE public."nc_jmsd___Pack" OWNER TO nocodb;

--
-- Name: nc_jmsd___Pack_Id_seq; Type: SEQUENCE; Schema: public; Owner: nocodb
--

CREATE SEQUENCE public."nc_jmsd___Pack_Id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public."nc_jmsd___Pack_Id_seq" OWNER TO nocodb;

--
-- Name: nc_jmsd___Pack_Id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: nocodb
--

ALTER SEQUENCE public."nc_jmsd___Pack_Id_seq" OWNED BY public."nc_jmsd___Pack"."Id";


--
-- Name: nc_jmsd___Research_Snapshot; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public."nc_jmsd___Research_Snapshot" (
    "Id" integer NOT NULL,
    company character varying,
    lead character varying,
    source text,
    signals text,
    signal_hash text,
    created_at timestamp without time zone,
    created_at1 timestamp without time zone,
    updated_at timestamp without time zone,
    created_by character varying,
    updated_by character varying
);


ALTER TABLE public."nc_jmsd___Research_Snapshot" OWNER TO nocodb;

--
-- Name: nc_jmsd___Research_Snapshot_Id_seq; Type: SEQUENCE; Schema: public; Owner: nocodb
--

CREATE SEQUENCE public."nc_jmsd___Research_Snapshot_Id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public."nc_jmsd___Research_Snapshot_Id_seq" OWNER TO nocodb;

--
-- Name: nc_jmsd___Research_Snapshot_Id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: nocodb
--

ALTER SEQUENCE public."nc_jmsd___Research_Snapshot_Id_seq" OWNED BY public."nc_jmsd___Research_Snapshot"."Id";


--
-- Name: nc_jmsd___Segment; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public."nc_jmsd___Segment" (
    "Id" integer NOT NULL,
    segment_key text,
    pack character varying,
    name text,
    type text,
    status text DEFAULT 'RUNNING'::text,
    definition text,
    daily_invite_cap bigint DEFAULT 10,
    start_date date,
    end_date date,
    notes text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    created_by character varying,
    updated_by character varying
);


ALTER TABLE public."nc_jmsd___Segment" OWNER TO nocodb;

--
-- Name: nc_jmsd___Segment_Id_seq; Type: SEQUENCE; Schema: public; Owner: nocodb
--

CREATE SEQUENCE public."nc_jmsd___Segment_Id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public."nc_jmsd___Segment_Id_seq" OWNER TO nocodb;

--
-- Name: nc_jmsd___Segment_Id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: nocodb
--

ALTER SEQUENCE public."nc_jmsd___Segment_Id_seq" OWNED BY public."nc_jmsd___Segment"."Id";


--
-- Name: nc_jobs; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public.nc_jobs (
    id character varying(20) NOT NULL,
    job character varying(255),
    status character varying(20),
    result text,
    fk_user_id character varying(20),
    fk_workspace_id character varying(20),
    base_id character varying(20),
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.nc_jobs OWNER TO nocodb;

--
-- Name: nc_kanban_view_columns_v2; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public.nc_kanban_view_columns_v2 (
    id character varying(20) NOT NULL,
    source_id character varying(20),
    base_id character varying(20),
    fk_view_id character varying(20),
    fk_column_id character varying(20),
    uuid character varying(255),
    label character varying(255),
    help character varying(255),
    show boolean,
    "order" real,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.nc_kanban_view_columns_v2 OWNER TO nocodb;

--
-- Name: nc_kanban_view_v2; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public.nc_kanban_view_v2 (
    fk_view_id character varying(20) NOT NULL,
    source_id character varying(20),
    base_id character varying(20),
    show boolean,
    "order" real,
    uuid character varying(255),
    title character varying(255),
    public boolean,
    password character varying(255),
    show_all_fields boolean,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    fk_grp_col_id character varying(20),
    fk_cover_image_col_id character varying(20),
    meta text
);


ALTER TABLE public.nc_kanban_view_v2 OWNER TO nocodb;

--
-- Name: nc_map_view_columns_v2; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public.nc_map_view_columns_v2 (
    id character varying(20) NOT NULL,
    base_id character varying(20),
    project_id character varying(128),
    fk_view_id character varying(20),
    fk_column_id character varying(20),
    uuid character varying(255),
    label character varying(255),
    help character varying(255),
    show boolean,
    "order" real,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.nc_map_view_columns_v2 OWNER TO nocodb;

--
-- Name: nc_map_view_v2; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public.nc_map_view_v2 (
    fk_view_id character varying(20) NOT NULL,
    source_id character varying(20),
    base_id character varying(20),
    uuid character varying(255),
    title character varying(255),
    fk_geo_data_col_id character varying(20),
    meta text,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);


ALTER TABLE public.nc_map_view_v2 OWNER TO nocodb;

--
-- Name: nc_models_v2; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public.nc_models_v2 (
    id character varying(20) NOT NULL,
    source_id character varying(20),
    base_id character varying(20),
    table_name character varying(255),
    title character varying(255),
    type character varying(255) DEFAULT 'table'::character varying,
    meta text,
    schema text,
    enabled boolean DEFAULT true,
    mm boolean DEFAULT false,
    tags character varying(255),
    pinned boolean,
    deleted boolean,
    "order" real,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    description character varying(255)
);


ALTER TABLE public.nc_models_v2 OWNER TO nocodb;

--
-- Name: nc_orgs_v2; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public.nc_orgs_v2 (
    id character varying(20) NOT NULL,
    title character varying(255),
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.nc_orgs_v2 OWNER TO nocodb;

--
-- Name: nc_plugins_v2; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public.nc_plugins_v2 (
    id character varying(20) NOT NULL,
    title character varying(45),
    description text,
    active boolean DEFAULT false,
    rating real,
    version character varying(255),
    docs character varying(255),
    status character varying(255) DEFAULT 'install'::character varying,
    status_details character varying(255),
    logo character varying(255),
    icon character varying(255),
    tags character varying(255),
    category character varying(255),
    input_schema text,
    input text,
    creator character varying(255),
    creator_website character varying(255),
    price character varying(255),
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.nc_plugins_v2 OWNER TO nocodb;

--
-- Name: nc_shared_bases; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public.nc_shared_bases (
    id integer NOT NULL,
    project_id character varying(255),
    db_alias character varying(255),
    roles character varying(255) DEFAULT 'viewer'::character varying,
    shared_base_id character varying(255),
    enabled boolean DEFAULT true,
    password character varying(255),
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.nc_shared_bases OWNER TO nocodb;

--
-- Name: nc_shared_bases_id_seq; Type: SEQUENCE; Schema: public; Owner: nocodb
--

CREATE SEQUENCE public.nc_shared_bases_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.nc_shared_bases_id_seq OWNER TO nocodb;

--
-- Name: nc_shared_bases_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: nocodb
--

ALTER SEQUENCE public.nc_shared_bases_id_seq OWNED BY public.nc_shared_bases.id;


--
-- Name: nc_shared_views_v2; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public.nc_shared_views_v2 (
    id character varying(20) NOT NULL,
    fk_view_id character varying(20),
    meta text,
    query_params text,
    view_id character varying(255),
    show_all_fields boolean,
    allow_copy boolean,
    password character varying(255),
    deleted boolean,
    "order" real,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.nc_shared_views_v2 OWNER TO nocodb;

--
-- Name: nc_sort_v2; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public.nc_sort_v2 (
    id character varying(20) NOT NULL,
    source_id character varying(20),
    base_id character varying(20),
    fk_view_id character varying(20),
    fk_column_id character varying(20),
    direction character varying(255) DEFAULT 'false'::character varying,
    "order" real,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.nc_sort_v2 OWNER TO nocodb;

--
-- Name: nc_sources_v2; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public.nc_sources_v2 (
    id character varying(20) NOT NULL,
    base_id character varying(20),
    alias character varying(255),
    config text,
    meta text,
    is_meta boolean,
    type character varying(255),
    inflection_column character varying(255),
    inflection_table character varying(255),
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    enabled boolean DEFAULT true,
    "order" real,
    description character varying(255),
    erd_uuid character varying(255),
    deleted boolean DEFAULT false,
    is_schema_readonly boolean DEFAULT false,
    is_data_readonly boolean DEFAULT false,
    fk_integration_id character varying(20)
);


ALTER TABLE public.nc_sources_v2 OWNER TO nocodb;

--
-- Name: nc_store; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public.nc_store (
    id integer NOT NULL,
    base_id character varying(255),
    db_alias character varying(255) DEFAULT 'db'::character varying,
    key character varying(255),
    value text,
    type character varying(255),
    env character varying(255),
    tag character varying(255),
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);


ALTER TABLE public.nc_store OWNER TO nocodb;

--
-- Name: nc_store_id_seq; Type: SEQUENCE; Schema: public; Owner: nocodb
--

CREATE SEQUENCE public.nc_store_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.nc_store_id_seq OWNER TO nocodb;

--
-- Name: nc_store_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: nocodb
--

ALTER SEQUENCE public.nc_store_id_seq OWNED BY public.nc_store.id;


--
-- Name: nc_sync_logs_v2; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public.nc_sync_logs_v2 (
    id character varying(20) NOT NULL,
    base_id character varying(20),
    fk_sync_source_id character varying(20),
    time_taken integer,
    status character varying(255),
    status_details text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.nc_sync_logs_v2 OWNER TO nocodb;

--
-- Name: nc_sync_source_v2; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public.nc_sync_source_v2 (
    id character varying(20) NOT NULL,
    title character varying(255),
    type character varying(255),
    details text,
    deleted boolean,
    enabled boolean DEFAULT true,
    "order" real,
    base_id character varying(20),
    fk_user_id character varying(20),
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    source_id character varying(20)
);


ALTER TABLE public.nc_sync_source_v2 OWNER TO nocodb;

--
-- Name: nc_team_users_v2; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public.nc_team_users_v2 (
    org_id character varying(20),
    user_id character varying(20),
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.nc_team_users_v2 OWNER TO nocodb;

--
-- Name: nc_teams_v2; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public.nc_teams_v2 (
    id character varying(20) NOT NULL,
    title character varying(255),
    org_id character varying(20),
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.nc_teams_v2 OWNER TO nocodb;

--
-- Name: nc_user_comment_notifications_preference; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public.nc_user_comment_notifications_preference (
    id character varying(20) NOT NULL,
    row_id character varying(255),
    user_id character varying(20),
    fk_model_id character varying(20),
    source_id character varying(20),
    base_id character varying(20),
    preferences character varying(255),
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.nc_user_comment_notifications_preference OWNER TO nocodb;

--
-- Name: nc_user_refresh_tokens; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public.nc_user_refresh_tokens (
    fk_user_id character varying(20),
    token character varying(255),
    meta text,
    expires_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.nc_user_refresh_tokens OWNER TO nocodb;

--
-- Name: nc_users_v2; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public.nc_users_v2 (
    id character varying(20) NOT NULL,
    email character varying(255),
    password character varying(255),
    salt character varying(255),
    invite_token character varying(255),
    invite_token_expires character varying(255),
    reset_password_expires timestamp with time zone,
    reset_password_token character varying(255),
    email_verification_token character varying(255),
    email_verified boolean,
    roles character varying(255) DEFAULT 'editor'::character varying,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    token_version character varying(255),
    display_name character varying(255),
    user_name character varying(255),
    blocked boolean DEFAULT false,
    blocked_reason character varying(255)
);


ALTER TABLE public.nc_users_v2 OWNER TO nocodb;

--
-- Name: nc_views_v2; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public.nc_views_v2 (
    id character varying(20) NOT NULL,
    source_id character varying(20),
    base_id character varying(20),
    fk_model_id character varying(20),
    title character varying(255),
    type integer,
    is_default boolean,
    show_system_fields boolean,
    lock_type character varying(255) DEFAULT 'collaborative'::character varying,
    uuid character varying(255),
    password character varying(255),
    show boolean,
    "order" real,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    meta text,
    description character varying(255)
);


ALTER TABLE public.nc_views_v2 OWNER TO nocodb;

--
-- Name: notification; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public.notification (
    id character varying(20) NOT NULL,
    type character varying(40),
    body text,
    is_read boolean DEFAULT false,
    is_deleted boolean DEFAULT false,
    fk_user_id character varying(20),
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.notification OWNER TO nocodb;

--
-- Name: xc_knex_migrations; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public.xc_knex_migrations (
    id integer NOT NULL,
    name character varying(255),
    batch integer,
    migration_time timestamp with time zone
);


ALTER TABLE public.xc_knex_migrations OWNER TO nocodb;

--
-- Name: xc_knex_migrations_id_seq; Type: SEQUENCE; Schema: public; Owner: nocodb
--

CREATE SEQUENCE public.xc_knex_migrations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.xc_knex_migrations_id_seq OWNER TO nocodb;

--
-- Name: xc_knex_migrations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: nocodb
--

ALTER SEQUENCE public.xc_knex_migrations_id_seq OWNED BY public.xc_knex_migrations.id;


--
-- Name: xc_knex_migrations_lock; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public.xc_knex_migrations_lock (
    index integer NOT NULL,
    is_locked integer
);


ALTER TABLE public.xc_knex_migrations_lock OWNER TO nocodb;

--
-- Name: xc_knex_migrations_lock_index_seq; Type: SEQUENCE; Schema: public; Owner: nocodb
--

CREATE SEQUENCE public.xc_knex_migrations_lock_index_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.xc_knex_migrations_lock_index_seq OWNER TO nocodb;

--
-- Name: xc_knex_migrations_lock_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: nocodb
--

ALTER SEQUENCE public.xc_knex_migrations_lock_index_seq OWNED BY public.xc_knex_migrations_lock.index;


--
-- Name: xc_knex_migrationsv2; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public.xc_knex_migrationsv2 (
    id integer NOT NULL,
    name character varying(255),
    batch integer,
    migration_time timestamp with time zone
);


ALTER TABLE public.xc_knex_migrationsv2 OWNER TO nocodb;

--
-- Name: xc_knex_migrationsv2_id_seq; Type: SEQUENCE; Schema: public; Owner: nocodb
--

CREATE SEQUENCE public.xc_knex_migrationsv2_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.xc_knex_migrationsv2_id_seq OWNER TO nocodb;

--
-- Name: xc_knex_migrationsv2_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: nocodb
--

ALTER SEQUENCE public.xc_knex_migrationsv2_id_seq OWNED BY public.xc_knex_migrationsv2.id;


--
-- Name: xc_knex_migrationsv2_lock; Type: TABLE; Schema: public; Owner: nocodb
--

CREATE TABLE public.xc_knex_migrationsv2_lock (
    index integer NOT NULL,
    is_locked integer
);


ALTER TABLE public.xc_knex_migrationsv2_lock OWNER TO nocodb;

--
-- Name: xc_knex_migrationsv2_lock_index_seq; Type: SEQUENCE; Schema: public; Owner: nocodb
--

CREATE SEQUENCE public.xc_knex_migrationsv2_lock_index_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.xc_knex_migrationsv2_lock_index_seq OWNER TO nocodb;

--
-- Name: xc_knex_migrationsv2_lock_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: nocodb
--

ALTER SEQUENCE public.xc_knex_migrationsv2_lock_index_seq OWNED BY public.xc_knex_migrationsv2_lock.index;


--
-- Name: nc_api_tokens id; Type: DEFAULT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.nc_api_tokens ALTER COLUMN id SET DEFAULT nextval('public.nc_api_tokens_id_seq'::regclass);


--
-- Name: nc_fl6j___LeadAnswers id; Type: DEFAULT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public."nc_fl6j___LeadAnswers" ALTER COLUMN id SET DEFAULT nextval('public."nc_fl6j___LeadAnswers_id_seq"'::regclass);


--
-- Name: nc_fl6j___Leads id; Type: DEFAULT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public."nc_fl6j___Leads" ALTER COLUMN id SET DEFAULT nextval('public."nc_fl6j___Leads_id_seq"'::regclass);


--
-- Name: nc_fl6j___ServiceQuestionOptions id; Type: DEFAULT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public."nc_fl6j___ServiceQuestionOptions" ALTER COLUMN id SET DEFAULT nextval('public."nc_fl6j___ServiceQuestionOptions_id_seq"'::regclass);


--
-- Name: nc_fl6j___ServiceQuestions id; Type: DEFAULT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public."nc_fl6j___ServiceQuestions" ALTER COLUMN id SET DEFAULT nextval('public."nc_fl6j___ServiceQuestions_id_seq"'::regclass);


--
-- Name: nc_jmsd___Approval Id; Type: DEFAULT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public."nc_jmsd___Approval" ALTER COLUMN "Id" SET DEFAULT nextval('public."nc_jmsd___Approval_Id_seq"'::regclass);


--
-- Name: nc_jmsd___Attempt Id; Type: DEFAULT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public."nc_jmsd___Attempt" ALTER COLUMN "Id" SET DEFAULT nextval('public."nc_jmsd___Attempt_Id_seq"'::regclass);


--
-- Name: nc_jmsd___Company Id; Type: DEFAULT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public."nc_jmsd___Company" ALTER COLUMN "Id" SET DEFAULT nextval('public."nc_jmsd___Company_Id_seq"'::regclass);


--
-- Name: nc_jmsd___Conversation Id; Type: DEFAULT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public."nc_jmsd___Conversation" ALTER COLUMN "Id" SET DEFAULT nextval('public."nc_jmsd___Conversation_Id_seq"'::regclass);


--
-- Name: nc_jmsd___Lead Id; Type: DEFAULT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public."nc_jmsd___Lead" ALTER COLUMN "Id" SET DEFAULT nextval('public."nc_jmsd___Lead_Id_seq"'::regclass);


--
-- Name: nc_jmsd___Message_Template Id; Type: DEFAULT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public."nc_jmsd___Message_Template" ALTER COLUMN "Id" SET DEFAULT nextval('public."nc_jmsd___Message_Template_Id_seq"'::regclass);


--
-- Name: nc_jmsd___Outcome Id; Type: DEFAULT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public."nc_jmsd___Outcome" ALTER COLUMN "Id" SET DEFAULT nextval('public."nc_jmsd___Outcome_Id_seq"'::regclass);


--
-- Name: nc_jmsd___Pack Id; Type: DEFAULT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public."nc_jmsd___Pack" ALTER COLUMN "Id" SET DEFAULT nextval('public."nc_jmsd___Pack_Id_seq"'::regclass);


--
-- Name: nc_jmsd___Research_Snapshot Id; Type: DEFAULT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public."nc_jmsd___Research_Snapshot" ALTER COLUMN "Id" SET DEFAULT nextval('public."nc_jmsd___Research_Snapshot_Id_seq"'::regclass);


--
-- Name: nc_jmsd___Segment Id; Type: DEFAULT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public."nc_jmsd___Segment" ALTER COLUMN "Id" SET DEFAULT nextval('public."nc_jmsd___Segment_Id_seq"'::regclass);


--
-- Name: nc_shared_bases id; Type: DEFAULT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.nc_shared_bases ALTER COLUMN id SET DEFAULT nextval('public.nc_shared_bases_id_seq'::regclass);


--
-- Name: nc_store id; Type: DEFAULT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.nc_store ALTER COLUMN id SET DEFAULT nextval('public.nc_store_id_seq'::regclass);


--
-- Name: xc_knex_migrations id; Type: DEFAULT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.xc_knex_migrations ALTER COLUMN id SET DEFAULT nextval('public.xc_knex_migrations_id_seq'::regclass);


--
-- Name: xc_knex_migrations_lock index; Type: DEFAULT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.xc_knex_migrations_lock ALTER COLUMN index SET DEFAULT nextval('public.xc_knex_migrations_lock_index_seq'::regclass);


--
-- Name: xc_knex_migrationsv2 id; Type: DEFAULT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.xc_knex_migrationsv2 ALTER COLUMN id SET DEFAULT nextval('public.xc_knex_migrationsv2_id_seq'::regclass);


--
-- Name: xc_knex_migrationsv2_lock index; Type: DEFAULT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.xc_knex_migrationsv2_lock ALTER COLUMN index SET DEFAULT nextval('public.xc_knex_migrationsv2_lock_index_seq'::regclass);


--
-- Data for Name: nc_api_tokens; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public.nc_api_tokens (id, base_id, db_alias, description, permissions, token, expiry, enabled, created_at, updated_at, fk_user_id) FROM stdin;
1	\N	\N	Token-1	\N	jJmShDT1NH-MFb9GYg8UfzJ6lP3o87EWkPPclRYs	\N	t	2026-01-06 16:04:15+01	2026-01-06 16:04:15+01	us8g4rajnw6fzr9r
3	\N	\N	LinkedInStealthSourcing	\N	kY-buadug23tNkDSoooy5esG8Ns56ib_AZacB5em	\N	t	2026-02-03 10:51:02+01	2026-02-03 10:51:02+01	us5ceritq5sgzoni
4	\N	\N	Token-2-02-03-2025	\N	lj9BHM97WqSswj4vIjyySy9k00SX-ku4jWW9I7YN	\N	t	2026-02-03 11:05:01+01	2026-02-03 11:05:01+01	us8g4rajnw6fzr9r
\.


--
-- Data for Name: nc_audit_v2; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public.nc_audit_v2 (id, "user", ip, source_id, base_id, fk_model_id, row_id, op_type, op_sub_type, status, description, details, created_at, updated_at) FROM stdin;
adtki17bnmom3akwe	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___Features with alias Features has been created	\N	2025-12-30 17:27:36+01	2025-12-30 17:27:36+01
adt164duas2uosxgy	team@mailerblend.com	185.195.59.191	\N	\N	\N	\N	AUTHENTICATION	SIGNUP	\N	User has signed up	\N	2025-12-30 17:27:36+01	2025-12-30 17:27:36+01
adtrmqj9o01mq2r04	team@mailerblend.com	\N	\N	\N	\N	\N	AUTHENTICATION	SIGNIN	\N	\N	\N	2025-12-30 17:27:36+01	2025-12-30 17:27:36+01
adthzgtiqltnaww5v	team@mailerblend.com	\N	\N	\N	\N	\N	AUTHENTICATION	SIGNIN	\N	\N	\N	2025-12-30 17:30:37+01	2025-12-30 17:30:37+01
adtxnxxe3wcxg9x3v	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___table with alias Table has been created	\N	2025-12-30 17:42:31+01	2025-12-30 17:42:31+01
adtdga4ppuaehddee	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	muty094k043flo3	\N	DATA	BULK_INSERT	\N	1 record has been bulk inserted in Table	\N	2025-12-30 17:42:31+01	2025-12-30 17:42:31+01
adtbjb6v6m4a2by4z	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___Table-1 with alias Table-1 has been created	\N	2025-12-30 17:43:58+01	2025-12-30 17:43:58+01
adtjhfjw8oh04f8vv	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___table with alias Table  	\N	2025-12-30 17:46:28+01	2025-12-30 17:46:28+01
adtehnu759a8ap9v3	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___Table-2 with alias Table-2 has been created	\N	2025-12-30 17:46:35+01	2025-12-30 17:46:35+01
adtqfasndwa07cs17	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___Features with alias Features  	\N	2025-12-30 17:46:50+01	2025-12-30 17:46:50+01
adt5jj6zmxv42lbw4	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___Table-2 with alias Table-2  	\N	2025-12-30 17:46:55+01	2025-12-30 17:46:55+01
adta0ov1y44pxwlbj	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___Table-1 with alias Table-1  	\N	2025-12-30 17:47:00+01	2025-12-30 17:47:00+01
adtk1fj6webhwx0m5	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___table with alias Table has been created	\N	2025-12-30 17:47:36+01	2025-12-30 17:47:36+01
adtx9iasq8towhs26	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	mg1fxmvmfjq3m3z	\N	DATA	BULK_INSERT	\N	1 record has been bulk inserted in Table	\N	2025-12-30 17:47:37+01	2025-12-30 17:47:37+01
adtlr5ff5nyixogcl	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	mg1fxmvmfjq3m3z	2	DATA	INSERT	\N	Record with ID 2 has been inserted into Table Table	\N	2025-12-30 18:44:31+01	2025-12-30 18:44:31+01
adt3snpqtxblkf93s	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___table with alias Table  	\N	2025-12-30 18:46:21+01	2025-12-30 18:46:21+01
adtjeokpxkpy7coxl	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___table with alias Table has been created	\N	2025-12-30 18:46:47+01	2025-12-30 18:46:47+01
adt3yb3ke0ugeg89y	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	mzf98gj4iyqwn06	\N	DATA	BULK_INSERT	\N	7 records have been bulk inserted in Table	\N	2025-12-30 18:46:48+01	2025-12-30 18:46:48+01
adtj7kgjk2tcane8p	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___table with alias Table  	\N	2025-12-30 18:47:26+01	2025-12-30 18:47:26+01
adtk56vnktw18hfll	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___nombre_email_telefono_tipo_empresa_csv with alias NombreEmailTelefonoTipoEmpresaCsv has been created	\N	2025-12-30 18:54:06+01	2025-12-30 18:54:06+01
adtmv1ul8ef4h9qsv	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m0azl6o40lj1g4b	\N	DATA	BULK_INSERT	\N	7 records have been bulk inserted in NombreEmailTelefonoTipoEmpresaCsv	\N	2025-12-30 18:54:07+01	2025-12-30 18:54:07+01
adt6q0mm7hm7cdphs	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	UPDATE	\N	The column email with alias email from table nc_fl6j___nombre_email_telefono_tipo_empresa_csv has been updated	\N	2025-12-30 18:55:20+01	2025-12-30 18:55:20+01
adt4bick0wfqic8w5	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	UPDATE	\N	The column telefono with alias telefono from table nc_fl6j___nombre_email_telefono_tipo_empresa_csv has been updated	\N	2025-12-30 18:55:58+01	2025-12-30 18:55:58+01
adt4wdla3l4psr9ow	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	UPDATE	\N	The column tipo_empresa with alias tipo_empresa from table nc_fl6j___nombre_email_telefono_tipo_empresa_csv has been updated	\N	2025-12-30 18:58:05+01	2025-12-30 18:58:05+01
adt8127drg3gwyx57	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	UPDATE	\N	The column servicio with alias servicio from table nc_fl6j___nombre_email_telefono_tipo_empresa_csv has been updated	\N	2025-12-30 19:00:19+01	2025-12-30 19:00:19+01
adt3s1ezte6ztvtuz	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	UPDATE	\N	The column mensaje with alias mensaje from table nc_fl6j___nombre_email_telefono_tipo_empresa_csv has been updated	\N	2025-12-30 19:02:11+01	2025-12-30 19:02:11+01
adt8hxy69eq2whles	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	UPDATE	\N	The column como_nos_conociste with alias como_nos_conociste from table nc_fl6j__Prueba has been updated	\N	2025-12-30 19:05:09+01	2025-12-30 19:05:09+01
adttge7zktjut3f85	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j__Prueba with alias Prueba  	\N	2025-12-30 19:24:24+01	2025-12-30 19:24:24+01
adtm24u7uh6wybx6u	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___table with alias Table has been created	\N	2025-12-30 19:24:39+01	2025-12-30 19:24:39+01
adtbscvoivyjtr7jl	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	mycpnhd0osb4sf5	\N	DATA	BULK_INSERT	\N	1 record has been bulk inserted in Table	\N	2025-12-30 19:24:39+01	2025-12-30 19:24:39+01
adtaqseikj1jml4xi	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___table with alias Table  	\N	2025-12-30 19:24:48+01	2025-12-30 19:24:48+01
adt4v9hso2cry6fxf	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___table with alias Table has been created	\N	2025-12-30 19:27:36+01	2025-12-30 19:27:36+01
adt57fkppqw4mrsnc	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	mdkspv3wvfr0hzh	\N	DATA	BULK_INSERT	\N	1 record has been bulk inserted in Table	\N	2025-12-30 19:27:36+01	2025-12-30 19:27:36+01
adt2b628p9skziljb	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___table with alias Table  	\N	2025-12-30 19:33:37+01	2025-12-30 19:33:37+01
adtaz3czmq5mpgzn3	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___NT_FormularioContacto_Config with alias NT_FormularioContacto_Config has been created	\N	2025-12-30 19:33:57+01	2025-12-30 19:33:57+01
adtv4tz2i960915m2	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	mq5j8ipga0srjeu	1	DATA	INSERT	\N	Record with ID 1 has been inserted into Table NT_FormularioContacto_Config	\N	2025-12-30 19:34:06+01	2025-12-30 19:34:06+01
adtqr8g8cnihsycv4	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	UPDATE	\N	The column nombre with alias nombre from table nc_fl6j___NT_FormularioContacto_Config has been updated	\N	2025-12-30 19:34:17+01	2025-12-30 19:34:17+01
adty5fl4z7r0zjwm4	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___NT_FormularioContacto_Config with alias NT_FormularioContacto_Config  	\N	2025-12-30 19:35:11+01	2025-12-30 19:35:11+01
adtgb6rjqtsaxv5xj	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___table with alias Table has been created	\N	2025-12-30 19:43:36+01	2025-12-30 19:43:36+01
adt8o9zdcouylrjwq	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m0lqmkqgc7gpyzc	\N	DATA	BULK_INSERT	\N	1 record has been bulk inserted in Table	\N	2025-12-30 19:43:36+01	2025-12-30 19:43:36+01
adtnofjbe7tnkbhmg	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___table with alias Table  	\N	2025-12-30 20:18:13+01	2025-12-30 20:18:13+01
adteo3tj9exb0ws4h	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___table with alias Table has been created	\N	2025-12-30 20:25:53+01	2025-12-30 20:25:53+01
adtvqvsz6mskg4486	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m1q2thhh8ypuwaz	\N	DATA	BULK_INSERT	\N	1 record has been bulk inserted in Table	\N	2025-12-30 20:25:53+01	2025-12-30 20:25:53+01
adt0qmh1zo6tyvvji	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___table with alias Table  	\N	2025-12-30 20:27:46+01	2025-12-30 20:27:46+01
adtqghdtt3k0xiuvu	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___Table-1 with alias Table-1 has been created	\N	2025-12-30 20:27:50+01	2025-12-30 20:27:50+01
adtmjxlh2spte0f6a	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___Table-1 with alias Table-1  	\N	2025-12-30 20:28:00+01	2025-12-30 20:28:00+01
adtrtxafaerudl38c	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___table with alias Table has been created	\N	2025-12-30 20:28:14+01	2025-12-30 20:28:14+01
adth8n8vwtyuadtqh	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m9ca0e7p5cx1px4	\N	DATA	BULK_INSERT	\N	1 record has been bulk inserted in Table	\N	2025-12-30 20:28:14+01	2025-12-30 20:28:14+01
adtaqk3omvyubanz3	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___table with alias Table  	\N	2025-12-30 20:30:20+01	2025-12-30 20:30:20+01
adtbf8dc6nzvncz4w	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___table with alias Table has been created	\N	2025-12-30 20:30:38+01	2025-12-30 20:30:38+01
adtwjfavutsj4a0h1	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	mnaapaczlye8i3h	\N	DATA	BULK_INSERT	\N	1 record has been bulk inserted in Table	\N	2025-12-30 20:30:38+01	2025-12-30 20:30:38+01
adtiohw8nffawsxdy	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	mnaapaczlye8i3h	2	DATA	INSERT	\N	Record with ID 2 has been inserted into Table Table	\N	2025-12-30 20:30:51+01	2025-12-30 20:30:51+01
adtjmfyqh9tiqqh0c	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	mnaapaczlye8i3h	2	DATA	UPDATE	\N	Record with ID 2 has been updated in Table Table.\nColumn "field_types email" got changed from "null" to "bvcbcb"	<span class="">field_types email</span>\n  : <span class="text-decoration-line-through red px-2 lighten-4 black--text">null</span>\n  <span class="black--text green lighten-4 px-2">bvcbcb</span>	2025-12-30 20:30:53+01	2025-12-30 20:30:53+01
adt4yzu8s91bp6hvv	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	mnaapaczlye8i3h	3	DATA	INSERT	\N	Record with ID 3 has been inserted into Table Table	\N	2025-12-30 20:30:54+01	2025-12-30 20:30:54+01
adt6x9gi3xnssrvv0	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___table with alias Table  	\N	2025-12-30 20:33:11+01	2025-12-30 20:33:11+01
adtm8ghzmtim54p8s	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___table with alias Table has been created	\N	2025-12-30 20:33:32+01	2025-12-30 20:33:32+01
adtwfgcqpjpdfyj20	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m2nm9a74rn6oujk	\N	DATA	BULK_INSERT	\N	1 record has been bulk inserted in Table	\N	2025-12-30 20:33:32+01	2025-12-30 20:33:32+01
adtuvmef2tpj62jvu	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___table with alias Table  	\N	2025-12-30 20:34:28+01	2025-12-30 20:34:28+01
adtkllkbdhtfr98ea	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___table with alias Table has been created	\N	2025-12-30 20:34:48+01	2025-12-30 20:34:48+01
adtiamk0agksru8u1	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	myhpo7jq8jwe5x4	\N	DATA	BULK_INSERT	\N	1 record has been bulk inserted in Table	\N	2025-12-30 20:34:48+01	2025-12-30 20:34:48+01
adt9zv5a12dusrq4k	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	UPDATE	\N	The column nombre with alias nombre from table nc_fl6j___table has been updated	\N	2025-12-30 20:35:13+01	2025-12-30 20:35:13+01
adtbawhpqm9jj1v12	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___table with alias Table  	\N	2025-12-30 20:35:40+01	2025-12-30 20:35:40+01
adtkwfjpxzno9i45g	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___table with alias Table has been created	\N	2025-12-30 20:36:14+01	2025-12-30 20:36:14+01
adtxft7g06l39apvv	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	mgxxu0fz08jv4o9	\N	DATA	BULK_INSERT	\N	1 record has been bulk inserted in Table	\N	2025-12-30 20:36:15+01	2025-12-30 20:36:15+01
adt8ufoa5c3fzghx0	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___table with alias Table  	\N	2025-12-30 20:37:54+01	2025-12-30 20:37:54+01
adtlh7oc8zp394qi9	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___table with alias Table has been created	\N	2025-12-30 20:38:09+01	2025-12-30 20:38:09+01
adtzm0932xonnu5ik	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	myq50iir6rcwbw4	\N	DATA	BULK_INSERT	\N	1 record has been bulk inserted in Table	\N	2025-12-30 20:38:09+01	2025-12-30 20:38:09+01
adtbm6g7ol459gq6n	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___table with alias Table  	\N	2025-12-30 20:44:45+01	2025-12-30 20:44:45+01
adtwsfoufokuzsy7q	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___table with alias Table has been created	\N	2025-12-30 20:45:52+01	2025-12-30 20:45:52+01
adtss5qiqajk5ceik	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	UPDATE	\N	The column nombre with alias nombre from table nc_fl6j___table has been updated	\N	2025-12-30 20:47:23+01	2025-12-30 20:47:23+01
adto9hn0emqznliyx	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___table with alias Table  	\N	2025-12-30 20:47:35+01	2025-12-30 20:47:35+01
adt1mqbmqjajwd3lz	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___Table-1 with alias Table-1 has been created	\N	2025-12-30 20:48:10+01	2025-12-30 20:48:10+01
adtb8d0rax5c1c2pe	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___Table-1 with alias Table-1  	\N	2025-12-30 20:48:15+01	2025-12-30 20:48:15+01
adt6xjqsvw8xsvmht	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___leads_contacto_web with alias LeadsContactoWeb has been created	\N	2025-12-30 20:48:37+01	2025-12-30 20:48:37+01
adtu6hporakseaaw3	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	mqzg0ero42uy20v	\N	DATA	BULK_INSERT	\N	1 record has been bulk inserted in LeadsContactoWeb	\N	2025-12-30 20:48:37+01	2025-12-30 20:48:37+01
adt3f61onis6x8rhg	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	UPDATE	\N	The column nombre with alias nombre from table nc_fl6j___leads_contacto_web has been updated	\N	2025-12-30 20:48:47+01	2025-12-30 20:48:47+01
adtafk11sugax1ulb	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	UPDATE	\N	The column email with alias email from table nc_fl6j___leads_contacto_web has been updated	\N	2025-12-30 20:49:00+01	2025-12-30 20:49:00+01
adtp6js2r30nhb7eo	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___leads_contacto_web with alias LeadsContactoWeb  	\N	2025-12-30 20:50:27+01	2025-12-30 20:50:27+01
adtexxz959wluo5qb	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___table with alias Table has been created	\N	2025-12-30 20:50:40+01	2025-12-30 20:50:40+01
adtj2lc7amwsncd1x	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	muid2pv7cu5eszy	\N	DATA	BULK_INSERT	\N	8 records have been bulk inserted in Table	\N	2025-12-30 20:50:41+01	2025-12-30 20:50:41+01
adtm9vkzfwiu4pmiv	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___table with alias Table  	\N	2025-12-30 20:52:39+01	2025-12-30 20:52:39+01
adtcb3cr9kxjzm84h	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___table with alias Table has been created	\N	2025-12-30 20:52:55+01	2025-12-30 20:52:55+01
adtuzcmbk6g6u37uo	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m6byda09og452ap	\N	DATA	BULK_INSERT	\N	8 records have been bulk inserted in Table	\N	2025-12-30 20:52:55+01	2025-12-30 20:52:55+01
adtr7ue9u2ukwc4sk	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___table with alias Table  	\N	2025-12-30 20:53:02+01	2025-12-30 20:53:02+01
adtyh7vbe9y5bjngb	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___leads_contacto_web with alias LeadsContactoWeb has been created	\N	2025-12-30 20:53:21+01	2025-12-30 20:53:21+01
adtfz49lrge85jyaz	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m3bykxkpjw6war9	\N	DATA	BULK_INSERT	\N	1 record has been bulk inserted in LeadsContactoWeb	\N	2025-12-30 20:53:21+01	2025-12-30 20:53:21+01
adtftbtvec9uzmbvj	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	UPDATE	\N	The column nombre with alias nombre from table nc_fl6j___leads_contacto_web has been updated	\N	2025-12-30 20:53:30+01	2025-12-30 20:53:30+01
adtr6da0wfvouxeiq	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	UPDATE	\N	The column email with alias email from table nc_fl6j___leads_contacto_web has been updated	\N	2025-12-30 20:53:44+01	2025-12-30 20:53:44+01
adt2rkkdsql71asya	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m3bykxkpjw6war9	2	DATA	INSERT	\N	Record with ID 2 has been inserted into Table LeadsContactoWeb	\N	2025-12-30 20:53:49+01	2025-12-30 20:53:49+01
adt6wufgn9mo0pfhz	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	UPDATE	\N	The column telefono with alias telefono from table nc_fl6j___leads_contacto_web has been updated	\N	2025-12-30 20:54:14+01	2025-12-30 20:54:14+01
adtcthru6984ua8in	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m3bykxkpjw6war9	1	DATA	UPDATE	\N	Record with ID 1 has been updated in Table LeadsContactoWeb.\nColumn "telefono" got changed from "" to "631230488"	<span class="">telefono</span>\n  : <span class="text-decoration-line-through red px-2 lighten-4 black--text"></span>\n  <span class="black--text green lighten-4 px-2">631230488</span>	2025-12-30 20:54:21+01	2025-12-30 20:54:21+01
adtjqnsuxzd1w94zw	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m3bykxkpjw6war9	1	DATA	UPDATE	\N	Record with ID 1 has been updated in Table LeadsContactoWeb.\nColumn "telefono" got changed from "631230488" to "null"	<span class="">telefono</span>\n  : <span class="text-decoration-line-through red px-2 lighten-4 black--text">631230488</span>\n  <span class="black--text green lighten-4 px-2">null</span>	2025-12-30 20:54:23+01	2025-12-30 20:54:23+01
adt1dxi4cr474n374	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m3bykxkpjw6war9	1	DATA	UPDATE	\N	Record with ID 1 has been updated in Table LeadsContactoWeb.\nColumn "telefono" got changed from "null" to "+34631230488"	<span class="">telefono</span>\n  : <span class="text-decoration-line-through red px-2 lighten-4 black--text">null</span>\n  <span class="black--text green lighten-4 px-2">+34631230488</span>	2025-12-30 20:54:26+01	2025-12-30 20:54:26+01
adtycfpf7g24cqs24	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	UPDATE	\N	The column tipo_empresa with alias tipo_empresa from table nc_fl6j___leads_contacto_web has been updated	\N	2025-12-30 20:56:15+01	2025-12-30 20:56:15+01
adtqhozc8un5qkaff	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m3bykxkpjw6war9	1	DATA	UPDATE	\N	Record with ID 1 has been updated in Table LeadsContactoWeb.\nColumn "nombre" got changed from "" to "jose"	<span class="">nombre</span>\n  : <span class="text-decoration-line-through red px-2 lighten-4 black--text"></span>\n  <span class="black--text green lighten-4 px-2">jose</span>	2025-12-30 20:59:43+01	2025-12-30 20:59:43+01
adtq7x74gy3s7zk0n	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m3bykxkpjw6war9	1	DATA	UPDATE	\N	Record with ID 1 has been updated in Table LeadsContactoWeb.\nColumn "email" got changed from "" to "edu@edu.es"	<span class="">email</span>\n  : <span class="text-decoration-line-through red px-2 lighten-4 black--text"></span>\n  <span class="black--text green lighten-4 px-2">edu@edu.es</span>	2025-12-30 21:00:08+01	2025-12-30 21:00:08+01
adthhtogz3qxhg2rk	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m3bykxkpjw6war9	1	DATA	UPDATE	\N	Record with ID 1 has been updated in Table LeadsContactoWeb.\nColumn "tipo_empresa" got changed from "" to "Pyme"	<span class="">tipo_empresa</span>\n  : <span class="text-decoration-line-through red px-2 lighten-4 black--text"></span>\n  <span class="black--text green lighten-4 px-2">Pyme</span>	2025-12-30 21:00:15+01	2025-12-30 21:00:15+01
adtejzujemdamt16c	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m3bykxkpjw6war9	1	DATA	UPDATE	\N	Record with ID 1 has been updated in Table LeadsContactoWeb.\nColumn "servicio" got changed from "" to "Desarrollo web y software a medida"	<span class="">servicio</span>\n  : <span class="text-decoration-line-through red px-2 lighten-4 black--text"></span>\n  <span class="black--text green lighten-4 px-2">Desarrollo web y software a medida</span>	2025-12-30 21:00:29+01	2025-12-30 21:00:29+01
adt72g2smxlk1dhlm	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m3bykxkpjw6war9	1	DATA	UPDATE	\N	Record with ID 1 has been updated in Table LeadsContactoWeb.\nColumn "servicio" got changed from "Desarrollo web y software a medida" to "null"	<span class="">servicio</span>\n  : <span class="text-decoration-line-through red px-2 lighten-4 black--text">Desarrollo web y software a medida</span>\n  <span class="black--text green lighten-4 px-2">null</span>	2025-12-30 21:00:43+01	2025-12-30 21:00:43+01
adtg2rzvc37eqq2c2	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___leads_contacto_web with alias LeadsContactoWeb  	\N	2025-12-30 21:44:40+01	2025-12-30 21:44:40+01
adtaqua0lg5yy7ih1	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___Leads Contacto Nucleo Tecnologico with alias Leads contacto nucleo tecnologico has been created	\N	2025-12-30 21:46:20+01	2025-12-30 21:46:20+01
adt2d7bjnvgr2o030	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	msa1zswly1oh65e	\N	DATA	BULK_INSERT	\N	1 record has been bulk inserted in Leads contacto nucleo tecnologico	\N	2025-12-30 21:46:21+01	2025-12-30 21:46:21+01
adt8tkspw86mo72y7	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	UPDATE	\N	The column nombre with alias nombre from table nc_fl6j___Leads Contacto Nucleo Tecnologico has been updated	\N	2025-12-30 21:46:33+01	2025-12-30 21:46:33+01
adtagf3mrgo7jc9j9	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	UPDATE	\N	The column telefono with alias telefono from table nc_fl6j___Leads Contacto Nucleo Tecnologico has been updated	\N	2025-12-30 21:47:07+01	2025-12-30 21:47:07+01
adtd4mdmx43vmwx8l	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	UPDATE	\N	The column email with alias email from table nc_fl6j___Leads Contacto Nucleo Tecnologico has been updated	\N	2025-12-30 21:46:48+01	2025-12-30 21:46:48+01
adtlzk31sfvo4w4q3	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	UPDATE	\N	The column servicio with alias servicio from table nc_fl6j___Leads Contacto Nucleo Tecnologico has been updated	\N	2025-12-30 21:53:36+01	2025-12-30 21:53:36+01
adt7b9dli0l077e5m	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	UPDATE	\N	The column como_nos_conociste with alias como_nos_conociste from table nc_fl6j___Leads Contacto Nucleo Tecnologico has been updated	\N	2025-12-30 21:59:33+01	2025-12-30 21:59:33+01
adtifvl6u0dmxrcv4	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	UPDATE	\N	The column mensaje with alias mensaje from table nc_fl6j___Leads Contacto Nucleo Tecnologico has been updated	\N	2025-12-30 21:59:46+01	2025-12-30 21:59:46+01
adt9zmizaxb9sw4i5	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	UPDATE	\N	The column origen_lead with alias origen_lead from table nc_fl6j___Leads Contacto Nucleo Tecnologico has been updated	\N	2025-12-30 22:02:46+01	2025-12-30 22:02:46+01
adtokw6m3vlv0rp2x	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	UPDATE	\N	The column estado with alias estado from table nc_fl6j___Leads Contacto Nucleo Tecnologico has been updated	\N	2025-12-30 22:05:10+01	2025-12-30 22:05:10+01
adtfhrngachzvotya	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___Table-1 with alias Table-1 has been created	\N	2025-12-30 22:10:05+01	2025-12-30 22:10:05+01
adt34grv8p3gb2r0r	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___Table-1 with alias Table-1  	\N	2025-12-30 22:10:19+01	2025-12-30 22:10:19+01
adtds14p8tg2wq8xx	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___Leads Contacto Nucleo Tecnologico with alias Leads contacto nucleo tecnologico  	\N	2025-12-30 22:10:23+01	2025-12-30 22:10:23+01
adtl1j0nnno9jucxw	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___table with alias Table has been created	\N	2025-12-30 22:10:39+01	2025-12-30 22:10:39+01
adtg4c88u4wsxg1pk	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	msjumr0rpqaxh8i	\N	DATA	BULK_INSERT	\N	1 record has been bulk inserted in Table	\N	2025-12-30 22:10:39+01	2025-12-30 22:10:39+01
adtowqc041gg4p1oe	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___table_1 with alias Table1 has been created	\N	2025-12-30 22:11:58+01	2025-12-30 22:11:58+01
adt1o50drhbitfnys	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m52ojv4flvxaflg	\N	DATA	BULK_INSERT	\N	1 record has been bulk inserted in Table1	\N	2025-12-30 22:11:58+01	2025-12-30 22:11:58+01
adtgbuqfbjkih4ay4	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___table with alias Table  	\N	2025-12-30 22:12:30+01	2025-12-30 22:12:30+01
adt1yxmwhuqk85coz	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	UPDATE	\N	The column tipo_empresa with alias tipo_empresa from table nc_fl6j___table_1 has been updated	\N	2025-12-30 22:14:02+01	2025-12-30 22:14:02+01
adtfynix3ip2tj2i3	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m52ojv4flvxaflg	1	DATA	UPDATE	\N	Record with ID 1 has been updated in Table Table1.\nColumn "tipo_empresa" got changed from "" to "klñkljñ"	<span class="">tipo_empresa</span>\n  : <span class="text-decoration-line-through red px-2 lighten-4 black--text"></span>\n  <span class="black--text green lighten-4 px-2">klñkljñ</span>	2025-12-30 22:14:06+01	2025-12-30 22:14:06+01
adtdvo141lp4z6gae	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m52ojv4flvxaflg	2	DATA	INSERT	\N	Record with ID 2 has been inserted into Table Table1	<span class="">tipo_empresa</span>\n          : <span class="black--text green lighten-4 px-2">fhfghj</span>	2025-12-30 22:14:06+01	2025-12-30 22:14:06+01
adtuuj6stdp9ovh73	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m52ojv4flvxaflg	1	DATA	UPDATE	\N	Record with ID 1 has been updated in Table Table1.\nColumn "tipo_empresa" got changed from "klñkljñ" to "vzgbdfh"	<span class="">tipo_empresa</span>\n  : <span class="text-decoration-line-through red px-2 lighten-4 black--text">klñkljñ</span>\n  <span class="black--text green lighten-4 px-2">vzgbdfh</span>	2025-12-30 22:14:10+01	2025-12-30 22:14:10+01
adtq2pdjz8e7e8ys4	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m52ojv4flvxaflg	2	DATA	UPDATE	\N	Record with ID 2 has been updated in Table Table1.\nColumn "tipo_empresa" got changed from "fhfghj" to "fhfg"	<span class="">tipo_empresa</span>\n  : <span class="text-decoration-line-through red px-2 lighten-4 black--text">fhfghj</span>\n  <span class="black--text green lighten-4 px-2">fhfg</span>	2025-12-30 22:14:13+01	2025-12-30 22:14:13+01
adtfmj2ny0r75uad0	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m52ojv4flvxaflg	2	DATA	UPDATE	\N	Record with ID 2 has been updated in Table Table1.\nColumn "tipo_empresa" got changed from "fhfg" to ""	<span class="">tipo_empresa</span>\n  : <span class="text-decoration-line-through red px-2 lighten-4 black--text">fhfg</span>\n  <span class="black--text green lighten-4 px-2"></span>	2025-12-30 22:14:14+01	2025-12-30 22:14:14+01
adtpmbpfgvowqul8k	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m52ojv4flvxaflg	1	DATA	UPDATE	\N	Record with ID 1 has been updated in Table Table1.\nColumn "tipo_empresa" got changed from "vzgbdfh" to "null"	<span class="">tipo_empresa</span>\n  : <span class="text-decoration-line-through red px-2 lighten-4 black--text">vzgbdfh</span>\n  <span class="black--text green lighten-4 px-2">null</span>	2025-12-30 22:14:15+01	2025-12-30 22:14:15+01
adt16bg0cwv9e5fqn	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m52ojv4flvxaflg	3	DATA	INSERT	\N	Record with ID 3 has been inserted into Table Table1	<span class="">tipo_empresa</span>\n          : <span class="black--text green lighten-4 px-2">fhfghj</span>	2025-12-30 22:14:28+01	2025-12-30 22:14:28+01
adtllpzbcc0ybdffu	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m52ojv4flvxaflg	3	DATA	DELETE	\N	Record with ID 3 has been deleted in Table Table1	\N	2025-12-30 22:14:36+01	2025-12-30 22:14:36+01
adt6pw56aji7ntl2a	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	CREATE	\N	The column entrada with alias entrada from table nc_fl6j___table_1 has been created	\N	2025-12-30 22:15:08+01	2025-12-30 22:15:08+01
adtysblr87m5xzb7h	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___table_1 with alias Table1  	\N	2025-12-30 22:15:51+01	2025-12-30 22:15:51+01
adthpxa0qocrq1vbj	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___Leads Contacto Nucleo Tecnologico with alias Leads contacto nucleo tecnologico has been created	\N	2025-12-30 22:17:47+01	2025-12-30 22:17:47+01
adtjpbbpu3gc1avrk	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	masx7pt1333ot9x	\N	DATA	BULK_INSERT	\N	1 record has been bulk inserted in Leads contacto nucleo tecnologico	\N	2025-12-30 22:17:48+01	2025-12-30 22:17:48+01
adtk65zdlgt9lof2p	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	UPDATE	\N	The column Entrada with alias Entrada from table nc_fl6j___Leads Contacto Nucleo Tecnologico has been updated	\N	2025-12-30 22:18:06+01	2025-12-30 22:18:06+01
adtp97ghkjzhtiouk	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	UPDATE	\N	The column nombre with alias nombre from table nc_fl6j___Leads Contacto Nucleo Tecnologico has been updated	\N	2025-12-30 22:18:12+01	2025-12-30 22:18:12+01
adtqjj3mejvl2lkr5	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	UPDATE	\N	The column email with alias email from table nc_fl6j___Leads Contacto Nucleo Tecnologico has been updated	\N	2025-12-30 22:18:23+01	2025-12-30 22:18:23+01
adt0eyi7gwyvmlxjk	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	UPDATE	\N	The column telefono with alias telefono from table nc_fl6j___Leads Contacto Nucleo Tecnologico has been updated	\N	2025-12-30 22:18:32+01	2025-12-30 22:18:32+01
adt6umwcgmaexyqzi	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	masx7pt1333ot9x	\N	DATA	BULK_INSERT	\N	1 record has been bulk inserted in Leads contacto nucleo tecnologico	\N	2025-12-30 22:23:36+01	2025-12-30 22:23:36+01
adtm75tid9092p0t6	team@mailerblend.com	192.168.1.254	\N	\N	\N	\N	ORG_USER	INVITE	\N	dolaoye686@gmail.com has been invited to the organisation	\N	2025-12-31 11:09:27+01	2025-12-31 11:09:27+01
adt4fc1ebp4rarb8o	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___Leads Contacto Nucleo Tecnologico with alias Leads contacto nucleo tecnologico  	\N	2025-12-31 11:18:14+01	2025-12-31 11:18:14+01
adtskc0jx7owfz42b	dolaoye686@gmail.com	102.89.47.62	\N	\N	\N	\N	AUTHENTICATION	SIGNUP	\N	User has signed up	\N	2025-12-31 11:30:30+01	2025-12-31 11:30:30+01
adtwbqygzx4heepme	dolaoye686@gmail.com	\N	\N	\N	\N	\N	AUTHENTICATION	SIGNIN	\N	\N	\N	2025-12-31 11:30:30+01	2025-12-31 11:30:30+01
adt1qto027knq5t4l	team@mailerblend.com	\N	\N	\N	\N	\N	AUTHENTICATION	SIGNIN	\N	\N	\N	2025-12-31 14:55:04+01	2025-12-31 14:55:04+01
adtu9m88j3afoz07i	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	AUTHENTICATION	INVITE	\N	invited dolaoye686@gmail.com to pata00z3me9f1bz base 	\N	2026-01-02 00:51:12+01	2026-01-02 00:51:12+01
adt6chn5amjepc7t4	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	AUTHENTICATION	ROLES_MANAGEMENT	\N	Roles for dolaoye686@gmail.com with has been updated to owner	\N	2026-01-02 00:51:24+01	2026-01-02 00:51:24+01
adtw37gzp5wovm7cp	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	AUTHENTICATION	INVITE	\N	invited faidatonakoya@gmail.com to pata00z3me9f1bz base 	\N	2026-01-05 21:48:43+01	2026-01-05 21:48:43+01
adtsc5on2l3edrc9j	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	AUTHENTICATION	INVITE	\N	invited faidatonakoya74@gmail.com to pata00z3me9f1bz base 	\N	2026-01-06 09:26:37+01	2026-01-06 09:26:37+01
adtr46af36r24pyvw	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___Table-1 with alias Table-1 has been created	\N	2026-01-06 15:48:30+01	2026-01-06 15:48:30+01
adt1yk6mb6w05nztx	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___Table-1 with alias Table-1  	\N	2026-01-06 15:48:37+01	2026-01-06 15:48:37+01
adtxd087o4m3n2zed	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___table with alias Table has been created	\N	2026-01-06 15:49:02+01	2026-01-06 15:49:02+01
adtgp3f40a93qb8rs	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	mvgpsjfc4v2mifs	\N	DATA	BULK_INSERT	\N	1 record has been bulk inserted in Table	\N	2026-01-06 15:49:02+01	2026-01-06 15:49:02+01
adt458avflt8kx8yt	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___table with alias Table  	\N	2026-01-06 15:49:14+01	2026-01-06 15:49:14+01
adtapewstyhzog60f	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___table with alias Table has been created	\N	2026-01-06 15:50:17+01	2026-01-06 15:50:17+01
adtf44ulxsr2xc86r	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	mhujcuou6injr1q	\N	DATA	BULK_INSERT	\N	1 record has been bulk inserted in Table	\N	2026-01-06 15:50:17+01	2026-01-06 15:50:17+01
adtwm7qvym3uriimd	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___table with alias Table  	\N	2026-01-06 15:50:27+01	2026-01-06 15:50:27+01
adt4b6v4mw8m31ou8	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___table with alias Table has been created	\N	2026-01-06 15:54:27+01	2026-01-06 15:54:27+01
adtp2d4ihr0yb7nln	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	mcpi99t8sir1ie4	\N	DATA	BULK_INSERT	\N	1 record has been bulk inserted in Table	\N	2026-01-06 15:54:27+01	2026-01-06 15:54:27+01
adtvlx76jexlvf999	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___table with alias Table  	\N	2026-01-06 15:54:36+01	2026-01-06 15:54:36+01
adtsv0ye26v6yv3x0	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___leads with alias Leads has been created	\N	2026-01-06 16:11:08+01	2026-01-06 16:11:08+01
adtsidhfbwu0d9n6y	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___services with alias Services has been created	\N	2026-01-06 16:28:31+01	2026-01-06 16:28:31+01
adto025zdyhqpcn4g	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___questions with alias Questions has been created	\N	2026-01-06 16:28:51+01	2026-01-06 16:28:51+01
adtvo2383ihpm9puw	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___service_questions with alias ServiceQuestions has been created	\N	2026-01-06 16:29:04+01	2026-01-06 16:29:04+01
adt8r95iq4wv27rfs	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___question_rules with alias QuestionRules has been created	\N	2026-01-06 16:29:22+01	2026-01-06 16:29:22+01
adts2m0tup0wi1yhr	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___answers with alias Answers has been created	\N	2026-01-06 16:29:45+01	2026-01-06 16:29:45+01
adtw8ptburz5mwlh9	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___leads with alias Leads  	\N	2026-01-06 16:43:47+01	2026-01-06 16:43:47+01
adt91h673uasimcsg	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___services with alias Services  	\N	2026-01-06 16:43:52+01	2026-01-06 16:43:52+01
adtjd5u8imfu8bumh	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___questions with alias Questions  	\N	2026-01-06 16:43:56+01	2026-01-06 16:43:56+01
adtbt93m3ladk2ddi	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___service_questions with alias ServiceQuestions  	\N	2026-01-06 16:44:00+01	2026-01-06 16:44:00+01
adtyfp8l8hkjwn1ib	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___question_rules with alias QuestionRules  	\N	2026-01-06 16:44:06+01	2026-01-06 16:44:06+01
adtjfj1kwvixc8iqq	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___answers with alias Answers  	\N	2026-01-06 16:44:13+01	2026-01-06 16:44:13+01
adt98ertqjrxd1uhv	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___Contactos with alias Contactos has been created	\N	2026-01-06 16:45:27+01	2026-01-06 16:45:27+01
adtia7tf33zdw93z3	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___Contactos with alias Contactos  	\N	2026-01-06 16:52:18+01	2026-01-06 16:52:18+01
adt8nvb7eh77lzdeg	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___Clientes with alias Clientes has been created	\N	2026-01-06 16:54:41+01	2026-01-06 16:54:41+01
adt9ua9ta288nrp1b	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___Servicios with alias Servicios has been created	\N	2026-01-06 16:59:05+01	2026-01-06 16:59:05+01
adt19vg563wtk3slu	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___Preguntas with alias Preguntas has been created	\N	2026-01-06 17:01:30+01	2026-01-06 17:01:30+01
adt198bir41o4acnd	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___Respuestas with alias Respuestas has been created	\N	2026-01-06 17:03:01+01	2026-01-06 17:03:01+01
adtpad26c92tj75hn	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___leads_raw with alias LeadsRaw has been created	\N	2026-01-06 17:05:04+01	2026-01-06 17:05:04+01
adtnqq8y915l5p833	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___leads_raw_v2 with alias LeadsRawV2 has been created	\N	2026-01-06 17:08:06+01	2026-01-06 17:08:06+01
adt2b00fs7wv10xby	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___leads_raw_v3 with alias LeadsRawV3 has been created	\N	2026-01-06 17:08:53+01	2026-01-06 17:08:53+01
adtj55d9wfismiwye	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___Clientes with alias Clientes  	\N	2026-01-06 17:12:40+01	2026-01-06 17:12:40+01
adtcspft85gvpl4wa	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___Clientes with alias Clientes has been created	\N	2026-01-06 17:12:53+01	2026-01-06 17:12:53+01
adtffwsrbtx4h4lsw	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___Clientes with alias Clientes  	\N	2026-01-06 17:13:54+01	2026-01-06 17:13:54+01
adtui2fw3tv5u64qd	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___Contactos_Vip with alias ContactosVip has been created	\N	2026-01-06 17:14:58+01	2026-01-06 17:14:58+01
adtfxg5rmvj57yjez	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___Clientes_Nuevos with alias ClientesNuevos has been created	\N	2026-01-06 17:15:33+01	2026-01-06 17:15:33+01
adtl4ctqws02khhiv	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___Servicios with alias Servicios  	\N	2026-01-06 17:17:59+01	2026-01-06 17:17:59+01
adtgiqcn5krpdkqwp	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	DELETE	\N	The column Servicio_Relacionado with alias ServicioRelacionado from table nc_fl6j___Preguntas has been deleted	\N	2026-01-06 17:18:03+01	2026-01-06 17:18:03+01
adt1vqnawu9u4ahao	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___Preguntas with alias Preguntas  	\N	2026-01-06 17:18:03+01	2026-01-06 17:18:03+01
adti18qymn53jra0b	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	DELETE	\N	The column Cliente with alias Cliente from table nc_fl6j___Respuestas has been deleted	\N	2026-01-06 17:18:07+01	2026-01-06 17:18:07+01
adt7zm8zr3nbb3xba	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	DELETE	\N	The column Pregunta with alias Pregunta from table nc_fl6j___Respuestas has been deleted	\N	2026-01-06 17:18:07+01	2026-01-06 17:18:07+01
adti5fjk6cipgmw0s	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___Respuestas with alias Respuestas  	\N	2026-01-06 17:18:07+01	2026-01-06 17:18:07+01
adtaxx2nwa2lfgjk8	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___leads_raw with alias LeadsRaw  	\N	2026-01-06 17:18:10+01	2026-01-06 17:18:10+01
adt9q83yn584ithy3	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___leads_raw_v2 with alias LeadsRawV2  	\N	2026-01-06 17:18:15+01	2026-01-06 17:18:15+01
adtvq513ssa797po3	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___leads_raw_v3 with alias LeadsRawV3  	\N	2026-01-06 17:18:19+01	2026-01-06 17:18:19+01
adtflzt7mqkie360j	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___Contactos_Vip with alias ContactosVip  	\N	2026-01-06 17:18:23+01	2026-01-06 17:18:23+01
adt9hzmqesks9n60b	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___Clientes_Nuevos with alias ClientesNuevos  	\N	2026-01-06 17:18:28+01	2026-01-06 17:18:28+01
adt5p2uvojd0aw5d8	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___leads_raw_v1 with alias LeadsRawV1 has been created	\N	2026-01-06 17:19:01+01	2026-01-06 17:19:01+01
adt9odl526piaob5w	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___services with alias Services has been created	\N	2026-01-06 17:21:49+01	2026-01-06 17:21:49+01
adtkkmii23m8m9j33	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___questions with alias Questions has been created	\N	2026-01-06 17:22:12+01	2026-01-06 17:22:12+01
adtclny5u1q4ruq4h	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___question_options with alias QuestionOptions has been created	\N	2026-01-06 17:22:32+01	2026-01-06 17:22:32+01
adtrwljj1you8xmet	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___answers with alias Answers has been created	\N	2026-01-06 17:23:33+01	2026-01-06 17:23:33+01
adtn7dnlp8r3kb798	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	CREATE	\N	The column service with alias Service from table nc_fl6j___leads_raw_v1 has been created	\N	2026-01-06 17:24:21+01	2026-01-06 17:24:21+01
adteufnftwb9axqo9	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	CREATE	\N	The column service with alias Service from table nc_fl6j___questions has been created	\N	2026-01-06 17:24:40+01	2026-01-06 17:24:40+01
adtui4ced3zdqov2t	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	CREATE	\N	The column question with alias Question from table nc_fl6j___question_options has been created	\N	2026-01-06 17:24:53+01	2026-01-06 17:24:53+01
adtnxitc7udtv8mba	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	CREATE	\N	The column lead with alias Lead from table nc_fl6j___answers has been created	\N	2026-01-06 17:25:20+01	2026-01-06 17:25:20+01
adta9380iooa92vbm	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	CREATE	\N	The column question with alias Question from table nc_fl6j___answers has been created	\N	2026-01-06 17:25:40+01	2026-01-06 17:25:40+01
adtosthrpelmjs14v	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	mac7jzb3uago8e3	1	DATA	INSERT	\N	Record with ID 1 has been inserted into Table Services	<span class="">Name</span>\n          : <span class="black--text green lighten-4 px-2">IT Managed Services</span><span class="">Slug</span>\n          : <span class="black--text green lighten-4 px-2">it-managed</span><span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">true</span>	2026-01-06 17:29:23+01	2026-01-06 17:29:23+01
adtu0tn3dcz056phe	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	DELETE	\N	The column null with alias Service from table nc_fl6j___leads_raw_v1 has been deleted	\N	2026-01-06 18:51:59+01	2026-01-06 18:51:59+01
adtsafw326sl1oyh0	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	DELETE	\N	The column null with alias Answers from table nc_fl6j___leads_raw_v1 has been deleted	\N	2026-01-06 18:51:59+01	2026-01-06 18:51:59+01
adtwj8q2w94hvg5ds	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___leads_raw_v1 with alias LeadsRawV1  	\N	2026-01-06 18:51:59+01	2026-01-06 18:51:59+01
adtj6in5i4ufvbgac	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	DELETE	\N	The column null with alias Questions from table nc_fl6j___services has been deleted	\N	2026-01-06 18:52:04+01	2026-01-06 18:52:04+01
adtovc83pybsuqqag	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___services with alias Services  	\N	2026-01-06 18:52:04+01	2026-01-06 18:52:04+01
adtlnsoejztrha3i3	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	DELETE	\N	The column null with alias QuestionOptions from table nc_fl6j___questions has been deleted	\N	2026-01-06 18:52:09+01	2026-01-06 18:52:09+01
adt8l7ait7rswxc35	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	DELETE	\N	The column null with alias Answers from table nc_fl6j___questions has been deleted	\N	2026-01-06 18:52:09+01	2026-01-06 18:52:09+01
adt5qa0jwx876ez0h	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___questions with alias Questions  	\N	2026-01-06 18:52:09+01	2026-01-06 18:52:09+01
adtkm0zckc3x5vrpi	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___answers with alias Answers  	\N	2026-01-06 18:52:18+01	2026-01-06 18:52:18+01
adtwi5edxfa2h8t66	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___question_options with alias QuestionOptions  	\N	2026-01-06 18:52:13+01	2026-01-06 18:52:13+01
adt0hsjhbar5ibjlt	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___Leads with alias Leads has been created	\N	2026-01-06 18:56:02+01	2026-01-06 18:56:02+01
adt7yivgkzfahhk5n	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___ServiceQuestions with alias Servicequestions has been created	\N	2026-01-06 18:56:47+01	2026-01-06 18:56:47+01
adthmjbngb85u20xj	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___ServiceQuestionOptions with alias Servicequestionoptions has been created	\N	2026-01-06 19:00:07+01	2026-01-06 19:00:07+01
adt5jv2xgahqxobea	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___LeadAnswers with alias Leadanswers has been created	\N	2026-01-06 19:00:25+01	2026-01-06 19:00:25+01
adtobzaww57rkzg83	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	mzrlbxmjqox17ml	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Servicequestions	<span class="">Service</span>\n          : <span class="black--text green lighten-4 px-2">Desarrollo web y software a medida</span><span class="">Question Label</span>\n          : <span class="black--text green lighten-4 px-2">¿Qué tipo de solución necesitas?</span><span class="">Input Type</span>\n          : <span class="black--text green lighten-4 px-2">select</span><span class="">Is Enabled</span>\n          : <span class="black--text green lighten-4 px-2">true</span>	2026-01-06 19:05:55+01	2026-01-06 19:05:55+01
adthp2i6id02voomk	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	mzrlbxmjqox17ml	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Servicequestions	<span class="">Service</span>\n          : <span class="black--text green lighten-4 px-2">Desarrollo web y software a medida</span><span class="">Question Label</span>\n          : <span class="black--text green lighten-4 px-2">¿Qué tipo de solución necesitas?</span><span class="">Input Type</span>\n          : <span class="black--text green lighten-4 px-2">select</span><span class="">Is Enabled</span>\n          : <span class="black--text green lighten-4 px-2">true</span>	2026-01-06 19:05:55+01	2026-01-06 19:05:55+01
adts49rhw5mqw5ap8	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	mzrlbxmjqox17ml	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Servicequestions	<span class="">Service</span>\n          : <span class="black--text green lighten-4 px-2">Desarrollo web y software a medida</span><span class="">Question Label</span>\n          : <span class="black--text green lighten-4 px-2">¿Qué tipo de solución necesitas?</span><span class="">Input Type</span>\n          : <span class="black--text green lighten-4 px-2">select</span><span class="">Is Enabled</span>\n          : <span class="black--text green lighten-4 px-2">true</span>	2026-01-06 19:05:55+01	2026-01-06 19:05:55+01
adthasagig5z7649e	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	mzrlbxmjqox17ml	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Servicequestions	<span class="">Service</span>\n          : <span class="black--text green lighten-4 px-2">Desarrollo web y software a medida</span><span class="">Question Label</span>\n          : <span class="black--text green lighten-4 px-2">¿Qué tipo de solución necesitas?</span><span class="">Input Type</span>\n          : <span class="black--text green lighten-4 px-2">select</span><span class="">Is Enabled</span>\n          : <span class="black--text green lighten-4 px-2">true</span>	2026-01-06 19:05:55+01	2026-01-06 19:05:55+01
adtv65rz49aa4gv3u	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	mzrlbxmjqox17ml	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Servicequestions	<span class="">Service</span>\n          : <span class="black--text green lighten-4 px-2">Desarrollo web y software a medida</span><span class="">Question Label</span>\n          : <span class="black--text green lighten-4 px-2">¿Qué tipo de solución necesitas?</span><span class="">Input Type</span>\n          : <span class="black--text green lighten-4 px-2">select</span><span class="">Is Enabled</span>\n          : <span class="black--text green lighten-4 px-2">true</span>	2026-01-06 19:05:55+01	2026-01-06 19:05:55+01
adt7r9a11s5k4tpkk	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	mzrlbxmjqox17ml	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Servicequestions	<span class="">Service</span>\n          : <span class="black--text green lighten-4 px-2">Desarrollo web y software a medida</span><span class="">Question Label</span>\n          : <span class="black--text green lighten-4 px-2">¿Qué tipo de solución necesitas?</span><span class="">Input Type</span>\n          : <span class="black--text green lighten-4 px-2">select</span><span class="">Is Enabled</span>\n          : <span class="black--text green lighten-4 px-2">true</span>	2026-01-06 19:05:55+01	2026-01-06 19:05:55+01
adt4zac4f2btmprqa	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	mzrlbxmjqox17ml	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Servicequestions	<span class="">Service</span>\n          : <span class="black--text green lighten-4 px-2">Desarrollo web y software a medida</span><span class="">Question Label</span>\n          : <span class="black--text green lighten-4 px-2">¿Qué tipo de solución necesitas?</span><span class="">Input Type</span>\n          : <span class="black--text green lighten-4 px-2">select</span><span class="">Is Enabled</span>\n          : <span class="black--text green lighten-4 px-2">true</span>	2026-01-06 19:05:55+01	2026-01-06 19:05:55+01
adtoaxcdy7iwwpuqt	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	CREATE	\N	The column id with alias ID from table nc_fl6j___ServiceQuestionOptions has been created	\N	2026-01-06 19:09:00+01	2026-01-06 19:09:00+01
adtjmgq3juhpjtbq7	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	CREATE	\N	The column id with alias ID from table nc_fl6j___LeadAnswers has been created	\N	2026-01-06 19:09:07+01	2026-01-06 19:09:07+01
adt4kpwss9hbskq5l	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___Leads with alias Leads  	\N	2026-01-06 19:10:28+01	2026-01-06 19:10:28+01
adtq38xjq9t0f0dok	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___ServiceQuestions with alias Servicequestions  	\N	2026-01-06 19:10:38+01	2026-01-06 19:10:38+01
adtutlyfsgqnb7ykr	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___ServiceQuestionOptions with alias Servicequestionoptions  	\N	2026-01-06 19:10:44+01	2026-01-06 19:10:44+01
adtm5hlyezwhecagb	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___LeadAnswers with alias Leadanswers  	\N	2026-01-06 19:10:49+01	2026-01-06 19:10:49+01
adt0xclki5o3cb31r	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___Leads with alias Leads has been created	\N	2026-01-06 19:12:58+01	2026-01-06 19:12:58+01
adthfo24p19prp0yq	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___ServiceQuestions with alias Servicequestions has been created	\N	2026-01-06 19:13:18+01	2026-01-06 19:13:18+01
adt8f8ow6wbpwbhrk	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___ServiceQuestionOptions with alias Servicequestionoptions has been created	\N	2026-01-06 19:13:42+01	2026-01-06 19:13:42+01
adt5ibsbv5erta6ls	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___LeadAnswers with alias Leadanswers has been created	\N	2026-01-06 19:14:05+01	2026-01-06 19:14:05+01
adtvyfh9e0de8kf93	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	CREATE	\N	The column service_question with alias Service Question from table nc_fl6j___ServiceQuestionOptions has been created	\N	2026-01-06 19:15:13+01	2026-01-06 19:15:13+01
adtlk2qrpzbj2wx1y	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	CREATE	\N	The column lead with alias Lead from table nc_fl6j___LeadAnswers has been created	\N	2026-01-06 19:15:27+01	2026-01-06 19:15:27+01
adtm7epusatsu0e18	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	CREATE	\N	The column service_question with alias Service Question from table nc_fl6j___LeadAnswers has been created	\N	2026-01-06 19:15:44+01	2026-01-06 19:15:44+01
adta2y6reyd2pcx0i	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	CREATE	\N	The column selected_option with alias Selected Option from table nc_fl6j___LeadAnswers has been created	\N	2026-01-06 19:16:01+01	2026-01-06 19:16:01+01
adtnp8adkwe43anjx	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	mjqal34a5kc4g6c	1	DATA	INSERT	\N	Record with ID 1 has been inserted into Table Servicequestions	<span class="">Service</span>\n          : <span class="black--text green lighten-4 px-2">Desarrollo web y software a medida</span><span class="">Question Label</span>\n          : <span class="black--text green lighten-4 px-2">¿Qué tipo de solución necesitas?</span><span class="">Input Type</span>\n          : <span class="black--text green lighten-4 px-2">select</span><span class="">Is Enabled</span>\n          : <span class="black--text green lighten-4 px-2">true</span>	2026-01-06 19:17:56+01	2026-01-06 19:17:56+01
adtytg5snc6dq2oej	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	mjqal34a5kc4g6c	2	DATA	INSERT	\N	Record with ID 2 has been inserted into Table Servicequestions	<span class="">Service</span>\n          : <span class="black--text green lighten-4 px-2">Cloud &amp; DevOps</span><span class="">Question Label</span>\n          : <span class="black--text green lighten-4 px-2">¿Cuál es tu situación actual de infraestructura?</span><span class="">Input Type</span>\n          : <span class="black--text green lighten-4 px-2">select</span><span class="">Is Enabled</span>\n          : <span class="black--text green lighten-4 px-2">true</span>	2026-01-06 19:17:56+01	2026-01-06 19:17:56+01
adt9m3yjagjjn40ku	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	mjqal34a5kc4g6c	3	DATA	INSERT	\N	Record with ID 3 has been inserted into Table Servicequestions	<span class="">Service</span>\n          : <span class="black--text green lighten-4 px-2">SRE / Observabilidad</span><span class="">Question Label</span>\n          : <span class="black--text green lighten-4 px-2">¿Qué problema de fiabilidad o visibilidad tienes?</span><span class="">Input Type</span>\n          : <span class="black--text green lighten-4 px-2">select</span><span class="">Is Enabled</span>\n          : <span class="black--text green lighten-4 px-2">true</span>	2026-01-06 19:17:57+01	2026-01-06 19:17:57+01
adtite4ti0od1b6m9	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	mjqal34a5kc4g6c	4	DATA	INSERT	\N	Record with ID 4 has been inserted into Table Servicequestions	<span class="">Service</span>\n          : <span class="black--text green lighten-4 px-2">Infraestructura gestionada</span><span class="">Question Label</span>\n          : <span class="black--text green lighten-4 px-2">¿Qué parte de la infraestructura necesitas gestionar?</span><span class="">Input Type</span>\n          : <span class="black--text green lighten-4 px-2">select</span><span class="">Is Enabled</span>\n          : <span class="black--text green lighten-4 px-2">true</span>	2026-01-06 19:17:57+01	2026-01-06 19:17:57+01
adtcjng1eu6kz5o0j	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	mjqal34a5kc4g6c	5	DATA	INSERT	\N	Record with ID 5 has been inserted into Table Servicequestions	<span class="">Service</span>\n          : <span class="black--text green lighten-4 px-2">Integraciones / Automatización</span><span class="">Question Label</span>\n          : <span class="black--text green lighten-4 px-2">¿Qué herramientas o sistemas quieres conectar?</span><span class="">Input Type</span>\n          : <span class="black--text green lighten-4 px-2">text</span><span class="">Is Enabled</span>\n          : <span class="black--text green lighten-4 px-2">true</span>	2026-01-06 19:17:57+01	2026-01-06 19:17:57+01
adtimj7f6hct42jms	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	mjqal34a5kc4g6c	6	DATA	INSERT	\N	Record with ID 6 has been inserted into Table Servicequestions	<span class="">Service</span>\n          : <span class="black--text green lighten-4 px-2">Outsourcing IT / CAU</span><span class="">Question Label</span>\n          : <span class="black--text green lighten-4 px-2">¿Qué tipo de soporte necesitas?</span><span class="">Input Type</span>\n          : <span class="black--text green lighten-4 px-2">select</span><span class="">Is Enabled</span>\n          : <span class="black--text green lighten-4 px-2">true</span>	2026-01-06 19:17:57+01	2026-01-06 19:17:57+01
adt1xmrdxy821zaec	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	mjqal34a5kc4g6c	7	DATA	INSERT	\N	Record with ID 7 has been inserted into Table Servicequestions	<span class="">Service</span>\n          : <span class="black--text green lighten-4 px-2">No lo tengo claro</span><span class="">Question Label</span>\n          : <span class="black--text green lighten-4 px-2">Sin pregunta adicional</span><span class="">Input Type</span>\n          : <span class="black--text green lighten-4 px-2">select</span><span class="">Is Enabled</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-01-06 19:17:57+01	2026-01-06 19:17:57+01
adtvsdy8fjpm4vl0f	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m9k5uasnaoq4w92	1	DATA	INSERT	\N	Record with ID 1 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">Web profesional / landing</span><span class="">Sort Order</span>\n          : <span class="black--text green lighten-4 px-2">1</span>	2026-01-06 19:18:40+01	2026-01-06 19:18:40+01
adtknhpxmrtl9aupy	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m9k5uasnaoq4w92	2	DATA	INSERT	\N	Record with ID 2 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">CRM o sistema interno</span><span class="">Sort Order</span>\n          : <span class="black--text green lighten-4 px-2">2</span>	2026-01-06 19:18:40+01	2026-01-06 19:18:40+01
adtqdmilllpxsu8en	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m9k5uasnaoq4w92	3	DATA	INSERT	\N	Record with ID 3 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">App móvil o PWA</span><span class="">Sort Order</span>\n          : <span class="black--text green lighten-4 px-2">3</span>	2026-01-06 19:18:40+01	2026-01-06 19:18:40+01
adtj5i2mmj5z3ophz	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m9k5uasnaoq4w92	4	DATA	INSERT	\N	Record with ID 4 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">E-commerce / tienda online</span><span class="">Sort Order</span>\n          : <span class="black--text green lighten-4 px-2">4</span>	2026-01-06 19:18:40+01	2026-01-06 19:18:40+01
adth76o8spgxc8w07	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m9k5uasnaoq4w92	5	DATA	INSERT	\N	Record with ID 5 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">MVP para validar idea</span><span class="">Sort Order</span>\n          : <span class="black--text green lighten-4 px-2">5</span>	2026-01-06 19:18:40+01	2026-01-06 19:18:40+01
adte2tfgg3jfuzqno	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m9k5uasnaoq4w92	6	DATA	INSERT	\N	Record with ID 6 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">Otro</span><span class="">Sort Order</span>\n          : <span class="black--text green lighten-4 px-2">6</span>	2026-01-06 19:18:40+01	2026-01-06 19:18:40+01
adt6fr3bjqepxykc2	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m9k5uasnaoq4w92	7	DATA	INSERT	\N	Record with ID 7 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">Servidor tradicional (sin cloud)</span><span class="">Sort Order</span>\n          : <span class="black--text green lighten-4 px-2">1</span>	2026-01-06 19:18:54+01	2026-01-06 19:18:54+01
adtskz41mg9fyvdor	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m9k5uasnaoq4w92	8	DATA	INSERT	\N	Record with ID 8 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">AWS</span><span class="">Sort Order</span>\n          : <span class="black--text green lighten-4 px-2">2</span>	2026-01-06 19:18:54+01	2026-01-06 19:18:54+01
adt8tahw1r05ag57f	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m9k5uasnaoq4w92	9	DATA	INSERT	\N	Record with ID 9 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">Azure</span><span class="">Sort Order</span>\n          : <span class="black--text green lighten-4 px-2">3</span>	2026-01-06 19:18:54+01	2026-01-06 19:18:54+01
adt2ojsnoy6meph3x	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m9k5uasnaoq4w92	10	DATA	INSERT	\N	Record with ID 10 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">Google Cloud</span><span class="">Sort Order</span>\n          : <span class="black--text green lighten-4 px-2">4</span>	2026-01-06 19:18:54+01	2026-01-06 19:18:54+01
adtrfgoo1evlsg36w	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m9k5uasnaoq4w92	11	DATA	INSERT	\N	Record with ID 11 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">Varios proveedores mezclados</span><span class="">Sort Order</span>\n          : <span class="black--text green lighten-4 px-2">5</span>	2026-01-06 19:18:54+01	2026-01-06 19:18:54+01
adth155zbojyzvj0h	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m9k5uasnaoq4w92	12	DATA	INSERT	\N	Record with ID 12 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">No lo sé / lo gestiona otro</span><span class="">Sort Order</span>\n          : <span class="black--text green lighten-4 px-2">6</span>	2026-01-06 19:18:54+01	2026-01-06 19:18:54+01
adttj8oc5vija6xip	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m9k5uasnaoq4w92	13	DATA	INSERT	\N	Record with ID 13 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">Caídas frecuentes sin saber por qué</span><span class="">Sort Order</span>\n          : <span class="black--text green lighten-4 px-2">1</span>	2026-01-06 19:19:12+01	2026-01-06 19:19:12+01
adt5unkluwe4avdeg	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m9k5uasnaoq4w92	14	DATA	INSERT	\N	Record with ID 14 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">No tenemos alertas o llegan tarde</span><span class="">Sort Order</span>\n          : <span class="black--text green lighten-4 px-2">2</span>	2026-01-06 19:19:13+01	2026-01-06 19:19:13+01
adtp7rca0ob7s7nz5	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m9k5uasnaoq4w92	15	DATA	INSERT	\N	Record with ID 15 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">Rendimiento lento sin diagnóstico</span><span class="">Sort Order</span>\n          : <span class="black--text green lighten-4 px-2">3</span>	2026-01-06 19:19:13+01	2026-01-06 19:19:13+01
adtyogjyz5cy5xyvo	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m9k5uasnaoq4w92	16	DATA	INSERT	\N	Record with ID 16 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">No sabemos qué pasa en producción</span><span class="">Sort Order</span>\n          : <span class="black--text green lighten-4 px-2">4</span>	2026-01-06 19:19:13+01	2026-01-06 19:19:13+01
adtmepkjrl0bu9zi6	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m9k5uasnaoq4w92	17	DATA	INSERT	\N	Record with ID 17 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">Queremos definir SLOs/SLAs</span><span class="">Sort Order</span>\n          : <span class="black--text green lighten-4 px-2">5</span>	2026-01-06 19:19:13+01	2026-01-06 19:19:13+01
adt3y83xkstgmp5f2	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m9k5uasnaoq4w92	18	DATA	INSERT	\N	Record with ID 18 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">Otro</span><span class="">Sort Order</span>\n          : <span class="black--text green lighten-4 px-2">6</span>	2026-01-06 19:19:13+01	2026-01-06 19:19:13+01
adtm5ecyocc44c81r	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m9k5uasnaoq4w92	19	DATA	INSERT	\N	Record with ID 19 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">Hosting / servidores</span><span class="">Sort Order</span>\n          : <span class="black--text green lighten-4 px-2">1</span>	2026-01-06 19:19:49+01	2026-01-06 19:19:49+01
adto89jk6b55chcqn	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m9k5uasnaoq4w92	20	DATA	INSERT	\N	Record with ID 20 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">Dominios y DNS</span><span class="">Sort Order</span>\n          : <span class="black--text green lighten-4 px-2">2</span>	2026-01-06 19:19:49+01	2026-01-06 19:19:49+01
adt7eygv6buuynooc	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m9k5uasnaoq4w92	21	DATA	INSERT	\N	Record with ID 21 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">Certificados SSL</span><span class="">Sort Order</span>\n          : <span class="black--text green lighten-4 px-2">3</span>	2026-01-06 19:19:49+01	2026-01-06 19:19:49+01
adtt8asnkos4mgv50	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m9k5uasnaoq4w92	22	DATA	INSERT	\N	Record with ID 22 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">Backups y recuperación</span><span class="">Sort Order</span>\n          : <span class="black--text green lighten-4 px-2">4</span>	2026-01-06 19:19:49+01	2026-01-06 19:19:49+01
adtg098naq5gp5b46	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m9k5uasnaoq4w92	23	DATA	INSERT	\N	Record with ID 23 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">Todo lo anterior</span><span class="">Sort Order</span>\n          : <span class="black--text green lighten-4 px-2">5</span>	2026-01-06 19:19:49+01	2026-01-06 19:19:49+01
adt50pvwwra9uftc0	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m9k5uasnaoq4w92	24	DATA	INSERT	\N	Record with ID 24 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">Otro</span><span class="">Sort Order</span>\n          : <span class="black--text green lighten-4 px-2">6</span>	2026-01-06 19:19:49+01	2026-01-06 19:19:49+01
adtklvmuam63lov65	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m9k5uasnaoq4w92	25	DATA	INSERT	\N	Record with ID 25 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">Soporte a usuarios (incidencias)</span><span class="">Sort Order</span>\n          : <span class="black--text green lighten-4 px-2">1</span>	2026-01-06 19:20:13+01	2026-01-06 19:20:13+01
adt7u8ju8f9n9pysj	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m9k5uasnaoq4w92	26	DATA	INSERT	\N	Record with ID 26 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">Mantenimiento de equipos/sistemas</span><span class="">Sort Order</span>\n          : <span class="black--text green lighten-4 px-2">2</span>	2026-01-06 19:20:13+01	2026-01-06 19:20:13+01
adt5qbciszsp1nbdd	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m9k5uasnaoq4w92	27	DATA	INSERT	\N	Record with ID 27 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">Cobertura fuera de horario</span><span class="">Sort Order</span>\n          : <span class="black--text green lighten-4 px-2">3</span>	2026-01-06 19:20:13+01	2026-01-06 19:20:13+01
adtui034citwt2lru	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m9k5uasnaoq4w92	28	DATA	INSERT	\N	Record with ID 28 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">Refuerzo temporal del equipo IT</span><span class="">Sort Order</span>\n          : <span class="black--text green lighten-4 px-2">4</span>	2026-01-06 19:20:13+01	2026-01-06 19:20:13+01
adtvfcn81prapk5lb	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m9k5uasnaoq4w92	29	DATA	INSERT	\N	Record with ID 29 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">Externalización completa IT</span><span class="">Sort Order</span>\n          : <span class="black--text green lighten-4 px-2">5</span>	2026-01-06 19:20:13+01	2026-01-06 19:20:13+01
adtjb3aq88ud6x2pc	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m9k5uasnaoq4w92	30	DATA	INSERT	\N	Record with ID 30 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">Otro</span><span class="">Sort Order</span>\n          : <span class="black--text green lighten-4 px-2">6</span>	2026-01-06 19:20:13+01	2026-01-06 19:20:13+01
adtlactsdea1xq7q9	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	myi5yv5si1qz6w7	1	DATA	INSERT	\N	Record with ID 1 has been inserted into Table Leads	<span class="">Nombre</span>\n          : <span class="black--text green lighten-4 px-2">Juan Pérez</span><span class="">Email</span>\n          : <span class="black--text green lighten-4 px-2">juan.perez@ejemplo.com</span><span class="">Teléfono</span>\n          : <span class="black--text green lighten-4 px-2">+34612345678</span><span class="">Tipo Empresa</span>\n          : <span class="black--text green lighten-4 px-2">Pyme</span><span class="">Servicio</span>\n          : <span class="black--text green lighten-4 px-2">Desarrollo web y software a medida</span><span class="">Cómo nos conociste</span>\n          : <span class="black--text green lighten-4 px-2">Búsqueda Google</span><span class="">Mensaje</span>\n          : <span class="black--text green lighten-4 px-2">Necesito una web corporativa moderna para mi empresa</span><span class="">Entrada</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-06 17:30:00+00:00</span><span class="">Origen Lead</span>\n          : <span class="black--text green lighten-4 px-2">Formulario web</span><span class="">Estado</span>\n          : <span class="black--text green lighten-4 px-2">Nuevo</span><span class="">Prioridad</span>\n          : <span class="black--text green lighten-4 px-2">Alta</span><span class="">Next Action</span>\n          : <span class="black--text green lighten-4 px-2">NO_ACTION</span><span class="">GDPR Consent</span>\n          : <span class="black--text green lighten-4 px-2">true</span>	2026-01-06 19:21:27+01	2026-01-06 19:21:27+01
adtv2clvmnvhn840n	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	mfy8zy61pw73mwv	1	DATA	INSERT	\N	Record with ID 1 has been inserted into Table Leadanswers	<span class="">Captured At</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-06 17:30:00+00:00</span>	2026-01-06 19:21:27+01	2026-01-06 19:21:27+01
adtot3jczmdq64gcw	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	myi5yv5si1qz6w7	2	DATA	INSERT	\N	Record with ID 2 has been inserted into Table Leads	<span class="">Nombre</span>\n          : <span class="black--text green lighten-4 px-2">María García</span><span class="">Email</span>\n          : <span class="black--text green lighten-4 px-2">maria.garcia@ejemplo.com</span><span class="">Teléfono</span>\n          : <span class="black--text green lighten-4 px-2">+34623456789</span><span class="">Tipo Empresa</span>\n          : <span class="black--text green lighten-4 px-2">Startup</span><span class="">Servicio</span>\n          : <span class="black--text green lighten-4 px-2">Integraciones / Automatización</span><span class="">Cómo nos conociste</span>\n          : <span class="black--text green lighten-4 px-2">Recomendación</span><span class="">Mensaje</span>\n          : <span class="black--text green lighten-4 px-2">Queremos automatizar procesos entre nuestras herramientas</span><span class="">Entrada</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-06 18:00:00+00:00</span><span class="">Origen Lead</span>\n          : <span class="black--text green lighten-4 px-2">Formulario web</span><span class="">Estado</span>\n          : <span class="black--text green lighten-4 px-2">Nuevo</span><span class="">Prioridad</span>\n          : <span class="black--text green lighten-4 px-2">Media</span><span class="">Next Action</span>\n          : <span class="black--text green lighten-4 px-2">NO_ACTION</span><span class="">GDPR Consent</span>\n          : <span class="black--text green lighten-4 px-2">true</span>	2026-01-06 19:21:58+01	2026-01-06 19:21:58+01
adtm6zm5v4zhsef07	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	mfy8zy61pw73mwv	2	DATA	INSERT	\N	Record with ID 2 has been inserted into Table Leadanswers	<span class="">Free Text Answer</span>\n          : <span class="black--text green lighten-4 px-2">Zapier, Slack, Google Sheets, HubSpot</span><span class="">Captured At</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-06 18:00:00+00:00</span>	2026-01-06 19:21:58+01	2026-01-06 19:21:58+01
adtruw37b1kupxwsw	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	CREATE	\N	The column lost_reason with alias Lost Reason from table nc_fl6j___Leads has been created	\N	2026-01-06 20:26:42+01	2026-01-06 20:26:42+01
adtgiq1s3en5wzhm8	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	CREATE	\N	The column service_question with alias Service Question from table nc_fl6j___ServiceQuestionOptions has been created	\N	2026-01-06 20:27:52+01	2026-01-06 20:27:52+01
adtm8vbvutiafj9c1	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m3sym6yjlz48op4	9	DATA	INSERT	\N	Record with ID 9 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">Azure</span>	2026-01-06 20:28:48+01	2026-01-06 20:28:48+01
adt6rw3oe3mg4h1ju	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	myi5yv5si1qz6w7	3	DATA	INSERT	\N	Record with ID 3 has been inserted into Table Leads	<span class="">Nombre</span>\n          : <span class="black--text green lighten-4 px-2">Carlos Martínez</span><span class="">Email</span>\n          : <span class="black--text green lighten-4 px-2">carlos.martinez@ejemplo.com</span><span class="">Teléfono</span>\n          : <span class="black--text green lighten-4 px-2">+34634567890</span><span class="">Tipo Empresa</span>\n          : <span class="black--text green lighten-4 px-2">Emprendedor</span><span class="">Servicio</span>\n          : <span class="black--text green lighten-4 px-2">No lo tengo claro</span><span class="">Cómo nos conociste</span>\n          : <span class="black--text green lighten-4 px-2">Redes sociales</span><span class="">Mensaje</span>\n          : <span class="black--text green lighten-4 px-2">Estoy explorando opciones para digitalizar mi negocio</span><span class="">Entrada</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-06 18:30:00+00:00</span><span class="">Origen Lead</span>\n          : <span class="black--text green lighten-4 px-2">Formulario web</span><span class="">Estado</span>\n          : <span class="black--text green lighten-4 px-2">Nuevo</span><span class="">Prioridad</span>\n          : <span class="black--text green lighten-4 px-2">Baja</span><span class="">Next Action</span>\n          : <span class="black--text green lighten-4 px-2">NO_ACTION</span><span class="">GDPR Consent</span>\n          : <span class="black--text green lighten-4 px-2">true</span>	2026-01-06 19:22:13+01	2026-01-06 19:22:13+01
adtedw4my4cnnyt5f	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	CREATE	\N	The column extra_informacion with alias Extra Información from table nc_fl6j___Leads has been created	\N	2026-01-06 19:35:10+01	2026-01-06 19:35:10+01
adtexgzqmhyt20fke	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	myi5yv5si1qz6w7	1	DATA	DELETE	\N	Record with ID 1 has been deleted in Table Leads	\N	2026-01-06 19:36:40+01	2026-01-06 19:36:40+01
adtp5b91tc563doeg	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	myi5yv5si1qz6w7	2	DATA	DELETE	\N	Record with ID 2 has been deleted in Table Leads	\N	2026-01-06 19:36:44+01	2026-01-06 19:36:44+01
adt2jy1mtgr1uloeo	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	myi5yv5si1qz6w7	3	DATA	DELETE	\N	Record with ID 3 has been deleted in Table Leads	\N	2026-01-06 19:36:47+01	2026-01-06 19:36:47+01
adth4zzv46jwybfp1	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	myi5yv5si1qz6w7	4	DATA	INSERT	\N	Record with ID 4 has been inserted into Table Leads	<span class="">Nombre</span>\n          : <span class="black--text green lighten-4 px-2">Carlos Martínez</span><span class="">Email</span>\n          : <span class="black--text green lighten-4 px-2">carlos.martinez@ejemplo.com</span><span class="">Teléfono</span>\n          : <span class="black--text green lighten-4 px-2">+34634567890</span><span class="">Tipo Empresa</span>\n          : <span class="black--text green lighten-4 px-2">Emprendedor</span><span class="">Servicio</span>\n          : <span class="black--text green lighten-4 px-2">Cloud &amp; DevOps</span><span class="">Cómo nos conociste</span>\n          : <span class="black--text green lighten-4 px-2">Redes sociales</span><span class="">Mensaje</span>\n          : <span class="black--text green lighten-4 px-2">Estoy explorando opciones para digitalizar mi negocio</span><span class="">Entrada</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-06 18:30:00+00:00</span><span class="">Origen Lead</span>\n          : <span class="black--text green lighten-4 px-2">Formulario web</span><span class="">Estado</span>\n          : <span class="black--text green lighten-4 px-2">Nuevo</span><span class="">Prioridad</span>\n          : <span class="black--text green lighten-4 px-2">Baja</span><span class="">Next Action</span>\n          : <span class="black--text green lighten-4 px-2">NO_ACTION</span><span class="">GDPR Consent</span>\n          : <span class="black--text green lighten-4 px-2">true</span><span class="">Extra Información</span>\n          : <span class="black--text green lighten-4 px-2">AWS</span>	2026-01-06 19:58:59+01	2026-01-06 19:58:59+01
adtqmv575cut80j4e	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	DELETE	\N	The column null with alias Lead from table nc_fl6j___Leads has been deleted	\N	2026-01-06 20:16:23+01	2026-01-06 20:16:23+01
adtom5oi2bod3pnqk	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___Leads with alias Leads  	\N	2026-01-06 20:16:23+01	2026-01-06 20:16:23+01
adt1wwhk98pkty20z	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	DELETE	\N	The column null with alias Service Question from table nc_fl6j___ServiceQuestions has been deleted	\N	2026-01-06 20:16:29+01	2026-01-06 20:16:29+01
adt0sj12ys7zbn28z	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	DELETE	\N	The column null with alias Service Question1 from table nc_fl6j___ServiceQuestions has been deleted	\N	2026-01-06 20:16:29+01	2026-01-06 20:16:29+01
adteyz0g9g2vwte2i	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___ServiceQuestions with alias Servicequestions  	\N	2026-01-06 20:16:29+01	2026-01-06 20:16:29+01
adto3apvtw6g9thme	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	DELETE	\N	The column null with alias Selected Option from table nc_fl6j___ServiceQuestionOptions has been deleted	\N	2026-01-06 20:16:35+01	2026-01-06 20:16:35+01
adtczme4bkajun7vr	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___ServiceQuestionOptions with alias Servicequestionoptions  	\N	2026-01-06 20:16:35+01	2026-01-06 20:16:35+01
adtj4nilz8u0kzkmv	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___LeadAnswers with alias Leadanswers  	\N	2026-01-06 20:16:40+01	2026-01-06 20:16:40+01
adt4axp7o8lzhqwvl	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___Leads with alias Leads has been created	\N	2026-01-06 20:17:57+01	2026-01-06 20:17:57+01
adt8u6hobk5uoo34v	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___Leads with alias Leads  	\N	2026-01-06 20:21:38+01	2026-01-06 20:21:38+01
adt7usn0ai32igksk	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___Leads with alias Leads has been created	\N	2026-01-06 20:22:54+01	2026-01-06 20:22:54+01
adtg7sun5kgqimvc5	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___ServiceQuestions with alias Servicequestions has been created	\N	2026-01-06 20:24:26+01	2026-01-06 20:24:26+01
adtvee6pvzf5bjo0b	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___ServiceQuestionOptions with alias Servicequestionoptions has been created	\N	2026-01-06 20:24:39+01	2026-01-06 20:24:39+01
adtftnvbkn6zabhca	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	CREATE	\N	The column notas_internas with alias Notas Internas from table nc_fl6j___Leads has been created	\N	2026-01-06 20:26:42+01	2026-01-06 20:26:42+01
adt255pfvrwzzxrr3	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	CREATE	\N	The column owner with alias Owner from table nc_fl6j___Leads has been created	\N	2026-01-06 20:26:42+01	2026-01-06 20:26:42+01
adtr4jn1dhc5o9vnr	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	CREATE	\N	The column last_contact_at with alias Last Contact At from table nc_fl6j___Leads has been created	\N	2026-01-06 20:26:42+01	2026-01-06 20:26:42+01
adtfk5larmlsn2kya	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m54esyy04vrjkyz	1	DATA	INSERT	\N	Record with ID 1 has been inserted into Table Servicequestions	<span class="">Service</span>\n          : <span class="black--text green lighten-4 px-2">Desarrollo web y software a medida</span><span class="">Question Label</span>\n          : <span class="black--text green lighten-4 px-2">¿Qué tipo de solución necesitas?</span><span class="">Input Type</span>\n          : <span class="black--text green lighten-4 px-2">select</span><span class="">Is Enabled</span>\n          : <span class="black--text green lighten-4 px-2">true</span>	2026-01-06 20:28:31+01	2026-01-06 20:28:31+01
adtwyy4xr193bipe0	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m54esyy04vrjkyz	2	DATA	INSERT	\N	Record with ID 2 has been inserted into Table Servicequestions	<span class="">Service</span>\n          : <span class="black--text green lighten-4 px-2">Cloud &amp; DevOps</span><span class="">Question Label</span>\n          : <span class="black--text green lighten-4 px-2">¿Cuál es tu situación actual de infraestructura?</span><span class="">Input Type</span>\n          : <span class="black--text green lighten-4 px-2">select</span><span class="">Is Enabled</span>\n          : <span class="black--text green lighten-4 px-2">true</span>	2026-01-06 20:28:31+01	2026-01-06 20:28:31+01
adth2x0kzi3firors	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m54esyy04vrjkyz	3	DATA	INSERT	\N	Record with ID 3 has been inserted into Table Servicequestions	<span class="">Service</span>\n          : <span class="black--text green lighten-4 px-2">SRE / Observabilidad</span><span class="">Question Label</span>\n          : <span class="black--text green lighten-4 px-2">¿Qué problema de fiabilidad o visibilidad tienes?</span><span class="">Input Type</span>\n          : <span class="black--text green lighten-4 px-2">select</span><span class="">Is Enabled</span>\n          : <span class="black--text green lighten-4 px-2">true</span>	2026-01-06 20:28:32+01	2026-01-06 20:28:32+01
adtz8l7gbdsj4tfjt	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m54esyy04vrjkyz	4	DATA	INSERT	\N	Record with ID 4 has been inserted into Table Servicequestions	<span class="">Service</span>\n          : <span class="black--text green lighten-4 px-2">Infraestructura gestionada</span><span class="">Question Label</span>\n          : <span class="black--text green lighten-4 px-2">¿Qué parte de la infraestructura necesitas gestionar?</span><span class="">Input Type</span>\n          : <span class="black--text green lighten-4 px-2">select</span><span class="">Is Enabled</span>\n          : <span class="black--text green lighten-4 px-2">true</span>	2026-01-06 20:28:32+01	2026-01-06 20:28:32+01
adtqxg3guvjmcx048	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m54esyy04vrjkyz	5	DATA	INSERT	\N	Record with ID 5 has been inserted into Table Servicequestions	<span class="">Service</span>\n          : <span class="black--text green lighten-4 px-2">Integraciones / Automatización</span><span class="">Question Label</span>\n          : <span class="black--text green lighten-4 px-2">¿Qué herramientas o sistemas quieres conectar?</span><span class="">Input Type</span>\n          : <span class="black--text green lighten-4 px-2">text</span><span class="">Is Enabled</span>\n          : <span class="black--text green lighten-4 px-2">true</span>	2026-01-06 20:28:32+01	2026-01-06 20:28:32+01
adtmysmuvagk16wbv	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m54esyy04vrjkyz	6	DATA	INSERT	\N	Record with ID 6 has been inserted into Table Servicequestions	<span class="">Service</span>\n          : <span class="black--text green lighten-4 px-2">Outsourcing IT / CAU</span><span class="">Question Label</span>\n          : <span class="black--text green lighten-4 px-2">¿Qué tipo de soporte necesitas?</span><span class="">Input Type</span>\n          : <span class="black--text green lighten-4 px-2">select</span><span class="">Is Enabled</span>\n          : <span class="black--text green lighten-4 px-2">true</span>	2026-01-06 20:28:32+01	2026-01-06 20:28:32+01
adttmo3fpfmny7lm5	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m54esyy04vrjkyz	7	DATA	INSERT	\N	Record with ID 7 has been inserted into Table Servicequestions	<span class="">Service</span>\n          : <span class="black--text green lighten-4 px-2">No lo tengo claro</span><span class="">Question Label</span>\n          : <span class="black--text green lighten-4 px-2">Sin pregunta adicional</span><span class="">Input Type</span>\n          : <span class="black--text green lighten-4 px-2">select</span><span class="">Is Enabled</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-01-06 20:28:32+01	2026-01-06 20:28:32+01
adtnch6kq1bzy7c3x	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m3sym6yjlz48op4	1	DATA	INSERT	\N	Record with ID 1 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">Web profesional / landing</span>	2026-01-06 20:28:41+01	2026-01-06 20:28:41+01
adtq8td900nokylhf	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m3sym6yjlz48op4	2	DATA	INSERT	\N	Record with ID 2 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">CRM o sistema interno</span>	2026-01-06 20:28:41+01	2026-01-06 20:28:41+01
adtuqpahd3r193msk	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m3sym6yjlz48op4	3	DATA	INSERT	\N	Record with ID 3 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">App móvil o PWA</span>	2026-01-06 20:28:41+01	2026-01-06 20:28:41+01
adtzao1f0fz25leed	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m3sym6yjlz48op4	4	DATA	INSERT	\N	Record with ID 4 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">E-commerce</span>	2026-01-06 20:28:42+01	2026-01-06 20:28:42+01
adt39alcmnp1m1s1f	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m3sym6yjlz48op4	5	DATA	INSERT	\N	Record with ID 5 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">MVP para validar idea</span>	2026-01-06 20:28:42+01	2026-01-06 20:28:42+01
adtxzsvmq0o0fy89j	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m3sym6yjlz48op4	6	DATA	INSERT	\N	Record with ID 6 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">Otro</span>	2026-01-06 20:28:42+01	2026-01-06 20:28:42+01
adt2v054hcvllqbx7	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m3sym6yjlz48op4	7	DATA	INSERT	\N	Record with ID 7 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">Servidor tradicional</span>	2026-01-06 20:28:48+01	2026-01-06 20:28:48+01
adt4alihzp6hfzcj2	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m3sym6yjlz48op4	8	DATA	INSERT	\N	Record with ID 8 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">AWS</span>	2026-01-06 20:28:48+01	2026-01-06 20:28:48+01
adt4cu0tiplt579p1	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	CREATE	\N	The column lead with alias Lead from table nc_fl6j___LeadAnswers has been created	\N	2026-01-06 20:54:16+01	2026-01-06 20:54:16+01
adth02gdpje5jud8y	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m3sym6yjlz48op4	10	DATA	INSERT	\N	Record with ID 10 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">Google Cloud</span>	2026-01-06 20:28:48+01	2026-01-06 20:28:48+01
adt9i9oukm214t7jb	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m3sym6yjlz48op4	11	DATA	INSERT	\N	Record with ID 11 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">Varios proveedores</span>	2026-01-06 20:28:48+01	2026-01-06 20:28:48+01
adt2l0euas53asgx2	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m3sym6yjlz48op4	12	DATA	INSERT	\N	Record with ID 12 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">No lo sé</span>	2026-01-06 20:28:48+01	2026-01-06 20:28:48+01
adtwo2kp9s67hymui	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	my9bef7rhdoed3p	1	DATA	INSERT	\N	Record with ID 1 has been inserted into Table Leads	<span class="">Nombre</span>\n          : <span class="black--text green lighten-4 px-2">Roberto Gómez</span><span class="">Entrada</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-05 23:00:00+00:00</span><span class="">Email</span>\n          : <span class="black--text green lighten-4 px-2">roberto@empresa.com</span><span class="">Servicio</span>\n          : <span class="black--text green lighten-4 px-2">Cloud &amp; DevOps</span><span class="">Extra Información</span>\n          : <span class="black--text green lighten-4 px-2">AWS (Migración urgente)</span><span class="">Cómo nos conociste</span>\n          : <span class="black--text green lighten-4 px-2">LinkedIn</span><span class="">Estado</span>\n          : <span class="black--text green lighten-4 px-2">Nuevo</span><span class="">Prioridad</span>\n          : <span class="black--text green lighten-4 px-2">Alta</span><span class="">GDPR Consent</span>\n          : <span class="black--text green lighten-4 px-2">true</span>	2026-01-06 20:29:32+01	2026-01-06 20:29:32+01
adt80c3whpq09cqyg	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	my9bef7rhdoed3p	2	DATA	INSERT	\N	Record with ID 2 has been inserted into Table Leads	<span class="">Nombre</span>\n          : <span class="black--text green lighten-4 px-2">Roberto Gómez</span><span class="">Entrada</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-05 23:00:00+00:00</span><span class="">Email</span>\n          : <span class="black--text green lighten-4 px-2">roberto@empresa.com</span><span class="">Teléfono</span>\n          : <span class="black--text green lighten-4 px-2">+34600112233</span><span class="">Tipo Empresa</span>\n          : <span class="black--text green lighten-4 px-2">Startup</span><span class="">Servicio</span>\n          : <span class="black--text green lighten-4 px-2">Cloud &amp; DevOps</span><span class="">Extra Información</span>\n          : <span class="black--text green lighten-4 px-2">AWS (Migración urgente)</span><span class="">Cómo nos conociste</span>\n          : <span class="black--text green lighten-4 px-2">LinkedIn</span><span class="">Mensaje</span>\n          : <span class="black--text green lighten-4 px-2">Hola, estamos escalando rápido y nuestra infraestructura actual en servidores físicos no aguanta. Necesitamos migrar a AWS antes del próximo mes.</span><span class="">Estado</span>\n          : <span class="black--text green lighten-4 px-2">Nuevo</span><span class="">Prioridad</span>\n          : <span class="black--text green lighten-4 px-2">Alta</span><span class="">GDPR Consent</span>\n          : <span class="black--text green lighten-4 px-2">true</span>	2026-01-06 20:31:44+01	2026-01-06 20:31:44+01
adtcq6oh05e4xg9zi	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	my9bef7rhdoed3p	3	DATA	INSERT	\N	Record with ID 3 has been inserted into Table Leads	<span class="">Nombre</span>\n          : <span class="black--text green lighten-4 px-2">Carlos Martínez</span><span class="">Entrada</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-06 18:30:00+00:00</span><span class="">Email</span>\n          : <span class="black--text green lighten-4 px-2">carlos.martinez@ejemplo.com</span><span class="">Teléfono</span>\n          : <span class="black--text green lighten-4 px-2">+34634567890</span><span class="">Tipo Empresa</span>\n          : <span class="black--text green lighten-4 px-2">Emprendedor</span><span class="">Servicio</span>\n          : <span class="black--text green lighten-4 px-2">Cloud &amp; DevOps</span><span class="">Extra Información</span>\n          : <span class="black--text green lighten-4 px-2">AWS</span><span class="">Cómo nos conociste</span>\n          : <span class="black--text green lighten-4 px-2">Redes sociales</span><span class="">Mensaje</span>\n          : <span class="black--text green lighten-4 px-2">Estoy explorando opciones para digitalizar mi negocio</span><span class="">Estado</span>\n          : <span class="black--text green lighten-4 px-2">Nuevo</span><span class="">Prioridad</span>\n          : <span class="black--text green lighten-4 px-2">Baja</span><span class="">GDPR Consent</span>\n          : <span class="black--text green lighten-4 px-2">true</span>	2026-01-06 20:32:48+01	2026-01-06 20:32:48+01
adtluhwu1mycp3ufn	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	my9bef7rhdoed3p	3	DATA	UPDATE	\N	Record with ID 3 has been updated in Table Leads.\nColumn "Last Contact At" got changed from "null" to "2026-01-06 23:00:00+00:00"	<span class="">Last Contact At</span>\n  : <span class="text-decoration-line-through red px-2 lighten-4 black--text">null</span>\n  <span class="black--text green lighten-4 px-2">2026-01-06 23:00:00+00:00</span>	2026-01-06 20:33:35+01	2026-01-06 20:33:35+01
adtvwqooz5mrz160g	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___Leads with alias Leads  	\N	2026-01-06 20:43:20+01	2026-01-06 20:43:20+01
adtrql7atrrn4u74m	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	DELETE	\N	The column null with alias Service Question from table nc_fl6j___ServiceQuestions has been deleted	\N	2026-01-06 20:43:28+01	2026-01-06 20:43:28+01
adtwdkfqzyc9loxt5	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___ServiceQuestions with alias Servicequestions  	\N	2026-01-06 20:43:28+01	2026-01-06 20:43:28+01
adt8avjy35h1mmamu	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___ServiceQuestionOptions with alias Servicequestionoptions  	\N	2026-01-06 20:43:33+01	2026-01-06 20:43:33+01
adt0h8rz2kgghtwie	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___Leads with alias Leads has been created	\N	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01
adt7ddvje05c44psd	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___ServiceQuestions with alias Servicequestions has been created	\N	2026-01-06 20:52:52+01	2026-01-06 20:52:52+01
adt82s4n6jfdm0clg	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___ServiceQuestionOptions with alias Servicequestionoptions has been created	\N	2026-01-06 20:53:13+01	2026-01-06 20:53:13+01
adtqbb8hajnum4qfn	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___LeadAnswers with alias Leadanswers has been created	\N	2026-01-06 20:53:28+01	2026-01-06 20:53:28+01
adt7glu41gkxk3vmf	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	CREATE	\N	The column service_question with alias Service Question from table nc_fl6j___ServiceQuestionOptions has been created	\N	2026-01-06 20:54:00+01	2026-01-06 20:54:00+01
adtuijzf10eapu2ny	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	CREATE	\N	The column service_question with alias Service Question from table nc_fl6j___LeadAnswers has been created	\N	2026-01-06 20:54:35+01	2026-01-06 20:54:35+01
adtwp73vmgi4bi9qf	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	CREATE	\N	The column selected_option with alias Selected Option from table nc_fl6j___LeadAnswers has been created	\N	2026-01-06 20:55:02+01	2026-01-06 20:55:02+01
adtsv31e2rflxjmhr	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	meivlfimb46wep7	1	DATA	INSERT	\N	Record with ID 1 has been inserted into Table Servicequestions	<span class="">Service</span>\n          : <span class="black--text green lighten-4 px-2">Desarrollo web y software a medida</span><span class="">Question Label</span>\n          : <span class="black--text green lighten-4 px-2">¿Qué tipo de solución necesitas?</span><span class="">Input Type</span>\n          : <span class="black--text green lighten-4 px-2">select</span><span class="">Is Enabled</span>\n          : <span class="black--text green lighten-4 px-2">true</span>	2026-01-06 20:57:03+01	2026-01-06 20:57:03+01
adtw7rvio6c7kxtmi	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	meivlfimb46wep7	2	DATA	INSERT	\N	Record with ID 2 has been inserted into Table Servicequestions	<span class="">Service</span>\n          : <span class="black--text green lighten-4 px-2">Cloud &amp; DevOps</span><span class="">Question Label</span>\n          : <span class="black--text green lighten-4 px-2">¿Cuál es tu situación actual de infraestructura?</span><span class="">Input Type</span>\n          : <span class="black--text green lighten-4 px-2">select</span><span class="">Is Enabled</span>\n          : <span class="black--text green lighten-4 px-2">true</span>	2026-01-06 20:57:35+01	2026-01-06 20:57:35+01
adtdv4wlh9ltddaw9	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	meivlfimb46wep7	3	DATA	INSERT	\N	Record with ID 3 has been inserted into Table Servicequestions	<span class="">Service</span>\n          : <span class="black--text green lighten-4 px-2">SRE / Observabilidad</span><span class="">Question Label</span>\n          : <span class="black--text green lighten-4 px-2">¿Qué problema de fiabilidad o visibilidad tienes?</span><span class="">Input Type</span>\n          : <span class="black--text green lighten-4 px-2">select</span><span class="">Is Enabled</span>\n          : <span class="black--text green lighten-4 px-2">true</span>	2026-01-06 20:57:53+01	2026-01-06 20:57:53+01
adtucx8yuui805q08	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	meivlfimb46wep7	4	DATA	INSERT	\N	Record with ID 4 has been inserted into Table Servicequestions	<span class="">Service</span>\n          : <span class="black--text green lighten-4 px-2">Infraestructura gestionada</span><span class="">Question Label</span>\n          : <span class="black--text green lighten-4 px-2">¿Qué parte de la infraestructura necesitas gestionar?</span><span class="">Input Type</span>\n          : <span class="black--text green lighten-4 px-2">select</span><span class="">Is Enabled</span>\n          : <span class="black--text green lighten-4 px-2">true</span>	2026-01-06 20:58:15+01	2026-01-06 20:58:15+01
adtwojyjacnz354p4	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	meivlfimb46wep7	5	DATA	INSERT	\N	Record with ID 5 has been inserted into Table Servicequestions	<span class="">Service</span>\n          : <span class="black--text green lighten-4 px-2">Integraciones / Automatización</span><span class="">Question Label</span>\n          : <span class="black--text green lighten-4 px-2">¿Qué herramientas o sistemas quieres conectar?</span><span class="">Input Type</span>\n          : <span class="black--text green lighten-4 px-2">text</span><span class="">Is Enabled</span>\n          : <span class="black--text green lighten-4 px-2">true</span>	2026-01-06 20:58:34+01	2026-01-06 20:58:34+01
adtrz657qweqvpr5h	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	meivlfimb46wep7	6	DATA	INSERT	\N	Record with ID 6 has been inserted into Table Servicequestions	<span class="">Service</span>\n          : <span class="black--text green lighten-4 px-2">Outsourcing IT / CAU</span><span class="">Question Label</span>\n          : <span class="black--text green lighten-4 px-2">¿Qué tipo de soporte necesitas?</span><span class="">Input Type</span>\n          : <span class="black--text green lighten-4 px-2">select</span><span class="">Is Enabled</span>\n          : <span class="black--text green lighten-4 px-2">true</span>	2026-01-06 20:58:55+01	2026-01-06 20:58:55+01
adtq26b51s0e3uwag	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	meivlfimb46wep7	7	DATA	INSERT	\N	Record with ID 7 has been inserted into Table Servicequestions	<span class="">Service</span>\n          : <span class="black--text green lighten-4 px-2">No lo tengo claro</span><span class="">Question Label</span>\n          : <span class="black--text green lighten-4 px-2">Sin pregunta adicional</span><span class="">Input Type</span>\n          : <span class="black--text green lighten-4 px-2">select</span><span class="">Is Enabled</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-01-06 20:59:25+01	2026-01-06 20:59:25+01
adti58s9iqkhte7v0	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	myz6dmx69dbmfod	1	DATA	INSERT	\N	Record with ID 1 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">Web profesional / landing</span><span class="">Sort Order</span>\n          : <span class="black--text green lighten-4 px-2">1</span>	2026-01-06 20:59:38+01	2026-01-06 20:59:38+01
adtwmcvurkz7h7hoo	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	myz6dmx69dbmfod	2	DATA	INSERT	\N	Record with ID 2 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">CRM o sistema interno</span><span class="">Sort Order</span>\n          : <span class="black--text green lighten-4 px-2">2</span>	2026-01-06 20:59:38+01	2026-01-06 20:59:38+01
adtl26kc0fylr9isp	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	myz6dmx69dbmfod	3	DATA	INSERT	\N	Record with ID 3 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">App móvil o PWA</span><span class="">Sort Order</span>\n          : <span class="black--text green lighten-4 px-2">3</span>	2026-01-06 20:59:38+01	2026-01-06 20:59:38+01
adt690jh97aym7tqp	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	myz6dmx69dbmfod	4	DATA	INSERT	\N	Record with ID 4 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">E-commerce / tienda online</span><span class="">Sort Order</span>\n          : <span class="black--text green lighten-4 px-2">4</span>	2026-01-06 20:59:38+01	2026-01-06 20:59:38+01
adt07w698m3z4sviz	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	myz6dmx69dbmfod	5	DATA	INSERT	\N	Record with ID 5 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">MVP para validar idea</span><span class="">Sort Order</span>\n          : <span class="black--text green lighten-4 px-2">5</span>	2026-01-06 20:59:39+01	2026-01-06 20:59:39+01
adthy1nzug2rec46b	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	CREATE	\N	The column ads_click_id_type_v4 with alias Ads Click ID Type v4 from table nc_fl6j___Leads has been created	\N	2026-01-07 00:41:13+01	2026-01-07 00:41:13+01
adt21ppd1ndltz1st	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	myz6dmx69dbmfod	6	DATA	INSERT	\N	Record with ID 6 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">Otro</span><span class="">Sort Order</span>\n          : <span class="black--text green lighten-4 px-2">6</span>	2026-01-06 20:59:39+01	2026-01-06 20:59:39+01
adt5djzke1pp5e1yr	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	myz6dmx69dbmfod	7	DATA	INSERT	\N	Record with ID 7 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">Servidor tradicional (sin cloud)</span><span class="">Sort Order</span>\n          : <span class="black--text green lighten-4 px-2">1</span>	2026-01-06 20:59:47+01	2026-01-06 20:59:47+01
adtaw4o883y4m3i9r	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	myz6dmx69dbmfod	8	DATA	INSERT	\N	Record with ID 8 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">AWS</span><span class="">Sort Order</span>\n          : <span class="black--text green lighten-4 px-2">2</span>	2026-01-06 20:59:47+01	2026-01-06 20:59:47+01
adtiq6uism2iwu1f9	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	myz6dmx69dbmfod	9	DATA	INSERT	\N	Record with ID 9 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">Azure</span><span class="">Sort Order</span>\n          : <span class="black--text green lighten-4 px-2">3</span>	2026-01-06 20:59:48+01	2026-01-06 20:59:48+01
adt34k33009pnk1s9	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	myz6dmx69dbmfod	10	DATA	INSERT	\N	Record with ID 10 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">Google Cloud</span><span class="">Sort Order</span>\n          : <span class="black--text green lighten-4 px-2">4</span>	2026-01-06 20:59:48+01	2026-01-06 20:59:48+01
adt8phyroqfdu6vo9	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	myz6dmx69dbmfod	11	DATA	INSERT	\N	Record with ID 11 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">Varios proveedores mezclados</span><span class="">Sort Order</span>\n          : <span class="black--text green lighten-4 px-2">5</span>	2026-01-06 20:59:48+01	2026-01-06 20:59:48+01
adtpni01v2vktx7h5	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	myz6dmx69dbmfod	12	DATA	INSERT	\N	Record with ID 12 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">No lo sé / lo gestiona otro</span><span class="">Sort Order</span>\n          : <span class="black--text green lighten-4 px-2">6</span>	2026-01-06 20:59:48+01	2026-01-06 20:59:48+01
adtb768o5v4m7ixgv	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	myz6dmx69dbmfod	13	DATA	INSERT	\N	Record with ID 13 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">Caídas frecuentes sin saber por qué</span><span class="">Sort Order</span>\n          : <span class="black--text green lighten-4 px-2">1</span>	2026-01-06 20:59:58+01	2026-01-06 20:59:58+01
adt2j2lws026do5qx	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	myz6dmx69dbmfod	14	DATA	INSERT	\N	Record with ID 14 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">No tenemos alertas o llegan tarde</span><span class="">Sort Order</span>\n          : <span class="black--text green lighten-4 px-2">2</span>	2026-01-06 20:59:58+01	2026-01-06 20:59:58+01
adt5rpve8mpc9zo59	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	myz6dmx69dbmfod	15	DATA	INSERT	\N	Record with ID 15 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">Rendimiento lento sin diagnóstico</span><span class="">Sort Order</span>\n          : <span class="black--text green lighten-4 px-2">3</span>	2026-01-06 20:59:58+01	2026-01-06 20:59:58+01
adtptdg2601k76a0k	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	myz6dmx69dbmfod	16	DATA	INSERT	\N	Record with ID 16 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">No sabemos qué pasa en producción</span><span class="">Sort Order</span>\n          : <span class="black--text green lighten-4 px-2">4</span>	2026-01-06 20:59:58+01	2026-01-06 20:59:58+01
adto1ixuqk00cp63x	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	myz6dmx69dbmfod	17	DATA	INSERT	\N	Record with ID 17 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">Queremos definir SLOs/SLAs</span><span class="">Sort Order</span>\n          : <span class="black--text green lighten-4 px-2">5</span>	2026-01-06 20:59:59+01	2026-01-06 20:59:59+01
adtq0ur4pe3fh3fgn	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	myz6dmx69dbmfod	18	DATA	INSERT	\N	Record with ID 18 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">Otro</span><span class="">Sort Order</span>\n          : <span class="black--text green lighten-4 px-2">6</span>	2026-01-06 20:59:59+01	2026-01-06 20:59:59+01
adtwtnq2dw8nnw09d	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	myz6dmx69dbmfod	19	DATA	INSERT	\N	Record with ID 19 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">Hosting / servidores</span><span class="">Sort Order</span>\n          : <span class="black--text green lighten-4 px-2">1</span>	2026-01-06 21:00:54+01	2026-01-06 21:00:54+01
adt2k32gv4frj65w4	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	myz6dmx69dbmfod	20	DATA	INSERT	\N	Record with ID 20 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">Dominios y DNS</span><span class="">Sort Order</span>\n          : <span class="black--text green lighten-4 px-2">2</span>	2026-01-06 21:00:54+01	2026-01-06 21:00:54+01
adt3sbq8tlwzkzy69	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	myz6dmx69dbmfod	21	DATA	INSERT	\N	Record with ID 21 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">Certificados SSL</span><span class="">Sort Order</span>\n          : <span class="black--text green lighten-4 px-2">3</span>	2026-01-06 21:00:54+01	2026-01-06 21:00:54+01
adtyfrqzg36patpvy	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	myz6dmx69dbmfod	22	DATA	INSERT	\N	Record with ID 22 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">Backups y recuperación</span><span class="">Sort Order</span>\n          : <span class="black--text green lighten-4 px-2">4</span>	2026-01-06 21:00:54+01	2026-01-06 21:00:54+01
adt7peows8p4vqpcn	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	myz6dmx69dbmfod	23	DATA	INSERT	\N	Record with ID 23 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">Todo lo anterior</span><span class="">Sort Order</span>\n          : <span class="black--text green lighten-4 px-2">5</span>	2026-01-06 21:00:54+01	2026-01-06 21:00:54+01
adtadnvjxr4nivmb1	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	myz6dmx69dbmfod	24	DATA	INSERT	\N	Record with ID 24 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">Otro</span><span class="">Sort Order</span>\n          : <span class="black--text green lighten-4 px-2">6</span>	2026-01-06 21:00:54+01	2026-01-06 21:00:54+01
adtyfuogwu48oc9lj	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	myz6dmx69dbmfod	25	DATA	INSERT	\N	Record with ID 25 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">Soporte a usuarios (incidencias)</span><span class="">Sort Order</span>\n          : <span class="black--text green lighten-4 px-2">1</span>	2026-01-06 21:01:04+01	2026-01-06 21:01:04+01
adt9e2q7ht5lo3wnl	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	myz6dmx69dbmfod	26	DATA	INSERT	\N	Record with ID 26 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">Mantenimiento de equipos/sistemas</span><span class="">Sort Order</span>\n          : <span class="black--text green lighten-4 px-2">2</span>	2026-01-06 21:01:04+01	2026-01-06 21:01:04+01
adt6jmbp94eqxhlv0	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	myz6dmx69dbmfod	27	DATA	INSERT	\N	Record with ID 27 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">Cobertura fuera de horario</span><span class="">Sort Order</span>\n          : <span class="black--text green lighten-4 px-2">3</span>	2026-01-06 21:01:04+01	2026-01-06 21:01:04+01
adtcpa3v3ub7lw4ut	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	myz6dmx69dbmfod	28	DATA	INSERT	\N	Record with ID 28 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">Refuerzo temporal del equipo IT</span><span class="">Sort Order</span>\n          : <span class="black--text green lighten-4 px-2">4</span>	2026-01-06 21:01:04+01	2026-01-06 21:01:04+01
adtar3jlwqz8dx50f	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	myz6dmx69dbmfod	29	DATA	INSERT	\N	Record with ID 29 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">Externalización completa IT</span><span class="">Sort Order</span>\n          : <span class="black--text green lighten-4 px-2">5</span>	2026-01-06 21:01:04+01	2026-01-06 21:01:04+01
adtwlock57at5nrtm	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	myz6dmx69dbmfod	30	DATA	INSERT	\N	Record with ID 30 has been inserted into Table Servicequestionoptions	<span class="">Option Label</span>\n          : <span class="black--text green lighten-4 px-2">Otro</span><span class="">Sort Order</span>\n          : <span class="black--text green lighten-4 px-2">6</span>	2026-01-06 21:01:04+01	2026-01-06 21:01:04+01
adtipjrfobmo11zq6	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	1	DATA	INSERT	\N	Record with ID 1 has been inserted into Table Leads	<span class="">Nombre</span>\n          : <span class="black--text green lighten-4 px-2">Juan Pérez</span><span class="">Entrada</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-06</span><span class="">Email</span>\n          : <span class="black--text green lighten-4 px-2">juan.perez@ejemplo.com</span><span class="">Teléfono</span>\n          : <span class="black--text green lighten-4 px-2">+34612345678</span><span class="">Tipo Empresa</span>\n          : <span class="black--text green lighten-4 px-2">Pyme</span><span class="">Comuna</span>\n          : <span class="black--text green lighten-4 px-2">Barcelona</span><span class="">Servicio</span>\n          : <span class="black--text green lighten-4 px-2">Desarrollo web y software a medida</span><span class="">Extra Información</span>\n          : <span class="black--text green lighten-4 px-2">Web profesional / landing</span><span class="">Cómo nos conociste</span>\n          : <span class="black--text green lighten-4 px-2">Google / Buscador</span><span class="">Mensaje</span>\n          : <span class="black--text green lighten-4 px-2">Necesito una web corporativa moderna para mi empresa</span><span class="">Origen Lead</span>\n          : <span class="black--text green lighten-4 px-2">Formulario web</span><span class="">Estado</span>\n          : <span class="black--text green lighten-4 px-2">Nuevo</span><span class="">Prioridad</span>\n          : <span class="black--text green lighten-4 px-2">Alta</span><span class="">Next Action</span>\n          : <span class="black--text green lighten-4 px-2">NO_ACTION</span><span class="">GDPR Consent</span>\n          : <span class="black--text green lighten-4 px-2">true</span>	2026-01-06 21:02:26+01	2026-01-06 21:02:26+01
adtwsct4206jtlygt	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m2t8ts768utecu3	1	DATA	INSERT	\N	Record with ID 1 has been inserted into Table Leadanswers	<span class="">Captured At</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-06 17:30:00+00:00</span>	2026-01-06 21:02:36+01	2026-01-06 21:02:36+01
adt443y6x71pkkcfz	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	2	DATA	INSERT	\N	Record with ID 2 has been inserted into Table Leads	<span class="">Nombre</span>\n          : <span class="black--text green lighten-4 px-2">María García</span><span class="">Entrada</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-06</span><span class="">Email</span>\n          : <span class="black--text green lighten-4 px-2">maria.garcia@ejemplo.com</span><span class="">Teléfono</span>\n          : <span class="black--text green lighten-4 px-2">+34623456789</span><span class="">Tipo Empresa</span>\n          : <span class="black--text green lighten-4 px-2">Startup</span><span class="">Comuna</span>\n          : <span class="black--text green lighten-4 px-2">Badalona</span><span class="">Servicio</span>\n          : <span class="black--text green lighten-4 px-2">Integraciones / Automatización</span><span class="">Extra Información</span>\n          : <span class="black--text green lighten-4 px-2">Zapier, Slack, Google Sheets, HubSpot</span><span class="">Cómo nos conociste</span>\n          : <span class="black--text green lighten-4 px-2">Recomendación de un conocido</span><span class="">Mensaje</span>\n          : <span class="black--text green lighten-4 px-2">Queremos automatizar procesos entre nuestras herramientas</span><span class="">Origen Lead</span>\n          : <span class="black--text green lighten-4 px-2">Formulario web</span><span class="">Estado</span>\n          : <span class="black--text green lighten-4 px-2">Nuevo</span><span class="">Prioridad</span>\n          : <span class="black--text green lighten-4 px-2">Media</span><span class="">Next Action</span>\n          : <span class="black--text green lighten-4 px-2">NO_ACTION</span><span class="">GDPR Consent</span>\n          : <span class="black--text green lighten-4 px-2">true</span>	2026-01-06 21:02:46+01	2026-01-06 21:02:46+01
adtyf8m62d5cmj588	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	m2t8ts768utecu3	2	DATA	INSERT	\N	Record with ID 2 has been inserted into Table Leadanswers	<span class="">Free Text Answer</span>\n          : <span class="black--text green lighten-4 px-2">Zapier, Slack, Google Sheets, HubSpot</span><span class="">Captured At</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-06 18:00:00+00:00</span>	2026-01-06 21:02:55+01	2026-01-06 21:02:55+01
adtm46cazleqbk9so	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	3	DATA	INSERT	\N	Record with ID 3 has been inserted into Table Leads	<span class="">Nombre</span>\n          : <span class="black--text green lighten-4 px-2">Carlos Martínez</span><span class="">Entrada</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-06</span><span class="">Email</span>\n          : <span class="black--text green lighten-4 px-2">carlos.martinez@ejemplo.com</span><span class="">Teléfono</span>\n          : <span class="black--text green lighten-4 px-2">+34634567890</span><span class="">Tipo Empresa</span>\n          : <span class="black--text green lighten-4 px-2">Emprendedor</span><span class="">Comuna</span>\n          : <span class="black--text green lighten-4 px-2">Hospitalet</span><span class="">Servicio</span>\n          : <span class="black--text green lighten-4 px-2">No lo tengo claro</span><span class="">Cómo nos conociste</span>\n          : <span class="black--text green lighten-4 px-2">Redes sociales</span><span class="">Mensaje</span>\n          : <span class="black--text green lighten-4 px-2">Estoy explorando opciones para digitalizar mi negocio</span><span class="">Origen Lead</span>\n          : <span class="black--text green lighten-4 px-2">Formulario web</span><span class="">Estado</span>\n          : <span class="black--text green lighten-4 px-2">Nuevo</span><span class="">Prioridad</span>\n          : <span class="black--text green lighten-4 px-2">Baja</span><span class="">Next Action</span>\n          : <span class="black--text green lighten-4 px-2">NO_ACTION</span><span class="">GDPR Consent</span>\n          : <span class="black--text green lighten-4 px-2">true</span>	2026-01-06 21:03:57+01	2026-01-06 21:03:57+01
adtmg5e978hbsdkl9	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	2	DATA	UPDATE	\N	Record with ID 2 has been updated in Table Leads.\nColumn "Last Contact At" got changed from "null" to "2026-01-08"	<span class="">Last Contact At</span>\n  : <span class="text-decoration-line-through red px-2 lighten-4 black--text">null</span>\n  <span class="black--text green lighten-4 px-2">2026-01-08</span>	2026-01-06 21:07:16+01	2026-01-06 21:07:16+01
adtxuvwgix8tc22q6	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	4	DATA	INSERT	\N	Record with ID 4 has been inserted into Table Leads	<span class="">Origen Lead</span>\n          : <span class="black--text green lighten-4 px-2">Formulario web</span><span class="">Estado</span>\n          : <span class="black--text green lighten-4 px-2">Nuevo</span><span class="">Prioridad</span>\n          : <span class="black--text green lighten-4 px-2">Media</span><span class="">Next Action</span>\n          : <span class="black--text green lighten-4 px-2">NO_ACTION</span><span class="">GDPR Consent</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-01-06 21:09:10+01	2026-01-06 21:09:10+01
adtpy5g47l7d7zoni	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	4	DATA	UPDATE	\N	Record with ID 4 has been updated in Table Leads.\nColumn "Nombre" got changed from "null" to "juaan"	<span class="">Nombre</span>\n  : <span class="text-decoration-line-through red px-2 lighten-4 black--text">null</span>\n  <span class="black--text green lighten-4 px-2">juaan</span>	2026-01-06 21:09:14+01	2026-01-06 21:09:14+01
adthtchnzfw3b12xh	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	4	DATA	UPDATE	\N	Record with ID 4 has been updated in Table Leads.\nColumn "Nombre" got changed from "juaan" to "juaan pepe"	<span class="">Nombre</span>\n  : <span class="text-decoration-line-through red px-2 lighten-4 black--text">juaan</span>\n  <span class="black--text green lighten-4 px-2">juaan pepe</span>	2026-01-06 21:09:16+01	2026-01-06 21:09:16+01
adtmiy7caybtc2fm7	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	4	DATA	UPDATE	\N	Record with ID 4 has been updated in Table Leads.\nColumn "Entrada" got changed from "null" to "2026-01-07"	<span class="">Entrada</span>\n  : <span class="text-decoration-line-through red px-2 lighten-4 black--text">null</span>\n  <span class="black--text green lighten-4 px-2">2026-01-07</span>	2026-01-06 21:10:40+01	2026-01-06 21:10:40+01
adt2aikq9cbyxh09h	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	4	DATA	UPDATE	\N	Record with ID 4 has been updated in Table Leads.\nColumn "Email" got changed from "null" to "DFHGDFS"	<span class="">Email</span>\n  : <span class="text-decoration-line-through red px-2 lighten-4 black--text">null</span>\n  <span class="black--text green lighten-4 px-2">DFHGDFS</span>	2026-01-06 21:10:43+01	2026-01-06 21:10:43+01
adtbzeadeptge35u5	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	4	DATA	UPDATE	\N	Record with ID 4 has been updated in Table Leads.\nColumn "Teléfono" got changed from "null" to "52552FD"	<span class="">Teléfono</span>\n  : <span class="text-decoration-line-through red px-2 lighten-4 black--text">null</span>\n  <span class="black--text green lighten-4 px-2">52552FD</span>	2026-01-06 21:10:53+01	2026-01-06 21:10:53+01
adtd5bel6hcnpprt3	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	4	DATA	UPDATE	\N	Record with ID 4 has been updated in Table Leads.\nColumn "Tipo Empresa" got changed from "null" to "Agencia"	<span class="">Tipo Empresa</span>\n  : <span class="text-decoration-line-through red px-2 lighten-4 black--text">null</span>\n  <span class="black--text green lighten-4 px-2">Agencia</span>	2026-01-06 21:10:58+01	2026-01-06 21:10:58+01
adtvbe6sl1wgvtryc	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	5	DATA	INSERT	\N	Record with ID 5 has been inserted into Table Leads	<span class="">Origen Lead</span>\n          : <span class="black--text green lighten-4 px-2">Formulario web</span><span class="">Estado</span>\n          : <span class="black--text green lighten-4 px-2">Nuevo</span><span class="">Prioridad</span>\n          : <span class="black--text green lighten-4 px-2">Media</span><span class="">Next Action</span>\n          : <span class="black--text green lighten-4 px-2">NO_ACTION</span><span class="">GDPR Consent</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-01-06 21:11:26+01	2026-01-06 21:11:26+01
adtqhesrxl0h7q3k9	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	5	DATA	UPDATE	\N	Record with ID 5 has been updated in Table Leads.\nColumn "Origen Lead" got changed from "Formulario web" to "null"	<span class="">Origen Lead</span>\n  : <span class="text-decoration-line-through red px-2 lighten-4 black--text">Formulario web</span>\n  <span class="black--text green lighten-4 px-2">null</span>	2026-01-06 21:11:38+01	2026-01-06 21:11:38+01
adt8xqaxovjkv8yqa	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	5	DATA	UPDATE	\N	Record with ID 5 has been updated in Table Leads.\nColumn "Origen Lead" got changed from "null" to "Llamada telefónica"	<span class="">Origen Lead</span>\n  : <span class="text-decoration-line-through red px-2 lighten-4 black--text">null</span>\n  <span class="black--text green lighten-4 px-2">Llamada telefónica</span>	2026-01-06 21:11:41+01	2026-01-06 21:11:41+01
adtlipjgm0kh225vb	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	5	DATA	UPDATE	\N	Record with ID 5 has been updated in Table Leads.\nColumn "Notas Internas" got changed from "null" to "HHFHFH"	<span class="">Notas Internas</span>\n  : <span class="text-decoration-line-through red px-2 lighten-4 black--text">null</span>\n  <span class="black--text green lighten-4 px-2">HHFHFH</span>	2026-01-06 21:11:58+01	2026-01-06 21:11:58+01
adt49xbzyi00jla9q	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	5	DATA	UPDATE	\N	Record with ID 5 has been updated in Table Leads.\nColumn "Next Action" got changed from "NO_ACTION" to "null"	<span class="">Next Action</span>\n  : <span class="text-decoration-line-through red px-2 lighten-4 black--text">NO_ACTION</span>\n  <span class="black--text green lighten-4 px-2">null</span>	2026-01-06 21:12:08+01	2026-01-06 21:12:08+01
adttbo8obab6bfhd3	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	5	DATA	UPDATE	\N	Record with ID 5 has been updated in Table Leads.\nColumn "Estado" got changed from "Nuevo" to "Ganado"	<span class="">Estado</span>\n  : <span class="text-decoration-line-through red px-2 lighten-4 black--text">Nuevo</span>\n  <span class="black--text green lighten-4 px-2">Ganado</span>	2026-01-06 21:14:27+01	2026-01-06 21:14:27+01
adt80ukaiic829q12	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	CREATE	\N	The column utm_source with alias utm_source from table nc_fl6j___Leads has been created	\N	2026-01-06 21:25:40+01	2026-01-06 21:25:40+01
adt932fo0fmzqxqhr	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	CREATE	\N	The column utm_medium with alias utm_medium from table nc_fl6j___Leads has been created	\N	2026-01-06 21:25:40+01	2026-01-06 21:25:40+01
adt085gu4sdb9i4b0	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	CREATE	\N	The column utm_campaign with alias utm_campaign from table nc_fl6j___Leads has been created	\N	2026-01-06 21:25:40+01	2026-01-06 21:25:40+01
adtrojd83btwd943u	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	CREATE	\N	The column utm_term with alias utm_term from table nc_fl6j___Leads has been created	\N	2026-01-06 21:25:40+01	2026-01-06 21:25:40+01
adtsvi9q5076694si	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	CREATE	\N	The column utm_content with alias utm_content from table nc_fl6j___Leads has been created	\N	2026-01-06 21:25:41+01	2026-01-06 21:25:41+01
adt7hpvykhb6zmdim	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	CREATE	\N	The column landing_url with alias landing_url from table nc_fl6j___Leads has been created	\N	2026-01-06 21:25:41+01	2026-01-06 21:25:41+01
adtn4qy2zi19ozpbe	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	CREATE	\N	The column referrer with alias referrer from table nc_fl6j___Leads has been created	\N	2026-01-06 21:25:41+01	2026-01-06 21:25:41+01
adt4mg731wukimji7	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	CREATE	\N	The column bing_click_id_msclkid with alias Bing Click ID (msclkid) from table nc_fl6j___Leads has been created	\N	2026-01-06 21:31:22+01	2026-01-06 21:31:22+01
adtcc7sl63a5nfeex	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	CREATE	\N	The column google_click_id_gclid with alias Google Click ID (gclid) from table nc_fl6j___Leads has been created	\N	2026-01-06 21:31:28+01	2026-01-06 21:31:28+01
adt693mbjm53rinkx	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	CREATE	\N	The column google_click_id_gbraid with alias Google Click ID (gbraid) from table nc_fl6j___Leads has been created	\N	2026-01-06 21:31:42+01	2026-01-06 21:31:42+01
adt7r836yn7rwbqtk	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	CREATE	\N	The column google_click_id_wbraid with alias Google Click ID (wbraid) from table nc_fl6j___Leads has been created	\N	2026-01-06 21:31:42+01	2026-01-06 21:31:42+01
adtkyc9npoy9nlr0d	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	CREATE	\N	The column linkedin_click_id_li_fat_id with alias LinkedIn Click ID (li_fat_id) from table nc_fl6j___Leads has been created	\N	2026-01-06 21:31:50+01	2026-01-06 21:31:50+01
adtfqhrq437acqnnc	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	CREATE	\N	The column ads_platform with alias Ads Platform from table nc_fl6j___Leads has been created	\N	2026-01-06 21:31:59+01	2026-01-06 21:31:59+01
adtpx7fyk1sujnn47	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	CREATE	\N	The column ads_click_id with alias Ads Click ID (unified) from table nc_fl6j___Leads has been created	\N	2026-01-06 21:32:00+01	2026-01-06 21:32:00+01
adt045slith18h25o	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	CREATE	\N	The column ads_click_id_type with alias Ads Click ID Type from table nc_fl6j___Leads has been created	\N	2026-01-06 21:32:00+01	2026-01-06 21:32:00+01
adtib9t6pazih24o3	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	DELETE	\N	The column comuna with alias Comuna from table nc_fl6j___Leads has been deleted	\N	2026-01-06 21:33:27+01	2026-01-06 21:33:27+01
adtqfm2ll944r73zb	team@mailerblend.com	54.78.232.36	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	6	DATA	INSERT	\N	Record with ID 6 has been inserted into Table Leads	<span class="">Nombre</span>\n          : <span class="black--text green lighten-4 px-2">Lead Sandbox Test</span><span class="">Entrada</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-06</span><span class="">Email</span>\n          : <span class="black--text green lighten-4 px-2">lead.sandbox@test.com</span><span class="">Teléfono</span>\n          : <span class="black--text green lighten-4 px-2">+34600000000</span><span class="">Tipo Empresa</span>\n          : <span class="black--text green lighten-4 px-2">Pyme</span><span class="">Servicio</span>\n          : <span class="black--text green lighten-4 px-2">Cloud &amp; DevOps</span><span class="">Extra Información</span>\n          : <span class="black--text green lighten-4 px-2">AWS</span><span class="">Cómo nos conociste</span>\n          : <span class="black--text green lighten-4 px-2">Google / Buscador</span><span class="">Mensaje</span>\n          : <span class="black--text green lighten-4 px-2">Test from Amplify sandbox REST API</span><span class="">Origen Lead</span>\n          : <span class="black--text green lighten-4 px-2">Formulario web</span><span class="">Estado</span>\n          : <span class="black--text green lighten-4 px-2">Nuevo</span><span class="">Prioridad</span>\n          : <span class="black--text green lighten-4 px-2">Media</span><span class="">Next Action</span>\n          : <span class="black--text green lighten-4 px-2">NO_ACTION</span><span class="">GDPR Consent</span>\n          : <span class="black--text green lighten-4 px-2">true</span>	2026-01-06 22:40:48+01	2026-01-06 22:40:48+01
adtp1op3d1r24u4ch	team@mailerblend.com	108.130.87.184	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	16	DATA	INSERT	\N	Record with ID 16 has been inserted into Table Leads	<span class="">Nombre</span>\n          : <span class="black--text green lighten-4 px-2">E2E Ads v4 Test</span><span class="">Entrada</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-06</span><span class="">Email</span>\n          : <span class="black--text green lighten-4 px-2">e2e.ads.v4@test.com</span><span class="">Teléfono</span>\n          : <span class="black--text green lighten-4 px-2">+34644444555</span><span class="">Tipo Empresa</span>\n          : <span class="black--text green lighten-4 px-2">Pyme</span><span class="">Servicio</span>\n          : <span class="black--text green lighten-4 px-2">SRE / Observabilidad</span><span class="">Extra Información</span>\n          : <span class="black--text green lighten-4 px-2">Caídas frecuentes sin saber por qué</span><span class="">Cómo nos conociste</span>\n          : <span class="black--text green lighten-4 px-2">Bing Ads</span><span class="">Mensaje</span>\n          : <span class="black--text green lighten-4 px-2">URGENTE: test ads platform/type v4</span><span class="">Origen Lead</span>\n          : <span class="black--text green lighten-4 px-2">Formulario web</span><span class="">Estado</span>\n          : <span class="black--text green lighten-4 px-2">Nuevo</span><span class="">Prioridad</span>\n          : <span class="black--text green lighten-4 px-2">Alta</span><span class="">Lead Tag</span>\n          : <span class="black--text green lighten-4 px-2">Hot</span><span class="">Next Action</span>\n          : <span class="black--text green lighten-4 px-2">CALL</span><span class="">Next Action Key</span>\n          : <span class="black--text green lighten-4 px-2">URGENT_CALL_NOW</span><span class="">GDPR Consent</span>\n          : <span class="black--text green lighten-4 px-2">true</span><span class="">Bing Click ID (msclkid)</span>\n          : <span class="black--text green lighten-4 px-2">MSCLKID_TEST_V4_888</span><span class="">Entrada At</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-06 22:42:09+00:00</span><span class="">Ads Click ID (unified) v2</span>\n          : <span class="black--text green lighten-4 px-2">MSCLKID_TEST_V4_888</span><span class="">Ads Platform v4</span>\n          : <span class="black--text green lighten-4 px-2">BING</span><span class="">Ads Click ID Type v4</span>\n          : <span class="black--text green lighten-4 px-2">msclkid</span>	2026-01-07 00:42:10+01	2026-01-07 00:42:10+01
adt1a5duf76pdml44	team@mailerblend.com	54.78.232.36	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	7	DATA	INSERT	\N	Record with ID 7 has been inserted into Table Leads	<span class="">Nombre</span>\n          : <span class="black--text green lighten-4 px-2">Lead Sandbox Test</span><span class="">Entrada</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-06</span><span class="">Email</span>\n          : <span class="black--text green lighten-4 px-2">lead.sandbox@test.com</span><span class="">Teléfono</span>\n          : <span class="black--text green lighten-4 px-2">+34600000000</span><span class="">Tipo Empresa</span>\n          : <span class="black--text green lighten-4 px-2">Pyme</span><span class="">Servicio</span>\n          : <span class="black--text green lighten-4 px-2">Cloud &amp; DevOps</span><span class="">Extra Información</span>\n          : <span class="black--text green lighten-4 px-2">AWS</span><span class="">Cómo nos conociste</span>\n          : <span class="black--text green lighten-4 px-2">Google / Buscador</span><span class="">Mensaje</span>\n          : <span class="black--text green lighten-4 px-2">Test from Amplify sandbox REST API</span><span class="">Origen Lead</span>\n          : <span class="black--text green lighten-4 px-2">Formulario web</span><span class="">Estado</span>\n          : <span class="black--text green lighten-4 px-2">Nuevo</span><span class="">Prioridad</span>\n          : <span class="black--text green lighten-4 px-2">Media</span><span class="">Next Action</span>\n          : <span class="black--text green lighten-4 px-2">NO_ACTION</span><span class="">GDPR Consent</span>\n          : <span class="black--text green lighten-4 px-2">true</span>	2026-01-06 22:42:14+01	2026-01-06 22:42:14+01
adtu3kj94st0zzx6z	team@mailerblend.com	3.250.141.30	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	8	DATA	INSERT	\N	Record with ID 8 has been inserted into Table Leads	<span class="">Nombre</span>\n          : <span class="black--text green lighten-4 px-2">Lead Mapper Test</span><span class="">Entrada</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-06</span><span class="">Email</span>\n          : <span class="black--text green lighten-4 px-2">lead.mapper@test.com</span><span class="">Teléfono</span>\n          : <span class="black--text green lighten-4 px-2">+34600000001</span><span class="">Tipo Empresa</span>\n          : <span class="black--text green lighten-4 px-2">Pyme</span><span class="">Servicio</span>\n          : <span class="black--text green lighten-4 px-2">Cloud &amp; DevOps</span><span class="">Extra Información</span>\n          : <span class="black--text green lighten-4 px-2">AWS</span><span class="">Cómo nos conociste</span>\n          : <span class="black--text green lighten-4 px-2">Google / Buscador</span><span class="">Mensaje</span>\n          : <span class="black--text green lighten-4 px-2">Test mapper</span><span class="">Origen Lead</span>\n          : <span class="black--text green lighten-4 px-2">Formulario web</span><span class="">Estado</span>\n          : <span class="black--text green lighten-4 px-2">Nuevo</span><span class="">Prioridad</span>\n          : <span class="black--text green lighten-4 px-2">Media</span><span class="">Next Action</span>\n          : <span class="black--text green lighten-4 px-2">NO_ACTION</span><span class="">GDPR Consent</span>\n          : <span class="black--text green lighten-4 px-2">true</span>	2026-01-06 22:44:41+01	2026-01-06 22:44:41+01
adtafhl6ykudg5uge	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	9	DATA	INSERT	\N	Record with ID 9 has been inserted into Table Leads	<span class="">Origen Lead</span>\n          : <span class="black--text green lighten-4 px-2">Formulario web</span><span class="">Estado</span>\n          : <span class="black--text green lighten-4 px-2">Nuevo</span><span class="">Prioridad</span>\n          : <span class="black--text green lighten-4 px-2">Media</span><span class="">Next Action</span>\n          : <span class="black--text green lighten-4 px-2">NO_ACTION</span><span class="">GDPR Consent</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-01-06 23:09:13+01	2026-01-06 23:09:13+01
adt4kfrsjmrd5cnvp	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	1	DATA	UPDATE	\N	Record with ID 1 has been updated in Table Leads.\nColumn "Next Action Key" got changed from "null" to "g"	<span class="">Next Action Key</span>\n  : <span class="text-decoration-line-through red px-2 lighten-4 black--text">null</span>\n  <span class="black--text green lighten-4 px-2">g</span>	2026-01-06 23:10:49+01	2026-01-06 23:10:49+01
adto8usepo2o41r4e	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	1	DATA	UPDATE	\N	Record with ID 1 has been updated in Table Leads.\nColumn "Next Action" got changed from "NO_ACTION" to "null"	<span class="">Next Action</span>\n  : <span class="text-decoration-line-through red px-2 lighten-4 black--text">NO_ACTION</span>\n  <span class="black--text green lighten-4 px-2">null</span>	2026-01-06 23:11:16+01	2026-01-06 23:11:16+01
adtsocxrkufmi4ux4	team@mailerblend.com	108.130.61.147	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	10	DATA	INSERT	\N	Record with ID 10 has been inserted into Table Leads	<span class="">Nombre</span>\n          : <span class="black--text green lighten-4 px-2">Urgent Lead</span><span class="">Entrada</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-06</span><span class="">Email</span>\n          : <span class="black--text green lighten-4 px-2">urgent@test.com</span><span class="">Teléfono</span>\n          : <span class="black--text green lighten-4 px-2">+34600000002</span><span class="">Tipo Empresa</span>\n          : <span class="black--text green lighten-4 px-2">Pyme</span><span class="">Servicio</span>\n          : <span class="black--text green lighten-4 px-2">SRE / Observabilidad</span><span class="">Extra Información</span>\n          : <span class="black--text green lighten-4 px-2">Caídas frecuentes sin saber por qué</span><span class="">Cómo nos conociste</span>\n          : <span class="black--text green lighten-4 px-2">Bing Ads</span><span class="">Mensaje</span>\n          : <span class="black--text green lighten-4 px-2">URGENTE: producción caído hoy, necesitamos ayuda ASAP</span><span class="">Origen Lead</span>\n          : <span class="black--text green lighten-4 px-2">Formulario web</span><span class="">Estado</span>\n          : <span class="black--text green lighten-4 px-2">Nuevo</span><span class="">Prioridad</span>\n          : <span class="black--text green lighten-4 px-2">Alta</span><span class="">Lead Tag</span>\n          : <span class="black--text green lighten-4 px-2">Hot</span><span class="">Next Action</span>\n          : <span class="black--text green lighten-4 px-2">CALL</span><span class="">Next Action Key</span>\n          : <span class="black--text green lighten-4 px-2">URGENT_CALL_NOW</span><span class="">GDPR Consent</span>\n          : <span class="black--text green lighten-4 px-2">true</span>	2026-01-06 23:15:37+01	2026-01-06 23:15:37+01
adtmhhff7yzswmkp8	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	DELETE	\N	The column ads_platform_v3 with alias Ads Platform v3 from table nc_fl6j___Leads has been deleted	\N	2026-01-07 00:55:40+01	2026-01-07 00:55:40+01
adtwfqtuuv0dfs9zm	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	DELETE	\N	The column ads_click_id_type_v3 with alias Ads Click ID Type v3 from table nc_fl6j___Leads has been deleted	\N	2026-01-07 00:56:15+01	2026-01-07 00:56:15+01
adthgtd9e6w21ldtl	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	DELETE	\N	The column ads_click_id_type with alias Ads Click ID Type from table nc_fl6j___Leads has been deleted	\N	2026-01-07 00:58:31+01	2026-01-07 00:58:31+01
adtpqgidi4fjk5ear	team@mailerblend.com	108.130.24.239	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	11	DATA	INSERT	\N	Record with ID 11 has been inserted into Table Leads	<span class="">Nombre</span>\n          : <span class="black--text green lighten-4 px-2">Jainer Eduardo</span><span class="">Entrada</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-06</span><span class="">Email</span>\n          : <span class="black--text green lighten-4 px-2">info@comovivirdeltrading.com</span><span class="">Teléfono</span>\n          : <span class="black--text green lighten-4 px-2">+34631230488</span><span class="">Tipo Empresa</span>\n          : <span class="black--text green lighten-4 px-2">Emprendedor</span><span class="">Cómo nos conociste</span>\n          : <span class="black--text green lighten-4 px-2">Google Ads</span><span class="">Mensaje</span>\n          : <span class="black--text green lighten-4 px-2">hola estoy interesado </span><span class="">Origen Lead</span>\n          : <span class="black--text green lighten-4 px-2">Formulario web</span><span class="">Estado</span>\n          : <span class="black--text green lighten-4 px-2">Nuevo</span><span class="">Prioridad</span>\n          : <span class="black--text green lighten-4 px-2">Media</span><span class="">Lead Tag</span>\n          : <span class="black--text green lighten-4 px-2">Cold</span><span class="">Next Action</span>\n          : <span class="black--text green lighten-4 px-2">SEND_EMAIL</span><span class="">Next Action Key</span>\n          : <span class="black--text green lighten-4 px-2">GENERIC_REQUEST_NEEDS_CONTEXT</span><span class="">GDPR Consent</span>\n          : <span class="black--text green lighten-4 px-2">true</span><span class="">landing_url</span>\n          : <span class="black--text green lighten-4 px-2">https://beb4b4f8-23ec-4b06-8a60-e3a681dd9c3b.lovableproject.com/contacto?__lovable_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNURVdjRIOEhaeVUwOUxFN3p4YVdkZmljbDdaMiIsInByb2plY3RfaWQiOiJiZWI0YjRmOC0yM2VjLTRiMDYtOGE2MC1lM2E2ODFkZDljM2IiLCJub25jZSI6IjBjNDY1ODg0NDY1OWU1ZGQwYzdkNjdmOGJiMmVkODJmIiwiaXNzIjoibG92YWJsZS1hcGkiLCJzdWIiOiJiZWI0YjRmOC0yM2VjLTRiMDYtOGE2MC1lM2E2ODFkZDljM2IiLCJhdWQiOlsibG92YWJsZS1hcHAiXSwiZXhwIjoxNzY4MzM5Mzg2LCJuYmYiOjE3Njc3MzQ1ODYsImlhdCI6MTc2NzczNDU4Nn0.9VVT7kimvqU29baYFGHA_XPvLB9PmVc3KysMulPkzUI</span><span class="">referrer</span>\n          : <span class="black--text green lighten-4 px-2">https://lovable.dev/</span>	2026-01-06 23:33:57+01	2026-01-06 23:33:57+01
adtjq88gscaw1grbu	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	UPDATE	\N	The column entrada with alias Entrada from table nc_fl6j___Leads has been updated	\N	2026-01-06 23:35:02+01	2026-01-06 23:35:02+01
adt1l0ts25u5kky0z	team@mailerblend.com	108.130.24.239	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	12	DATA	INSERT	\N	Record with ID 12 has been inserted into Table Leads	<span class="">Nombre</span>\n          : <span class="black--text green lighten-4 px-2">jainer test 2</span><span class="">Entrada</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-06</span><span class="">Email</span>\n          : <span class="black--text green lighten-4 px-2">info@comovivirdeltrading.com</span><span class="">Teléfono</span>\n          : <span class="black--text green lighten-4 px-2">+34631230488</span><span class="">Tipo Empresa</span>\n          : <span class="black--text green lighten-4 px-2">Agencia</span><span class="">Servicio</span>\n          : <span class="black--text green lighten-4 px-2">Desarrollo web y software a medida</span><span class="">Extra Información</span>\n          : <span class="black--text green lighten-4 px-2">CRM o sistema interno</span><span class="">Cómo nos conociste</span>\n          : <span class="black--text green lighten-4 px-2">Bing Ads</span><span class="">Mensaje</span>\n          : <span class="black--text green lighten-4 px-2">URGENTE: producción caído hoy, necesitamos ayuda ASAP</span><span class="">Origen Lead</span>\n          : <span class="black--text green lighten-4 px-2">Formulario web</span><span class="">Estado</span>\n          : <span class="black--text green lighten-4 px-2">Nuevo</span><span class="">Prioridad</span>\n          : <span class="black--text green lighten-4 px-2">Alta</span><span class="">Lead Tag</span>\n          : <span class="black--text green lighten-4 px-2">Hot</span><span class="">Next Action</span>\n          : <span class="black--text green lighten-4 px-2">CALL</span><span class="">Next Action Key</span>\n          : <span class="black--text green lighten-4 px-2">URGENT_CALL_NOW</span><span class="">GDPR Consent</span>\n          : <span class="black--text green lighten-4 px-2">true</span><span class="">landing_url</span>\n          : <span class="black--text green lighten-4 px-2">https://beb4b4f8-23ec-4b06-8a60-e3a681dd9c3b.lovableproject.com/contacto?__lovable_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNURVdjRIOEhaeVUwOUxFN3p4YVdkZmljbDdaMiIsInByb2plY3RfaWQiOiJiZWI0YjRmOC0yM2VjLTRiMDYtOGE2MC1lM2E2ODFkZDljM2IiLCJub25jZSI6IjBjNDY1ODg0NDY1OWU1ZGQwYzdkNjdmOGJiMmVkODJmIiwiaXNzIjoibG92YWJsZS1hcGkiLCJzdWIiOiJiZWI0YjRmOC0yM2VjLTRiMDYtOGE2MC1lM2E2ODFkZDljM2IiLCJhdWQiOlsibG92YWJsZS1hcHAiXSwiZXhwIjoxNzY4MzM5Mzg2LCJuYmYiOjE3Njc3MzQ1ODYsImlhdCI6MTc2NzczNDU4Nn0.9VVT7kimvqU29baYFGHA_XPvLB9PmVc3KysMulPkzUI</span><span class="">referrer</span>\n          : <span class="black--text green lighten-4 px-2">https://lovable.dev/</span>	2026-01-06 23:36:12+01	2026-01-06 23:36:12+01
adtkdud0iq35iokvx	team@mailerblend.com	108.130.24.239	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	13	DATA	INSERT	\N	Record with ID 13 has been inserted into Table Leads	<span class="">Nombre</span>\n          : <span class="black--text green lighten-4 px-2">eduardo velazquez</span><span class="">Entrada</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-06</span><span class="">Email</span>\n          : <span class="black--text green lighten-4 px-2">info@comovivirdeltrading.com</span><span class="">Teléfono</span>\n          : <span class="black--text green lighten-4 px-2">+34631230488</span><span class="">Tipo Empresa</span>\n          : <span class="black--text green lighten-4 px-2">Startup</span><span class="">Servicio</span>\n          : <span class="black--text green lighten-4 px-2">Cloud &amp; DevOps</span><span class="">Extra Información</span>\n          : <span class="black--text green lighten-4 px-2">Servidor tradicional (sin cloud)</span><span class="">Cómo nos conociste</span>\n          : <span class="black--text green lighten-4 px-2">LinkedIn</span><span class="">Mensaje</span>\n          : <span class="black--text green lighten-4 px-2">Hola, estoy buscando informacion para pasarme a la nube</span><span class="">Origen Lead</span>\n          : <span class="black--text green lighten-4 px-2">Formulario web</span><span class="">Estado</span>\n          : <span class="black--text green lighten-4 px-2">Nuevo</span><span class="">Prioridad</span>\n          : <span class="black--text green lighten-4 px-2">Alta</span><span class="">Lead Tag</span>\n          : <span class="black--text green lighten-4 px-2">Hot</span><span class="">Next Action</span>\n          : <span class="black--text green lighten-4 px-2">CALL</span><span class="">Next Action Key</span>\n          : <span class="black--text green lighten-4 px-2">HIGH_VALUE_WITH_PHONE</span><span class="">GDPR Consent</span>\n          : <span class="black--text green lighten-4 px-2">true</span><span class="">landing_url</span>\n          : <span class="black--text green lighten-4 px-2">https://beb4b4f8-23ec-4b06-8a60-e3a681dd9c3b.lovableproject.com/contacto?__lovable_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNURVdjRIOEhaeVUwOUxFN3p4YVdkZmljbDdaMiIsInByb2plY3RfaWQiOiJiZWI0YjRmOC0yM2VjLTRiMDYtOGE2MC1lM2E2ODFkZDljM2IiLCJub25jZSI6IjBjNDY1ODg0NDY1OWU1ZGQwYzdkNjdmOGJiMmVkODJmIiwiaXNzIjoibG92YWJsZS1hcGkiLCJzdWIiOiJiZWI0YjRmOC0yM2VjLTRiMDYtOGE2MC1lM2E2ODFkZDljM2IiLCJhdWQiOlsibG92YWJsZS1hcHAiXSwiZXhwIjoxNzY4MzM5Mzg2LCJuYmYiOjE3Njc3MzQ1ODYsImlhdCI6MTc2NzczNDU4Nn0.9VVT7kimvqU29baYFGHA_XPvLB9PmVc3KysMulPkzUI</span><span class="">referrer</span>\n          : <span class="black--text green lighten-4 px-2">https://lovable.dev/</span>	2026-01-06 23:39:40+01	2026-01-06 23:39:40+01
adtvfhs0k3k2h3ibl	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	UPDATE	\N	The column last_contact_at with alias Last Contact At from table nc_fl6j___Leads has been updated	\N	2026-01-06 23:40:32+01	2026-01-06 23:40:32+01
adtr7owkxkqeg24at	team@mailerblend.com	52.49.255.144	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	14	DATA	INSERT	\N	Record with ID 14 has been inserted into Table Leads	<span class="">Nombre</span>\n          : <span class="black--text green lighten-4 px-2">E2E Tracking Test</span><span class="">Entrada</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-06</span><span class="">Email</span>\n          : <span class="black--text green lighten-4 px-2">e2e.tracking@test.com</span><span class="">Teléfono</span>\n          : <span class="black--text green lighten-4 px-2">+34611111222</span><span class="">Tipo Empresa</span>\n          : <span class="black--text green lighten-4 px-2">Pyme</span><span class="">Servicio</span>\n          : <span class="black--text green lighten-4 px-2">SRE / Observabilidad</span><span class="">Extra Información</span>\n          : <span class="black--text green lighten-4 px-2">Caídas frecuentes sin saber por qué</span><span class="">Cómo nos conociste</span>\n          : <span class="black--text green lighten-4 px-2">Bing Ads</span><span class="">Mensaje</span>\n          : <span class="black--text green lighten-4 px-2">URGENTE: producción caído hoy. Vengo desde anuncio Bing.</span><span class="">Origen Lead</span>\n          : <span class="black--text green lighten-4 px-2">Formulario web</span><span class="">Estado</span>\n          : <span class="black--text green lighten-4 px-2">Nuevo</span><span class="">Prioridad</span>\n          : <span class="black--text green lighten-4 px-2">Alta</span><span class="">Lead Tag</span>\n          : <span class="black--text green lighten-4 px-2">Hot</span><span class="">Next Action</span>\n          : <span class="black--text green lighten-4 px-2">CALL</span><span class="">Next Action Key</span>\n          : <span class="black--text green lighten-4 px-2">URGENT_CALL_NOW</span><span class="">GDPR Consent</span>\n          : <span class="black--text green lighten-4 px-2">true</span><span class="">utm_source</span>\n          : <span class="black--text green lighten-4 px-2">bing</span><span class="">utm_medium</span>\n          : <span class="black--text green lighten-4 px-2">cpc</span><span class="">utm_campaign</span>\n          : <span class="black--text green lighten-4 px-2">nucleo_brand_es</span><span class="">utm_term</span>\n          : <span class="black--text green lighten-4 px-2">partner it</span><span class="">utm_content</span>\n          : <span class="black--text green lighten-4 px-2">adgroup_01</span><span class="">landing_url</span>\n          : <span class="black--text green lighten-4 px-2">https://nucleotecnologico.es/contacto?utm_source=bing&amp;utm_medium=cpc&amp;utm_campaign=nucleo_brand_es&amp;utm_term=partner%20it&amp;utm_content=adgroup_01&amp;msclkid=MSCLKID_TEST_123</span><span class="">referrer</span>\n          : <span class="black--text green lighten-4 px-2">https://www.bing.com/</span><span class="">Bing Click ID (msclkid)</span>\n          : <span class="black--text green lighten-4 px-2">MSCLKID_TEST_123</span><span class="">Google Click ID (gclid)</span>\n          : <span class="black--text green lighten-4 px-2">GCLID_TEST_456</span><span class="">LinkedIn Click ID (li_fat_id)</span>\n          : <span class="black--text green lighten-4 px-2">LIFATID_TEST_789</span>	2026-01-06 23:50:25+01	2026-01-06 23:50:25+01
adtui4hxbvyjxm7h7	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	CREATE	\N	The column entrada_at with alias Entrada At from table nc_fl6j___Leads has been created	\N	2026-01-07 00:03:20+01	2026-01-07 00:03:20+01
adtg4leslaq0kbis4	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	CREATE	\N	The column ads_click_id_unified_v2 with alias Ads Click ID (unified) v2 from table nc_fl6j___Leads has been created	\N	2026-01-07 00:18:12+01	2026-01-07 00:18:12+01
adtsvkz8y8sw3nv5b	team@mailerblend.com	34.242.116.182	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	15	DATA	INSERT	\N	Record with ID 15 has been inserted into Table Leads	<span class="">Nombre</span>\n          : <span class="black--text green lighten-4 px-2">E2E Hour + Ads Platform Test</span><span class="">Entrada</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-06</span><span class="">Email</span>\n          : <span class="black--text green lighten-4 px-2">e2e.hour.ads@test.com</span><span class="">Teléfono</span>\n          : <span class="black--text green lighten-4 px-2">+34622222333</span><span class="">Tipo Empresa</span>\n          : <span class="black--text green lighten-4 px-2">Pyme</span><span class="">Servicio</span>\n          : <span class="black--text green lighten-4 px-2">SRE / Observabilidad</span><span class="">Extra Información</span>\n          : <span class="black--text green lighten-4 px-2">Caídas frecuentes sin saber por qué</span><span class="">Cómo nos conociste</span>\n          : <span class="black--text green lighten-4 px-2">Bing Ads</span><span class="">Mensaje</span>\n          : <span class="black--text green lighten-4 px-2">URGENTE: producción caído hoy. Test para hora + ads platform.</span><span class="">Origen Lead</span>\n          : <span class="black--text green lighten-4 px-2">Formulario web</span><span class="">Estado</span>\n          : <span class="black--text green lighten-4 px-2">Nuevo</span><span class="">Prioridad</span>\n          : <span class="black--text green lighten-4 px-2">Alta</span><span class="">Lead Tag</span>\n          : <span class="black--text green lighten-4 px-2">Hot</span><span class="">Next Action</span>\n          : <span class="black--text green lighten-4 px-2">CALL</span><span class="">Next Action Key</span>\n          : <span class="black--text green lighten-4 px-2">URGENT_CALL_NOW</span><span class="">GDPR Consent</span>\n          : <span class="black--text green lighten-4 px-2">true</span><span class="">utm_source</span>\n          : <span class="black--text green lighten-4 px-2">bing</span><span class="">utm_medium</span>\n          : <span class="black--text green lighten-4 px-2">cpc</span><span class="">utm_campaign</span>\n          : <span class="black--text green lighten-4 px-2">nucleo_brand_es</span><span class="">utm_term</span>\n          : <span class="black--text green lighten-4 px-2">partner it</span><span class="">utm_content</span>\n          : <span class="black--text green lighten-4 px-2">adgroup_01</span><span class="">landing_url</span>\n          : <span class="black--text green lighten-4 px-2">https://nucleotecnologico.es/contacto?utm_source=bing&amp;utm_medium=cpc&amp;utm_campaign=nucleo_brand_es&amp;msclkid=MSCLKID_TEST_999</span><span class="">referrer</span>\n          : <span class="black--text green lighten-4 px-2">https://www.bing.com/</span><span class="">Bing Click ID (msclkid)</span>\n          : <span class="black--text green lighten-4 px-2">MSCLKID_TEST_999</span><span class="">Entrada At</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-06 22:20:42+00:00</span><span class="">Ads Click ID (unified) v2</span>\n          : <span class="black--text green lighten-4 px-2">MSCLKID_TEST_999</span>	2026-01-07 00:20:43+01	2026-01-07 00:20:43+01
adt02yt5hor1bratm	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	CREATE	\N	The column ads_platform_v3 with alias Ads Platform v3 from table nc_fl6j___Leads has been created	\N	2026-01-07 00:34:41+01	2026-01-07 00:34:41+01
adtvfq235u6wulihe	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	CREATE	\N	The column ads_click_id_type_v3 with alias Ads Click ID Type v3 from table nc_fl6j___Leads has been created	\N	2026-01-07 00:34:55+01	2026-01-07 00:34:55+01
adtpl4vm73v3pvi1m	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	CREATE	\N	The column ads_platform_v4 with alias Ads Platform v4 from table nc_fl6j___Leads has been created	\N	2026-01-07 00:41:07+01	2026-01-07 00:41:07+01
adtrrb973meveeywr	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	DELETE	\N	The column ads_platform with alias Ads Platform from table nc_fl6j___Leads has been deleted	\N	2026-01-07 00:55:19+01	2026-01-07 00:55:19+01
adt6znyw6e8fajq10	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	UPDATE	\N	The column Ads_Platform with alias Ads Platform from table nc_fl6j___Leads has been updated	\N	2026-01-07 00:59:03+01	2026-01-07 00:59:03+01
adtqa36n0yutceb3b	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	UPDATE	\N	The column Ads_Click_ID_Type with alias Ads Click ID Type from table nc_fl6j___Leads has been updated	\N	2026-01-07 00:59:13+01	2026-01-07 00:59:13+01
adtcud9umfd7zc9mj	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	DELETE	\N	The column ads_click_id with alias Ads Click ID (unified) from table nc_fl6j___Leads has been deleted	\N	2026-01-07 00:59:41+01	2026-01-07 00:59:41+01
adtqgyrv4rmdodbf1	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	UPDATE	\N	The column Ads_Click_ID__unified_ with alias Ads Click ID (unified) from table nc_fl6j___Leads has been updated	\N	2026-01-07 00:59:51+01	2026-01-07 00:59:51+01
adt44y4dkoor5b3ef	team@mailerblend.com	18.201.40.145	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	17	DATA	INSERT	\N	Record with ID 17 has been inserted into Table Leads	<span class="">Nombre</span>\n          : <span class="black--text green lighten-4 px-2">E2E Clean Names Test</span><span class="">Entrada</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-07</span><span class="">Email</span>\n          : <span class="black--text green lighten-4 px-2">e2e.clean@test.com</span><span class="">Teléfono</span>\n          : <span class="black--text green lighten-4 px-2">+34655555666</span><span class="">Tipo Empresa</span>\n          : <span class="black--text green lighten-4 px-2">Pyme</span><span class="">Servicio</span>\n          : <span class="black--text green lighten-4 px-2">SRE / Observabilidad</span><span class="">Extra Información</span>\n          : <span class="black--text green lighten-4 px-2">Caídas frecuentes sin saber por qué</span><span class="">Cómo nos conociste</span>\n          : <span class="black--text green lighten-4 px-2">Bing Ads</span><span class="">Mensaje</span>\n          : <span class="black--text green lighten-4 px-2">Test nombres finales sin v2/v4</span><span class="">Origen Lead</span>\n          : <span class="black--text green lighten-4 px-2">Formulario web</span><span class="">Estado</span>\n          : <span class="black--text green lighten-4 px-2">Nuevo</span><span class="">Prioridad</span>\n          : <span class="black--text green lighten-4 px-2">Alta</span><span class="">Lead Tag</span>\n          : <span class="black--text green lighten-4 px-2">Hot</span><span class="">Next Action</span>\n          : <span class="black--text green lighten-4 px-2">CALL</span><span class="">Next Action Key</span>\n          : <span class="black--text green lighten-4 px-2">HIGH_VALUE_WITH_PHONE</span><span class="">GDPR Consent</span>\n          : <span class="black--text green lighten-4 px-2">true</span><span class="">Bing Click ID (msclkid)</span>\n          : <span class="black--text green lighten-4 px-2">MSCLKID_CLEAN_001</span><span class="">Entrada At</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-06 23:01:03+00:00</span><span class="">Ads Click ID (unified)</span>\n          : <span class="black--text green lighten-4 px-2">MSCLKID_CLEAN_001</span><span class="">Ads Platform</span>\n          : <span class="black--text green lighten-4 px-2">BING</span><span class="">Ads Click ID Type</span>\n          : <span class="black--text green lighten-4 px-2">msclkid</span>	2026-01-07 01:01:03+01	2026-01-07 01:01:03+01
adttb5gkug3l7xm2o	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	1	DATA	DELETE	\N	Record with ID 1 has been deleted in Table Leads	\N	2026-01-07 01:09:39+01	2026-01-07 01:09:39+01
adt2pqog3lrav9rk3	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	\N	DATA	BULK_DELETE	\N	16 records have been bulk deleted in Leads	\N	2026-01-07 01:09:44+01	2026-01-07 01:09:44+01
adtomldtd9ufzfy14	team@mailerblend.com	34.252.112.226	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	18	DATA	INSERT	\N	Record with ID 18 has been inserted into Table Leads	<span class="">Nombre</span>\n          : <span class="black--text green lighten-4 px-2">PROD ENV FIX OK</span><span class="">Entrada</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-07</span><span class="">Email</span>\n          : <span class="black--text green lighten-4 px-2">prod.env.fix@test.com</span><span class="">Tipo Empresa</span>\n          : <span class="black--text green lighten-4 px-2">Pyme</span><span class="">Cómo nos conociste</span>\n          : <span class="black--text green lighten-4 px-2">Google / Buscador</span><span class="">Mensaje</span>\n          : <span class="black--text green lighten-4 px-2">Confirmación variables entorno Lambda</span><span class="">Origen Lead</span>\n          : <span class="black--text green lighten-4 px-2">Formulario web</span><span class="">Estado</span>\n          : <span class="black--text green lighten-4 px-2">Nuevo</span><span class="">Prioridad</span>\n          : <span class="black--text green lighten-4 px-2">Media</span><span class="">Lead Tag</span>\n          : <span class="black--text green lighten-4 px-2">Qualified</span><span class="">Next Action</span>\n          : <span class="black--text green lighten-4 px-2">SEND_EMAIL</span><span class="">Next Action Key</span>\n          : <span class="black--text green lighten-4 px-2">REPLY_WITH_NEXT_STEPS</span><span class="">GDPR Consent</span>\n          : <span class="black--text green lighten-4 px-2">true</span><span class="">Entrada At</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-07 01:45:41+00:00</span>	2026-01-07 03:45:41+01	2026-01-07 03:45:41+01
adt3cbbqqkvjlt8t9	team@mailerblend.com	54.171.216.119	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	19	DATA	INSERT	\N	Record with ID 19 has been inserted into Table Leads	<span class="">Nombre</span>\n          : <span class="black--text green lighten-4 px-2">test prod-lov 2</span><span class="">Entrada</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-07</span><span class="">Email</span>\n          : <span class="black--text green lighten-4 px-2">info@comovivirdeltrading.com</span><span class="">Teléfono</span>\n          : <span class="black--text green lighten-4 px-2">+34631230488</span><span class="">Tipo Empresa</span>\n          : <span class="black--text green lighten-4 px-2">Emprendedor</span><span class="">Servicio</span>\n          : <span class="black--text green lighten-4 px-2">Infraestructura gestionada</span><span class="">Extra Información</span>\n          : <span class="black--text green lighten-4 px-2">Hosting / servidores</span><span class="">Cómo nos conociste</span>\n          : <span class="black--text green lighten-4 px-2">Redes sociales</span><span class="">Mensaje</span>\n          : <span class="black--text green lighten-4 px-2">pueden llamarme urgente</span><span class="">Origen Lead</span>\n          : <span class="black--text green lighten-4 px-2">Formulario web</span><span class="">Estado</span>\n          : <span class="black--text green lighten-4 px-2">Nuevo</span><span class="">Prioridad</span>\n          : <span class="black--text green lighten-4 px-2">Alta</span><span class="">Lead Tag</span>\n          : <span class="black--text green lighten-4 px-2">Hot</span><span class="">Next Action</span>\n          : <span class="black--text green lighten-4 px-2">CALL</span><span class="">Next Action Key</span>\n          : <span class="black--text green lighten-4 px-2">URGENT_CALL_NOW</span><span class="">GDPR Consent</span>\n          : <span class="black--text green lighten-4 px-2">true</span><span class="">landing_url</span>\n          : <span class="black--text green lighten-4 px-2">https://www.nucleotecnologico.es/contacto</span><span class="">Entrada At</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-07 02:30:44+00:00</span>	2026-01-07 04:30:45+01	2026-01-07 04:30:45+01
adtsec1zzpyr9qyy1	team@mailerblend.com	\N	\N	\N	\N	\N	AUTHENTICATION	SIGNIN	\N	\N	\N	2026-01-07 10:33:52+01	2026-01-07 10:33:52+01
adtj7pbnqh36yba1o	team@mailerblend.com	3.253.241.189	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	20	DATA	INSERT	\N	Record with ID 20 has been inserted into Table Leads	<span class="">Nombre</span>\n          : <span class="black--text green lighten-4 px-2">edu test 07-01-2026</span><span class="">Entrada</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-07</span><span class="">Email</span>\n          : <span class="black--text green lighten-4 px-2">info@comovivirdeltrading.com</span><span class="">Teléfono</span>\n          : <span class="black--text green lighten-4 px-2">+34631230488</span><span class="">Tipo Empresa</span>\n          : <span class="black--text green lighten-4 px-2">Agencia</span><span class="">Servicio</span>\n          : <span class="black--text green lighten-4 px-2">Desarrollo web y software a medida</span><span class="">Extra Información</span>\n          : <span class="black--text green lighten-4 px-2">MVP para validar idea</span><span class="">Cómo nos conociste</span>\n          : <span class="black--text green lighten-4 px-2">Google / Buscador</span><span class="">Mensaje</span>\n          : <span class="black--text green lighten-4 px-2">nuevo producto que estamos por lanzar </span><span class="">Origen Lead</span>\n          : <span class="black--text green lighten-4 px-2">Formulario web</span><span class="">Estado</span>\n          : <span class="black--text green lighten-4 px-2">Nuevo</span><span class="">Prioridad</span>\n          : <span class="black--text green lighten-4 px-2">Media</span><span class="">Lead Tag</span>\n          : <span class="black--text green lighten-4 px-2">Qualified</span><span class="">Next Action</span>\n          : <span class="black--text green lighten-4 px-2">SEND_EMAIL</span><span class="">Next Action Key</span>\n          : <span class="black--text green lighten-4 px-2">REPLY_WITH_NEXT_STEPS</span><span class="">GDPR Consent</span>\n          : <span class="black--text green lighten-4 px-2">true</span><span class="">landing_url</span>\n          : <span class="black--text green lighten-4 px-2">https://www.nucleotecnologico.es/contacto</span><span class="">Entrada At</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-07 08:35:12+00:00</span>	2026-01-07 10:35:12+01	2026-01-07 10:35:12+01
adtkm3ygltjvtmvbq	team@mailerblend.com	3.253.237.4	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	21	DATA	INSERT	\N	Record with ID 21 has been inserted into Table Leads	<span class="">Nombre</span>\n          : <span class="black--text green lighten-4 px-2">apiEnv PROD test</span><span class="">Entrada</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-07</span><span class="">Email</span>\n          : <span class="black--text green lighten-4 px-2">apienv.prod@test.com</span><span class="">Tipo Empresa</span>\n          : <span class="black--text green lighten-4 px-2">Pyme</span><span class="">Cómo nos conociste</span>\n          : <span class="black--text green lighten-4 px-2">Google / Buscador</span><span class="">Mensaje</span>\n          : <span class="black--text green lighten-4 px-2">apiEnv check</span><span class="">Origen Lead</span>\n          : <span class="black--text green lighten-4 px-2">Formulario web</span><span class="">Estado</span>\n          : <span class="black--text green lighten-4 px-2">Nuevo</span><span class="">Prioridad</span>\n          : <span class="black--text green lighten-4 px-2">Media</span><span class="">Lead Tag</span>\n          : <span class="black--text green lighten-4 px-2">Cold</span><span class="">Next Action</span>\n          : <span class="black--text green lighten-4 px-2">SEND_EMAIL</span><span class="">Next Action Key</span>\n          : <span class="black--text green lighten-4 px-2">ASK_FOR_DETAILS</span><span class="">GDPR Consent</span>\n          : <span class="black--text green lighten-4 px-2">true</span><span class="">Entrada At</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-07 10:05:34+00:00</span>	2026-01-07 12:05:34+01	2026-01-07 12:05:34+01
adth0hdanoixrstub	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	DELETE	\N	The column null with alias Leads from table nc_fl6j___Company has been deleted	\N	2026-02-03 11:25:58+01	2026-02-03 11:25:58+01
adtic8brjv0xl67zl	team@mailerblend.com	34.248.172.177	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	22	DATA	INSERT	\N	Record with ID 22 has been inserted into Table Leads	<span class="">Nombre</span>\n          : <span class="black--text green lighten-4 px-2">apiEnv PROD final test</span><span class="">Entrada</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-07</span><span class="">Email</span>\n          : <span class="black--text green lighten-4 px-2">api.env.final@test.com</span><span class="">Tipo Empresa</span>\n          : <span class="black--text green lighten-4 px-2">Pyme</span><span class="">Cómo nos conociste</span>\n          : <span class="black--text green lighten-4 px-2">Google / Buscador</span><span class="">Mensaje</span>\n          : <span class="black--text green lighten-4 px-2">Final apiEnv verification</span><span class="">Origen Lead</span>\n          : <span class="black--text green lighten-4 px-2">Formulario web</span><span class="">Estado</span>\n          : <span class="black--text green lighten-4 px-2">Nuevo</span><span class="">Prioridad</span>\n          : <span class="black--text green lighten-4 px-2">Media</span><span class="">Lead Tag</span>\n          : <span class="black--text green lighten-4 px-2">Qualified</span><span class="">Next Action</span>\n          : <span class="black--text green lighten-4 px-2">SEND_EMAIL</span><span class="">Next Action Key</span>\n          : <span class="black--text green lighten-4 px-2">REPLY_WITH_NEXT_STEPS</span><span class="">GDPR Consent</span>\n          : <span class="black--text green lighten-4 px-2">true</span><span class="">Entrada At</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-07 10:16:59+00:00</span>	2026-01-07 12:17:00+01	2026-01-07 12:17:00+01
adt6ma2oc79jcqgxf	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	20	DATA	UPDATE	\N	Record with ID 20 has been updated in Table Leads.\nColumn "Estado" got changed from "Nuevo" to "null"	<span class="">Estado</span>\n  : <span class="text-decoration-line-through red px-2 lighten-4 black--text">Nuevo</span>\n  <span class="black--text green lighten-4 px-2">null</span>	2026-01-07 13:51:35+01	2026-01-07 13:51:35+01
adtx1voe1l7llgd2k	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	20	DATA	UPDATE	\N	Record with ID 20 has been updated in Table Leads.\nColumn "Estado" got changed from "null" to "Nuevo"	<span class="">Estado</span>\n  : <span class="text-decoration-line-through red px-2 lighten-4 black--text">null</span>\n  <span class="black--text green lighten-4 px-2">Nuevo</span>	2026-01-07 13:51:42+01	2026-01-07 13:51:42+01
adtrj0ickn77yj50t	team@mailerblend.com	54.217.140.56	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	23	DATA	INSERT	\N	Record with ID 23 has been inserted into Table Leads	<span class="">Nombre</span>\n          : <span class="black--text green lighten-4 px-2">Marimar</span><span class="">Entrada</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-07</span><span class="">Email</span>\n          : <span class="black--text green lighten-4 px-2">info@help.es</span><span class="">Teléfono</span>\n          : <span class="black--text green lighten-4 px-2">+34625667655</span><span class="">Tipo Empresa</span>\n          : <span class="black--text green lighten-4 px-2">Pyme</span><span class="">Servicio</span>\n          : <span class="black--text green lighten-4 px-2">Desarrollo web y software a medida</span><span class="">Extra Información</span>\n          : <span class="black--text green lighten-4 px-2">CRM o sistema interno</span><span class="">Cómo nos conociste</span>\n          : <span class="black--text green lighten-4 px-2">Google Ads</span><span class="">Mensaje</span>\n          : <span class="black--text green lighten-4 px-2">No lo se </span><span class="">Origen Lead</span>\n          : <span class="black--text green lighten-4 px-2">Formulario web</span><span class="">Estado</span>\n          : <span class="black--text green lighten-4 px-2">Nuevo</span><span class="">Prioridad</span>\n          : <span class="black--text green lighten-4 px-2">Media</span><span class="">Lead Tag</span>\n          : <span class="black--text green lighten-4 px-2">Cold</span><span class="">Next Action</span>\n          : <span class="black--text green lighten-4 px-2">SEND_EMAIL</span><span class="">Next Action Key</span>\n          : <span class="black--text green lighten-4 px-2">ASK_FOR_DETAILS</span><span class="">GDPR Consent</span>\n          : <span class="black--text green lighten-4 px-2">true</span><span class="">landing_url</span>\n          : <span class="black--text green lighten-4 px-2">https://www.nucleotecnologico.es/contacto</span><span class="">Entrada At</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-07 17:26:56+00:00</span>	2026-01-07 19:26:57+01	2026-01-07 19:26:57+01
adtgb9hbi3t2scrha	team@mailerblend.com	\N	\N	\N	\N	\N	AUTHENTICATION	SIGNIN	\N	\N	\N	2026-01-07 20:54:08+01	2026-01-07 20:54:08+01
adtbpg1zrmmsmqs2q	team@mailerblend.com	108.129.232.140	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	24	DATA	INSERT	\N	Record with ID 24 has been inserted into Table Leads	<span class="">Nombre</span>\n          : <span class="black--text green lighten-4 px-2">YASMELI MARIA</span><span class="">Entrada</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-08</span><span class="">Email</span>\n          : <span class="black--text green lighten-4 px-2">yasme@yasme.es</span><span class="">Teléfono</span>\n          : <span class="black--text green lighten-4 px-2">+34613705216</span><span class="">Tipo Empresa</span>\n          : <span class="black--text green lighten-4 px-2">Pyme</span><span class="">Servicio</span>\n          : <span class="black--text green lighten-4 px-2">Integraciones / Automatización</span><span class="">Extra Información</span>\n          : <span class="black--text green lighten-4 px-2">AUTOMATIZAR CONTROL DE ASISTENCIAS, FACTURAS Y TRABAJOS REALIZADOS </span><span class="">Cómo nos conociste</span>\n          : <span class="black--text green lighten-4 px-2">Otro</span><span class="">Mensaje</span>\n          : <span class="black--text green lighten-4 px-2">TODA ESA VERGA</span><span class="">Origen Lead</span>\n          : <span class="black--text green lighten-4 px-2">Formulario web</span><span class="">Estado</span>\n          : <span class="black--text green lighten-4 px-2">Nuevo</span><span class="">Prioridad</span>\n          : <span class="black--text green lighten-4 px-2">Media</span><span class="">Lead Tag</span>\n          : <span class="black--text green lighten-4 px-2">Cold</span><span class="">Next Action</span>\n          : <span class="black--text green lighten-4 px-2">SEND_EMAIL</span><span class="">Next Action Key</span>\n          : <span class="black--text green lighten-4 px-2">ASK_FOR_DETAILS</span><span class="">GDPR Consent</span>\n          : <span class="black--text green lighten-4 px-2">true</span><span class="">landing_url</span>\n          : <span class="black--text green lighten-4 px-2">https://www.nucleotecnologico.es/contacto#form</span><span class="">Entrada At</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-08 15:54:46+00:00</span>	2026-01-08 17:54:46+01	2026-01-08 17:54:46+01
adt6u631jdbhcg95x	team@mailerblend.com	54.74.30.11	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	25	DATA	INSERT	\N	Record with ID 25 has been inserted into Table Leads	<span class="">Nombre</span>\n          : <span class="black--text green lighten-4 px-2">web test</span><span class="">Entrada</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-08</span><span class="">Email</span>\n          : <span class="black--text green lighten-4 px-2">info@comovivirdeltrading.com</span><span class="">Teléfono</span>\n          : <span class="black--text green lighten-4 px-2">+34631230488</span><span class="">Tipo Empresa</span>\n          : <span class="black--text green lighten-4 px-2">Agencia</span><span class="">Servicio</span>\n          : <span class="black--text green lighten-4 px-2">SRE / Observabilidad</span><span class="">Extra Información</span>\n          : <span class="black--text green lighten-4 px-2">No tenemos alertas o llegan tarde</span><span class="">Cómo nos conociste</span>\n          : <span class="black--text green lighten-4 px-2">LinkedIn</span><span class="">Mensaje</span>\n          : <span class="black--text green lighten-4 px-2">necesito ayuda urgente</span><span class="">Origen Lead</span>\n          : <span class="black--text green lighten-4 px-2">Formulario web</span><span class="">Estado</span>\n          : <span class="black--text green lighten-4 px-2">Nuevo</span><span class="">Prioridad</span>\n          : <span class="black--text green lighten-4 px-2">Alta</span><span class="">Lead Tag</span>\n          : <span class="black--text green lighten-4 px-2">Hot</span><span class="">Next Action</span>\n          : <span class="black--text green lighten-4 px-2">CALL</span><span class="">Next Action Key</span>\n          : <span class="black--text green lighten-4 px-2">URGENT_CALL_NOW</span><span class="">GDPR Consent</span>\n          : <span class="black--text green lighten-4 px-2">true</span><span class="">landing_url</span>\n          : <span class="black--text green lighten-4 px-2">https://www.nucleotecnologico.es/contacto</span><span class="">Entrada At</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-08 19:41:32+00:00</span>	2026-01-08 21:41:33+01	2026-01-08 21:41:33+01
adt9lvpxlh1d39n5y	team@mailerblend.com	34.241.124.186	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	26	DATA	INSERT	\N	Record with ID 26 has been inserted into Table Leads	<span class="">Nombre</span>\n          : <span class="black--text green lighten-4 px-2">eduardo</span><span class="">Entrada</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-08</span><span class="">Email</span>\n          : <span class="black--text green lighten-4 px-2">nu@nu.es</span><span class="">Teléfono</span>\n          : <span class="black--text green lighten-4 px-2">+34631230488</span><span class="">Tipo Empresa</span>\n          : <span class="black--text green lighten-4 px-2">Emprendedor</span><span class="">Servicio</span>\n          : <span class="black--text green lighten-4 px-2">Cloud &amp; DevOps</span><span class="">Extra Información</span>\n          : <span class="black--text green lighten-4 px-2">AWS</span><span class="">Cómo nos conociste</span>\n          : <span class="black--text green lighten-4 px-2">Directorio o listado</span><span class="">Mensaje</span>\n          : <span class="black--text green lighten-4 px-2">necesito revisar un servidor </span><span class="">Origen Lead</span>\n          : <span class="black--text green lighten-4 px-2">Formulario web</span><span class="">Estado</span>\n          : <span class="black--text green lighten-4 px-2">Nuevo</span><span class="">Prioridad</span>\n          : <span class="black--text green lighten-4 px-2">Alta</span><span class="">Lead Tag</span>\n          : <span class="black--text green lighten-4 px-2">Hot</span><span class="">Next Action</span>\n          : <span class="black--text green lighten-4 px-2">CALL</span><span class="">Next Action Key</span>\n          : <span class="black--text green lighten-4 px-2">HIGH_VALUE_WITH_PHONE</span><span class="">GDPR Consent</span>\n          : <span class="black--text green lighten-4 px-2">true</span><span class="">landing_url</span>\n          : <span class="black--text green lighten-4 px-2">https://www.nucleotecnologico.es/contacto</span><span class="">Entrada At</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-08 19:50:18+00:00</span>	2026-01-08 21:50:18+01	2026-01-08 21:50:18+01
adtsxq44gl5dmiutb	team@mailerblend.com	34.241.124.186	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	27	DATA	INSERT	\N	Record with ID 27 has been inserted into Table Leads	<span class="">Nombre</span>\n          : <span class="black--text green lighten-4 px-2">eduardo</span><span class="">Entrada</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-08</span><span class="">Email</span>\n          : <span class="black--text green lighten-4 px-2">nu@nu.es</span><span class="">Teléfono</span>\n          : <span class="black--text green lighten-4 px-2">+34631230488</span><span class="">Tipo Empresa</span>\n          : <span class="black--text green lighten-4 px-2">Emprendedor</span><span class="">Servicio</span>\n          : <span class="black--text green lighten-4 px-2">Cloud &amp; DevOps</span><span class="">Extra Información</span>\n          : <span class="black--text green lighten-4 px-2">Google Cloud</span><span class="">Cómo nos conociste</span>\n          : <span class="black--text green lighten-4 px-2">Google / Buscador</span><span class="">Mensaje</span>\n          : <span class="black--text green lighten-4 px-2">necesito urtgene ee </span><span class="">Origen Lead</span>\n          : <span class="black--text green lighten-4 px-2">Formulario web</span><span class="">Estado</span>\n          : <span class="black--text green lighten-4 px-2">Nuevo</span><span class="">Prioridad</span>\n          : <span class="black--text green lighten-4 px-2">Alta</span><span class="">Lead Tag</span>\n          : <span class="black--text green lighten-4 px-2">Hot</span><span class="">Next Action</span>\n          : <span class="black--text green lighten-4 px-2">CALL</span><span class="">Next Action Key</span>\n          : <span class="black--text green lighten-4 px-2">HIGH_VALUE_WITH_PHONE</span><span class="">GDPR Consent</span>\n          : <span class="black--text green lighten-4 px-2">true</span><span class="">landing_url</span>\n          : <span class="black--text green lighten-4 px-2">https://www.nucleotecnologico.es/contacto</span><span class="">Entrada At</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-08 19:51:53+00:00</span>	2026-01-08 21:51:53+01	2026-01-08 21:51:53+01
adtevwrn1l6b95uu7	team@mailerblend.com	34.241.124.186	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	28	DATA	INSERT	\N	Record with ID 28 has been inserted into Table Leads	<span class="">Nombre</span>\n          : <span class="black--text green lighten-4 px-2">datarows</span><span class="">Entrada</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-08</span><span class="">Email</span>\n          : <span class="black--text green lighten-4 px-2">info@comovivirdeltrading.com</span><span class="">Teléfono</span>\n          : <span class="black--text green lighten-4 px-2">+34631230488</span><span class="">Tipo Empresa</span>\n          : <span class="black--text green lighten-4 px-2">Agencia</span><span class="">Servicio</span>\n          : <span class="black--text green lighten-4 px-2">Cloud &amp; DevOps</span><span class="">Extra Información</span>\n          : <span class="black--text green lighten-4 px-2">Servidor tradicional (sin cloud)</span><span class="">Cómo nos conociste</span>\n          : <span class="black--text green lighten-4 px-2">Google / Buscador</span><span class="">Mensaje</span>\n          : <span class="black--text green lighten-4 px-2">esto es un ejemplo </span><span class="">Origen Lead</span>\n          : <span class="black--text green lighten-4 px-2">Formulario web</span><span class="">Estado</span>\n          : <span class="black--text green lighten-4 px-2">Nuevo</span><span class="">Prioridad</span>\n          : <span class="black--text green lighten-4 px-2">Alta</span><span class="">Lead Tag</span>\n          : <span class="black--text green lighten-4 px-2">Hot</span><span class="">Next Action</span>\n          : <span class="black--text green lighten-4 px-2">CALL</span><span class="">Next Action Key</span>\n          : <span class="black--text green lighten-4 px-2">HIGH_VALUE_WITH_PHONE</span><span class="">GDPR Consent</span>\n          : <span class="black--text green lighten-4 px-2">true</span><span class="">landing_url</span>\n          : <span class="black--text green lighten-4 px-2">https://www.nucleotecnologico.es/contacto</span><span class="">Entrada At</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-08 19:56:47+00:00</span>	2026-01-08 21:56:47+01	2026-01-08 21:56:47+01
adtbf73it0yuq2j9c	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___Company with alias Company  	\N	2026-02-03 11:25:58+01	2026-02-03 11:25:58+01
adtklcnjclo2xnc0a	team@mailerblend.com	34.246.177.225	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	29	DATA	INSERT	\N	Record with ID 29 has been inserted into Table Leads	<span class="">Nombre</span>\n          : <span class="black--text green lighten-4 px-2">claude</span><span class="">Entrada</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-08</span><span class="">Email</span>\n          : <span class="black--text green lighten-4 px-2">claude@claude.es</span><span class="">Teléfono</span>\n          : <span class="black--text green lighten-4 px-2">+34631230488</span><span class="">Tipo Empresa</span>\n          : <span class="black--text green lighten-4 px-2">Emprendedor</span><span class="">Servicio</span>\n          : <span class="black--text green lighten-4 px-2">Infraestructura gestionada</span><span class="">Extra Información</span>\n          : <span class="black--text green lighten-4 px-2">Hosting / servidores</span><span class="">Cómo nos conociste</span>\n          : <span class="black--text green lighten-4 px-2">Google / Buscador</span><span class="">Mensaje</span>\n          : <span class="black--text green lighten-4 px-2">hola necesito servicio para hoy </span><span class="">Origen Lead</span>\n          : <span class="black--text green lighten-4 px-2">Formulario web</span><span class="">Estado</span>\n          : <span class="black--text green lighten-4 px-2">Nuevo</span><span class="">Prioridad</span>\n          : <span class="black--text green lighten-4 px-2">Alta</span><span class="">Lead Tag</span>\n          : <span class="black--text green lighten-4 px-2">Hot</span><span class="">Next Action</span>\n          : <span class="black--text green lighten-4 px-2">CALL</span><span class="">Next Action Key</span>\n          : <span class="black--text green lighten-4 px-2">URGENT_CALL_NOW</span><span class="">GDPR Consent</span>\n          : <span class="black--text green lighten-4 px-2">true</span><span class="">landing_url</span>\n          : <span class="black--text green lighten-4 px-2">https://www.nucleotecnologico.es/contacto</span><span class="">Entrada At</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-08 20:08:18+00:00</span>	2026-01-08 22:08:19+01	2026-01-08 22:08:19+01
adtp34u29qiosjq53	team@mailerblend.com	34.246.177.225	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	30	DATA	INSERT	\N	Record with ID 30 has been inserted into Table Leads	<span class="">Nombre</span>\n          : <span class="black--text green lighten-4 px-2">claude</span><span class="">Entrada</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-08</span><span class="">Email</span>\n          : <span class="black--text green lighten-4 px-2">claude@claude.es</span><span class="">Teléfono</span>\n          : <span class="black--text green lighten-4 px-2">+34631230488</span><span class="">Tipo Empresa</span>\n          : <span class="black--text green lighten-4 px-2">Emprendedor</span><span class="">Servicio</span>\n          : <span class="black--text green lighten-4 px-2">Desarrollo web y software a medida</span><span class="">Extra Información</span>\n          : <span class="black--text green lighten-4 px-2">Web profesional / landing</span><span class="">Cómo nos conociste</span>\n          : <span class="black--text green lighten-4 px-2">Google Ads</span><span class="">Mensaje</span>\n          : <span class="black--text green lighten-4 px-2">Version A: Without brackets for spaced fields (try this first)\nKey changes:\nChanged rows.[0] to rows.0 (without brackets on the array index)\nLeft field names with spaces as-is: Tipo Empresa instead of [Tipo Empresa]</span><span class="">Origen Lead</span>\n          : <span class="black--text green lighten-4 px-2">Formulario web</span><span class="">Estado</span>\n          : <span class="black--text green lighten-4 px-2">Nuevo</span><span class="">Prioridad</span>\n          : <span class="black--text green lighten-4 px-2">Media</span><span class="">Lead Tag</span>\n          : <span class="black--text green lighten-4 px-2">Qualified</span><span class="">Next Action</span>\n          : <span class="black--text green lighten-4 px-2">SEND_EMAIL</span><span class="">Next Action Key</span>\n          : <span class="black--text green lighten-4 px-2">REPLY_WITH_NEXT_STEPS</span><span class="">GDPR Consent</span>\n          : <span class="black--text green lighten-4 px-2">true</span><span class="">landing_url</span>\n          : <span class="black--text green lighten-4 px-2">https://www.nucleotecnologico.es/contacto</span><span class="">Entrada At</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-08 20:12:32+00:00</span>	2026-01-08 22:12:32+01	2026-01-08 22:12:32+01
adt7ksxqk1gf3i5xc	team@mailerblend.com	34.246.177.225	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	31	DATA	INSERT	\N	Record with ID 31 has been inserted into Table Leads	<span class="">Nombre</span>\n          : <span class="black--text green lighten-4 px-2">eduardo</span><span class="">Entrada</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-08</span><span class="">Email</span>\n          : <span class="black--text green lighten-4 px-2">eduardo@ew.es</span><span class="">Teléfono</span>\n          : <span class="black--text green lighten-4 px-2">+34631230488</span><span class="">Tipo Empresa</span>\n          : <span class="black--text green lighten-4 px-2">Agencia</span><span class="">Servicio</span>\n          : <span class="black--text green lighten-4 px-2">SRE / Observabilidad</span><span class="">Extra Información</span>\n          : <span class="black--text green lighten-4 px-2">No sabemos qué pasa en producción</span><span class="">Cómo nos conociste</span>\n          : <span class="black--text green lighten-4 px-2">Google / Buscador</span><span class="">Mensaje</span>\n          : <span class="black--text green lighten-4 px-2">Version B: If Version A doesn't work, try quoted field names</span><span class="">Origen Lead</span>\n          : <span class="black--text green lighten-4 px-2">Formulario web</span><span class="">Estado</span>\n          : <span class="black--text green lighten-4 px-2">Nuevo</span><span class="">Prioridad</span>\n          : <span class="black--text green lighten-4 px-2">Alta</span><span class="">Lead Tag</span>\n          : <span class="black--text green lighten-4 px-2">Hot</span><span class="">Next Action</span>\n          : <span class="black--text green lighten-4 px-2">CALL</span><span class="">Next Action Key</span>\n          : <span class="black--text green lighten-4 px-2">HIGH_VALUE_WITH_PHONE</span><span class="">GDPR Consent</span>\n          : <span class="black--text green lighten-4 px-2">true</span><span class="">landing_url</span>\n          : <span class="black--text green lighten-4 px-2">https://www.nucleotecnologico.es/contacto</span><span class="">Entrada At</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-08 20:14:54+00:00</span>	2026-01-08 22:14:54+01	2026-01-08 22:14:54+01
adtkgl9oej68ifwrv	team@mailerblend.com	54.194.153.38	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	32	DATA	INSERT	\N	Record with ID 32 has been inserted into Table Leads	<span class="">Nombre</span>\n          : <span class="black--text green lighten-4 px-2">test</span><span class="">Entrada</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-08</span><span class="">Email</span>\n          : <span class="black--text green lighten-4 px-2">test@test.es</span><span class="">Teléfono</span>\n          : <span class="black--text green lighten-4 px-2">+34631230488</span><span class="">Tipo Empresa</span>\n          : <span class="black--text green lighten-4 px-2">Pyme</span><span class="">Servicio</span>\n          : <span class="black--text green lighten-4 px-2">Cloud &amp; DevOps</span><span class="">Extra Información</span>\n          : <span class="black--text green lighten-4 px-2">Azure</span><span class="">Cómo nos conociste</span>\n          : <span class="black--text green lighten-4 px-2">Google Ads</span><span class="">Mensaje</span>\n          : <span class="black--text green lighten-4 px-2">testingf </span><span class="">Origen Lead</span>\n          : <span class="black--text green lighten-4 px-2">Formulario web</span><span class="">Estado</span>\n          : <span class="black--text green lighten-4 px-2">Nuevo</span><span class="">Prioridad</span>\n          : <span class="black--text green lighten-4 px-2">Alta</span><span class="">Lead Tag</span>\n          : <span class="black--text green lighten-4 px-2">Hot</span><span class="">Next Action</span>\n          : <span class="black--text green lighten-4 px-2">CALL</span><span class="">Next Action Key</span>\n          : <span class="black--text green lighten-4 px-2">HIGH_VALUE_WITH_PHONE</span><span class="">GDPR Consent</span>\n          : <span class="black--text green lighten-4 px-2">true</span><span class="">landing_url</span>\n          : <span class="black--text green lighten-4 px-2">https://www.nucleotecnologico.es/contacto</span><span class="">Entrada At</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-08 20:21:39+00:00</span>	2026-01-08 22:21:40+01	2026-01-08 22:21:40+01
adtrnwvn3kloyaoqk	team@mailerblend.com	54.194.153.38	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	33	DATA	INSERT	\N	Record with ID 33 has been inserted into Table Leads	<span class="">Nombre</span>\n          : <span class="black--text green lighten-4 px-2">test</span><span class="">Entrada</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-08</span><span class="">Email</span>\n          : <span class="black--text green lighten-4 px-2">test@test.es</span><span class="">Teléfono</span>\n          : <span class="black--text green lighten-4 px-2">+34631230488</span><span class="">Tipo Empresa</span>\n          : <span class="black--text green lighten-4 px-2">Emprendedor</span><span class="">Servicio</span>\n          : <span class="black--text green lighten-4 px-2">Desarrollo web y software a medida</span><span class="">Extra Información</span>\n          : <span class="black--text green lighten-4 px-2">CRM o sistema interno</span><span class="">Cómo nos conociste</span>\n          : <span class="black--text green lighten-4 px-2">Google Ads</span><span class="">Mensaje</span>\n          : <span class="black--text green lighten-4 px-2">test te fgdghdshñlbsdf dhfsghfghsdhsfh</span><span class="">Origen Lead</span>\n          : <span class="black--text green lighten-4 px-2">Formulario web</span><span class="">Estado</span>\n          : <span class="black--text green lighten-4 px-2">Nuevo</span><span class="">Prioridad</span>\n          : <span class="black--text green lighten-4 px-2">Media</span><span class="">Lead Tag</span>\n          : <span class="black--text green lighten-4 px-2">Qualified</span><span class="">Next Action</span>\n          : <span class="black--text green lighten-4 px-2">SEND_EMAIL</span><span class="">Next Action Key</span>\n          : <span class="black--text green lighten-4 px-2">REPLY_WITH_NEXT_STEPS</span><span class="">GDPR Consent</span>\n          : <span class="black--text green lighten-4 px-2">true</span><span class="">landing_url</span>\n          : <span class="black--text green lighten-4 px-2">https://www.nucleotecnologico.es/contacto</span><span class="">Entrada At</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-08 20:26:10+00:00</span>	2026-01-08 22:26:10+01	2026-01-08 22:26:10+01
adt0uw31589zhnvph	team@mailerblend.com	3.254.191.206	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	34	DATA	INSERT	\N	Record with ID 34 has been inserted into Table Leads	<span class="">Nombre</span>\n          : <span class="black--text green lighten-4 px-2">chatgpt</span><span class="">Entrada</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-08</span><span class="">Email</span>\n          : <span class="black--text green lighten-4 px-2">eduardo@ew.es</span><span class="">Teléfono</span>\n          : <span class="black--text green lighten-4 px-2">+34631230488</span><span class="">Tipo Empresa</span>\n          : <span class="black--text green lighten-4 px-2">Pyme</span><span class="">Servicio</span>\n          : <span class="black--text green lighten-4 px-2">Desarrollo web y software a medida</span><span class="">Extra Información</span>\n          : <span class="black--text green lighten-4 px-2">CRM o sistema interno</span><span class="">Cómo nos conociste</span>\n          : <span class="black--text green lighten-4 px-2">Google / Buscador</span><span class="">Mensaje</span>\n          : <span class="black--text green lighten-4 px-2">probando, probando, probando </span><span class="">Origen Lead</span>\n          : <span class="black--text green lighten-4 px-2">Formulario web</span><span class="">Estado</span>\n          : <span class="black--text green lighten-4 px-2">Nuevo</span><span class="">Prioridad</span>\n          : <span class="black--text green lighten-4 px-2">Media</span><span class="">Lead Tag</span>\n          : <span class="black--text green lighten-4 px-2">Qualified</span><span class="">Next Action</span>\n          : <span class="black--text green lighten-4 px-2">SEND_EMAIL</span><span class="">Next Action Key</span>\n          : <span class="black--text green lighten-4 px-2">REPLY_WITH_NEXT_STEPS</span><span class="">GDPR Consent</span>\n          : <span class="black--text green lighten-4 px-2">true</span><span class="">landing_url</span>\n          : <span class="black--text green lighten-4 px-2">https://www.nucleotecnologico.es/contacto</span><span class="">Entrada At</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-08 20:33:14+00:00</span>	2026-01-08 22:33:15+01	2026-01-08 22:33:15+01
adtazikyi0t4wxfra	team@mailerblend.com	34.243.43.172	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	35	DATA	INSERT	\N	Record with ID 35 has been inserted into Table Leads	<span class="">Nombre</span>\n          : <span class="black--text green lighten-4 px-2">eduardo</span><span class="">Entrada</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-08</span><span class="">Email</span>\n          : <span class="black--text green lighten-4 px-2">eduardo@ew.es</span><span class="">Teléfono</span>\n          : <span class="black--text green lighten-4 px-2">+34631230488</span><span class="">Tipo Empresa</span>\n          : <span class="black--text green lighten-4 px-2">Pyme</span><span class="">Servicio</span>\n          : <span class="black--text green lighten-4 px-2">SRE / Observabilidad</span><span class="">Extra Información</span>\n          : <span class="black--text green lighten-4 px-2">No tenemos alertas o llegan tarde</span><span class="">Cómo nos conociste</span>\n          : <span class="black--text green lighten-4 px-2">Google / Buscador</span><span class="">Mensaje</span>\n          : <span class="black--text green lighten-4 px-2">The json helper is used to safely serialize values into valid JSON, whether they’re strings, objects, or arrays. It ensures proper quoting and escaping, preventing common errors with quotes, newlines, or special characters. For example, {{ json event }} outputs the full event object, while {{ json event.data.rows.[0].Title }} safely inserts a single field as a JSON string. This makes it the most reliable way to embed dynamic values in webhook paylo</span><span class="">Origen Lead</span>\n          : <span class="black--text green lighten-4 px-2">Formulario web</span><span class="">Estado</span>\n          : <span class="black--text green lighten-4 px-2">Nuevo</span><span class="">Prioridad</span>\n          : <span class="black--text green lighten-4 px-2">Alta</span><span class="">Lead Tag</span>\n          : <span class="black--text green lighten-4 px-2">Hot</span><span class="">Next Action</span>\n          : <span class="black--text green lighten-4 px-2">CALL</span><span class="">Next Action Key</span>\n          : <span class="black--text green lighten-4 px-2">HIGH_VALUE_WITH_PHONE</span><span class="">GDPR Consent</span>\n          : <span class="black--text green lighten-4 px-2">true</span><span class="">landing_url</span>\n          : <span class="black--text green lighten-4 px-2">https://www.nucleotecnologico.es/contacto</span><span class="">Entrada At</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-08 20:41:05+00:00</span>	2026-01-08 22:41:06+01	2026-01-08 22:41:06+01
adtdzacd1psut4os0	team@mailerblend.com	54.171.220.68	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	36	DATA	INSERT	\N	Record with ID 36 has been inserted into Table Leads	<span class="">Nombre</span>\n          : <span class="black--text green lighten-4 px-2">gemini</span><span class="">Entrada</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-08</span><span class="">Email</span>\n          : <span class="black--text green lighten-4 px-2">gemini@gemini.es</span><span class="">Teléfono</span>\n          : <span class="black--text green lighten-4 px-2">+34631230488</span><span class="">Tipo Empresa</span>\n          : <span class="black--text green lighten-4 px-2">Agencia</span><span class="">Servicio</span>\n          : <span class="black--text green lighten-4 px-2">Cloud &amp; DevOps</span><span class="">Extra Información</span>\n          : <span class="black--text green lighten-4 px-2">Servidor tradicional (sin cloud)</span><span class="">Cómo nos conociste</span>\n          : <span class="black--text green lighten-4 px-2">Google Ads</span><span class="">Mensaje</span>\n          : <span class="black--text green lighten-4 px-2">Great news! The diagnostic test confirms that for your NocoDB setup, the correct data path is {{data.ColumnName}}. It also confirms that for columns with spaces, the correct format is {{data.[Column Name]}}.</span><span class="">Origen Lead</span>\n          : <span class="black--text green lighten-4 px-2">Formulario web</span><span class="">Estado</span>\n          : <span class="black--text green lighten-4 px-2">Nuevo</span><span class="">Prioridad</span>\n          : <span class="black--text green lighten-4 px-2">Alta</span><span class="">Lead Tag</span>\n          : <span class="black--text green lighten-4 px-2">Hot</span><span class="">Next Action</span>\n          : <span class="black--text green lighten-4 px-2">CALL</span><span class="">Next Action Key</span>\n          : <span class="black--text green lighten-4 px-2">HIGH_VALUE_WITH_PHONE</span><span class="">GDPR Consent</span>\n          : <span class="black--text green lighten-4 px-2">true</span><span class="">landing_url</span>\n          : <span class="black--text green lighten-4 px-2">https://www.nucleotecnologico.es/contacto</span><span class="">Entrada At</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-08 20:46:29+00:00</span>	2026-01-08 22:46:30+01	2026-01-08 22:46:30+01
adt4osg3xtpu981us	team@mailerblend.com	\N	\N	\N	\N	\N	AUTHENTICATION	SIGNIN	\N	\N	\N	2026-01-22 11:29:41+01	2026-01-22 11:29:41+01
adth2b6yxhgnl68ub	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___Segment with alias Segment  	\N	2026-02-03 11:26:11+01	2026-02-03 11:26:11+01
adt4fa137ilw09jve	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___Pack with alias Pack  	\N	2026-02-03 11:26:23+01	2026-02-03 11:26:23+01
adtx0gc81t7pqrrjw	team@mailerblend.com	34.243.132.159	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	37	DATA	INSERT	\N	Record with ID 37 has been inserted into Table Leads	<span class="">Nombre</span>\n          : <span class="black--text green lighten-4 px-2">test</span><span class="">Entrada</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-23</span><span class="">Email</span>\n          : <span class="black--text green lighten-4 px-2">nu@nu.es</span><span class="">Teléfono</span>\n          : <span class="black--text green lighten-4 px-2">+34631230488</span><span class="">Tipo Empresa</span>\n          : <span class="black--text green lighten-4 px-2">Pyme</span><span class="">Servicio</span>\n          : <span class="black--text green lighten-4 px-2">Desarrollo web y software a medida</span><span class="">Extra Información</span>\n          : <span class="black--text green lighten-4 px-2">Web profesional / landing</span><span class="">Cómo nos conociste</span>\n          : <span class="black--text green lighten-4 px-2">Google Ads</span><span class="">Mensaje</span>\n          : <span class="black--text green lighten-4 px-2">prueba conversion</span><span class="">Origen Lead</span>\n          : <span class="black--text green lighten-4 px-2">Formulario web</span><span class="">Estado</span>\n          : <span class="black--text green lighten-4 px-2">Nuevo</span><span class="">Prioridad</span>\n          : <span class="black--text green lighten-4 px-2">Media</span><span class="">Lead Tag</span>\n          : <span class="black--text green lighten-4 px-2">Qualified</span><span class="">Next Action</span>\n          : <span class="black--text green lighten-4 px-2">SEND_EMAIL</span><span class="">Next Action Key</span>\n          : <span class="black--text green lighten-4 px-2">REPLY_WITH_NEXT_STEPS</span><span class="">GDPR Consent</span>\n          : <span class="black--text green lighten-4 px-2">true</span><span class="">landing_url</span>\n          : <span class="black--text green lighten-4 px-2">https://www.nucleotecnologico.es/contacto#form</span><span class="">referrer</span>\n          : <span class="black--text green lighten-4 px-2">https://tagassistant.google.com/</span><span class="">Entrada At</span>\n          : <span class="black--text green lighten-4 px-2">2026-01-23 18:41:24+00:00</span>	2026-01-23 20:40:23+01	2026-01-23 20:40:23+01
adt13fwkhfldfnfyx	team@mailerblend.com	\N	\N	\N	\N	\N	AUTHENTICATION	SIGNIN	\N	\N	\N	2026-02-03 09:23:46+01	2026-02-03 09:23:46+01
adtxdrogp3qrvg18b	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___Pack with alias Pack has been created	\N	2026-02-03 09:55:12+01	2026-02-03 09:55:12+01
adtivq4pm1kkv475t	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___Segment with alias Segment has been created	\N	2026-02-03 09:55:13+01	2026-02-03 09:55:13+01
adto5b12jjhvwz62x	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___Company with alias Company has been created	\N	2026-02-03 09:55:14+01	2026-02-03 09:55:14+01
adt5u5bw4i3m93xwk	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___Lead with alias Lead has been created	\N	2026-02-03 09:55:14+01	2026-02-03 09:55:14+01
adtq9vtl2rih0ztln	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___Attempt with alias Attempt has been created	\N	2026-02-03 09:55:15+01	2026-02-03 09:55:15+01
adtdyyym6lc4ul1zp	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___Research_Snapshot with alias Research_Snapshot has been created	\N	2026-02-03 09:55:16+01	2026-02-03 09:55:16+01
adtcgaa71ulkyjsa4	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___Message_Template with alias Message_Template has been created	\N	2026-02-03 09:55:16+01	2026-02-03 09:55:16+01
adt7m876b9iib9dh9	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___Approval with alias Approval has been created	\N	2026-02-03 09:55:17+01	2026-02-03 09:55:17+01
adtgbnq9mr3urh16l	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___Conversation with alias Conversation has been created	\N	2026-02-03 09:55:18+01	2026-02-03 09:55:18+01
adta48pa6l5gbiylv	team@mailerblend.com	\N	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	CREATE	\N	Table nc_fl6j___Outcome with alias Outcome has been created	\N	2026-02-03 09:55:18+01	2026-02-03 09:55:18+01
adtfygjjo5ismhgqj	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	CREATE	\N	The column company_id with alias company_id from table nc_fl6j___Lead has been created	\N	2026-02-03 09:55:23+01	2026-02-03 09:55:23+01
adt4ux8pv299jc4yf	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	CREATE	\N	The column lead_id with alias lead_id from table nc_fl6j___Attempt has been created	\N	2026-02-03 09:55:31+01	2026-02-03 09:55:31+01
adtb2aqt1oq4qkbnp	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	CREATE	\N	The column company_id with alias company_id from table nc_fl6j___Research_Snapshot has been created	\N	2026-02-03 09:55:32+01	2026-02-03 09:55:32+01
adtgtyn1xbob1llmd	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	CREATE	\N	The column lead_id with alias lead_id from table nc_fl6j___Research_Snapshot has been created	\N	2026-02-03 09:55:33+01	2026-02-03 09:55:33+01
adtdxqmgitmfjkh3i	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	CREATE	\N	The column lead_id with alias lead_id from table nc_fl6j___Approval has been created	\N	2026-02-03 09:55:41+01	2026-02-03 09:55:41+01
adtudvsl9gqvrzq1s	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	CREATE	\N	The column lead_id with alias lead_id from table nc_fl6j___Conversation has been created	\N	2026-02-03 09:55:45+01	2026-02-03 09:55:45+01
adtg7iznx9h86kkx3	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	CREATE	\N	The column lead_id with alias lead_id from table nc_fl6j___Outcome has been created	\N	2026-02-03 09:55:46+01	2026-02-03 09:55:46+01
adtdgqta10fzlv8xs	team@mailerblend.com	192.168.1.254	\N	\N	\N	\N	ORG_USER	INVITE	\N	gestionads15.21@gmail.com has been invited to the organisation	\N	2026-02-03 10:43:58+01	2026-02-03 10:43:58+01
adteognc0bfwgj6lv	gestionads15.21@gmail.com	192.168.1.254	\N	\N	\N	\N	AUTHENTICATION	SIGNUP	\N	User has signed up	\N	2026-02-03 10:48:26+01	2026-02-03 10:48:26+01
adta9pm4q5hvfzmjg	gestionads15.21@gmail.com	\N	\N	\N	\N	\N	AUTHENTICATION	SIGNIN	\N	\N	\N	2026-02-03 10:48:26+01	2026-02-03 10:48:26+01
adtuokwps162xjqy7	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	AUTHENTICATION	INVITE	\N	invited gestionads15.21@gmail.com to pbydkvvvbvv4pdf base 	\N	2026-02-03 10:57:27+01	2026-02-03 10:57:27+01
adtsa9uzqkjub4wdq	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___Message_Template with alias Message_Template  	\N	2026-02-03 11:24:45+01	2026-02-03 11:24:45+01
adtho2g9bh1fnr59x	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	DELETE	\N	The column null with alias lead_id from table nc_fl6j___Approval has been deleted	\N	2026-02-03 11:25:15+01	2026-02-03 11:25:15+01
adtkd6q56j5xvp778	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___Approval with alias Approval  	\N	2026-02-03 11:25:15+01	2026-02-03 11:25:15+01
adtzhm02tr386oywr	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	DELETE	\N	The column null with alias lead_id from table nc_fl6j___Outcome has been deleted	\N	2026-02-03 11:25:24+01	2026-02-03 11:25:24+01
adtwnlykesj331tcp	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___Outcome with alias Outcome  	\N	2026-02-03 11:25:24+01	2026-02-03 11:25:24+01
adtb8508hcodvs51n	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	DELETE	\N	The column null with alias lead_id from table nc_fl6j___Conversation has been deleted	\N	2026-02-03 11:25:32+01	2026-02-03 11:25:32+01
adt7xjti0rf5tqhej	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___Conversation with alias Conversation  	\N	2026-02-03 11:25:32+01	2026-02-03 11:25:32+01
adtam4weyvb79e96p	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	DELETE	\N	The column null with alias lead_id from table nc_fl6j___Attempt has been deleted	\N	2026-02-03 11:25:39+01	2026-02-03 11:25:39+01
adtd3xz6p11krsfp7	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___Attempt with alias Attempt  	\N	2026-02-03 11:25:39+01	2026-02-03 11:25:39+01
adthe9plluhxy1sig	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	DELETE	\N	The column null with alias company_id from table nc_fl6j___Research_Snapshot has been deleted	\N	2026-02-03 11:25:47+01	2026-02-03 11:25:47+01
adtnunh4hanngq0eb	team@mailerblend.com	192.168.1.254	\N	pata00z3me9f1bz	\N	\N	TABLE_COLUMN	DELETE	\N	The column null with alias lead_id from table nc_fl6j___Research_Snapshot has been deleted	\N	2026-02-03 11:25:47+01	2026-02-03 11:25:47+01
adt70fkwkpz26q72p	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___Research_Snapshot with alias Research_Snapshot  	\N	2026-02-03 11:25:47+01	2026-02-03 11:25:47+01
adtsixltt6sk5h4gd	team@mailerblend.com	192.168.1.254	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	TABLE	DELETE	\N	Deleted table nc_fl6j___Lead with alias Lead  	\N	2026-02-03 11:26:37+01	2026-02-03 11:26:37+01
adt0p7zphjdoy7h5s	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Pack with alias Pack has been created	\N	2026-02-03 13:02:37+01	2026-02-03 13:02:37+01
adtzxlyu6p2qvwvkd	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Segment with alias Segment has been created	\N	2026-02-03 13:02:37+01	2026-02-03 13:02:37+01
adt4c5hpq4h7g1rio	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Company with alias Company has been created	\N	2026-02-03 13:02:38+01	2026-02-03 13:02:38+01
adt5qneijztjvgzar	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Lead with alias Lead has been created	\N	2026-02-03 13:02:38+01	2026-02-03 13:02:38+01
adt3ahuwjwa1tsqmr	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Attempt with alias Attempt has been created	\N	2026-02-03 13:02:38+01	2026-02-03 13:02:38+01
adtyhg7ki3u1l5t44	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Approval with alias Approval has been created	\N	2026-02-03 13:02:38+01	2026-02-03 13:02:38+01
adtc7ssx8m7utvema	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Outcome with alias Outcome has been created	\N	2026-02-03 13:02:38+01	2026-02-03 13:02:38+01
adtgqwo1u2pzsw30r	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Pack with alias Pack  	\N	2026-02-03 13:06:10+01	2026-02-03 13:06:10+01
adtr1ctwm9cntyv57	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Segment with alias Segment  	\N	2026-02-03 13:06:14+01	2026-02-03 13:06:14+01
adts5vrh4fmy3e3u0	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Company with alias Company  	\N	2026-02-03 13:06:18+01	2026-02-03 13:06:18+01
adtrd1mpcsrb4mef3	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Lead with alias Lead  	\N	2026-02-03 13:06:23+01	2026-02-03 13:06:23+01
adtltdjvlhjxjsmlr	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Attempt with alias Attempt  	\N	2026-02-03 13:06:27+01	2026-02-03 13:06:27+01
adt0n7po4ufvj00gg	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Approval with alias Approval  	\N	2026-02-03 13:06:31+01	2026-02-03 13:06:31+01
adteqt44psh47h6bh	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Outcome with alias Outcome  	\N	2026-02-03 13:06:35+01	2026-02-03 13:06:35+01
adt34k3qttl4ru5pk	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Pack with alias Pack has been created	\N	2026-02-03 14:01:11+01	2026-02-03 14:01:11+01
adtlkzf5hx7hdl95c	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Segment with alias Segment has been created	\N	2026-02-03 14:01:12+01	2026-02-03 14:01:12+01
adtmdjpzhev012ilu	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Company with alias Company has been created	\N	2026-02-03 14:01:12+01	2026-02-03 14:01:12+01
adtco1n8hn9rhkkb6	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Lead with alias Lead has been created	\N	2026-02-03 14:01:12+01	2026-02-03 14:01:12+01
adtthrm7fz1l2qnjk	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Attempt with alias Attempt has been created	\N	2026-02-03 14:01:12+01	2026-02-03 14:01:12+01
adtua7pnhl6jogfkl	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Research_Snapshot with alias ResearchSnapshot has been created	\N	2026-02-03 14:01:12+01	2026-02-03 14:01:12+01
adt5gsjk30oplayag	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Message_Template with alias MessageTemplate has been created	\N	2026-02-03 14:01:12+01	2026-02-03 14:01:12+01
adthoxid4ti0c1t79	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Approval with alias Approval has been created	\N	2026-02-03 14:01:12+01	2026-02-03 14:01:12+01
adt74l99v0tls0yf0	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Conversation with alias Conversation has been created	\N	2026-02-03 14:01:12+01	2026-02-03 14:01:12+01
adtvyzoc6cq7xvqim	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Outcome with alias Outcome has been created	\N	2026-02-03 14:01:12+01	2026-02-03 14:01:12+01
adtzqxhdvhlczj08t	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Pack with alias Pack  	\N	2026-02-03 14:07:37+01	2026-02-03 14:07:37+01
adtagtv8gxp5750r5	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Segment with alias Segment  	\N	2026-02-03 14:07:37+01	2026-02-03 14:07:37+01
adtdp71yiv8ov5w0k	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Company with alias Company  	\N	2026-02-03 14:07:37+01	2026-02-03 14:07:37+01
adt7v87s1jf8spadg	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Lead with alias Lead  	\N	2026-02-03 14:07:37+01	2026-02-03 14:07:37+01
adtea0favr6fbqlv0	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Attempt with alias Attempt  	\N	2026-02-03 14:07:38+01	2026-02-03 14:07:38+01
adtzfv3yh640txoqx	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Approval with alias Approval  	\N	2026-02-03 14:07:38+01	2026-02-03 14:07:38+01
adtzshdrv1vra7xov	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Conversation with alias Conversation  	\N	2026-02-03 14:07:38+01	2026-02-03 14:07:38+01
adt6hhhbm2gp1wpls	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Outcome with alias Outcome  	\N	2026-02-03 14:07:38+01	2026-02-03 14:07:38+01
adts4dvnne3ri7b0l	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Pack with alias Pack has been created	\N	2026-02-03 14:07:38+01	2026-02-03 14:07:38+01
adtaloc1r3nj5dtem	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Segment with alias Segment has been created	\N	2026-02-03 14:07:38+01	2026-02-03 14:07:38+01
adtfif43mygux42t0	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Company with alias Company has been created	\N	2026-02-03 14:07:38+01	2026-02-03 14:07:38+01
adt2hxj8qsjhlbc3g	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Lead with alias Lead has been created	\N	2026-02-03 14:07:38+01	2026-02-03 14:07:38+01
adtpmqe9bmzxvdyr5	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Attempt with alias Attempt has been created	\N	2026-02-03 14:07:38+01	2026-02-03 14:07:38+01
adttyuavaw5p4c1gg	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Research_Snapshot with alias ResearchSnapshot  	\N	2026-02-03 14:08:24+01	2026-02-03 14:08:24+01
adtfhug2xbijr9wuu	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Message_Template with alias MessageTemplate  	\N	2026-02-03 14:08:29+01	2026-02-03 14:08:29+01
adt9fbpc75zycnlqz	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Pack with alias Pack  	\N	2026-02-03 14:08:33+01	2026-02-03 14:08:33+01
adtylzam9zzmc1oey	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Segment with alias Segment  	\N	2026-02-03 14:08:38+01	2026-02-03 14:08:38+01
adt94hhec9wcvrdr1	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Company with alias Company  	\N	2026-02-03 14:08:43+01	2026-02-03 14:08:43+01
adt2yfq36x4ac0qdc	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Lead with alias Lead  	\N	2026-02-03 14:08:47+01	2026-02-03 14:08:47+01
adt9491gcwwu82kdg	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Attempt with alias Attempt  	\N	2026-02-03 14:08:51+01	2026-02-03 14:08:51+01
adtehor1ptsutg7f0	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Pack with alias Pack has been created	\N	2026-02-03 14:10:30+01	2026-02-03 14:10:30+01
adtlgn78ehg4lv17g	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Segment with alias Segment has been created	\N	2026-02-03 14:10:30+01	2026-02-03 14:10:30+01
adthrn161jmqo7w6b	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Company with alias Company has been created	\N	2026-02-03 14:10:30+01	2026-02-03 14:10:30+01
adtvgb7l92bieoime	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Lead with alias Lead has been created	\N	2026-02-03 14:10:30+01	2026-02-03 14:10:30+01
adtswmz3jqv6bsrnp	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Attempt with alias Attempt has been created	\N	2026-02-03 14:10:30+01	2026-02-03 14:10:30+01
adtj66mc8vudfikmu	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Research_Snapshot with alias ResearchSnapshot has been created	\N	2026-02-03 14:10:30+01	2026-02-03 14:10:30+01
adt4v4y9lutik7td4	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Message_Template with alias MessageTemplate has been created	\N	2026-02-03 14:10:30+01	2026-02-03 14:10:30+01
adt400hdy0gjrj4dx	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Approval with alias Approval has been created	\N	2026-02-03 14:10:31+01	2026-02-03 14:10:31+01
adtvbf66h0hpughfn	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Conversation with alias Conversation has been created	\N	2026-02-03 14:10:31+01	2026-02-03 14:10:31+01
adtqtswye9b7e7hyx	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Outcome with alias Outcome has been created	\N	2026-02-03 14:10:31+01	2026-02-03 14:10:31+01
adtl84lllghxob8im	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___TEST_Company with alias TestCompany has been created	\N	2026-02-03 14:56:40+01	2026-02-03 14:56:40+01
adty1e3cibbbiq8i2	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___TEST_Lead with alias TestLead has been created	\N	2026-02-03 14:56:40+01	2026-02-03 14:56:40+01
adtd6rx9aac3c8su0	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___TEST_Lead with alias TestLead  	\N	2026-02-03 14:57:18+01	2026-02-03 14:57:18+01
adt71nf44v7x0m9jd	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___TEST_Company with alias TestCompany  	\N	2026-02-03 14:57:25+01	2026-02-03 14:57:25+01
adtvhjqvnmbjjxnoq	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___TEST_Company with alias TestCompany has been created	\N	2026-02-03 14:58:33+01	2026-02-03 14:58:33+01
adtvmnu3bfopfyldb	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___TEST_Lead with alias TestLead has been created	\N	2026-02-03 14:58:33+01	2026-02-03 14:58:33+01
adthzqzybum1wk1hv	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___TEST_Company with alias TestCompany  	\N	2026-02-03 14:58:51+01	2026-02-03 14:58:51+01
adtq0ey828cfo6lph	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___TEST_Lead with alias TestLead  	\N	2026-02-03 14:58:56+01	2026-02-03 14:58:56+01
adtqwhkoayrkgmir3	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___TEST_Company with alias TestCompany has been created	\N	2026-02-03 15:00:30+01	2026-02-03 15:00:30+01
adtvlkena3y81uovk	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___TEST_Lead with alias TestLead has been created	\N	2026-02-03 15:00:30+01	2026-02-03 15:00:30+01
adta6ja6g8vwf59qn	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___TEST_Lead with alias TestLead  	\N	2026-02-03 15:07:06+01	2026-02-03 15:07:06+01
adtol5ru57nfi8bm6	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___TEST_Company with alias TestCompany  	\N	2026-02-03 15:07:12+01	2026-02-03 15:07:12+01
adtszmjuxdhsechbi	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___TEST_Company with alias TestCompany has been created	\N	2026-02-03 15:07:18+01	2026-02-03 15:07:18+01
adtt6ma4bc01e6zf5	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___TEST_Lead with alias TestLead has been created	\N	2026-02-03 15:07:18+01	2026-02-03 15:07:18+01
adttahz5qmeb6g9i2	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___TEST_Lead with alias TestLead  	\N	2026-02-03 15:08:43+01	2026-02-03 15:08:43+01
adt5asemdqfbzwu53	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___TEST_Company with alias TestCompany  	\N	2026-02-03 15:08:47+01	2026-02-03 15:08:47+01
adt8w20c2rij8mabh	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___TEST_Company_Final with alias TestCompanyFinal has been created	\N	2026-02-03 15:09:02+01	2026-02-03 15:09:02+01
adt2disao9ktur0vc	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___TEST_Lead_Final with alias TestLeadFinal has been created	\N	2026-02-03 15:09:02+01	2026-02-03 15:09:02+01
adtbgior51bqlqtsz	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___TEST_Company_Final with alias TestCompanyFinal  	\N	2026-02-03 15:11:13+01	2026-02-03 15:11:13+01
adt45yb1o54u6e7ol	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column Empresa_Id with alias Empresa_Id from table nc_jmsd___TEST_Lead_Final has been deleted	\N	2026-02-03 15:11:17+01	2026-02-03 15:11:17+01
adthjxchk446h4hrq	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___TEST_Lead_Final with alias TestLeadFinal  	\N	2026-02-03 15:11:17+01	2026-02-03 15:11:17+01
adto1ht7ogkstlt38	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Pack with alias Pack  	\N	2026-02-03 15:12:18+01	2026-02-03 15:12:18+01
adtgg5ftmh1xw08x0	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Segment with alias Segment  	\N	2026-02-03 15:12:22+01	2026-02-03 15:12:22+01
adtgn1stf8x6oa1zn	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Lead with alias Lead  	\N	2026-02-03 15:12:30+01	2026-02-03 15:12:30+01
adtmaljzztjpjez0v	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Research_Snapshot with alias ResearchSnapshot  	\N	2026-02-03 15:12:40+01	2026-02-03 15:12:40+01
adt4vd9h58q096uby	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Approval with alias Approval  	\N	2026-02-03 15:12:48+01	2026-02-03 15:12:48+01
adtsslbbsbo3nu91a	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Outcome with alias Outcome  	\N	2026-02-03 15:12:57+01	2026-02-03 15:12:57+01
adteukx0d6lsuy571	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Lead with alias Lead has been created	\N	2026-02-03 15:13:04+01	2026-02-03 15:13:04+01
adt4t8rakb8g1ysad	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Attempt with alias Attempt has been created	\N	2026-02-03 15:13:04+01	2026-02-03 15:13:04+01
adtwf30ifyp9ixne9	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Company with alias Company  	\N	2026-02-03 15:12:26+01	2026-02-03 15:12:26+01
adt01h2g38vdif742	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Attempt with alias Attempt  	\N	2026-02-03 15:12:35+01	2026-02-03 15:12:35+01
adtdwemujtpgryxsv	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Message_Template with alias MessageTemplate  	\N	2026-02-03 15:12:44+01	2026-02-03 15:12:44+01
adtq4hkbw9scf5k6b	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Conversation with alias Conversation  	\N	2026-02-03 15:12:52+01	2026-02-03 15:12:52+01
adt9odz94y9q1w46z	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Pack with alias Pack has been created	\N	2026-02-03 15:13:04+01	2026-02-03 15:13:04+01
adtcowsxio4k6md1k	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Company with alias Company has been created	\N	2026-02-03 15:13:04+01	2026-02-03 15:13:04+01
adtoboc6oojwv8gi2	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Segment with alias Segment has been created	\N	2026-02-03 15:13:04+01	2026-02-03 15:13:04+01
adtyo962dt73q6hii	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Pack with alias Pack  	\N	2026-02-03 15:14:56+01	2026-02-03 15:14:56+01
adtbol0rcupowpywj	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Company with alias Company  	\N	2026-02-03 15:15:01+01	2026-02-03 15:15:01+01
adteiv4bhi7t6ts9a	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column pack_id with alias pack_id from table nc_jmsd___Segment has been deleted	\N	2026-02-03 15:15:06+01	2026-02-03 15:15:06+01
adtnksjo5e2az9cjb	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Segment with alias Segment  	\N	2026-02-03 15:15:06+01	2026-02-03 15:15:06+01
adttkx1dvz3sht9wb	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column company_id with alias company_id from table nc_jmsd___Lead has been deleted	\N	2026-02-03 15:15:10+01	2026-02-03 15:15:10+01
adtehxhg5s9o251di	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column pack_candidate with alias pack_candidate from table nc_jmsd___Lead has been deleted	\N	2026-02-03 15:15:10+01	2026-02-03 15:15:10+01
adt31s3cvwhqz12w8	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Lead with alias Lead  	\N	2026-02-03 15:15:10+01	2026-02-03 15:15:10+01
adtr0ia31c6zjmbt3	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column lead_id with alias lead_id from table nc_jmsd___Attempt has been deleted	\N	2026-02-03 15:15:16+01	2026-02-03 15:15:16+01
adtuy6r94932zxhjg	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Attempt with alias Attempt  	\N	2026-02-03 15:15:16+01	2026-02-03 15:15:16+01
adtnc9thyuqmfunuf	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Pack with alias Pack has been created	\N	2026-02-03 15:16:10+01	2026-02-03 15:16:10+01
adtfyzjst0qh9khju	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Company with alias Company has been created	\N	2026-02-03 15:16:10+01	2026-02-03 15:16:10+01
adt18qlgzfyt1u71j	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Segment with alias Segment has been created	\N	2026-02-03 15:16:10+01	2026-02-03 15:16:10+01
adtwb4515pc3qyugb	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Lead with alias Lead has been created	\N	2026-02-03 15:16:10+01	2026-02-03 15:16:10+01
adt5zt579xnez8dcn	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Message_Template with alias MessageTemplate has been created	\N	2026-02-03 15:16:10+01	2026-02-03 15:16:10+01
adtfit1bj4q1ncdvg	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Attempt with alias Attempt has been created	\N	2026-02-03 15:16:10+01	2026-02-03 15:16:10+01
adte6kgfhtpk2i9mi	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Research_Snapshot with alias ResearchSnapshot has been created	\N	2026-02-03 15:16:10+01	2026-02-03 15:16:10+01
adtjeyv25e433jr28	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Approval with alias Approval has been created	\N	2026-02-03 15:16:11+01	2026-02-03 15:16:11+01
adtcvy79ntxwhkxzs	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Conversation with alias Conversation has been created	\N	2026-02-03 15:16:11+01	2026-02-03 15:16:11+01
adtqlqt01ntxij317	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Outcome with alias Outcome has been created	\N	2026-02-03 15:16:11+01	2026-02-03 15:16:11+01
adtb4ldryn2yuyxcp	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Pack with alias Pack  	\N	2026-02-03 15:19:49+01	2026-02-03 15:19:49+01
adt1o8cmfk8u518m9	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Company with alias Company  	\N	2026-02-03 15:19:54+01	2026-02-03 15:19:54+01
adthdjvwh6ipqsh10	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column pack_id with alias pack_id from table nc_jmsd___Segment has been deleted	\N	2026-02-03 15:19:59+01	2026-02-03 15:19:59+01
adtlro8bnstyofy18	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Segment with alias Segment  	\N	2026-02-03 15:19:59+01	2026-02-03 15:19:59+01
adtv27vy3lf6024d2	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column company_id with alias company_id from table nc_jmsd___Lead has been deleted	\N	2026-02-03 15:20:03+01	2026-02-03 15:20:03+01
adtmyetohagc12tg3	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column segment_id with alias segment_id from table nc_jmsd___Lead has been deleted	\N	2026-02-03 15:20:03+01	2026-02-03 15:20:03+01
adtxoj1rw3pxoszh3	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Lead with alias Lead  	\N	2026-02-03 15:20:03+01	2026-02-03 15:20:03+01
adtteu2ddgg02wm8p	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column pack_id with alias pack_id from table nc_jmsd___Message_Template has been deleted	\N	2026-02-03 15:20:07+01	2026-02-03 15:20:07+01
adtxd8m2l8jibqh0f	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Message_Template with alias MessageTemplate  	\N	2026-02-03 15:20:07+01	2026-02-03 15:20:07+01
adtpao2j7xpat5kuo	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column lead_id with alias lead_id from table nc_jmsd___Attempt has been deleted	\N	2026-02-03 15:20:12+01	2026-02-03 15:20:12+01
adtcfq6cxic87e9ws	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Attempt with alias Attempt  	\N	2026-02-03 15:20:12+01	2026-02-03 15:20:12+01
adt2yrhehpbrec5sk	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column lead_id with alias lead_id from table nc_jmsd___Research_Snapshot has been deleted	\N	2026-02-03 15:20:16+01	2026-02-03 15:20:16+01
adtakcw1rd9gg4wl7	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Research_Snapshot with alias ResearchSnapshot  	\N	2026-02-03 15:20:16+01	2026-02-03 15:20:16+01
adt2tk2zttdaqtggq	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column lead_id with alias lead_id from table nc_jmsd___Approval has been deleted	\N	2026-02-03 15:20:20+01	2026-02-03 15:20:20+01
adtvkp127q1umnq1w	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column template_id with alias template_id from table nc_jmsd___Approval has been deleted	\N	2026-02-03 15:20:20+01	2026-02-03 15:20:20+01
adtyuj4sd63h7hv8x	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Approval with alias Approval  	\N	2026-02-03 15:20:20+01	2026-02-03 15:20:20+01
adth5066wh2wsfvjl	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column lead_id with alias lead_id from table nc_jmsd___Conversation has been deleted	\N	2026-02-03 15:20:25+01	2026-02-03 15:20:25+01
adtlwj5ki6ed912ks	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Conversation with alias Conversation  	\N	2026-02-03 15:20:25+01	2026-02-03 15:20:25+01
adttzsglo0rm8ovl9	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column lead_id with alias lead_id from table nc_jmsd___Outcome has been deleted	\N	2026-02-03 15:20:30+01	2026-02-03 15:20:30+01
adtwgr3u7uapoei5n	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Outcome with alias Outcome  	\N	2026-02-03 15:20:30+01	2026-02-03 15:20:30+01
adt0hbblcow90irek	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Pack with alias Pack has been created	\N	2026-02-03 15:29:35+01	2026-02-03 15:29:35+01
adtfsd7530r3rr9c9	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Segment with alias Segment has been created	\N	2026-02-03 15:29:35+01	2026-02-03 15:29:35+01
adt0ema4mbr65v86e	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Company with alias Company has been created	\N	2026-02-03 15:29:35+01	2026-02-03 15:29:35+01
adtpj88hkv49mz7n7	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Lead with alias Lead has been created	\N	2026-02-03 15:29:35+01	2026-02-03 15:29:35+01
adtm3a2jscilkw5re	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Attempt with alias Attempt has been created	\N	2026-02-03 15:29:35+01	2026-02-03 15:29:35+01
adtye63we2ndgngng	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Research_Snapshot with alias ResearchSnapshot has been created	\N	2026-02-03 15:29:35+01	2026-02-03 15:29:35+01
adt7hecssrzznsry9	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Message_Template with alias MessageTemplate has been created	\N	2026-02-03 15:29:35+01	2026-02-03 15:29:35+01
adtoetq76q2sb4cni	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Approval with alias Approval has been created	\N	2026-02-03 15:29:35+01	2026-02-03 15:29:35+01
adtxaolplq3rb7tn9	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Conversation with alias Conversation has been created	\N	2026-02-03 15:29:35+01	2026-02-03 15:29:35+01
adtwej629b7u7l6gf	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Outcome with alias Outcome has been created	\N	2026-02-03 15:29:36+01	2026-02-03 15:29:36+01
adttu62ikcvxckeu9	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mewfs6jhoaowaf4	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Pack	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:14:45+01	2026-02-03 16:14:45+01
adtpzjhvnpq34hbht	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mewfs6jhoaowaf4	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Pack	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:14:46+01	2026-02-03 16:14:46+01
adtes866qa6q67dhb	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mewfs6jhoaowaf4	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Pack	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:14:46+01	2026-02-03 16:14:46+01
adtz541hv5flv04i2	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mewfs6jhoaowaf4	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Pack	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:18:21+01	2026-02-03 16:18:21+01
adt63kv7mn49801uf	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mewfs6jhoaowaf4	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Pack	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:18:48+01	2026-02-03 16:18:48+01
adt2ovjbn4lajvmqw	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mewfs6jhoaowaf4	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Pack	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:27:09+01	2026-02-03 16:27:09+01
adtc9ajij1u4fkxzr	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mewfs6jhoaowaf4	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Pack	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:27:10+01	2026-02-03 16:27:10+01
adtxvqj9ugb60qooe	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mewfs6jhoaowaf4	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Pack	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:27:10+01	2026-02-03 16:27:10+01
adtj79zpsundpngpn	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mewfs6jhoaowaf4	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Pack	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:30:30+01	2026-02-03 16:30:30+01
adtg9sbhuu8c1558s	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mewfs6jhoaowaf4	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Pack	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:30:30+01	2026-02-03 16:30:30+01
adtvsdcgt70ds3xb4	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mewfs6jhoaowaf4	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Pack	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:30:30+01	2026-02-03 16:30:30+01
adt4h7xobne41is5x	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mewfs6jhoaowaf4	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Pack	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:30:31+01	2026-02-03 16:30:31+01
adt9qk0g7rmpi4zou	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mewfs6jhoaowaf4	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Pack	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:30:31+01	2026-02-03 16:30:31+01
adttbxxy7xxhvcl6w	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mewfs6jhoaowaf4	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Pack	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:30:32+01	2026-02-03 16:30:32+01
adtpsx1amtgl133yr	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mewfs6jhoaowaf4	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Pack	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:30:32+01	2026-02-03 16:30:32+01
adtjkuff4401yq446	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Research_Snapshot with alias ResearchSnapshot  	\N	2026-02-03 22:38:38+01	2026-02-03 22:38:38+01
adtkwau8g7i9qwy6v	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mewfs6jhoaowaf4	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Pack	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:30:33+01	2026-02-03 16:30:33+01
adt7bu1rmrtfqk1lf	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mewfs6jhoaowaf4	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Pack	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:30:33+01	2026-02-03 16:30:33+01
adt5zfm93gk6qipb2	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mewfs6jhoaowaf4	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Pack	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:30:34+01	2026-02-03 16:30:34+01
adt07sfjiohsmpow5	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mewfs6jhoaowaf4	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Pack	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:30:35+01	2026-02-03 16:30:35+01
adthjcaa4894894ep	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mewfs6jhoaowaf4	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Pack	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:30:35+01	2026-02-03 16:30:35+01
adtjmo1y8gafqbhuo	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mewfs6jhoaowaf4	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Pack	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:30:35+01	2026-02-03 16:30:35+01
adtz3qfimgp6n1cc0	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mewfs6jhoaowaf4	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Pack	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:30:37+01	2026-02-03 16:30:37+01
adtrup2wkw6cxwyfv	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mewfs6jhoaowaf4	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Pack	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:30:37+01	2026-02-03 16:30:37+01
adtieboeaedsewllk	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:30:39+01	2026-02-03 16:30:39+01
adtpkbrbcpa4zzwka	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:30:39+01	2026-02-03 16:30:39+01
adt5x8uqracs4ztcj	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:30:40+01	2026-02-03 16:30:40+01
adt4jrokl3lgjthd7	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:30:41+01	2026-02-03 16:30:41+01
adtm13mu9veq1jt81	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:30:41+01	2026-02-03 16:30:41+01
adt8ssypz599w2mnk	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:30:42+01	2026-02-03 16:30:42+01
adtwqc5c0563n8nbn	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:30:43+01	2026-02-03 16:30:43+01
adth7b9glwlkzxeyk	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:30:44+01	2026-02-03 16:30:44+01
adt1ak1ksqctycan6	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:30:44+01	2026-02-03 16:30:44+01
adti4io21naea9yh2	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:30:45+01	2026-02-03 16:30:45+01
adtbjpvc2x6lu7xfi	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:30:46+01	2026-02-03 16:30:46+01
adtc81geksp7gnsb8	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:30:49+01	2026-02-03 16:30:49+01
adtssgzliwijh9umn	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:30:49+01	2026-02-03 16:30:49+01
adtzbiod70t9yegrw	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:30:50+01	2026-02-03 16:30:50+01
adt3j0dyc59qcx9fs	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:30:51+01	2026-02-03 16:30:51+01
adt1di4t51av0yrsz	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:30:51+01	2026-02-03 16:30:51+01
adt1iu6jzlf9fzkt6	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:30:52+01	2026-02-03 16:30:52+01
adt3iho0mcy326k9e	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:30:53+01	2026-02-03 16:30:53+01
adth9f7k6f5z2k2ic	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:30:54+01	2026-02-03 16:30:54+01
adtmgz9kom8v4lwoz	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:30:54+01	2026-02-03 16:30:54+01
adtpq1u2dvijtvfbc	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:30:55+01	2026-02-03 16:30:55+01
adt08jmgky7uipabl	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:30:56+01	2026-02-03 16:30:56+01
adt489e7b0cmhkg79	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:30:57+01	2026-02-03 16:30:57+01
adtxe8os9w33pqfps	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mewfs6jhoaowaf4	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Pack	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:30:33+01	2026-02-03 16:30:33+01
adtxa99orov2gvqm7	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mewfs6jhoaowaf4	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Pack	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:30:34+01	2026-02-03 16:30:34+01
adt0fs6uvgguiyczt	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mewfs6jhoaowaf4	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Pack	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:30:36+01	2026-02-03 16:30:36+01
adtt1q2pzltoia2qg	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mewfs6jhoaowaf4	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Pack	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:30:36+01	2026-02-03 16:30:36+01
adt70fivp3jcgx194	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mewfs6jhoaowaf4	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Pack	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:30:37+01	2026-02-03 16:30:37+01
adt3w29klf70mwbk3	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mewfs6jhoaowaf4	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Pack	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:30:38+01	2026-02-03 16:30:38+01
adtrwy6863ajb0r6x	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:30:38+01	2026-02-03 16:30:38+01
adt3m3mboi7s3zb41	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:30:40+01	2026-02-03 16:30:40+01
adt81ag7u1cmcmyx5	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:30:40+01	2026-02-03 16:30:40+01
adtpde5ijdm97jzvy	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:30:42+01	2026-02-03 16:30:42+01
adtd25nj27rxos0x2	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:30:43+01	2026-02-03 16:30:43+01
adtdm15noc6ldnf7f	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:30:43+01	2026-02-03 16:30:43+01
adtnsl5ik79h25aj7	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:30:45+01	2026-02-03 16:30:45+01
adtzoz0xnl4l4aprl	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:30:45+01	2026-02-03 16:30:45+01
adtvppzc4bz5085i9	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:30:46+01	2026-02-03 16:30:46+01
adt7nsxdit4osrfme	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:30:47+01	2026-02-03 16:30:47+01
adtz2ms4mc3vlqo0a	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:30:47+01	2026-02-03 16:30:47+01
adtr811vtezg7txp0	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:30:50+01	2026-02-03 16:30:50+01
adtavs5qikapkvh5a	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:30:50+01	2026-02-03 16:30:50+01
adtubxntrw9zuostb	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:30:52+01	2026-02-03 16:30:52+01
adt7ehd0kk0vz5xci	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:30:52+01	2026-02-03 16:30:52+01
adt50gkfrfqqr46j0	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:30:53+01	2026-02-03 16:30:53+01
adtnsun9iw8a361kz	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:30:55+01	2026-02-03 16:30:55+01
adt7d95xvttl9r325	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:30:55+01	2026-02-03 16:30:55+01
adts0xl377wphna42	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:30:56+01	2026-02-03 16:30:56+01
adt7kyr745fxv26k9	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:30:57+01	2026-02-03 16:30:57+01
adt44l8c0jvq459ko	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:30:58+01	2026-02-03 16:30:58+01
adtc1uepvg4a2tfao	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:30:59+01	2026-02-03 16:30:59+01
adtgxckhn5k35v9eq	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:31:00+01	2026-02-03 16:31:00+01
adtg8l03hf1kezf2s	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:31:02+01	2026-02-03 16:31:02+01
adt8hu76hd3um1tv7	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:31:02+01	2026-02-03 16:31:02+01
adt206c83xnpngymq	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:31:03+01	2026-02-03 16:31:03+01
adtouf7u9qh4k92a2	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:30:57+01	2026-02-03 16:30:57+01
adt39vuawvzdyxzr9	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:30:58+01	2026-02-03 16:30:58+01
adt6ds96chen0beg4	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:30:59+01	2026-02-03 16:30:59+01
adt6yv1brwnzqeybq	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:31:00+01	2026-02-03 16:31:00+01
adt210ksomys06a9x	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:31:00+01	2026-02-03 16:31:00+01
adtxr8k8ccsvbq95e	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:31:01+01	2026-02-03 16:31:01+01
adte6zlg6azbt8pof	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:31:01+01	2026-02-03 16:31:01+01
adtt22zeh1mx9jib1	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:31:02+01	2026-02-03 16:31:02+01
adtemqvaonco4u6mv	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:31:03+01	2026-02-03 16:31:03+01
adtxt4v8qxcs4rkb2	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:31:04+01	2026-02-03 16:31:04+01
adtha91xdiv645wdz	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:31:05+01	2026-02-03 16:31:05+01
adtn19sjj9lzgy1vh	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:31:06+01	2026-02-03 16:31:06+01
adt0zxnltvpo6n1va	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:31:04+01	2026-02-03 16:31:04+01
adthpsvvjk519bpad	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:31:05+01	2026-02-03 16:31:05+01
adtvslr92enyhxy64	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:31:05+01	2026-02-03 16:31:05+01
adttlv5amgdaf6e9y	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:31:06+01	2026-02-03 16:31:06+01
adtxsodj0e4xr7r7b	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:31:07+01	2026-02-03 16:31:07+01
adtm1ezen1wp34mrn	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:31:07+01	2026-02-03 16:31:07+01
adt8cuowkr7pf0d8y	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:31:07+01	2026-02-03 16:31:07+01
adtca63b2rfkj2127	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:31:08+01	2026-02-03 16:31:08+01
adtm086srf7tkolj4	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:31:09+01	2026-02-03 16:31:09+01
adt6b818ejfd7cfe4	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:31:10+01	2026-02-03 16:31:10+01
adt4wk6uqdjha9y7o	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:31:10+01	2026-02-03 16:31:10+01
adt7t14wzb1hc9mwg	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:31:11+01	2026-02-03 16:31:11+01
adtpj8y8c4kotcb3i	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:31:11+01	2026-02-03 16:31:11+01
adt15e02m6dbxuze6	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:31:11+01	2026-02-03 16:31:11+01
adt5n1w7ka543uf0p	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:31:12+01	2026-02-03 16:31:12+01
adtrmk7rw18glzecu	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:31:12+01	2026-02-03 16:31:12+01
adtrk387ilog81joe	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:31:13+01	2026-02-03 16:31:13+01
adtky492u880ix9js	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:31:13+01	2026-02-03 16:31:13+01
adt4ztmaxz31qb8ko	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:31:14+01	2026-02-03 16:31:14+01
adtion4vkavixgwrp	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:31:14+01	2026-02-03 16:31:14+01
adtapufle0sezm8t1	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:31:14+01	2026-02-03 16:31:14+01
adtn03jvnvx19n6b6	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:31:15+01	2026-02-03 16:31:15+01
adtlb5ft1z21goxas	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	\N	2026-02-03 16:31:15+01	2026-02-03 16:31:15+01
adt56t6ebigc9x8b0	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:16+01	2026-02-03 16:31:16+01
adtya18qzgg76hc0w	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:16+01	2026-02-03 16:31:16+01
adtxngab4b5ljgof3	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:17+01	2026-02-03 16:31:17+01
adt4i92maxk1d8t3h	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:17+01	2026-02-03 16:31:17+01
adtgtf3mspiinqtss	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:17+01	2026-02-03 16:31:17+01
adt8t3u0gdy9469zt	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:18+01	2026-02-03 16:31:18+01
adtu5xulz36g79itr	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:18+01	2026-02-03 16:31:18+01
adt0daxsf57y6bclo	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column lead with alias lead from table nc_jmsd___Research_Snapshot has been deleted	\N	2026-02-03 22:38:38+01	2026-02-03 22:38:38+01
adts0g7njxfw093xl	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:19+01	2026-02-03 16:31:19+01
adty0iltx1aab7tlh	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:20+01	2026-02-03 16:31:20+01
adtxo1919w4iw8xok	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:21+01	2026-02-03 16:31:21+01
adt9b2pot20yg0le2	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:22+01	2026-02-03 16:31:22+01
adt55h8t7oup2k9ah	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:23+01	2026-02-03 16:31:23+01
adtm67qh0quof594y	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:24+01	2026-02-03 16:31:24+01
adtq60jz4hystoi71	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:25+01	2026-02-03 16:31:25+01
adtecd4kpcojm11y0	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:26+01	2026-02-03 16:31:26+01
adtl1r840jbm89m2h	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:27+01	2026-02-03 16:31:27+01
adtuzte8u9e1ih92l	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:28+01	2026-02-03 16:31:28+01
adty2wezcxt8k1bq4	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:30+01	2026-02-03 16:31:30+01
adtmrjkpx55l9a82s	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:30+01	2026-02-03 16:31:30+01
adt3upjjzl3eldvk1	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:31+01	2026-02-03 16:31:31+01
adt97c6l6xvcp8iwh	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:31+01	2026-02-03 16:31:31+01
adtn146jxwu91cgwj	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:32+01	2026-02-03 16:31:32+01
adteot9nz3zrli77l	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:33+01	2026-02-03 16:31:33+01
adt3l0ms7mu8ew8e3	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:34+01	2026-02-03 16:31:34+01
adtr9gdwwy4up9gje	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:34+01	2026-02-03 16:31:34+01
adtaplhtnfrmyao7m	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:35+01	2026-02-03 16:31:35+01
adttkhw58947s7uau	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:36+01	2026-02-03 16:31:36+01
adtxm10lw0b1omfp4	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:37+01	2026-02-03 16:31:37+01
adt0zp6z8v3kcsog4	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:38+01	2026-02-03 16:31:38+01
adt6mowaadqa2pp48	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:39+01	2026-02-03 16:31:39+01
adtmmzs2acu0op0ki	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:19+01	2026-02-03 16:31:19+01
adtvwqdivyew62c96	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:19+01	2026-02-03 16:31:19+01
adtaiywg388xgmkbc	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:20+01	2026-02-03 16:31:20+01
adtnnz1kxjdlhm55g	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:21+01	2026-02-03 16:31:21+01
adtklyymcbi29yqn0	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:22+01	2026-02-03 16:31:22+01
adth46g8va2w3jlch	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:22+01	2026-02-03 16:31:22+01
adtbgk3rzmwuvbkye	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:23+01	2026-02-03 16:31:23+01
adtilwstrgd4yhlm6	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:24+01	2026-02-03 16:31:24+01
adtvyy1360hgipa0n	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:25+01	2026-02-03 16:31:25+01
adtdpgr1bywgifp8p	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:25+01	2026-02-03 16:31:25+01
adtygwhhbn6b6n86h	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:26+01	2026-02-03 16:31:26+01
adtz361srd5yaupyd	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:27+01	2026-02-03 16:31:27+01
adtc3ui25wbbx179a	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:28+01	2026-02-03 16:31:28+01
adtjf3dr1qlh7ofwd	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:28+01	2026-02-03 16:31:28+01
adtsu8do5yp82ay2n	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:31+01	2026-02-03 16:31:31+01
adt7l9gkpm9q9bjm0	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:32+01	2026-02-03 16:31:32+01
adto5vwdkvbq9kpjm	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:33+01	2026-02-03 16:31:33+01
adtm2useox39hwa68	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:34+01	2026-02-03 16:31:34+01
adtnwrydbs0nmw9t8	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:35+01	2026-02-03 16:31:35+01
adtagn72i14nusjyz	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:36+01	2026-02-03 16:31:36+01
adt0zqrq5a2bf5vtz	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:36+01	2026-02-03 16:31:36+01
adtpokh1yhzozujzk	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:37+01	2026-02-03 16:31:37+01
adtmz2kf42at00dab	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:38+01	2026-02-03 16:31:38+01
adt83b2xhnxg1yc78	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:39+01	2026-02-03 16:31:39+01
adt22fchnu3fccdtj	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:40+01	2026-02-03 16:31:40+01
adtygn6gk5orc3lbw	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:41+01	2026-02-03 16:31:41+01
adt2q213ffdj32l2j	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:42+01	2026-02-03 16:31:42+01
adt84m7io4samiq4o	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:39+01	2026-02-03 16:31:39+01
adttp0fb45krbr2ap	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:40+01	2026-02-03 16:31:40+01
adtm8if823y0hot38	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:41+01	2026-02-03 16:31:41+01
adtnf4i730c2iy9ug	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:42+01	2026-02-03 16:31:42+01
adtnuto78v8l69yiu	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:42+01	2026-02-03 16:31:42+01
adt1c276zr05du205	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb3lg405sgfbuea	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table MessageTemplate	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:31:43+01	2026-02-03 16:31:43+01
adt9tkreqpnjab2j6	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mewfs6jhoaowaf4	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Pack	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:44:29+01	2026-02-03 16:44:29+01
adts3o2b8sie7fdxm	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mewfs6jhoaowaf4	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Pack	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:44:29+01	2026-02-03 16:44:29+01
adtamvdtui4foi0o9	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mewfs6jhoaowaf4	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Pack	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:44:30+01	2026-02-03 16:44:30+01
adtjj06w6o1i4avsn	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mewfs6jhoaowaf4	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Pack	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:45:10+01	2026-02-03 16:45:10+01
adtqhdxfy9brlabpq	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mewfs6jhoaowaf4	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Pack	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:45:10+01	2026-02-03 16:45:10+01
adt955d09szxwm3v7	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mewfs6jhoaowaf4	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Pack	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:45:11+01	2026-02-03 16:45:11+01
adtwlbqrztir271ti	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mewfs6jhoaowaf4	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Pack	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:50:03+01	2026-02-03 16:50:03+01
adt50o5zso3ma150m	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mewfs6jhoaowaf4	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Pack	<span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">false</span>	2026-02-03 16:58:15+01	2026-02-03 16:58:15+01
adtflsh7j3c99dsiz	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mewfs6jhoaowaf4	\N	DATA	BULK_INSERT	\N	3 records have been bulk inserted in Pack	\N	2026-02-03 17:09:17+01	2026-02-03 17:09:17+01
adt00gsxtsnfuj2yw	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m3c1gct1b0z5swu	\N	DATA	BULK_INSERT	\N	15 records have been bulk inserted in Lead	\N	2026-02-03 17:09:17+01	2026-02-03 17:09:17+01
adtadpszytxgibqd3	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	muyr6z1znpv90if	\N	DATA	BULK_INSERT	\N	1 record has been bulk inserted in Segment	\N	2026-02-03 17:17:23+01	2026-02-03 17:17:23+01
adtozn8mfqxboq72h	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m3c1gct1b0z5swu	\N	DATA	BULK_INSERT	\N	15 records have been bulk inserted in Lead	\N	2026-02-03 17:17:24+01	2026-02-03 17:17:24+01
adtixbwnfck6yghwh	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Pack with alias Pack  	\N	2026-02-03 22:38:15+01	2026-02-03 22:38:15+01
adtuezje2a6be513p	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column pack with alias pack from table nc_jmsd___Segment has been deleted	\N	2026-02-03 22:38:19+01	2026-02-03 22:38:19+01
adtgjcvnwyhfsrh74	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Segment with alias Segment  	\N	2026-02-03 22:38:19+01	2026-02-03 22:38:19+01
adtfqo5nx1bkvwexa	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Company with alias Company  	\N	2026-02-03 22:38:24+01	2026-02-03 22:38:24+01
adt341pfrri77j1mc	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column company with alias company from table nc_jmsd___Lead has been deleted	\N	2026-02-03 22:38:29+01	2026-02-03 22:38:29+01
adtntx77ek3ceqwqw	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column pack_candidate with alias pack_candidate from table nc_jmsd___Lead has been deleted	\N	2026-02-03 22:38:29+01	2026-02-03 22:38:29+01
adtickjuzvuiv3cam	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column segment with alias segment from table nc_jmsd___Lead has been deleted	\N	2026-02-03 22:38:29+01	2026-02-03 22:38:29+01
adtx22c2ilazmw9e9	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Lead with alias Lead  	\N	2026-02-03 22:38:29+01	2026-02-03 22:38:29+01
adtywkib36sxchter	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column lead with alias lead from table nc_jmsd___Attempt has been deleted	\N	2026-02-03 22:38:33+01	2026-02-03 22:38:33+01
adt0r0mzdgz8froeh	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Attempt with alias Attempt  	\N	2026-02-03 22:38:33+01	2026-02-03 22:38:33+01
adtg6ajpy5wwh2ncv	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column company with alias company from table nc_jmsd___Research_Snapshot has been deleted	\N	2026-02-03 22:38:38+01	2026-02-03 22:38:38+01
adt025nf0qzxkt18x	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column pack with alias pack from table nc_jmsd___Message_Template has been deleted	\N	2026-02-03 22:38:43+01	2026-02-03 22:38:43+01
adtcw9h2km579kzlm	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column segment with alias segment from table nc_jmsd___Message_Template has been deleted	\N	2026-02-03 22:38:43+01	2026-02-03 22:38:43+01
adt92qvea8o3rymta	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Message_Template with alias MessageTemplate  	\N	2026-02-03 22:38:43+01	2026-02-03 22:38:43+01
adtmqtn0t12p6srzw	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column lead with alias lead from table nc_jmsd___Approval has been deleted	\N	2026-02-03 22:38:48+01	2026-02-03 22:38:48+01
adtfcwh58m7boau89	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column template with alias template from table nc_jmsd___Approval has been deleted	\N	2026-02-03 22:38:48+01	2026-02-03 22:38:48+01
adtedud15jxja6m5r	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Approval with alias Approval  	\N	2026-02-03 22:38:48+01	2026-02-03 22:38:48+01
adt2hvxmgvqdhqcww	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column lead with alias lead from table nc_jmsd___Conversation has been deleted	\N	2026-02-03 22:38:51+01	2026-02-03 22:38:51+01
adtpflgjfidx3jacp	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Conversation with alias Conversation  	\N	2026-02-03 22:38:52+01	2026-02-03 22:38:52+01
adttf2wri9htdjioi	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column lead with alias lead from table nc_jmsd___Outcome has been deleted	\N	2026-02-03 22:38:56+01	2026-02-03 22:38:56+01
adta5sc6vsvbh9nl2	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column package_recommended with alias package_recommended from table nc_jmsd___Outcome has been deleted	\N	2026-02-03 22:38:56+01	2026-02-03 22:38:56+01
adt04hlba6oex877i	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Outcome with alias Outcome  	\N	2026-02-03 22:38:56+01	2026-02-03 22:38:56+01
adtusos26v6nz0lpp	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Pack with alias Pack has been created	\N	2026-02-03 22:39:42+01	2026-02-03 22:39:42+01
adtat04elxe740613	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Segment with alias Segment has been created	\N	2026-02-03 22:39:42+01	2026-02-03 22:39:42+01
adtif9cvp7c9r1la8	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Company with alias Company has been created	\N	2026-02-03 22:39:42+01	2026-02-03 22:39:42+01
adtjxnq1a21pvmuvn	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Lead with alias Lead has been created	\N	2026-02-03 22:39:42+01	2026-02-03 22:39:42+01
adtujk6b75mw8bjzx	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Attempt with alias Attempt has been created	\N	2026-02-03 22:39:42+01	2026-02-03 22:39:42+01
adtckg6t1d09r24ke	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Research_Snapshot with alias ResearchSnapshot has been created	\N	2026-02-03 22:39:42+01	2026-02-03 22:39:42+01
adtbihy2v8s7artow	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Message_Template with alias MessageTemplate has been created	\N	2026-02-03 22:39:43+01	2026-02-03 22:39:43+01
adtocjnp2tpqokmsx	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Approval with alias Approval has been created	\N	2026-02-03 22:39:43+01	2026-02-03 22:39:43+01
adtnhmm7g3bb26ix8	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Conversation with alias Conversation has been created	\N	2026-02-03 22:39:43+01	2026-02-03 22:39:43+01
adtm4hru2qlvx1poj	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Outcome with alias Outcome has been created	\N	2026-02-03 22:39:43+01	2026-02-03 22:39:43+01
adtpgr3c5zdxeb6we	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___TEST_Company_Final with alias TestCompanyFinal has been created	\N	2026-02-03 22:40:21+01	2026-02-03 22:40:21+01
adtqe91dfkn1qcq4i	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___TEST_Lead_Final with alias TestLeadFinal has been created	\N	2026-02-03 22:40:21+01	2026-02-03 22:40:21+01
adt08a3rwbialoo3s	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Pack with alias Pack  	\N	2026-02-03 22:47:58+01	2026-02-03 22:47:58+01
adthxfpzd4u4o6gt8	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column pack with alias pack from table nc_jmsd___Segment has been deleted	\N	2026-02-03 22:48:02+01	2026-02-03 22:48:02+01
adtseoqmbqt220jes	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Segment with alias Segment  	\N	2026-02-03 22:48:02+01	2026-02-03 22:48:02+01
adt9c7j4pworr159a	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Company with alias Company  	\N	2026-02-03 22:48:07+01	2026-02-03 22:48:07+01
adt22vfsrb8nryy4w	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column company with alias company from table nc_jmsd___Lead has been deleted	\N	2026-02-03 22:48:11+01	2026-02-03 22:48:11+01
adt33t7sjauhcnw5o	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column pack_candidate with alias pack_candidate from table nc_jmsd___Lead has been deleted	\N	2026-02-03 22:48:11+01	2026-02-03 22:48:11+01
adtx8kdy9p4fed1si	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column segment with alias segment from table nc_jmsd___Lead has been deleted	\N	2026-02-03 22:48:11+01	2026-02-03 22:48:11+01
adttuqtk7i41nxdf3	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Lead with alias Lead  	\N	2026-02-03 22:48:11+01	2026-02-03 22:48:11+01
adti4omp0i81q538i	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column lead with alias lead from table nc_jmsd___Attempt has been deleted	\N	2026-02-03 22:48:15+01	2026-02-03 22:48:15+01
adtodaeco65607tzf	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Attempt with alias Attempt  	\N	2026-02-03 22:48:15+01	2026-02-03 22:48:15+01
adt4k77n9thptl9g5	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column lead with alias lead from table nc_jmsd___Research_Snapshot has been deleted	\N	2026-02-03 22:49:49+01	2026-02-03 22:49:49+01
adt8e36aabwf3uyvo	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column company with alias company from table nc_jmsd___Research_Snapshot has been deleted	\N	2026-02-03 22:49:49+01	2026-02-03 22:49:49+01
adtwzhwkmojrtp0hj	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Research_Snapshot with alias ResearchSnapshot  	\N	2026-02-03 22:49:49+01	2026-02-03 22:49:49+01
adt7y8j5xwv3299ii	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column pack with alias pack from table nc_jmsd___Message_Template has been deleted	\N	2026-02-03 22:49:54+01	2026-02-03 22:49:54+01
adt2f4dh49buxd6sn	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column segment with alias segment from table nc_jmsd___Message_Template has been deleted	\N	2026-02-03 22:49:54+01	2026-02-03 22:49:54+01
adttbu13zo0njikc0	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Message_Template with alias MessageTemplate  	\N	2026-02-03 22:49:54+01	2026-02-03 22:49:54+01
adt7jlq37bpmt0m55	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column lead with alias lead from table nc_jmsd___Approval has been deleted	\N	2026-02-03 22:49:59+01	2026-02-03 22:49:59+01
adtvizq7lwnm08l8d	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column template with alias template from table nc_jmsd___Approval has been deleted	\N	2026-02-03 22:49:59+01	2026-02-03 22:49:59+01
adts0gx4twdiz32wh	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Approval with alias Approval  	\N	2026-02-03 22:49:59+01	2026-02-03 22:49:59+01
adtu75vlsyk8j4gr1	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column lead with alias lead from table nc_jmsd___Conversation has been deleted	\N	2026-02-03 22:50:04+01	2026-02-03 22:50:04+01
adt7beqkvtdu7y0vt	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Conversation with alias Conversation  	\N	2026-02-03 22:50:04+01	2026-02-03 22:50:04+01
adtx5moutmahv2vit	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column lead with alias lead from table nc_jmsd___Outcome has been deleted	\N	2026-02-03 22:50:08+01	2026-02-03 22:50:08+01
adt58rk2irwdzksc9	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column package_recommended with alias package_recommended from table nc_jmsd___Outcome has been deleted	\N	2026-02-03 22:50:08+01	2026-02-03 22:50:08+01
adt51ng3dsccig4zc	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Outcome with alias Outcome  	\N	2026-02-03 22:50:08+01	2026-02-03 22:50:08+01
adtu43o5bic0943xg	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___TEST_Company_Final with alias TestCompanyFinal  	\N	2026-02-03 22:50:13+01	2026-02-03 22:50:13+01
adtlamwgr7p9gikgm	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column Empresa_Id with alias Empresa_Id from table nc_jmsd___TEST_Lead_Final has been deleted	\N	2026-02-03 22:50:22+01	2026-02-03 22:50:22+01
adt0d8y5cykfs74on	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___TEST_Lead_Final with alias TestLeadFinal  	\N	2026-02-03 22:50:22+01	2026-02-03 22:50:22+01
adt3z5s7e2nfvl9ck	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Pack with alias Pack has been created	\N	2026-02-03 22:51:17+01	2026-02-03 22:51:17+01
adtxs7z2hjs7jezv8	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Segment with alias Segment has been created	\N	2026-02-03 22:51:17+01	2026-02-03 22:51:17+01
adt9pvcniofn3x2f8	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Company with alias Company has been created	\N	2026-02-03 22:51:17+01	2026-02-03 22:51:17+01
adt6bk6y4waz3vi8z	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Lead with alias Lead has been created	\N	2026-02-03 22:51:17+01	2026-02-03 22:51:17+01
adttq6y6107srxrxc	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Attempt with alias Attempt has been created	\N	2026-02-03 22:51:17+01	2026-02-03 22:51:17+01
adt7a4uyepwet174t	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Research_Snapshot with alias ResearchSnapshot has been created	\N	2026-02-03 22:51:18+01	2026-02-03 22:51:18+01
adtf2cld3ololht3a	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Message_Template with alias MessageTemplate has been created	\N	2026-02-03 22:51:18+01	2026-02-03 22:51:18+01
adtyuhfkrzw7ytu3z	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Approval with alias Approval has been created	\N	2026-02-03 22:51:18+01	2026-02-03 22:51:18+01
adtkkwe30p6vff5z0	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Conversation with alias Conversation has been created	\N	2026-02-03 22:51:18+01	2026-02-03 22:51:18+01
adte8iqmqbrjjz06x	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Outcome with alias Outcome has been created	\N	2026-02-03 22:51:18+01	2026-02-03 22:51:18+01
adtayl4is4yw73t8i	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Pack with alias Pack  	\N	2026-02-03 22:56:16+01	2026-02-03 22:56:16+01
adt0zjfxu9kqbulm7	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Segment with alias Segment  	\N	2026-02-03 22:56:21+01	2026-02-03 22:56:21+01
adt2wuk2j2vfrtmrw	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Company with alias Company  	\N	2026-02-03 22:56:25+01	2026-02-03 22:56:25+01
adtnh6u86wc7jqlcd	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Lead with alias Lead  	\N	2026-02-03 22:56:29+01	2026-02-03 22:56:29+01
adtsr4bai5tob3725	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Attempt with alias Attempt  	\N	2026-02-03 22:56:35+01	2026-02-03 22:56:35+01
adt5y7eol3ok5w4fc	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Research_Snapshot with alias ResearchSnapshot  	\N	2026-02-03 22:56:39+01	2026-02-03 22:56:39+01
adt4suzsvl5c9hy3c	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Message_Template with alias MessageTemplate  	\N	2026-02-03 22:56:43+01	2026-02-03 22:56:43+01
adtmf2ui6vk9m64sy	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Approval with alias Approval  	\N	2026-02-03 22:56:48+01	2026-02-03 22:56:48+01
adtl7jri3vzspf7xg	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Conversation with alias Conversation  	\N	2026-02-03 22:56:52+01	2026-02-03 22:56:52+01
adtar35jzwbjrb98v	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Outcome with alias Outcome  	\N	2026-02-03 22:56:58+01	2026-02-03 22:56:58+01
adt6e6hvnxa8c1gm9	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Pack with alias Pack has been created	\N	2026-02-03 22:58:47+01	2026-02-03 22:58:47+01
adt45dlqi3tmpp46w	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Company with alias Company has been created	\N	2026-02-03 22:58:48+01	2026-02-03 22:58:48+01
adtcv9nshor3swg2z	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Segment with alias Segment has been created	\N	2026-02-03 22:58:48+01	2026-02-03 22:58:48+01
adthxd41romw6bqw9	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Message_Template with alias MessageTemplate has been created	\N	2026-02-03 22:58:48+01	2026-02-03 22:58:48+01
adtkiwc8vfmj5jwjw	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Lead with alias Lead has been created	\N	2026-02-03 22:58:48+01	2026-02-03 22:58:48+01
adt0jh3j8q71bff6n	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Attempt with alias Attempt has been created	\N	2026-02-03 22:58:48+01	2026-02-03 22:58:48+01
adt8wykzpishz2wc0	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Research_Snapshot with alias ResearchSnapshot has been created	\N	2026-02-03 22:58:48+01	2026-02-03 22:58:48+01
adt39s4zwme0rsbkf	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Approval with alias Approval has been created	\N	2026-02-03 22:58:48+01	2026-02-03 22:58:48+01
adttv81hb2shfu54l	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Conversation with alias Conversation has been created	\N	2026-02-03 22:58:48+01	2026-02-03 22:58:48+01
adtvv355a62346hbk	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Outcome with alias Outcome has been created	\N	2026-02-03 22:58:48+01	2026-02-03 22:58:48+01
adtr3fnrlnxru8488	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mq7of9o76cw5y3a	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Pack	<span class="">PackKey</span>\n          : <span class="black--text green lighten-4 px-2">TEST_V2</span><span class="">Name</span>\n          : <span class="black--text green lighten-4 px-2">Test v2</span><span class="">PriceMin</span>\n          : <span class="black--text green lighten-4 px-2">100</span><span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">true</span>	2026-02-03 23:09:12+01	2026-02-03 23:09:12+01
adt0zpy19g55gbj56	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mq7of9o76cw5y3a	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Pack	<span class="">PackKey</span>\n          : <span class="black--text green lighten-4 px-2">TEST_V2</span><span class="">Name</span>\n          : <span class="black--text green lighten-4 px-2">Test v2</span><span class="">PriceMin</span>\n          : <span class="black--text green lighten-4 px-2">100</span><span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">true</span>	2026-02-03 23:10:28+01	2026-02-03 23:10:28+01
adty7y6fsuhxmnx9i	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Pack with alias Pack  	\N	2026-02-03 23:15:32+01	2026-02-03 23:15:32+01
adtktswgr94qr9jcn	gestionads15.21@gmail.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column pack with alias pack from table nc_jmsd___Segment has been deleted	\N	2026-02-03 23:15:32+01	2026-02-03 23:15:32+01
adt9oyb9wywthuz9l	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Segment with alias Segment  	\N	2026-02-03 23:15:32+01	2026-02-03 23:15:32+01
adthofnljkrywfjny	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Company with alias Company  	\N	2026-02-03 23:15:32+01	2026-02-03 23:15:32+01
adtf5s0mv0arq6dup	gestionads15.21@gmail.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column company with alias company from table nc_jmsd___Lead has been deleted	\N	2026-02-03 23:15:32+01	2026-02-03 23:15:32+01
adtnq3yt222hrhdk8	gestionads15.21@gmail.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column pack_candidate with alias pack_candidate from table nc_jmsd___Lead has been deleted	\N	2026-02-03 23:15:32+01	2026-02-03 23:15:32+01
adtj7suv7fbolaw2k	gestionads15.21@gmail.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column segment with alias segment from table nc_jmsd___Lead has been deleted	\N	2026-02-03 23:15:32+01	2026-02-03 23:15:32+01
adtnlo2gjbbpa0u3z	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Lead with alias Lead  	\N	2026-02-03 23:15:32+01	2026-02-03 23:15:32+01
adt0dkq6ig4rh0jm2	gestionads15.21@gmail.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column lead with alias lead from table nc_jmsd___Attempt has been deleted	\N	2026-02-03 23:15:32+01	2026-02-03 23:15:32+01
adtrcd3x17ozb6mvu	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Attempt with alias Attempt  	\N	2026-02-03 23:15:32+01	2026-02-03 23:15:32+01
adtjefr2c8f4cjxeu	gestionads15.21@gmail.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column pack with alias pack from table nc_jmsd___Message_Template has been deleted	\N	2026-02-03 23:15:32+01	2026-02-03 23:15:32+01
adt7gfys9c6igcd01	gestionads15.21@gmail.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column segment with alias segment from table nc_jmsd___Message_Template has been deleted	\N	2026-02-03 23:15:32+01	2026-02-03 23:15:32+01
adtcgwh10fewtt5iy	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Message_Template with alias MessageTemplate  	\N	2026-02-03 23:15:32+01	2026-02-03 23:15:32+01
adtr58mgo6skybb64	gestionads15.21@gmail.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column lead with alias lead from table nc_jmsd___Approval has been deleted	\N	2026-02-03 23:15:32+01	2026-02-03 23:15:32+01
adt0rtg6gq8nbfwau	gestionads15.21@gmail.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column template with alias template from table nc_jmsd___Approval has been deleted	\N	2026-02-03 23:15:32+01	2026-02-03 23:15:32+01
adtneknknkr2gdi4l	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Approval with alias Approval  	\N	2026-02-03 23:15:32+01	2026-02-03 23:15:32+01
adth5z8v9igfoc4xd	gestionads15.21@gmail.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column lead with alias lead from table nc_jmsd___Conversation has been deleted	\N	2026-02-03 23:15:32+01	2026-02-03 23:15:32+01
adtbibh324annsqnt	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Conversation with alias Conversation  	\N	2026-02-03 23:15:32+01	2026-02-03 23:15:32+01
adtclly6thmfayyg5	gestionads15.21@gmail.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column lead with alias lead from table nc_jmsd___Outcome has been deleted	\N	2026-02-03 23:15:32+01	2026-02-03 23:15:32+01
adth3peoxjl365aqi	gestionads15.21@gmail.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column package_recommended with alias package_recommended from table nc_jmsd___Outcome has been deleted	\N	2026-02-03 23:15:32+01	2026-02-03 23:15:32+01
adthwzfilxx6g5i1q	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Outcome with alias Outcome  	\N	2026-02-03 23:15:33+01	2026-02-03 23:15:33+01
adtpisevtcroetg32	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Pack with alias Pack has been created	\N	2026-02-03 23:15:33+01	2026-02-03 23:15:33+01
adtma26vtdtm7bisj	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Company with alias Company has been created	\N	2026-02-03 23:15:33+01	2026-02-03 23:15:33+01
adtd43rbf091f3yr3	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Segment with alias Segment has been created	\N	2026-02-03 23:15:33+01	2026-02-03 23:15:33+01
adtteof7eav3sc5iw	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Message_Template with alias MessageTemplate has been created	\N	2026-02-03 23:15:33+01	2026-02-03 23:15:33+01
adt8z0ytnxa859tpc	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Lead with alias Lead has been created	\N	2026-02-03 23:15:33+01	2026-02-03 23:15:33+01
adtatm4tvz83h0cm9	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Attempt with alias Attempt has been created	\N	2026-02-03 23:15:33+01	2026-02-03 23:15:33+01
adt63evjj7zisnyhp	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column company with alias company from table nc_jmsd___Research_Snapshot has been deleted	\N	2026-02-03 23:16:22+01	2026-02-03 23:16:22+01
adt5dz77fvf7wavzi	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column lead with alias lead from table nc_jmsd___Research_Snapshot has been deleted	\N	2026-02-03 23:16:22+01	2026-02-03 23:16:22+01
adtetqu6051nkptnw	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Research_Snapshot with alias ResearchSnapshot  	\N	2026-02-03 23:16:22+01	2026-02-03 23:16:22+01
adtz5ky1710eitq6b	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Pack with alias Pack  	\N	2026-02-03 23:16:27+01	2026-02-03 23:16:27+01
adtn79njrb7bbqteu	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Company with alias Company  	\N	2026-02-03 23:16:31+01	2026-02-03 23:16:31+01
adtwd30pih4cd62cm	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column pack with alias pack from table nc_jmsd___Segment has been deleted	\N	2026-02-03 23:16:35+01	2026-02-03 23:16:35+01
adtc9izfdxtpey7fp	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Segment with alias Segment  	\N	2026-02-03 23:16:35+01	2026-02-03 23:16:35+01
adta9g9ov5j8ph9n7	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column pack with alias pack from table nc_jmsd___Message_Template has been deleted	\N	2026-02-03 23:16:40+01	2026-02-03 23:16:40+01
adtfaxde06qiezl6l	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column segment with alias segment from table nc_jmsd___Message_Template has been deleted	\N	2026-02-03 23:16:40+01	2026-02-03 23:16:40+01
adt2y649qqfj9a0yt	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Lead with alias Lead has been created	\N	2026-02-03 23:16:56+01	2026-02-03 23:16:56+01
adtmfyyw08asxpysr	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Message_Template with alias MessageTemplate  	\N	2026-02-03 23:16:40+01	2026-02-03 23:16:40+01
adteg5uqr942cian5	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column company with alias company from table nc_jmsd___Lead has been deleted	\N	2026-02-03 23:16:44+01	2026-02-03 23:16:44+01
adtx3cydl5d4cj060	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Message_Template with alias MessageTemplate has been created	\N	2026-02-03 23:16:55+01	2026-02-03 23:16:55+01
adtjv7dy5lmr53xc5	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Outcome with alias Outcome has been created	\N	2026-02-03 23:16:56+01	2026-02-03 23:16:56+01
adte8sggav7a4urpf	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column pack_candidate with alias pack_candidate from table nc_jmsd___Lead has been deleted	\N	2026-02-03 23:16:44+01	2026-02-03 23:16:44+01
adt5hcijlv07m9bhp	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column segment with alias segment from table nc_jmsd___Lead has been deleted	\N	2026-02-03 23:16:44+01	2026-02-03 23:16:44+01
adtfs2o83buqiokb4	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Lead with alias Lead  	\N	2026-02-03 23:16:44+01	2026-02-03 23:16:44+01
adtpw4rgnoopfqpyd	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column lead with alias lead from table nc_jmsd___Attempt has been deleted	\N	2026-02-03 23:16:48+01	2026-02-03 23:16:48+01
adt61lolq83kj5ozp	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Attempt with alias Attempt  	\N	2026-02-03 23:16:48+01	2026-02-03 23:16:48+01
adtex5m74oipjroqm	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Pack with alias Pack has been created	\N	2026-02-03 23:16:55+01	2026-02-03 23:16:55+01
adtbul3exfsaqjrm2	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Company with alias Company has been created	\N	2026-02-03 23:16:55+01	2026-02-03 23:16:55+01
adtg7lsi4haxdie46	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Segment with alias Segment has been created	\N	2026-02-03 23:16:55+01	2026-02-03 23:16:55+01
adt8f70lhohclu3js	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Attempt with alias Attempt has been created	\N	2026-02-03 23:16:56+01	2026-02-03 23:16:56+01
adth9guaaqfjb7fj4	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Research_Snapshot with alias ResearchSnapshot has been created	\N	2026-02-03 23:16:56+01	2026-02-03 23:16:56+01
adt3u6zicuuqvdwlk	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Approval with alias Approval has been created	\N	2026-02-03 23:16:56+01	2026-02-03 23:16:56+01
adttuy59duvpcsg0a	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Conversation with alias Conversation has been created	\N	2026-02-03 23:16:56+01	2026-02-03 23:16:56+01
adt58nx6zu3ie2yjw	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mjq02g79yg81u0q	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Pack	<span class="">PackKey</span>\n          : <span class="black--text green lighten-4 px-2">GUARDIAN</span><span class="">Name</span>\n          : <span class="black--text green lighten-4 px-2">El Guardián</span><span class="">PriceMin</span>\n          : <span class="black--text green lighten-4 px-2">500</span><span class="">PriceMax</span>\n          : <span class="black--text green lighten-4 px-2">800</span><span class="">Description</span>\n          : <span class="black--text green lighten-4 px-2">Soporte operativo y continuidad para empresas sin IT interno.</span><span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">true</span><span class="">IcpRules</span>\n          : <span class="black--text green lighten-4 px-2">{"employees": "1-10", "no_it": true, "owner_non_technical": true}</span><span class="">ScoringWeights</span>\n          : <span class="black--text green lighten-4 px-2">{"fit": 40, "maps": 40, "web": 20}</span>	2026-02-03 23:17:52+01	2026-02-03 23:17:52+01
adtwu5urxafymrjx3	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mnucx6gwisg1vmn	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	<span class="">SegmentKey</span>\n          : <span class="black--text green lighten-4 px-2">BCN_A_LT50REV_GUARDIAN_TEST</span><span class="">Name</span>\n          : <span class="black--text green lighten-4 px-2">BCN A &lt;50 reviews [TEST]</span><span class="">Type</span>\n          : <span class="black--text green lighten-4 px-2">AB_TEST</span><span class="">Status</span>\n          : <span class="black--text green lighten-4 px-2">RUNNING</span><span class="">Definition</span>\n          : <span class="black--text green lighten-4 px-2">{"city": "Barcelona", "reviews_bucket": "LT50", "test": true}</span><span class="">DailyInviteCap</span>\n          : <span class="black--text green lighten-4 px-2">10</span><span class="">Notes</span>\n          : <span class="black--text green lighten-4 px-2">Segmento de test — se puede eliminar.</span>	2026-02-03 23:17:52+01	2026-02-03 23:17:52+01
adt8h6kqnerlizc4l	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Pack with alias Pack  	\N	2026-02-03 23:22:00+01	2026-02-03 23:22:00+01
adt5sh4ydtnqhvfyu	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Company with alias Company  	\N	2026-02-03 23:22:04+01	2026-02-03 23:22:04+01
adtmm3aczzqpws8up	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column pack with alias pack from table nc_jmsd___Segment has been deleted	\N	2026-02-03 23:22:08+01	2026-02-03 23:22:08+01
adtmhbryecofso65w	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Segment with alias Segment  	\N	2026-02-03 23:22:08+01	2026-02-03 23:22:08+01
adt2jhf1m3e36q7c4	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column pack with alias pack from table nc_jmsd___Message_Template has been deleted	\N	2026-02-03 23:22:13+01	2026-02-03 23:22:13+01
adtzu61zowdedz070	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column segment with alias segment from table nc_jmsd___Message_Template has been deleted	\N	2026-02-03 23:22:13+01	2026-02-03 23:22:13+01
adtq58lpaxks4tv1i	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Message_Template with alias MessageTemplate  	\N	2026-02-03 23:22:13+01	2026-02-03 23:22:13+01
adtwntbnk02t6fauz	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column company with alias company from table nc_jmsd___Lead has been deleted	\N	2026-02-03 23:22:17+01	2026-02-03 23:22:17+01
adtjtmx8tmgefy3ty	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column pack_candidate with alias pack_candidate from table nc_jmsd___Lead has been deleted	\N	2026-02-03 23:22:17+01	2026-02-03 23:22:17+01
adtbrccw1nx4gs3gl	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column segment with alias segment from table nc_jmsd___Lead has been deleted	\N	2026-02-03 23:22:17+01	2026-02-03 23:22:17+01
adtc7wj7pnrah2uoe	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Lead with alias Lead  	\N	2026-02-03 23:22:17+01	2026-02-03 23:22:17+01
adt74mnpiw1exo4g5	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column lead with alias lead from table nc_jmsd___Attempt has been deleted	\N	2026-02-03 23:22:21+01	2026-02-03 23:22:21+01
adtyn0ncmdb03e1uw	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Attempt with alias Attempt  	\N	2026-02-03 23:22:21+01	2026-02-03 23:22:21+01
adtxbrr3gtjrfmgbl	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column company with alias company from table nc_jmsd___Research_Snapshot has been deleted	\N	2026-02-03 23:22:25+01	2026-02-03 23:22:25+01
adtuofl6a4e1nocmj	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column lead with alias lead from table nc_jmsd___Research_Snapshot has been deleted	\N	2026-02-03 23:22:25+01	2026-02-03 23:22:25+01
adtia73umuozlfxda	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Research_Snapshot with alias ResearchSnapshot  	\N	2026-02-03 23:22:25+01	2026-02-03 23:22:25+01
adtg0igko1l5t3k4l	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column lead with alias lead from table nc_jmsd___Approval has been deleted	\N	2026-02-03 23:22:29+01	2026-02-03 23:22:29+01
adtjh7fy6fczveoc6	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column template with alias template from table nc_jmsd___Approval has been deleted	\N	2026-02-03 23:22:29+01	2026-02-03 23:22:29+01
adt6gcr5nyukpxjlu	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Approval with alias Approval  	\N	2026-02-03 23:22:29+01	2026-02-03 23:22:29+01
adtsfzf75rg9y2wb5	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column lead with alias lead from table nc_jmsd___Conversation has been deleted	\N	2026-02-03 23:22:33+01	2026-02-03 23:22:33+01
adtr88uvv12vmv6xc	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Conversation with alias Conversation  	\N	2026-02-03 23:22:33+01	2026-02-03 23:22:33+01
adtm1ebjljdmpdoie	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column lead with alias lead from table nc_jmsd___Outcome has been deleted	\N	2026-02-03 23:22:37+01	2026-02-03 23:22:37+01
adtpi6oa1j9edhgfy	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column package_recommended with alias package_recommended from table nc_jmsd___Outcome has been deleted	\N	2026-02-03 23:22:37+01	2026-02-03 23:22:37+01
adthz7qdhpfmofcfv	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Outcome with alias Outcome  	\N	2026-02-03 23:22:37+01	2026-02-03 23:22:37+01
adtsnkqgbzk06tzo1	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Pack with alias Pack has been created	\N	2026-02-03 23:23:27+01	2026-02-03 23:23:27+01
adtxug3en0y9vkica	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Company with alias Company has been created	\N	2026-02-03 23:23:27+01	2026-02-03 23:23:27+01
adte41r96u058znw1	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Segment with alias Segment has been created	\N	2026-02-03 23:23:27+01	2026-02-03 23:23:27+01
adtzh9eeqqa6v3qk0	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Message_Template with alias MessageTemplate has been created	\N	2026-02-03 23:23:27+01	2026-02-03 23:23:27+01
adt03hfu7hnunlg1g	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Lead with alias Lead has been created	\N	2026-02-03 23:23:27+01	2026-02-03 23:23:27+01
adtgkflr7jymf6dj9	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Attempt with alias Attempt has been created	\N	2026-02-03 23:23:27+01	2026-02-03 23:23:27+01
adtopuv9c5rqn2ej1	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Research_Snapshot with alias ResearchSnapshot has been created	\N	2026-02-03 23:23:28+01	2026-02-03 23:23:28+01
adtyprjli8gkefdml	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Approval with alias Approval has been created	\N	2026-02-03 23:23:28+01	2026-02-03 23:23:28+01
adtkvhwh0fvpdl8eo	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Conversation with alias Conversation has been created	\N	2026-02-03 23:23:28+01	2026-02-03 23:23:28+01
adtirc72x90h3tmw2	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Outcome with alias Outcome has been created	\N	2026-02-03 23:23:28+01	2026-02-03 23:23:28+01
adtlz4m4dkbzrhzy4	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mz8ym2ofjyg4cw1	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Pack	<span class="">PackKey</span>\n          : <span class="black--text green lighten-4 px-2">GUARDIAN</span><span class="">Name</span>\n          : <span class="black--text green lighten-4 px-2">El Guardián</span><span class="">PriceMin</span>\n          : <span class="black--text green lighten-4 px-2">500</span><span class="">PriceMax</span>\n          : <span class="black--text green lighten-4 px-2">800</span><span class="">Description</span>\n          : <span class="black--text green lighten-4 px-2">Soporte operativo y continuidad para empresas sin IT interno.</span><span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">true</span><span class="">IcpRules</span>\n          : <span class="black--text green lighten-4 px-2">{"employees": "1-10", "no_it": true, "owner_non_technical": true}</span><span class="">ScoringWeights</span>\n          : <span class="black--text green lighten-4 px-2">{"fit": 40, "maps": 40, "web": 20}</span>	2026-02-03 23:24:27+01	2026-02-03 23:24:27+01
adt4hunveqt9lyiwp	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mj5teal9t147sf8	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	<span class="">SegmentKey</span>\n          : <span class="black--text green lighten-4 px-2">BCN_A_LT50REV_GUARDIAN_TEST</span><span class="">Name</span>\n          : <span class="black--text green lighten-4 px-2">BCN A &lt;50 reviews [TEST]</span><span class="">Type</span>\n          : <span class="black--text green lighten-4 px-2">AB_TEST</span><span class="">Status</span>\n          : <span class="black--text green lighten-4 px-2">RUNNING</span><span class="">Definition</span>\n          : <span class="black--text green lighten-4 px-2">{"city": "Barcelona", "reviews_bucket": "LT50", "test": true}</span><span class="">DailyInviteCap</span>\n          : <span class="black--text green lighten-4 px-2">10</span><span class="">Notes</span>\n          : <span class="black--text green lighten-4 px-2">Segmento de test — se puede eliminar.</span>	2026-02-03 23:24:27+01	2026-02-03 23:24:27+01
adt6auix4jlsbfo13	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	UPDATE	\N	The column places_rating with alias PlacesRating from table nc_jmsd___Company has been updated	\N	2026-02-03 23:27:51+01	2026-02-03 23:27:51+01
adtc0t8nvf1anm01p	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mktsbl5l1v0euv2	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Company	<span class="">Name</span>\n          : <span class="black--text green lighten-4 px-2">Talleres García SL [TEST]</span><span class="">Domain</span>\n          : <span class="black--text green lighten-4 px-2">talleresgarcia-test.com</span><span class="">WebUrl</span>\n          : <span class="black--text green lighten-4 px-2">https://talleresgarcia-test.com</span><span class="">Industry</span>\n          : <span class="black--text green lighten-4 px-2">Automocion</span><span class="">LocationCity</span>\n          : <span class="black--text green lighten-4 px-2">Barcelona</span><span class="">LocationRegion</span>\n          : <span class="black--text green lighten-4 px-2">Catalunya</span><span class="">EmployeesRange</span>\n          : <span class="black--text green lighten-4 px-2">1-10</span><span class="">RevenueEstimateRange</span>\n          : <span class="black--text green lighten-4 px-2">150-600k</span><span class="">PlacesPlaceId</span>\n          : <span class="black--text green lighten-4 px-2">ChIJtest123Barcelona</span><span class="">PlacesRating</span>\n          : <span class="black--text green lighten-4 px-2">4.1</span><span class="">PlacesReviewsTotal</span>\n          : <span class="black--text green lighten-4 px-2">38</span><span class="">PlacesTypes</span>\n          : <span class="black--text green lighten-4 px-2">{"types":["car_repair","point_of_interest"]}</span><span class="">PlacesWebsite</span>\n          : <span class="black--text green lighten-4 px-2">https://talleresgarcia-test.com</span><span class="">PlacesPhone</span>\n          : <span class="black--text green lighten-4 px-2">+34 93 123 45 67</span><span class="">PlacesAddress</span>\n          : <span class="black--text green lighten-4 px-2">C/ Test 42, 08001 Barcelona</span><span class="">PlacesSignalHash</span>\n          : <span class="black--text green lighten-4 px-2">sha256:test_places_hash_001</span><span class="">WebSignalHash</span>\n          : <span class="black--text green lighten-4 px-2">sha256:test_web_hash_001</span>	2026-02-03 23:28:38+01	2026-02-03 23:28:38+01
adtkbrvnyqmy16gce	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Pack with alias Pack  	\N	2026-02-03 23:29:57+01	2026-02-03 23:29:57+01
adtnebzoa61cm5a4q	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Company with alias Company  	\N	2026-02-03 23:30:05+01	2026-02-03 23:30:05+01
adt8rnbkyjzeomjvy	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column pack with alias pack from table nc_jmsd___Segment has been deleted	\N	2026-02-03 23:30:09+01	2026-02-03 23:30:09+01
adt2ft9fu94gdif5o	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Segment with alias Segment  	\N	2026-02-03 23:30:09+01	2026-02-03 23:30:09+01
adtn50130v2a3y9gw	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column pack with alias pack from table nc_jmsd___Message_Template has been deleted	\N	2026-02-03 23:30:15+01	2026-02-03 23:30:15+01
adt613nw3rg0dzsfn	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column segment with alias segment from table nc_jmsd___Message_Template has been deleted	\N	2026-02-03 23:30:15+01	2026-02-03 23:30:15+01
adt2vy0srzlj2si3l	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Message_Template with alias MessageTemplate  	\N	2026-02-03 23:30:15+01	2026-02-03 23:30:15+01
adt0x4kp3sfot3yll	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column company with alias company from table nc_jmsd___Lead has been deleted	\N	2026-02-03 23:30:20+01	2026-02-03 23:30:20+01
adtomcjmimnqsh1ua	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column pack_candidate with alias pack_candidate from table nc_jmsd___Lead has been deleted	\N	2026-02-03 23:30:20+01	2026-02-03 23:30:20+01
adtp0p1aevkxsb6nd	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column segment with alias segment from table nc_jmsd___Lead has been deleted	\N	2026-02-03 23:30:20+01	2026-02-03 23:30:20+01
adtgaootr2qd5ymhd	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Lead with alias Lead  	\N	2026-02-03 23:30:20+01	2026-02-03 23:30:20+01
adtlqixhb1z8cp7zf	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column lead with alias lead from table nc_jmsd___Attempt has been deleted	\N	2026-02-03 23:30:24+01	2026-02-03 23:30:24+01
adtts0s4za1xdsog5	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Attempt with alias Attempt  	\N	2026-02-03 23:30:24+01	2026-02-03 23:30:24+01
adtodp82jrfwxzup6	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column company with alias company from table nc_jmsd___Research_Snapshot has been deleted	\N	2026-02-03 23:30:29+01	2026-02-03 23:30:29+01
adto5901hd61en14u	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column lead with alias lead from table nc_jmsd___Research_Snapshot has been deleted	\N	2026-02-03 23:30:29+01	2026-02-03 23:30:29+01
adtj34k2k09nnijp2	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Research_Snapshot with alias ResearchSnapshot  	\N	2026-02-03 23:30:29+01	2026-02-03 23:30:29+01
adtshvosuasdwgzze	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column lead with alias lead from table nc_jmsd___Approval has been deleted	\N	2026-02-03 23:30:34+01	2026-02-03 23:30:34+01
adt8nsgmtaw6elpvq	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column template with alias template from table nc_jmsd___Approval has been deleted	\N	2026-02-03 23:30:34+01	2026-02-03 23:30:34+01
adtmfoy8ykvn3i6sh	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Approval with alias Approval  	\N	2026-02-03 23:30:34+01	2026-02-03 23:30:34+01
adtf24zgudvkckqbv	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column lead with alias lead from table nc_jmsd___Conversation has been deleted	\N	2026-02-03 23:30:38+01	2026-02-03 23:30:38+01
adtzuwfvf7m9krd0e	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Conversation with alias Conversation  	\N	2026-02-03 23:30:38+01	2026-02-03 23:30:38+01
adtdxyspdayyd13q7	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column lead with alias lead from table nc_jmsd___Outcome has been deleted	\N	2026-02-03 23:30:42+01	2026-02-03 23:30:42+01
adtxg82atg07k2jwm	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column package_recommended with alias package_recommended from table nc_jmsd___Outcome has been deleted	\N	2026-02-03 23:30:42+01	2026-02-03 23:30:42+01
adt9l44m36ojdhdk1	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Outcome with alias Outcome  	\N	2026-02-03 23:30:42+01	2026-02-03 23:30:42+01
adtaus6p74jtti4vc	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Pack with alias Pack has been created	\N	2026-02-03 23:30:52+01	2026-02-03 23:30:52+01
adth1pjc158f0g91m	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Company with alias Company has been created	\N	2026-02-03 23:30:52+01	2026-02-03 23:30:52+01
adtk41hx8jj3i1zd0	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Segment with alias Segment has been created	\N	2026-02-03 23:30:52+01	2026-02-03 23:30:52+01
adtarqgtm6i1b8b5f	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Message_Template with alias MessageTemplate has been created	\N	2026-02-03 23:30:52+01	2026-02-03 23:30:52+01
adtxhoxs0qe9td8nh	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Lead with alias Lead has been created	\N	2026-02-03 23:30:53+01	2026-02-03 23:30:53+01
adtpok6yk6khkgj6g	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Attempt with alias Attempt has been created	\N	2026-02-03 23:30:53+01	2026-02-03 23:30:53+01
adt4zj0m8ck9aziz4	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Research_Snapshot with alias ResearchSnapshot has been created	\N	2026-02-03 23:30:53+01	2026-02-03 23:30:53+01
adtrl12703txe2p13	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Approval with alias Approval has been created	\N	2026-02-03 23:30:53+01	2026-02-03 23:30:53+01
adtjo9jtprb2mcz2x	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Conversation with alias Conversation has been created	\N	2026-02-03 23:30:53+01	2026-02-03 23:30:53+01
adtk5h6e0yivxcbrz	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Outcome with alias Outcome has been created	\N	2026-02-03 23:30:53+01	2026-02-03 23:30:53+01
adt1iy883i4oskl74	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	UPDATE	\N	The column places_rating with alias PlacesRating from table nc_jmsd___Company has been updated	\N	2026-02-03 23:34:15+01	2026-02-03 23:34:15+01
adtuk5x2f3jrxnjfr	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	msj7irqrtbgijlg	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Pack	<span class="">PackKey</span>\n          : <span class="black--text green lighten-4 px-2">GUARDIAN</span><span class="">Name</span>\n          : <span class="black--text green lighten-4 px-2">El Guardián</span><span class="">PriceMin</span>\n          : <span class="black--text green lighten-4 px-2">500</span><span class="">PriceMax</span>\n          : <span class="black--text green lighten-4 px-2">800</span><span class="">Description</span>\n          : <span class="black--text green lighten-4 px-2">Soporte operativo y continuidad para empresas sin IT interno.</span><span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">true</span><span class="">IcpRules</span>\n          : <span class="black--text green lighten-4 px-2">{"employees": "1-10", "no_it": true, "owner_non_technical": true}</span><span class="">ScoringWeights</span>\n          : <span class="black--text green lighten-4 px-2">{"fit": 40, "maps": 40, "web": 20}</span>	2026-02-03 23:34:24+01	2026-02-03 23:34:24+01
adtba2esnrvmdm2zx	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mkadykbj2vudub2	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	<span class="">SegmentKey</span>\n          : <span class="black--text green lighten-4 px-2">BCN_A_LT50REV_GUARDIAN_TEST</span><span class="">Name</span>\n          : <span class="black--text green lighten-4 px-2">BCN A &lt;50 reviews [TEST]</span><span class="">Type</span>\n          : <span class="black--text green lighten-4 px-2">AB_TEST</span><span class="">Status</span>\n          : <span class="black--text green lighten-4 px-2">RUNNING</span><span class="">Definition</span>\n          : <span class="black--text green lighten-4 px-2">{"city": "Barcelona", "reviews_bucket": "LT50", "test": true}</span><span class="">DailyInviteCap</span>\n          : <span class="black--text green lighten-4 px-2">10</span><span class="">Notes</span>\n          : <span class="black--text green lighten-4 px-2">Segmento de test — se puede eliminar.</span>	2026-02-03 23:34:24+01	2026-02-03 23:34:24+01
adtx4m4mauxfoiplc	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mo6zgdp4taiq8h3	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Company	<span class="">Name</span>\n          : <span class="black--text green lighten-4 px-2">Talleres García SL [TEST]</span><span class="">Domain</span>\n          : <span class="black--text green lighten-4 px-2">talleresgarcia-test.com</span><span class="">WebUrl</span>\n          : <span class="black--text green lighten-4 px-2">https://talleresgarcia-test.com</span><span class="">Industry</span>\n          : <span class="black--text green lighten-4 px-2">Automocion</span><span class="">LocationCity</span>\n          : <span class="black--text green lighten-4 px-2">Barcelona</span><span class="">LocationRegion</span>\n          : <span class="black--text green lighten-4 px-2">Catalunya</span><span class="">EmployeesRange</span>\n          : <span class="black--text green lighten-4 px-2">1-10</span><span class="">RevenueEstimateRange</span>\n          : <span class="black--text green lighten-4 px-2">150-600k</span><span class="">PlacesPlaceId</span>\n          : <span class="black--text green lighten-4 px-2">ChIJtest123Barcelona</span><span class="">PlacesRating</span>\n          : <span class="black--text green lighten-4 px-2">4.1</span><span class="">PlacesReviewsTotal</span>\n          : <span class="black--text green lighten-4 px-2">38</span><span class="">PlacesTypes</span>\n          : <span class="black--text green lighten-4 px-2">["car_repair", "point_of_interest"]</span><span class="">PlacesWebsite</span>\n          : <span class="black--text green lighten-4 px-2">https://talleresgarcia-test.com</span><span class="">PlacesPhone</span>\n          : <span class="black--text green lighten-4 px-2">+34 93 123 45 67</span><span class="">PlacesAddress</span>\n          : <span class="black--text green lighten-4 px-2">C/ Test 42, 08001 Barcelona</span><span class="">PlacesSignalHash</span>\n          : <span class="black--text green lighten-4 px-2">sha256:test_places_hash_001</span><span class="">WebSignalHash</span>\n          : <span class="black--text green lighten-4 px-2">sha256:test_web_hash_001</span>	2026-02-03 23:34:25+01	2026-02-03 23:34:25+01
adt3txkwj5yyx18ij	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column lead with alias lead from table nc_jmsd___Research_Snapshot has been deleted	\N	2026-02-04 10:54:37+01	2026-02-04 10:54:37+01
adti3l13kd3pl6drl	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mxzt07n7nn6lnxm	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Lead	<span class="">LinkedinUrl</span>\n          : <span class="black--text green lighten-4 px-2">https://linkedin.com/in/carlos-garcia-test-001</span><span class="">FullName</span>\n          : <span class="black--text green lighten-4 px-2">Carlos García [TEST]</span><span class="">Title</span>\n          : <span class="black--text green lighten-4 px-2">Owner</span><span class="">RoleType</span>\n          : <span class="black--text green lighten-4 px-2">OWNER</span><span class="">LocationCity</span>\n          : <span class="black--text green lighten-4 px-2">Barcelona</span><span class="">Language</span>\n          : <span class="black--text green lighten-4 px-2">ES</span><span class="">Source</span>\n          : <span class="black--text green lighten-4 px-2">SALES_NAV</span><span class="">Status</span>\n          : <span class="black--text green lighten-4 px-2">NEW</span><span class="">Priority</span>\n          : <span class="black--text green lighten-4 px-2">HIGH</span><span class="">LeadScore</span>\n          : <span class="black--text green lighten-4 px-2">78</span><span class="">ScoreBreakdown</span>\n          : <span class="black--text green lighten-4 px-2">{"fit": 40, "maps": 28, "web": 10}</span><span class="">ScoringVersion</span>\n          : <span class="black--text green lighten-4 px-2">v1.0</span><span class="">WaitWindowDays</span>\n          : <span class="black--text green lighten-4 px-2">14</span><span class="">SignalChanged</span>\n          : <span class="black--text green lighten-4 px-2">false</span><span class="">DoNotContact</span>\n          : <span class="black--text green lighten-4 px-2">false</span><span class="">Email</span>\n          : <span class="black--text green lighten-4 px-2">carlos@talleresgarcia-test.com</span><span class="">Phone</span>\n          : <span class="black--text green lighten-4 px-2">+34 93 987 65 43</span>	2026-02-03 23:34:25+01	2026-02-03 23:34:25+01
adtx45hy3pcfdi61v	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mv2m91z0yyuevjj	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Attempt	<span class="">AttemptType</span>\n          : <span class="black--text green lighten-4 px-2">INVITE</span><span class="">Phase</span>\n          : <span class="black--text green lighten-4 px-2">INVITE</span><span class="">Result</span>\n          : <span class="black--text green lighten-4 px-2">SUCCESS</span><span class="">Reason</span>\n          : <span class="black--text green lighten-4 px-2">invite_sent_ok</span><span class="">Metadata</span>\n          : <span class="black--text green lighten-4 px-2">{"http_status": 200, "duration_ms": 1200, "test": true}</span>	2026-02-03 23:34:25+01	2026-02-03 23:34:25+01
adtvz3ev04xdndex7	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mu5g9zho84722ov	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table ResearchSnapshot	<span class="">Source</span>\n          : <span class="black--text green lighten-4 px-2">MIXED</span><span class="">Signals</span>\n          : <span class="black--text green lighten-4 px-2">{"web": {"speed_score": 42, "last_updated": "2024-11-15", "tools_detected": ["WordPress", "Calendly"]}, "places": {"rating": 4.1, "reviews": 38, "types": ["car_repair"]}, "test": true}</span><span class="">SignalHash</span>\n          : <span class="black--text green lighten-4 px-2">sha256:test_snapshot_hash_001</span>	2026-02-03 23:34:25+01	2026-02-03 23:34:25+01
adtozvd5r86yq6tx8	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	ml3j7jdsqc0wee7	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Approval	<span class="">Phase</span>\n          : <span class="black--text green lighten-4 px-2">FIRST_MESSAGE</span><span class="">DraftMessage</span>\n          : <span class="black--text green lighten-4 px-2">Hola Carlos, vi que llevas un tiempo gestionando los talleres sin equipo técnico y que la web se nota un poco antigua. ¿Te gustaría que te comentara cómo otros negocios similares en Barcelona han resuelto esto?</span><span class="">FinalMessage</span>\n          : <span class="black--text green lighten-4 px-2">Hola Carlos, vi que llevas un tiempo gestionando los talleres sin equipo técnico y que la web se nota un poco antigua. ¿Te gustaría que te comentara cómo otros negocios similares en Barcelona han resuelto esto?</span><span class="">Rationale</span>\n          : <span class="black--text green lighten-4 px-2">Rating 4.1 (&lt;4.3) + reviews &lt;50 + web antigua → señales fuertes Pack 1. Ángulo: operativo simple, sin fricción técnica.</span><span class="">AngleQuality</span>\n          : <span class="black--text green lighten-4 px-2">GOOD</span><span class="">PainQuality</span>\n          : <span class="black--text green lighten-4 px-2">REAL</span><span class="">Note</span>\n          : <span class="black--text green lighten-4 px-2">Tono consultivo, sin presión.</span><span class="">ApprovedBy</span>\n          : <span class="black--text green lighten-4 px-2">Eduardo</span>	2026-02-03 23:34:25+01	2026-02-03 23:34:25+01
adt9m9qt55jqyhmjr	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mas8e38rxg6rods	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Conversation	<span class="">State</span>\n          : <span class="black--text green lighten-4 px-2">ACTIVE</span><span class="">InterestLevel</span>\n          : <span class="black--text green lighten-4 px-2">WARM</span><span class="">Notes</span>\n          : <span class="black--text green lighten-4 px-2">Respondió al primer mensaje. Preguntó por precios aproximativos. [TEST]</span>	2026-02-03 23:34:25+01	2026-02-03 23:34:25+01
adtn2lrjgn3bl0dy5	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m0xutsg95og0her	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Outcome	<span class="">Outcome</span>\n          : <span class="black--text green lighten-4 px-2">QUALIFIED</span><span class="">ValueEstimate</span>\n          : <span class="black--text green lighten-4 px-2">650</span><span class="">Notes</span>\n          : <span class="black--text green lighten-4 px-2">Interesado en Pack Guardián. Estimar cierre en 2 semanas. [TEST]</span>	2026-02-03 23:34:25+01	2026-02-03 23:34:25+01
adtr6xohkhcd3wl3f	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	msj7irqrtbgijlg	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Pack	<span class="">PackKey</span>\n          : <span class="black--text green lighten-4 px-2">GUARDIAN</span><span class="">Name</span>\n          : <span class="black--text green lighten-4 px-2">El Guardián</span><span class="">PriceMin</span>\n          : <span class="black--text green lighten-4 px-2">500</span><span class="">PriceMax</span>\n          : <span class="black--text green lighten-4 px-2">800</span><span class="">Description</span>\n          : <span class="black--text green lighten-4 px-2">Soporte operativo y continuidad para empresas sin IT interno.</span><span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">true</span><span class="">IcpRules</span>\n          : <span class="black--text green lighten-4 px-2">{"employees": "1-10", "no_it": true, "owner_non_technical": true}</span><span class="">ScoringWeights</span>\n          : <span class="black--text green lighten-4 px-2">{"fit": 40, "maps": 40, "web": 20}</span>	2026-02-03 23:58:23+01	2026-02-03 23:58:23+01
adt7oz7e8mk2pkkdq	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mkadykbj2vudub2	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	<span class="">SegmentKey</span>\n          : <span class="black--text green lighten-4 px-2">BCN_A_LT50REV_GUARDIAN_TEST</span><span class="">Name</span>\n          : <span class="black--text green lighten-4 px-2">BCN A &lt;50 reviews [TEST]</span><span class="">Type</span>\n          : <span class="black--text green lighten-4 px-2">AB_TEST</span><span class="">Status</span>\n          : <span class="black--text green lighten-4 px-2">RUNNING</span><span class="">Definition</span>\n          : <span class="black--text green lighten-4 px-2">{"city": "Barcelona", "reviews_bucket": "LT50", "test": true}</span><span class="">DailyInviteCap</span>\n          : <span class="black--text green lighten-4 px-2">10</span><span class="">Notes</span>\n          : <span class="black--text green lighten-4 px-2">Segmento de test — se puede eliminar.</span>	2026-02-04 00:10:53+01	2026-02-04 00:10:53+01
adthxnjy0r8ziyus0	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Research_Snapshot with alias ResearchSnapshot  	\N	2026-02-04 10:54:37+01	2026-02-04 10:54:37+01
adtmrxt7vsurhweab	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column lead with alias lead from table nc_jmsd___Approval has been deleted	\N	2026-02-04 10:54:42+01	2026-02-04 10:54:42+01
adt00vtaaopgstq51	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column template with alias template from table nc_jmsd___Approval has been deleted	\N	2026-02-04 10:54:42+01	2026-02-04 10:54:42+01
adt1fn3u4velm9562	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	msj7irqrtbgijlg	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Pack	<span class="">PackKey</span>\n          : <span class="black--text green lighten-4 px-2">GUARDIAN</span><span class="">Name</span>\n          : <span class="black--text green lighten-4 px-2">El Guardián</span><span class="">PriceMin</span>\n          : <span class="black--text green lighten-4 px-2">500</span><span class="">PriceMax</span>\n          : <span class="black--text green lighten-4 px-2">800</span><span class="">Description</span>\n          : <span class="black--text green lighten-4 px-2">Soporte operativo y continuidad para empresas sin IT interno.</span><span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">true</span><span class="">IcpRules</span>\n          : <span class="black--text green lighten-4 px-2">{"employees": "1-10", "no_it": true, "owner_non_technical": true}</span><span class="">ScoringWeights</span>\n          : <span class="black--text green lighten-4 px-2">{"fit": 40, "maps": 40, "web": 20}</span>	2026-02-04 00:19:36+01	2026-02-04 00:19:36+01
adty0b12dybwmm7xy	team@mailerblend.com	\N	\N	\N	\N	\N	AUTHENTICATION	SIGNIN	\N	\N	\N	2026-02-04 10:19:24+01	2026-02-04 10:19:24+01
adt79mzd9kdl403a3	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___prueba_de_nuevo with alias prueba_de_nuevo has been created	\N	2026-02-04 10:26:58+01	2026-02-04 10:26:58+01
adt85cuo1zsgxrh1u	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mh1zjs5mk8y4m5i	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table prueba_de_nuevo	<span class="">decimar</span>\n          : <span class="black--text green lighten-4 px-2">4.5</span>	2026-02-04 10:26:58+01	2026-02-04 10:26:58+01
adtpnkdtvgb0pzann	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___prueba_de_nuevo with alias prueba_de_nuevo  	\N	2026-02-04 10:29:02+01	2026-02-04 10:29:02+01
adtqwjwo5cit6qg31	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___prueba_de_nuevo with alias prueba_de_nuevo has been created	\N	2026-02-04 10:29:11+01	2026-02-04 10:29:11+01
adt30censq3d40b6l	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mt8aod0rw02urd5	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table prueba_de_nuevo	<span class="">decimar</span>\n          : <span class="black--text green lighten-4 px-2">4.5</span>	2026-02-04 10:29:11+01	2026-02-04 10:29:11+01
adtdc0txkyfkx1cji	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___prueba_de_nuevo with alias prueba_de_nuevo  	\N	2026-02-04 10:30:27+01	2026-02-04 10:30:27+01
adtjnagdrecaquj9w	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___prueba_de_nuevo with alias prueba_de_nuevo has been created	\N	2026-02-04 10:30:33+01	2026-02-04 10:30:33+01
adtk57telv05nw62f	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m588mghnvz4ehjd	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table prueba_de_nuevo	\N	2026-02-04 10:30:33+01	2026-02-04 10:30:33+01
adt5sunp2nx8fdyku	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___prueba_de_nuevo with alias prueba_de_nuevo  	\N	2026-02-04 10:33:26+01	2026-02-04 10:33:26+01
adtzhv1jeqky0yshd	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___prueba_de_nuevo with alias prueba_de_nuevo has been created	\N	2026-02-04 10:33:32+01	2026-02-04 10:33:32+01
adt2hjfnvfy6wpxx8	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	ma4m5jxkcqp9b5s	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table prueba_de_nuevo	<span class="">rankingUpdate</span>\n          : <span class="black--text green lighten-4 px-2">4.5</span>	2026-02-04 10:33:32+01	2026-02-04 10:33:32+01
adt7azdlv32y5miq0	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___prueba_de_nuevo with alias prueba_de_nuevo  	\N	2026-02-04 10:41:03+01	2026-02-04 10:41:03+01
adt9bap7ucc64a0ka	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___prueba_decimal with alias prueba_decimal has been created	\N	2026-02-04 10:41:31+01	2026-02-04 10:41:31+01
adtqkay04ec772pqe	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mb59jscaxel473x	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table prueba_decimal	<span class="">Ranking</span>\n          : <span class="black--text green lighten-4 px-2">4.5</span>	2026-02-04 10:41:31+01	2026-02-04 10:41:31+01
adt64663kx42ebxiz	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Pack with alias Pack  	\N	2026-02-04 10:54:08+01	2026-02-04 10:54:08+01
adtgxwbrixw66iv36	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Company with alias Company  	\N	2026-02-04 10:54:12+01	2026-02-04 10:54:12+01
adtjog000z8uauala	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column pack with alias pack from table nc_jmsd___Segment has been deleted	\N	2026-02-04 10:54:18+01	2026-02-04 10:54:18+01
adt5doj76phkd19sg	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Segment with alias Segment  	\N	2026-02-04 10:54:18+01	2026-02-04 10:54:18+01
adt8r6zn4tkqh51vf	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column pack with alias pack from table nc_jmsd___Message_Template has been deleted	\N	2026-02-04 10:54:22+01	2026-02-04 10:54:22+01
adtm7sf03urfq77a4	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column segment with alias segment from table nc_jmsd___Message_Template has been deleted	\N	2026-02-04 10:54:22+01	2026-02-04 10:54:22+01
adtsxtm2ywt8qewp6	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Message_Template with alias MessageTemplate  	\N	2026-02-04 10:54:22+01	2026-02-04 10:54:22+01
adti1x24xnyzuwp24	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column company with alias company from table nc_jmsd___Lead has been deleted	\N	2026-02-04 10:54:27+01	2026-02-04 10:54:27+01
adtilozzak2jhlwgg	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column pack_candidate with alias pack_candidate from table nc_jmsd___Lead has been deleted	\N	2026-02-04 10:54:27+01	2026-02-04 10:54:27+01
adty3j5h83rxtsf1m	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column segment with alias segment from table nc_jmsd___Lead has been deleted	\N	2026-02-04 10:54:27+01	2026-02-04 10:54:27+01
adt38yfg8up1ejnm8	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Lead with alias Lead  	\N	2026-02-04 10:54:27+01	2026-02-04 10:54:27+01
adtezrts4uknujzs3	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column lead with alias lead from table nc_jmsd___Attempt has been deleted	\N	2026-02-04 10:54:32+01	2026-02-04 10:54:32+01
adtl4mp5wzpy5vqi4	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Attempt with alias Attempt  	\N	2026-02-04 10:54:32+01	2026-02-04 10:54:32+01
adttgy3tkl7w408pq	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column company with alias company from table nc_jmsd___Research_Snapshot has been deleted	\N	2026-02-04 10:54:37+01	2026-02-04 10:54:37+01
adtw7g410neubgbjt	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Approval with alias Approval  	\N	2026-02-04 10:54:42+01	2026-02-04 10:54:42+01
adt58ooy5jgh4xeoh	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column lead with alias lead from table nc_jmsd___Conversation has been deleted	\N	2026-02-04 10:54:47+01	2026-02-04 10:54:47+01
adtxyvo8w4z2ifydo	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Conversation with alias Conversation  	\N	2026-02-04 10:54:47+01	2026-02-04 10:54:47+01
adtbw9m1hriuhy14k	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column lead with alias lead from table nc_jmsd___Outcome has been deleted	\N	2026-02-04 10:54:52+01	2026-02-04 10:54:52+01
adtmv8my7lx4ou6eh	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column package_recommended with alias package_recommended from table nc_jmsd___Outcome has been deleted	\N	2026-02-04 10:54:52+01	2026-02-04 10:54:52+01
adt3cs4ya1zes60qp	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Outcome with alias Outcome  	\N	2026-02-04 10:54:52+01	2026-02-04 10:54:52+01
adttfyccw181f98q9	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___prueba_decimal with alias prueba_decimal  	\N	2026-02-04 10:54:59+01	2026-02-04 10:54:59+01
adt2wxsl9wg1jj3mt	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Pack with alias Pack has been created	\N	2026-02-04 11:00:03+01	2026-02-04 11:00:03+01
adtcl1r60q3g9yung	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Company with alias Company has been created	\N	2026-02-04 11:00:03+01	2026-02-04 11:00:03+01
adtom93h6sgpdeuzr	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Segment with alias Segment has been created	\N	2026-02-04 11:00:03+01	2026-02-04 11:00:03+01
adtul6uydbcjscr1k	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Message_Template with alias MessageTemplate has been created	\N	2026-02-04 11:00:03+01	2026-02-04 11:00:03+01
adtvmo5wk6n0e3ajb	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Lead with alias Lead has been created	\N	2026-02-04 11:00:03+01	2026-02-04 11:00:03+01
adtz9ufirtoyk0i6f	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Attempt with alias Attempt has been created	\N	2026-02-04 11:00:03+01	2026-02-04 11:00:03+01
adtaekvfxi5z0rye4	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Research_Snapshot with alias ResearchSnapshot has been created	\N	2026-02-04 11:00:03+01	2026-02-04 11:00:03+01
adtmsya1x3i1w5gvl	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Approval with alias Approval has been created	\N	2026-02-04 11:00:03+01	2026-02-04 11:00:03+01
adtdpo7e7dh9s6rcb	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Conversation with alias Conversation has been created	\N	2026-02-04 11:00:04+01	2026-02-04 11:00:04+01
adtk69oesbi5x6yzu	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Outcome with alias Outcome has been created	\N	2026-02-04 11:00:04+01	2026-02-04 11:00:04+01
adtxycinbncx9jq66	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m1lm2filrcm38vs	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Pack	<span class="">PackKey</span>\n          : <span class="black--text green lighten-4 px-2">GUARDIAN</span><span class="">Name</span>\n          : <span class="black--text green lighten-4 px-2">El Guardián</span><span class="">PriceMin</span>\n          : <span class="black--text green lighten-4 px-2">500</span><span class="">PriceMax</span>\n          : <span class="black--text green lighten-4 px-2">800</span><span class="">Description</span>\n          : <span class="black--text green lighten-4 px-2">Soporte operativo y continuidad para empresas sin IT interno.</span><span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">true</span><span class="">IcpRules</span>\n          : <span class="black--text green lighten-4 px-2">{"employees": "1-10", "no_it": true, "owner_non_technical": true}</span><span class="">ScoringWeights</span>\n          : <span class="black--text green lighten-4 px-2">{"fit": 40, "maps": 40, "web": 20}</span>	2026-02-04 11:04:26+01	2026-02-04 11:04:26+01
adtyh0lvs6clhixt8	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mmfk5l38ik8mt1t	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Segment	<span class="">SegmentKey</span>\n          : <span class="black--text green lighten-4 px-2">BCN_A_LT50REV_GUARDIAN_TEST</span><span class="">Name</span>\n          : <span class="black--text green lighten-4 px-2">BCN A &lt;50 reviews [TEST]</span><span class="">Type</span>\n          : <span class="black--text green lighten-4 px-2">AB_TEST</span><span class="">Status</span>\n          : <span class="black--text green lighten-4 px-2">RUNNING</span><span class="">Definition</span>\n          : <span class="black--text green lighten-4 px-2">{"city": "Barcelona", "reviews_bucket": "LT50", "test": true}</span><span class="">DailyInviteCap</span>\n          : <span class="black--text green lighten-4 px-2">10</span><span class="">Notes</span>\n          : <span class="black--text green lighten-4 px-2">Segmento de test — se puede eliminar.</span>	2026-02-04 11:04:26+01	2026-02-04 11:04:26+01
adt5pyi8nbibciyh4	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m0nv9w1shj1g1u1	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Company	<span class="">Name</span>\n          : <span class="black--text green lighten-4 px-2">Talleres García SL [TEST]</span><span class="">Domain</span>\n          : <span class="black--text green lighten-4 px-2">talleresgarcia-test.com</span><span class="">WebUrl</span>\n          : <span class="black--text green lighten-4 px-2">https://talleresgarcia-test.com</span><span class="">Industry</span>\n          : <span class="black--text green lighten-4 px-2">Automocion</span><span class="">LocationCity</span>\n          : <span class="black--text green lighten-4 px-2">Barcelona</span><span class="">LocationRegion</span>\n          : <span class="black--text green lighten-4 px-2">Catalunya</span><span class="">EmployeesRange</span>\n          : <span class="black--text green lighten-4 px-2">1-10</span><span class="">RevenueEstimateRange</span>\n          : <span class="black--text green lighten-4 px-2">150-600k</span><span class="">PlacesPlaceId</span>\n          : <span class="black--text green lighten-4 px-2">ChIJtest123Barcelona</span><span class="">places_rating</span>\n          : <span class="black--text green lighten-4 px-2">4.1</span><span class="">PlacesReviewsTotal</span>\n          : <span class="black--text green lighten-4 px-2">38</span><span class="">PlacesTypes</span>\n          : <span class="black--text green lighten-4 px-2">["car_repair", "point_of_interest"]</span><span class="">PlacesWebsite</span>\n          : <span class="black--text green lighten-4 px-2">https://talleresgarcia-test.com</span><span class="">PlacesPhone</span>\n          : <span class="black--text green lighten-4 px-2">+34 93 123 45 67</span><span class="">PlacesAddress</span>\n          : <span class="black--text green lighten-4 px-2">C/ Test 42, 08001 Barcelona</span><span class="">PlacesSignalHash</span>\n          : <span class="black--text green lighten-4 px-2">sha256:test_places_hash_001</span><span class="">WebSignalHash</span>\n          : <span class="black--text green lighten-4 px-2">sha256:test_web_hash_001</span>	2026-02-04 11:04:26+01	2026-02-04 11:04:26+01
adtpf38tlhy25ly1w	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mr7cph5hlh1gyqc	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Lead	<span class="">LinkedinUrl</span>\n          : <span class="black--text green lighten-4 px-2">https://linkedin.com/in/carlos-garcia-test-001</span><span class="">FullName</span>\n          : <span class="black--text green lighten-4 px-2">Carlos García [TEST]</span><span class="">Title</span>\n          : <span class="black--text green lighten-4 px-2">Owner</span><span class="">RoleType</span>\n          : <span class="black--text green lighten-4 px-2">OWNER</span><span class="">LocationCity</span>\n          : <span class="black--text green lighten-4 px-2">Barcelona</span><span class="">Language</span>\n          : <span class="black--text green lighten-4 px-2">ES</span><span class="">Source</span>\n          : <span class="black--text green lighten-4 px-2">SALES_NAV</span><span class="">Status</span>\n          : <span class="black--text green lighten-4 px-2">NEW</span><span class="">Priority</span>\n          : <span class="black--text green lighten-4 px-2">HIGH</span><span class="">LeadScore</span>\n          : <span class="black--text green lighten-4 px-2">78</span><span class="">ScoreBreakdown</span>\n          : <span class="black--text green lighten-4 px-2">{"fit": 40, "maps": 28, "web": 10}</span><span class="">ScoringVersion</span>\n          : <span class="black--text green lighten-4 px-2">v1.0</span><span class="">WaitWindowDays</span>\n          : <span class="black--text green lighten-4 px-2">14</span><span class="">SignalChanged</span>\n          : <span class="black--text green lighten-4 px-2">false</span><span class="">DoNotContact</span>\n          : <span class="black--text green lighten-4 px-2">false</span><span class="">Email</span>\n          : <span class="black--text green lighten-4 px-2">carlos@talleresgarcia-test.com</span><span class="">Phone</span>\n          : <span class="black--text green lighten-4 px-2">+34 93 987 65 43</span>	2026-02-04 11:04:26+01	2026-02-04 11:04:26+01
adtx4ca6qnfsu41qz	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m2khp8uar3b9r21	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Attempt	<span class="">AttemptType</span>\n          : <span class="black--text green lighten-4 px-2">INVITE</span><span class="">Phase</span>\n          : <span class="black--text green lighten-4 px-2">INVITE</span><span class="">Result</span>\n          : <span class="black--text green lighten-4 px-2">SUCCESS</span><span class="">Reason</span>\n          : <span class="black--text green lighten-4 px-2">invite_sent_ok</span><span class="">Metadata</span>\n          : <span class="black--text green lighten-4 px-2">{"http_status": 200, "duration_ms": 1200, "test": true}</span>	2026-02-04 11:04:26+01	2026-02-04 11:04:26+01
adte93gkc5q63htb2	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column lead with alias lead from table nc_jmsd___Conversation has been deleted	\N	2026-02-04 12:50:49+01	2026-02-04 12:50:49+01
adt1ef5yatbigdta0	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Conversation with alias Conversation  	\N	2026-02-04 12:50:49+01	2026-02-04 12:50:49+01
adtlkcvbp67rj5pjy	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m02lr443tsv645w	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table ResearchSnapshot	<span class="">Source</span>\n          : <span class="black--text green lighten-4 px-2">MIXED</span><span class="">Signals</span>\n          : <span class="black--text green lighten-4 px-2">{"web": {"speed_score": 42, "last_updated": "2024-11-15", "tools_detected": ["WordPress", "Calendly"]}, "places": {"rating": 4.1, "reviews": 38, "types": ["car_repair"]}, "test": true}</span><span class="">SignalHash</span>\n          : <span class="black--text green lighten-4 px-2">sha256:test_snapshot_hash_001</span>	2026-02-04 11:04:26+01	2026-02-04 11:04:26+01
adt167p4qevifjk3z	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mt291p31hwv9ihq	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Outcome	<span class="">Outcome</span>\n          : <span class="black--text green lighten-4 px-2">QUALIFIED</span><span class="">ValueEstimate</span>\n          : <span class="black--text green lighten-4 px-2">650</span><span class="">Notes</span>\n          : <span class="black--text green lighten-4 px-2">Interesado en Pack Guardián. Estimar cierre en 2 semanas. [TEST]</span>	2026-02-04 11:04:26+01	2026-02-04 11:04:26+01
adtxy9eekwfzk3504	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mk4d9czzgo8k0u0	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Approval	<span class="">Phase</span>\n          : <span class="black--text green lighten-4 px-2">FIRST_MESSAGE</span><span class="">DraftMessage</span>\n          : <span class="black--text green lighten-4 px-2">Hola Carlos, vi que llevas un tiempo gestionando los talleres sin equipo técnico y que la web se nota un poco antigua. ¿Te gustaría que te comentara cómo otros negocios similares en Barcelona han resuelto esto?</span><span class="">FinalMessage</span>\n          : <span class="black--text green lighten-4 px-2">Hola Carlos, vi que llevas un tiempo gestionando los talleres sin equipo técnico y que la web se nota un poco antigua. ¿Te gustaría que te comentara cómo otros negocios similares en Barcelona han resuelto esto?</span><span class="">Rationale</span>\n          : <span class="black--text green lighten-4 px-2">Rating 4.1 (&lt;4.3) + reviews &lt;50 + web antigua → señales fuertes Pack 1. Ángulo: operativo simple, sin fricción técnica.</span><span class="">AngleQuality</span>\n          : <span class="black--text green lighten-4 px-2">GOOD</span><span class="">PainQuality</span>\n          : <span class="black--text green lighten-4 px-2">REAL</span><span class="">Note</span>\n          : <span class="black--text green lighten-4 px-2">Tono consultivo, sin presión.</span><span class="">ApprovedBy</span>\n          : <span class="black--text green lighten-4 px-2">Eduardo</span>	2026-02-04 11:04:26+01	2026-02-04 11:04:26+01
adtugahxib9sa0ieg	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	my8ukw0z6ivu95a	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table Conversation	<span class="">State</span>\n          : <span class="black--text green lighten-4 px-2">ACTIVE</span><span class="">InterestLevel</span>\n          : <span class="black--text green lighten-4 px-2">WARM</span><span class="">Notes</span>\n          : <span class="black--text green lighten-4 px-2">Respondió al primer mensaje. Preguntó por precios aproximativos. [TEST]</span>	2026-02-04 11:04:26+01	2026-02-04 11:04:26+01
adt1jwhhscow0wfan	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___prueba_decimal with alias prueba_decimal has been created	\N	2026-02-04 11:41:45+01	2026-02-04 11:41:45+01
adtga8dnps7rr9knw	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mn4av0p80z3b6gx	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table prueba_decimal	<span class="">Ranking</span>\n          : <span class="black--text green lighten-4 px-2">4.5</span>	2026-02-04 11:41:45+01	2026-02-04 11:41:45+01
adtltu9vs1idntmaz	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___tabla_test_id with alias tabla_test_id has been created	\N	2026-02-04 11:50:48+01	2026-02-04 11:50:48+01
adtrvidaeaoiemthm	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mc01xvnub0qtm7n	N/A	DATA	INSERT	\N	Record with ID N/A has been inserted into Table tabla_test_id	<span class="">Puntos</span>\n          : <span class="black--text green lighten-4 px-2">4.1</span>	2026-02-04 11:50:48+01	2026-02-04 11:50:48+01
adt1z086ox4kfx14v	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___tabla_test_id_v2 with alias tabla_test_id_v2 has been created	\N	2026-02-04 12:21:30+01	2026-02-04 12:21:30+01
adt9exnc3jwii31tq	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mlzoxoykxqadcm5	1	DATA	INSERT	\N	Record with ID 1 has been inserted into Table tabla_test_id_v2	<span class="">Puntos</span>\n          : <span class="black--text green lighten-4 px-2">9.5</span>	2026-02-04 12:21:30+01	2026-02-04 12:21:30+01
adt0aqlslt4mtnq2v	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Pack with alias Pack  	\N	2026-02-04 12:50:07+01	2026-02-04 12:50:07+01
adtpqnomsflm90357	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Company with alias Company  	\N	2026-02-04 12:50:13+01	2026-02-04 12:50:13+01
adtg5ift5rrl0xwm1	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column pack with alias pack from table nc_jmsd___Segment has been deleted	\N	2026-02-04 12:50:17+01	2026-02-04 12:50:17+01
adtqw1kzrv5vku4vv	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Segment with alias Segment  	\N	2026-02-04 12:50:17+01	2026-02-04 12:50:17+01
adtehyim1kp0q67wr	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column pack with alias pack from table nc_jmsd___Message_Template has been deleted	\N	2026-02-04 12:50:21+01	2026-02-04 12:50:21+01
adteur3l3yatc2n9y	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column segment with alias segment from table nc_jmsd___Message_Template has been deleted	\N	2026-02-04 12:50:21+01	2026-02-04 12:50:21+01
adtjkqwf9q9gnrief	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Message_Template with alias MessageTemplate  	\N	2026-02-04 12:50:21+01	2026-02-04 12:50:21+01
adt3e25oc7mk5r4rn	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column company with alias company from table nc_jmsd___Lead has been deleted	\N	2026-02-04 12:50:26+01	2026-02-04 12:50:26+01
adt2mm7i7y6oiw9uu	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column pack_candidate with alias pack_candidate from table nc_jmsd___Lead has been deleted	\N	2026-02-04 12:50:26+01	2026-02-04 12:50:26+01
adtprivuibcewferx	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column segment with alias segment from table nc_jmsd___Lead has been deleted	\N	2026-02-04 12:50:26+01	2026-02-04 12:50:26+01
adtp3flu7078ykyab	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Lead with alias Lead  	\N	2026-02-04 12:50:26+01	2026-02-04 12:50:26+01
adtnqph17wwt2fwtr	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column lead with alias lead from table nc_jmsd___Attempt has been deleted	\N	2026-02-04 12:50:33+01	2026-02-04 12:50:33+01
adt4rsmdsif6r12e8	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Attempt with alias Attempt  	\N	2026-02-04 12:50:33+01	2026-02-04 12:50:33+01
adtocwttcynha2xva	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column company with alias company from table nc_jmsd___Research_Snapshot has been deleted	\N	2026-02-04 12:50:38+01	2026-02-04 12:50:38+01
adtgglnels86calgo	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column lead with alias lead from table nc_jmsd___Research_Snapshot has been deleted	\N	2026-02-04 12:50:38+01	2026-02-04 12:50:38+01
adt4kc56ysh7n65n6	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Research_Snapshot with alias ResearchSnapshot  	\N	2026-02-04 12:50:38+01	2026-02-04 12:50:38+01
adtrpi2vivr22buhl	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column lead with alias lead from table nc_jmsd___Approval has been deleted	\N	2026-02-04 12:50:44+01	2026-02-04 12:50:44+01
adtceaopwo66qizqg	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column template with alias template from table nc_jmsd___Approval has been deleted	\N	2026-02-04 12:50:44+01	2026-02-04 12:50:44+01
adtmyjqs4d406oegx	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Approval with alias Approval  	\N	2026-02-04 12:50:44+01	2026-02-04 12:50:44+01
adtl27dbmyw5ma207	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column lead with alias lead from table nc_jmsd___Outcome has been deleted	\N	2026-02-04 12:50:54+01	2026-02-04 12:50:54+01
adtzkn9a0q7618wwx	team@mailerblend.com	192.168.1.254	\N	pbydkvvvbvv4pdf	\N	\N	TABLE_COLUMN	DELETE	\N	The column package_recommended with alias package_recommended from table nc_jmsd___Outcome has been deleted	\N	2026-02-04 12:50:54+01	2026-02-04 12:50:54+01
adt8tu25otbvku9rp	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___Outcome with alias Outcome  	\N	2026-02-04 12:50:54+01	2026-02-04 12:50:54+01
adt507o37cpjb1cvi	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___prueba_decimal with alias prueba_decimal  	\N	2026-02-04 12:50:58+01	2026-02-04 12:50:58+01
adtiatb08egcalm9k	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	DELETE	\N	Deleted table nc_jmsd___tabla_test_id_v2 with alias tabla_test_id_v2  	\N	2026-02-04 12:51:09+01	2026-02-04 12:51:09+01
adtk0y2klxecgsui6	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Pack with alias Pack has been created	\N	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01
adtevja6gp9cldpl0	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Company with alias Company has been created	\N	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01
adtagdlzbfk1ftzc7	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Segment with alias Segment has been created	\N	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01
adtllnake1m5pauxf	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Message_Template with alias MessageTemplate has been created	\N	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01
adttpguq4fcvwlsb2	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Lead with alias Lead has been created	\N	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01
adtxi7q5tubbwuqrr	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Attempt with alias Attempt has been created	\N	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01
adtisov2ehkg0846r	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Research_Snapshot with alias ResearchSnapshot has been created	\N	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01
adtxaeosxx77avoa2	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Approval with alias Approval has been created	\N	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01
adtx5w7ldr8wthgxd	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Conversation with alias Conversation has been created	\N	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01
adtozvqh4lra0guok	gestionads15.21@gmail.com	\N	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	TABLE	CREATE	\N	Table nc_jmsd___Outcome with alias Outcome has been created	\N	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01
adtlx7rq7pugr77ki	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m965eotz3l7hxbi	1	DATA	INSERT	\N	Record with ID 1 has been inserted into Table Pack	<span class="">PackKey</span>\n          : <span class="black--text green lighten-4 px-2">GUARDIAN</span><span class="">Name</span>\n          : <span class="black--text green lighten-4 px-2">El Guardián</span><span class="">PriceMin</span>\n          : <span class="black--text green lighten-4 px-2">500</span><span class="">PriceMax</span>\n          : <span class="black--text green lighten-4 px-2">800</span><span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">true</span>	2026-02-04 12:54:30+01	2026-02-04 12:54:30+01
adt4e4vljxcv6ywya	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m965eotz3l7hxbi	1	DATA	DELETE	\N	Record with ID 1 has been deleted in Table Pack	\N	2026-02-04 12:59:17+01	2026-02-04 12:59:17+01
adt71sd0xfzqhznl4	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m965eotz3l7hxbi	3	DATA	INSERT	\N	Record with ID 3 has been inserted into Table Pack	<span class="">PackKey</span>\n          : <span class="black--text green lighten-4 px-2">GUARDIAN</span><span class="">Name</span>\n          : <span class="black--text green lighten-4 px-2">El Guardián</span><span class="">PriceMin</span>\n          : <span class="black--text green lighten-4 px-2">500</span><span class="">PriceMax</span>\n          : <span class="black--text green lighten-4 px-2">800</span><span class="">Description</span>\n          : <span class="black--text green lighten-4 px-2">Soporte operativo y continuidad para empresas sin IT interno.</span><span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">true</span><span class="">IcpRules</span>\n          : <span class="black--text green lighten-4 px-2">{"employees": "1-10", "no_it": true, "owner_non_technical": true}</span><span class="">ScoringWeights</span>\n          : <span class="black--text green lighten-4 px-2">{"fit": 40, "maps": 40, "web": 20}</span>	2026-02-04 12:59:43+01	2026-02-04 12:59:43+01
adtaabqrd4p1t7bew	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m7nt9pg5uw1e4h3	1	DATA	INSERT	\N	Record with ID 1 has been inserted into Table Segment	<span class="">SegmentKey</span>\n          : <span class="black--text green lighten-4 px-2">BCN_A_LT50REV_GUARDIAN_TEST</span><span class="">Name</span>\n          : <span class="black--text green lighten-4 px-2">BCN A &lt;50 reviews [TEST]</span><span class="">Type</span>\n          : <span class="black--text green lighten-4 px-2">AB_TEST</span><span class="">Status</span>\n          : <span class="black--text green lighten-4 px-2">RUNNING</span><span class="">Definition</span>\n          : <span class="black--text green lighten-4 px-2">{"city": "Barcelona", "reviews_bucket": "LT50", "test": true}</span><span class="">DailyInviteCap</span>\n          : <span class="black--text green lighten-4 px-2">10</span><span class="">Notes</span>\n          : <span class="black--text green lighten-4 px-2">Segmento de test — se puede eliminar.</span>	2026-02-04 12:59:44+01	2026-02-04 12:59:44+01
adtpg2cc999o9n4lj	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	merj80wv3zr0yzl	1	DATA	INSERT	\N	Record with ID 1 has been inserted into Table Company	<span class="">Name</span>\n          : <span class="black--text green lighten-4 px-2">Talleres García SL [TEST]</span><span class="">Domain</span>\n          : <span class="black--text green lighten-4 px-2">talleresgarcia-test.com</span><span class="">WebUrl</span>\n          : <span class="black--text green lighten-4 px-2">https://talleresgarcia-test.com</span><span class="">Industry</span>\n          : <span class="black--text green lighten-4 px-2">Automocion</span><span class="">LocationCity</span>\n          : <span class="black--text green lighten-4 px-2">Barcelona</span><span class="">LocationRegion</span>\n          : <span class="black--text green lighten-4 px-2">Catalunya</span><span class="">EmployeesRange</span>\n          : <span class="black--text green lighten-4 px-2">1-10</span><span class="">RevenueEstimateRange</span>\n          : <span class="black--text green lighten-4 px-2">150-600k</span><span class="">PlacesPlaceId</span>\n          : <span class="black--text green lighten-4 px-2">ChIJtest123Barcelona</span><span class="">places_rating</span>\n          : <span class="black--text green lighten-4 px-2">4.1</span><span class="">PlacesReviewsTotal</span>\n          : <span class="black--text green lighten-4 px-2">38</span><span class="">PlacesTypes</span>\n          : <span class="black--text green lighten-4 px-2">{"types": ["car_repair", "point_of_interest"]}</span><span class="">PlacesWebsite</span>\n          : <span class="black--text green lighten-4 px-2">https://talleresgarcia-test.com</span><span class="">PlacesPhone</span>\n          : <span class="black--text green lighten-4 px-2">+34 93 123 45 67</span><span class="">PlacesAddress</span>\n          : <span class="black--text green lighten-4 px-2">C/ Test 42, 08001 Barcelona</span><span class="">PlacesSignalHash</span>\n          : <span class="black--text green lighten-4 px-2">sha256:test_places_hash_001</span><span class="">WebSignalHash</span>\n          : <span class="black--text green lighten-4 px-2">sha256:test_web_hash_001</span>	2026-02-04 12:59:44+01	2026-02-04 12:59:44+01
adtczsxgfnaqfm5wa	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mc5itfivoyx2rp5	1	DATA	INSERT	\N	Record with ID 1 has been inserted into Table Lead	<span class="">LinkedinUrl</span>\n          : <span class="black--text green lighten-4 px-2">https://linkedin.com/in/carlos-garcia-test-001</span><span class="">FullName</span>\n          : <span class="black--text green lighten-4 px-2">Carlos García [TEST]</span><span class="">Title</span>\n          : <span class="black--text green lighten-4 px-2">Owner</span><span class="">RoleType</span>\n          : <span class="black--text green lighten-4 px-2">OWNER</span><span class="">LocationCity</span>\n          : <span class="black--text green lighten-4 px-2">Barcelona</span><span class="">Language</span>\n          : <span class="black--text green lighten-4 px-2">ES</span><span class="">Source</span>\n          : <span class="black--text green lighten-4 px-2">SALES_NAV</span><span class="">Status</span>\n          : <span class="black--text green lighten-4 px-2">NEW</span><span class="">Priority</span>\n          : <span class="black--text green lighten-4 px-2">HIGH</span><span class="">LeadScore</span>\n          : <span class="black--text green lighten-4 px-2">78</span><span class="">ScoreBreakdown</span>\n          : <span class="black--text green lighten-4 px-2">{"fit": 40, "maps": 28, "web": 10}</span><span class="">ScoringVersion</span>\n          : <span class="black--text green lighten-4 px-2">v1.0</span><span class="">WaitWindowDays</span>\n          : <span class="black--text green lighten-4 px-2">14</span><span class="">SignalChanged</span>\n          : <span class="black--text green lighten-4 px-2">false</span><span class="">DoNotContact</span>\n          : <span class="black--text green lighten-4 px-2">false</span><span class="">Email</span>\n          : <span class="black--text green lighten-4 px-2">carlos@talleresgarcia-test.com</span><span class="">Phone</span>\n          : <span class="black--text green lighten-4 px-2">+34 93 987 65 43</span>	2026-02-04 12:59:44+01	2026-02-04 12:59:44+01
adtgbg4y2nubrvl0t	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mcyckhd2a05m772	1	DATA	INSERT	\N	Record with ID 1 has been inserted into Table Attempt	<span class="">AttemptType</span>\n          : <span class="black--text green lighten-4 px-2">INVITE</span><span class="">Phase</span>\n          : <span class="black--text green lighten-4 px-2">INVITE</span><span class="">Result</span>\n          : <span class="black--text green lighten-4 px-2">SUCCESS</span><span class="">Reason</span>\n          : <span class="black--text green lighten-4 px-2">Invitación enviada sin problemas</span><span class="">Metadata</span>\n          : <span class="black--text green lighten-4 px-2">{"linkedin_status": "sent"}</span>	2026-02-04 12:59:44+01	2026-02-04 12:59:44+01
adt7tofz6xvdzm5cu	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mx1ud1d86w1d4y6	1	DATA	INSERT	\N	Record with ID 1 has been inserted into Table Approval	<span class="">Phase</span>\n          : <span class="black--text green lighten-4 px-2">FIRST_MESSAGE</span><span class="">DraftMessage</span>\n          : <span class="black--text green lighten-4 px-2">Hola Carlos, vi tu taller y me pareció muy profesional.</span><span class="">FinalMessage</span>\n          : <span class="black--text green lighten-4 px-2">Hola Carlos, vi tu taller en Barcelona y me impresionó la calidad.</span><span class="">Rationale</span>\n          : <span class="black--text green lighten-4 px-2">Mensaje personalizado basado en las señales de Google Places.</span><span class="">AngleQuality</span>\n          : <span class="black--text green lighten-4 px-2">GOOD</span><span class="">PainQuality</span>\n          : <span class="black--text green lighten-4 px-2">REAL</span><span class="">Note</span>\n          : <span class="black--text green lighten-4 px-2">Test approval</span><span class="">ApprovedBy</span>\n          : <span class="black--text green lighten-4 px-2">test_user</span>	2026-02-04 12:59:44+01	2026-02-04 12:59:44+01
adt4z25x5ydbfjsed	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mzvwidn4z544pas	1	DATA	INSERT	\N	Record with ID 1 has been inserted into Table Conversation	<span class="">State</span>\n          : <span class="black--text green lighten-4 px-2">ACTIVE</span><span class="">InterestLevel</span>\n          : <span class="black--text green lighten-4 px-2">WARM</span><span class="">Notes</span>\n          : <span class="black--text green lighten-4 px-2">Conversación de test activa</span>	2026-02-04 12:59:44+01	2026-02-04 12:59:44+01
adt8vbbl9v7qjmed2	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m4dhntou135vxm1	1	DATA	INSERT	\N	Record with ID 1 has been inserted into Table ResearchSnapshot	<span class="">Source</span>\n          : <span class="black--text green lighten-4 px-2">MIXED</span><span class="">Signals</span>\n          : <span class="black--text green lighten-4 px-2">{"web": "modern_tech", "places": "high_rating"}</span><span class="">SignalHash</span>\n          : <span class="black--text green lighten-4 px-2">sha256:snapshot_test_001</span>	2026-02-04 12:59:44+01	2026-02-04 12:59:44+01
adte0iwu1z19u9fd0	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m7d1wkpymm3kj7l	1	DATA	INSERT	\N	Record with ID 1 has been inserted into Table MessageTemplate	<span class="">TemplateKey</span>\n          : <span class="black--text green lighten-4 px-2">GUARDIAN_FIRST_TEST</span><span class="">Phase</span>\n          : <span class="black--text green lighten-4 px-2">FIRST_MESSAGE</span><span class="">Language</span>\n          : <span class="black--text green lighten-4 px-2">ES</span><span class="">TemplateText</span>\n          : <span class="black--text green lighten-4 px-2">Hola {{name}}, vi tu taller y me pareció {{signal}}.</span><span class="">Variables</span>\n          : <span class="black--text green lighten-4 px-2">["name", "signal"]</span><span class="">Version</span>\n          : <span class="black--text green lighten-4 px-2">1</span><span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">true</span><span class="">Notes</span>\n          : <span class="black--text green lighten-4 px-2">Template de test</span>	2026-02-04 12:59:44+01	2026-02-04 12:59:44+01
adtqhreowsxj6ccvz	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mp45w6rbyjyh6ks	1	DATA	INSERT	\N	Record with ID 1 has been inserted into Table Outcome	<span class="">Outcome</span>\n          : <span class="black--text green lighten-4 px-2">QUALIFIED</span><span class="">ValueEstimate</span>\n          : <span class="black--text green lighten-4 px-2">650</span><span class="">Notes</span>\n          : <span class="black--text green lighten-4 px-2">Test outcome — qualified lead</span>	2026-02-04 12:59:44+01	2026-02-04 12:59:44+01
adtg3m1sy4qqyycte	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m965eotz3l7hxbi	3	DATA	DELETE	\N	Record with ID 3 has been deleted in Table Pack	\N	2026-02-04 14:07:15+01	2026-02-04 14:07:15+01
adtm7hndu04vn4ena	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	merj80wv3zr0yzl	1	DATA	DELETE	\N	Record with ID 1 has been deleted in Table Company	\N	2026-02-04 14:07:23+01	2026-02-04 14:07:23+01
adtpwkirnlzxkp0od	gestionads15.21@gmail.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m965eotz3l7hxbi	4	DATA	INSERT	\N	Record with ID 4 has been inserted into Table Pack	<span class="">PackKey</span>\n          : <span class="black--text green lighten-4 px-2">GUARDIAN</span><span class="">Name</span>\n          : <span class="black--text green lighten-4 px-2">El Guardián</span><span class="">PriceMin</span>\n          : <span class="black--text green lighten-4 px-2">500</span><span class="">PriceMax</span>\n          : <span class="black--text green lighten-4 px-2">800</span><span class="">Description</span>\n          : <span class="black--text green lighten-4 px-2">Soporte operativo y continuidad para empresas sin IT interno.</span><span class="">IsActive</span>\n          : <span class="black--text green lighten-4 px-2">true</span><span class="">IcpRules</span>\n          : <span class="black--text green lighten-4 px-2">{"employees": "1-10", "no_it": true, "owner_non_technical": true}</span><span class="">ScoringWeights</span>\n          : <span class="black--text green lighten-4 px-2">{"fit": 40, "maps": 40, "web": 20}</span>	2026-02-04 14:08:28+01	2026-02-04 14:08:28+01
adtst5vlrlp1pu408	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m965eotz3l7hxbi	4	DATA	DELETE	\N	Record with ID 4 has been deleted in Table Pack	\N	2026-02-04 14:09:21+01	2026-02-04 14:09:21+01
adti2bgjghelauhop	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mx1ud1d86w1d4y6	2	DATA	INSERT	\N	Record with ID 2 has been inserted into Table Approval	\N	2026-02-04 14:28:12+01	2026-02-04 14:28:12+01
adt92rjit3lfc3fum	team@mailerblend.com	192.168.1.254	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mx1ud1d86w1d4y6	1	DATA	DELETE	\N	Record with ID 1 has been deleted in Table Approval	\N	2026-02-04 14:28:26+01	2026-02-04 14:28:26+01
\.


--
-- Data for Name: nc_base_users_v2; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public.nc_base_users_v2 (base_id, fk_user_id, roles, starred, pinned, "group", color, "order", hidden, opened_date, created_at, updated_at, invited_by) FROM stdin;
pata00z3me9f1bz	us8g4rajnw6fzr9r	owner	\N	\N	\N	\N	\N	\N	\N	2025-12-30 17:27:36+01	2025-12-30 17:27:36+01	\N
pbydkvvvbvv4pdf	us8g4rajnw6fzr9r	owner	\N	\N	\N	\N	\N	\N	\N	2026-02-03 10:56:38+01	2026-02-03 10:56:38+01	\N
pbydkvvvbvv4pdf	us5ceritq5sgzoni	creator	\N	\N	\N	\N	\N	\N	\N	2026-02-03 10:57:27+01	2026-02-03 10:57:27+01	us8g4rajnw6fzr9r
\.


--
-- Data for Name: nc_bases_v2; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public.nc_bases_v2 (id, title, prefix, status, description, meta, color, uuid, password, roles, deleted, is_meta, "order", created_at, updated_at) FROM stdin;
pata00z3me9f1bz	Getting Started	nc_fl6j__	\N	\N	{"iconColor":"#36BFFF"}	\N	\N	\N	\N	f	t	1	2025-12-30 17:27:36+01	2025-12-30 17:27:43+01
pbydkvvvbvv4pdf	LinkedIn Stealth Sourcing	nc_jmsd__	\N	\N	{"iconColor":"#36BFFF"}	\N	\N	\N	\N	f	t	2	2026-02-03 10:56:38+01	2026-02-03 10:56:38+01
\.


--
-- Data for Name: nc_calendar_view_columns_v2; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public.nc_calendar_view_columns_v2 (id, base_id, source_id, fk_view_id, fk_column_id, show, bold, underline, italic, "order", created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: nc_calendar_view_range_v2; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public.nc_calendar_view_range_v2 (id, fk_view_id, fk_to_column_id, label, fk_from_column_id, created_at, updated_at, base_id) FROM stdin;
\.


--
-- Data for Name: nc_calendar_view_v2; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public.nc_calendar_view_v2 (fk_view_id, base_id, source_id, title, fk_cover_image_col_id, meta, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: nc_col_barcode_v2; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public.nc_col_barcode_v2 (id, fk_column_id, fk_barcode_value_column_id, barcode_format, deleted, created_at, updated_at, base_id) FROM stdin;
\.


--
-- Data for Name: nc_col_button_v2; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public.nc_col_button_v2 (id, base_id, type, label, theme, color, icon, formula, formula_raw, error, parsed_tree, fk_webhook_id, fk_column_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: nc_col_formula_v2; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public.nc_col_formula_v2 (id, fk_column_id, formula, formula_raw, error, deleted, "order", created_at, updated_at, parsed_tree, base_id) FROM stdin;
\.


--
-- Data for Name: nc_col_lookup_v2; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public.nc_col_lookup_v2 (id, fk_column_id, fk_relation_column_id, fk_lookup_column_id, deleted, created_at, updated_at, base_id) FROM stdin;
\.


--
-- Data for Name: nc_col_qrcode_v2; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public.nc_col_qrcode_v2 (id, fk_column_id, fk_qr_value_column_id, deleted, "order", created_at, updated_at, base_id) FROM stdin;
\.


--
-- Data for Name: nc_col_relations_v2; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public.nc_col_relations_v2 (id, ref_db_alias, type, virtual, db_type, fk_column_id, fk_related_model_id, fk_child_column_id, fk_parent_column_id, fk_mm_model_id, fk_mm_child_column_id, fk_mm_parent_column_id, ur, dr, fk_index_name, deleted, created_at, updated_at, fk_target_view_id, base_id) FROM stdin;
lfy88l4tab8dnu0	\N	bt	t	\N	cvue26t4z7n6b1q	meivlfimb46wep7	c934u2vpzrym0lj	c5sbbie1xkxtt2i	\N	\N	\N	\N	\N	\N	\N	2026-01-06 20:54:00+01	2026-01-06 20:54:00+01	\N	pata00z3me9f1bz
lji3dfpz3ql4c4p	\N	hm	t	\N	cj43y361lmgcxkl	myz6dmx69dbmfod	c934u2vpzrym0lj	c5sbbie1xkxtt2i	\N	\N	\N	\N	\N	\N	\N	2026-01-06 20:54:00+01	2026-01-06 20:54:00+01	\N	pata00z3me9f1bz
lvgvg2h5f6399ho	\N	bt	t	\N	c465mwb9s8y839s	mn7w22ahohc9ngr	ckrhmyg1j9o8fib	cr9281rkz5dpit0	\N	\N	\N	\N	\N	\N	\N	2026-01-06 20:54:15+01	2026-01-06 20:54:15+01	\N	pata00z3me9f1bz
lrhkl1gcpr23uzm	\N	hm	t	\N	cgt60wb5h0npnoo	m2t8ts768utecu3	ckrhmyg1j9o8fib	cr9281rkz5dpit0	\N	\N	\N	\N	\N	\N	\N	2026-01-06 20:54:15+01	2026-01-06 20:54:15+01	\N	pata00z3me9f1bz
l28g9mqwgq5gwqw	\N	bt	t	\N	c6td8i4yv4e4w17	meivlfimb46wep7	c4gfmfo60vtwsg0	c5sbbie1xkxtt2i	\N	\N	\N	\N	\N	\N	\N	2026-01-06 20:54:35+01	2026-01-06 20:54:35+01	\N	pata00z3me9f1bz
lskpaszm6hgthp6	\N	hm	t	\N	cuzqnnl9qiyhlk3	m2t8ts768utecu3	c4gfmfo60vtwsg0	c5sbbie1xkxtt2i	\N	\N	\N	\N	\N	\N	\N	2026-01-06 20:54:35+01	2026-01-06 20:54:35+01	\N	pata00z3me9f1bz
lzc7b5zuvfupdb8	\N	bt	t	\N	c8un30eflpsel7t	myz6dmx69dbmfod	cjc1wrl7dln3hk7	cwp6ckygxgsesvz	\N	\N	\N	\N	\N	\N	\N	2026-01-06 20:55:02+01	2026-01-06 20:55:02+01	\N	pata00z3me9f1bz
ljbi2cpkxx4toxw	\N	hm	t	\N	c8z468hq9d6sy4x	m2t8ts768utecu3	cjc1wrl7dln3hk7	cwp6ckygxgsesvz	\N	\N	\N	\N	\N	\N	\N	2026-01-06 20:55:02+01	2026-01-06 20:55:02+01	\N	pata00z3me9f1bz
lvwfltymdpfb0sw	\N	\N	\N	\N	ceui606d8jwe9ju	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	pbydkvvvbvv4pdf
lul3ibzw1rwxhb9	\N	\N	\N	\N	cymxw81qe37t06b	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	pbydkvvvbvv4pdf
lwai72g4ufy0chw	\N	\N	\N	\N	c6pmtlu10bgqi8e	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	pbydkvvvbvv4pdf
l9jrjssw18imvp7	\N	\N	\N	\N	c8a52kfs7igesr6	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	pbydkvvvbvv4pdf
ls4wzatmshdb27d	\N	\N	\N	\N	c0b6kxkcmknrmbz	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	pbydkvvvbvv4pdf
lw6fag8yi8tkbuk	\N	\N	\N	\N	c74e36i29wlgw2m	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	pbydkvvvbvv4pdf
l7f7ptm0kl2gj88	\N	\N	\N	\N	co17kfo1sg603dy	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	pbydkvvvbvv4pdf
ltolsvio73nxe5j	\N	\N	\N	\N	cgmp5gcjcaqzkzw	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	pbydkvvvbvv4pdf
l1o7vwsnzzch1ha	\N	\N	\N	\N	clya1e8vpxtnusj	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	pbydkvvvbvv4pdf
lz6lyc0bzs5zg94	\N	\N	\N	\N	cp68n1hirgxg4ac	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	pbydkvvvbvv4pdf
lh79gw85698w868	\N	\N	\N	\N	cl48g3sz3gwkigd	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	pbydkvvvbvv4pdf
lv9dmfmsklg0k9y	\N	\N	\N	\N	chbafyj23t8h3t8	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	\N	pbydkvvvbvv4pdf
l4ydchccfa31iu2	\N	\N	\N	\N	c2gc3o7nudv7tb8	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	\N	pbydkvvvbvv4pdf
lmv028v9oyq8hzg	\N	\N	\N	\N	chahes6qex1hndj	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	\N	pbydkvvvbvv4pdf
\.


--
-- Data for Name: nc_col_rollup_v2; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public.nc_col_rollup_v2 (id, fk_column_id, fk_relation_column_id, fk_rollup_column_id, rollup_function, deleted, created_at, updated_at, base_id) FROM stdin;
\.


--
-- Data for Name: nc_col_select_options_v2; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public.nc_col_select_options_v2 (id, fk_column_id, title, color, "order", created_at, updated_at, base_id) FROM stdin;
s4nps7l0jbr96bt	cuk8msv9e01r5qs	Pyme	#cfdffe	1	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	pata00z3me9f1bz
s4atezivzopb9cl	cuk8msv9e01r5qs	Agencia	#d0f1fd	2	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	pata00z3me9f1bz
s8xu7cwjiclunhj	cuk8msv9e01r5qs	Emprendedor	#c2f5e8	3	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	pata00z3me9f1bz
stsc8clykwvgjb9	cuk8msv9e01r5qs	Startup	#ffdaf6	4	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	pata00z3me9f1bz
sfkv9jkq2e5ic58	c99gznqsho81qmc	No lo tengo claro	#cfdffe	1	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	pata00z3me9f1bz
scu9lesahy0jw19	c99gznqsho81qmc	Desarrollo web y software a medida	#d0f1fd	2	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	pata00z3me9f1bz
s4b4341p9wdhaa3	c99gznqsho81qmc	Cloud & DevOps	#c2f5e8	3	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	pata00z3me9f1bz
smjrt7ko8182sjl	c99gznqsho81qmc	SRE / Observabilidad	#ffdaf6	4	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	pata00z3me9f1bz
sdrx4462loetvnv	c99gznqsho81qmc	Infraestructura gestionada	#ffdce5	5	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	pata00z3me9f1bz
sy9eujtvtkhz6iq	c99gznqsho81qmc	Integraciones / Automatización	#fee2d5	6	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	pata00z3me9f1bz
sthv3lxf8yq8brp	c99gznqsho81qmc	Outsourcing IT / CAU	#ffeab6	7	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	pata00z3me9f1bz
sla2sg8wfng3hna	cc9lfl109mgesga	Google / Buscador	#cfdffe	1	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	pata00z3me9f1bz
stsigsdo11mkebe	cc9lfl109mgesga	Google Ads	#d0f1fd	2	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	pata00z3me9f1bz
sls1o5nqjp71gfa	cc9lfl109mgesga	Bing Ads	#c2f5e8	3	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	pata00z3me9f1bz
skmbmvz7tbesqls	cc9lfl109mgesga	LinkedIn	#ffdaf6	4	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	pata00z3me9f1bz
solmundtz4axihs	cc9lfl109mgesga	Recomendación de un conocido	#ffdce5	5	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	pata00z3me9f1bz
so2qlu8tuvqog7x	cc9lfl109mgesga	Redes sociales	#fee2d5	6	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	pata00z3me9f1bz
sqtbatseu7zcbyr	cc9lfl109mgesga	Directorio o listado	#ffeab6	7	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	pata00z3me9f1bz
soe40mdcn3ul4ni	cc9lfl109mgesga	Ya habíamos trabajado antes	#d1f7c4	8	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	pata00z3me9f1bz
s1ubn14e0hbwheh	cc9lfl109mgesga	Otro	#ede2fe	9	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	pata00z3me9f1bz
s7nuxlk5kemvxjh	cmb9fgozmqj7j32	Formulario web	#cfdffe	1	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	pata00z3me9f1bz
s9rk58jktyfv6uf	cmb9fgozmqj7j32	Llamada telefónica	#d0f1fd	2	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	pata00z3me9f1bz
srhqworejp97ttg	cmb9fgozmqj7j32	Email directo	#c2f5e8	3	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	pata00z3me9f1bz
su89tlmf8uaswuy	cmb9fgozmqj7j32	WhatsApp	#ffdaf6	4	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	pata00z3me9f1bz
sr4ftm9r96npwnf	cmb9fgozmqj7j32	Manual	#ffdce5	5	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	pata00z3me9f1bz
s0dbz6gf4ad5drc	cc8mbs6beegxb27	Nuevo	#cfdffe	1	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	pata00z3me9f1bz
s4r5sxk0qgmam1a	cc8mbs6beegxb27	En contacto	#d0f1fd	2	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	pata00z3me9f1bz
swcnh3xrdlxqz56	cc8mbs6beegxb27	Presupuesto enviado	#c2f5e8	3	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	pata00z3me9f1bz
sjk0i2c8uqp2fn9	cc8mbs6beegxb27	Ganado	#ffdaf6	4	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	pata00z3me9f1bz
sn4f7zthlp5uvf8	cc8mbs6beegxb27	Perdido	#ffdce5	5	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	pata00z3me9f1bz
sbdzamzdav4i6r5	cp2i3cj0wlu3nyj	Alta	#cfdffe	1	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	pata00z3me9f1bz
swqiq6arwcsz8we	cp2i3cj0wlu3nyj	Media	#d0f1fd	2	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	pata00z3me9f1bz
suu2jrgpvbgurl3	cp2i3cj0wlu3nyj	Baja	#c2f5e8	3	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	pata00z3me9f1bz
sodoq6hxtpc417h	c3qulrp5ivk3s7i	Hot	#cfdffe	1	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	pata00z3me9f1bz
s6utqk7h8o8rq8g	c3qulrp5ivk3s7i	Warm	#d0f1fd	2	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	pata00z3me9f1bz
s3uoz6c70nicr6s	c3qulrp5ivk3s7i	Cold	#c2f5e8	3	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	pata00z3me9f1bz
sfh0wqhql49jzh4	c3qulrp5ivk3s7i	Qualified	#ffdaf6	4	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	pata00z3me9f1bz
sfwixtsc34tvdjg	c3qulrp5ivk3s7i	Unqualified	#ffdce5	5	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	pata00z3me9f1bz
sfsdotgb2u6eg28	c6i5br252s0bzjk	SEND_EMAIL	#cfdffe	1	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	pata00z3me9f1bz
s7gxbd4duqcok2w	c6i5br252s0bzjk	CALL	#d0f1fd	2	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	pata00z3me9f1bz
sklfn4dbytavfs3	c6i5br252s0bzjk	BOOK_MEETING	#c2f5e8	3	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	pata00z3me9f1bz
sr56zfd5tev4j0j	c6i5br252s0bzjk	NO_ACTION	#ffdaf6	4	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	pata00z3me9f1bz
syahw7efxhyzbmt	cl3mje9g06ndmn2	Sales Team	#cfdffe	1	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	pata00z3me9f1bz
sx4efxwvyfgvpcy	cl3mje9g06ndmn2	Support	#d0f1fd	2	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	pata00z3me9f1bz
sjdz9inxzr7ufnx	cl3mje9g06ndmn2	Management	#c2f5e8	3	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	pata00z3me9f1bz
sp1l8p97vr1su0l	cg9k96mozj92dk6	Precio	#cfdffe	1	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	pata00z3me9f1bz
suiaaxdjn5f0saf	cg9k96mozj92dk6	Sin respuesta	#d0f1fd	2	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	pata00z3me9f1bz
skyqsbkqmm81hbg	cg9k96mozj92dk6	Competencia	#c2f5e8	3	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	pata00z3me9f1bz
sy5wvekz0eu1lri	cg9k96mozj92dk6	No cualificado	#ffdaf6	4	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	pata00z3me9f1bz
sbc24dhtccjtomf	cg9k96mozj92dk6	Timing	#ffdce5	5	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	pata00z3me9f1bz
s0ka78h9avjkvf6	cg9k96mozj92dk6	Otro	#fee2d5	6	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	pata00z3me9f1bz
spc0n7ehoe6kzha	c9t1uu106dq5r8g	No lo tengo claro	#cfdffe	1	2026-01-06 20:52:52+01	2026-01-06 20:52:52+01	pata00z3me9f1bz
slshzsgzw84m3dx	c9t1uu106dq5r8g	Desarrollo web y software a medida	#d0f1fd	2	2026-01-06 20:52:52+01	2026-01-06 20:52:52+01	pata00z3me9f1bz
si23tl4bscs5aj1	c9t1uu106dq5r8g	Cloud & DevOps	#c2f5e8	3	2026-01-06 20:52:52+01	2026-01-06 20:52:52+01	pata00z3me9f1bz
stt7or9d0nxt4tl	c9t1uu106dq5r8g	SRE / Observabilidad	#ffdaf6	4	2026-01-06 20:52:52+01	2026-01-06 20:52:52+01	pata00z3me9f1bz
se4ub6imxd1x8fd	c9t1uu106dq5r8g	Infraestructura gestionada	#ffdce5	5	2026-01-06 20:52:52+01	2026-01-06 20:52:52+01	pata00z3me9f1bz
s0lidht40kp225k	c9t1uu106dq5r8g	Integraciones / Automatización	#fee2d5	6	2026-01-06 20:52:52+01	2026-01-06 20:52:52+01	pata00z3me9f1bz
shu5qsjra2r98cy	c9t1uu106dq5r8g	Outsourcing IT / CAU	#ffeab6	7	2026-01-06 20:52:52+01	2026-01-06 20:52:52+01	pata00z3me9f1bz
sis1dy81s0fvb6z	cl01772wjt5jlgc	select	#cfdffe	1	2026-01-06 20:52:52+01	2026-01-06 20:52:52+01	pata00z3me9f1bz
srj6yeunr4572ln	cl01772wjt5jlgc	text	#d0f1fd	2	2026-01-06 20:52:52+01	2026-01-06 20:52:52+01	pata00z3me9f1bz
s6rwd4j72g0zpjz	cb8doj0zxeltv44	Automocion	#cfdffe	1	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
sxkq99umtlydvtt	cb8doj0zxeltv44	Agencia_Marketing	#d0f1fd	2	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
s2hhklx6ef8hys2	cb8doj0zxeltv44	Agencia_Digital	#c2f5e8	3	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
sp7o2k2hyf1s3gx	cb8doj0zxeltv44	Tecnologia	#ffdaf6	4	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
sixcs9cz7tkqhdp	cb8doj0zxeltv44	Logistica	#ffdce5	5	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
sg09bje1fgxo9j1	cb8doj0zxeltv44	eCommerce	#fee2d5	6	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
skaqgsxvacsv56s	cb8doj0zxeltv44	Consultoria	#ffeab6	7	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
sk2j74xdf4po5ef	cb8doj0zxeltv44	Servicios_Profesionales	#d1f7c4	8	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
s24imdpzp8xd665	cb8doj0zxeltv44	Industria_Manufactura	#ede2fe	9	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
syk1zrewt6s6zdr	cb8doj0zxeltv44	Sanidad	#eeeeee	10	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
skeq6igqpe9hqtw	cb8doj0zxeltv44	Educacion	#cfdffe	11	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
sfptvgr40n77bj2	cb8doj0zxeltv44	Alimentacion	#d0f1fd	12	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
sva4nz34fv46mk6	cb8doj0zxeltv44	Construccion	#c2f5e8	13	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
sozxpfjrund9jfc	cb8doj0zxeltv44	Finanzas	#ffdaf6	14	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
scfagkag68e7gqc	cb8doj0zxeltv44	Otro	#ffdce5	15	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
sjs4w1nwhorkt77	c1mi3f7wfd8m9cj	1-10	#cfdffe	1	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
slih47yiurpgvw4	c1mi3f7wfd8m9cj	8-25	#d0f1fd	2	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
sm2kqjrcrlwrja8	c1mi3f7wfd8m9cj	20-50	#c2f5e8	3	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
sqqpnlhwwhje4cf	c1mi3f7wfd8m9cj	50-200	#ffdaf6	4	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
sssvxcwzs6abky4	c1mi3f7wfd8m9cj	200+	#ffdce5	5	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
s2f6tzq6fnht4hk	c1mi3f7wfd8m9cj	UNKNOWN	#fee2d5	6	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
scef7oluufxsis5	cwy90uck7umcg8k	150-600k	#cfdffe	1	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
suo27ywx7vq0zm2	cwy90uck7umcg8k	500k-2M	#d0f1fd	2	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
sux4o648czoc5gc	cwy90uck7umcg8k	1M+	#c2f5e8	3	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
s9zc42prybpjcep	cwy90uck7umcg8k	UNKNOWN	#ffdaf6	4	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
slksynwwn8niz40	cqvpzsa7muzvahe	INVITE_SEED	#cfdffe	1	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
s5r72ms9ae9z9e8	cqvpzsa7muzvahe	FIRST_MESSAGE	#d0f1fd	2	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
skw4330vsr5ftps	cqvpzsa7muzvahe	FOLLOWUP_1	#c2f5e8	3	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
sfhpyodv6yh63gq	cqvpzsa7muzvahe	FOLLOWUP_2	#ffdaf6	4	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
snklmvx7vxchcms	cqvpzsa7muzvahe	CTA	#ffdce5	5	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
su6425it87megju	czufc759mmzmzte	ES	#cfdffe	1	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
skikkzs64nqddyc	czufc759mmzmzte	EN	#d0f1fd	2	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
svw4diao4gv4n62	ca4lddk146v74zd	INVITE	#cfdffe	1	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
shzwa4r8jd9z4eg	ca4lddk146v74zd	MESSAGE	#d0f1fd	2	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
spj2bw6x023y6tz	ca4lddk146v74zd	RESEARCH	#c2f5e8	3	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
szom0yuk8oycweg	ca4lddk146v74zd	SIGNAL_CHECK	#ffdaf6	4	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
sh9h18y7kr3wi1e	ca4lddk146v74zd	OTHER	#ffdce5	5	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
sjtr8f32kio5u6g	ciar62fx5ef6659	INVITE	#cfdffe	1	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
skwyxids8fazg16	ciar62fx5ef6659	POST_ACCEPT_RESEARCH	#d0f1fd	2	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
s7wwi1qkzgbsszi	ciar62fx5ef6659	DRAFT	#c2f5e8	3	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
s88q39dlt99me0u	ciar62fx5ef6659	FOLLOWUP	#ffdaf6	4	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
sjm2tcqscnvhesg	ciar62fx5ef6659	CTA	#ffdce5	5	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
s6ftal0qgjvo8bw	c6uwnbjl1r5mju0	SUCCESS	#cfdffe	1	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
soypt1tsbt2rv6w	c6uwnbjl1r5mju0	SKIPPED	#d0f1fd	2	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
splo9lnmkqqhbeh	c6uwnbjl1r5mju0	FAILED	#c2f5e8	3	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
socb99d41tmfka6	c6uwnbjl1r5mju0	BLOCKED	#ffdaf6	4	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
sux468opx8qt9c1	c69gbr33uorqy7r	INVITE_SEED	#cfdffe	1	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
seibd1nlalis93v	c69gbr33uorqy7r	FIRST_MESSAGE	#d0f1fd	2	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
slubjcyjyk40oxa	c69gbr33uorqy7r	FOLLOWUP_1	#c2f5e8	3	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
smidvadhs42z1f0	c69gbr33uorqy7r	FOLLOWUP_2	#ffdaf6	4	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
syxggs4635k70s2	c69gbr33uorqy7r	CTA	#ffdce5	5	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
sygsyrkpxkf1rr3	colzu9quxnxbnh8	GOOD	#cfdffe	1	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
slttfpz77lavlcr	colzu9quxnxbnh8	OK	#d0f1fd	2	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
s3urb5mi8a0bhh7	colzu9quxnxbnh8	WRONG	#c2f5e8	3	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
soqt2riq0ee5nqm	cjmxnucuwdti0ov	REAL	#cfdffe	1	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
suy7s7p7es3jcob	cjmxnucuwdti0ov	SUPERFICIAL	#d0f1fd	2	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
s3a7n7ych51h3b3	cjmxnucuwdti0ov	INVENTED	#c2f5e8	3	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
ss0ubwqw4m8crfx	c2nn1lgezk2u5xy	NOT_STARTED	#cfdffe	1	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	pbydkvvvbvv4pdf
sw7ws4we1gi1w6g	c2nn1lgezk2u5xy	ACTIVE	#d0f1fd	2	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	pbydkvvvbvv4pdf
st2xu4dziag10tk	c2nn1lgezk2u5xy	PAUSED	#c2f5e8	3	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	pbydkvvvbvv4pdf
sl8sa3w9ea4akwp	c2nn1lgezk2u5xy	CLOSED	#ffdaf6	4	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	pbydkvvvbvv4pdf
si9ymsgi9juaq7x	cnn563xrm5wws3c	COLD	#cfdffe	1	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	pbydkvvvbvv4pdf
s951bukh7yerqz5	cnn563xrm5wws3c	WARM	#d0f1fd	2	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	pbydkvvvbvv4pdf
spbs3ugbpfvg6u7	cnn563xrm5wws3c	HOT	#c2f5e8	3	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	pbydkvvvbvv4pdf
ssc214my9v5pb1h	chwey76orqjoarm	QUALIFIED	#cfdffe	1	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	pbydkvvvbvv4pdf
sqzbkg8f1vuxcja	chwey76orqjoarm	NOT_FIT	#d0f1fd	2	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	pbydkvvvbvv4pdf
sk1grs6xsbzv54j	chwey76orqjoarm	NO_SHOW	#c2f5e8	3	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	pbydkvvvbvv4pdf
st87clqhlfegnh6	chwey76orqjoarm	FOLLOW_UP	#ffdaf6	4	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	pbydkvvvbvv4pdf
syoyaoussadh87r	chwey76orqjoarm	WON	#ffdce5	5	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	pbydkvvvbvv4pdf
s88a1tr08s6syjo	chwey76orqjoarm	LOST	#fee2d5	6	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	pbydkvvvbvv4pdf
sqxnrcmbnbbyw9m	cxgi277ii77m5fy	AB_TEST	#cfdffe	1	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
sb56r0o7zvrnqu5	cxgi277ii77m5fy	ALWAYS_ON	#d0f1fd	2	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
s2lkcaag3q2tp7x	cxgi277ii77m5fy	ONE_OFF	#c2f5e8	3	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
svldsyzodd2x3a4	colbujailyyr19l	RUNNING	#cfdffe	1	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
s10f1it8b44s6m6	colbujailyyr19l	PAUSED	#d0f1fd	2	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
s3pz42ks2sehvwk	colbujailyyr19l	FINISHED	#c2f5e8	3	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
sp1erltijk2yzln	czcjput7b3iz3qu	OWNER	#cfdffe	1	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
s8a2glht9vh6ibs	czcjput7b3iz3qu	CEO	#d0f1fd	2	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
so7rnw8erozw50g	czcjput7b3iz3qu	CTO	#c2f5e8	3	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
si2un1q5wr38frn	czcjput7b3iz3qu	IT_MANAGER	#ffdaf6	4	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
sryzhow9xrr3gqs	czcjput7b3iz3qu	OPS	#ffdce5	5	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
sucov0pzat5xob8	czcjput7b3iz3qu	OTHER	#fee2d5	6	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
syyr7koxxg8761y	czcjput7b3iz3qu	UNKNOWN	#ffeab6	7	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
sj50l9dtgemf9md	cn8plh9xmxlf1sd	ES	#cfdffe	1	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
s4f8cm622xfpr74	cn8plh9xmxlf1sd	EN	#d0f1fd	2	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
s8dnvrgg5xosbbz	cn8plh9xmxlf1sd	UNKNOWN	#c2f5e8	3	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
spl6b4cck3v24l8	cljj6490e5wy0z1	SALES_NAV	#cfdffe	1	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
so6iw6gqmc83w96	cljj6490e5wy0z1	GOOGLE	#d0f1fd	2	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
s63s4rgy4ligqhi	cljj6490e5wy0z1	LINKEDIN_SEARCH	#c2f5e8	3	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
s47svdet7o5usp2	cljj6490e5wy0z1	REFERRAL	#ffdaf6	4	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
s0yuosrfyw62636	cljj6490e5wy0z1	MANUAL	#ffdce5	5	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
sg2jh2te2jutv99	c6w114nfydog3o6	NEW	#cfdffe	1	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
sd3rqn5v60775xp	c6w114nfydog3o6	INVITE_QUEUED	#d0f1fd	2	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
sxt4evbd6chr5v9	c6w114nfydog3o6	INVITE_SENT	#c2f5e8	3	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
scd43zzzhch6360	c6w114nfydog3o6	PENDING	#ffdaf6	4	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
se8eln3b52614vm	c6w114nfydog3o6	NO_ACCEPT	#ffdce5	5	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
st76sm92112araw	c6w114nfydog3o6	ACCEPTED	#fee2d5	6	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
sxjehq370eyz8np	c6w114nfydog3o6	RESEARCH_READY	#ffeab6	7	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
sqza38g03d5xex0	c6w114nfydog3o6	DRAFT_READY	#d1f7c4	8	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
sjborizbgxbgmjv	c6w114nfydog3o6	AWAITING_APPROVAL	#ede2fe	9	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
ssnxazsh1lfje2w	c6w114nfydog3o6	MESSAGE_SENT	#eeeeee	10	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
s4vn9fw1086fkzz	c6w114nfydog3o6	CONVO_ACTIVE	#cfdffe	11	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
shmht8g5hmc93z9	c6w114nfydog3o6	CTA_READY	#d0f1fd	12	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
sb2a7n1kt7kaydq	c6w114nfydog3o6	BOOKED	#c2f5e8	13	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
senmibtkcgc4od1	c6w114nfydog3o6	RECYCLE_RETRY	#ffdaf6	14	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
sf9hqv1ortg20ky	c6w114nfydog3o6	ENGAGE_LATER	#ffdce5	15	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
shm2fa7bxxp4nbt	c6w114nfydog3o6	ARCHIVED	#fee2d5	16	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
sl5e47jzt05kei0	c6w114nfydog3o6	BLOCKED_OR_RESTRICTED	#ffeab6	17	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
sc4rtp2dar4unwx	cef82lzbg01fuhc	LOW	#cfdffe	1	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
sraz47qslcem14w	cef82lzbg01fuhc	MEDIUM	#d0f1fd	2	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
szp2mrmoa9xf683	cef82lzbg01fuhc	HIGH	#c2f5e8	3	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
s68th12dm0df824	cgk7qg876t5xi2y	WEB	#cfdffe	1	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
ste8htyuybf3t31	cgk7qg876t5xi2y	PLACES	#d0f1fd	2	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
sf27uhelxp5v4f0	cgk7qg876t5xi2y	LINKEDIN	#c2f5e8	3	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
sawkwu5ausu9ilu	cgk7qg876t5xi2y	MIXED	#ffdaf6	4	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	pbydkvvvbvv4pdf
\.


--
-- Data for Name: nc_columns_v2; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public.nc_columns_v2 (id, source_id, base_id, fk_model_id, title, column_name, uidt, dt, np, ns, clen, cop, pk, pv, rqd, un, ct, ai, "unique", cdf, cc, csn, dtx, dtxp, dtxs, au, validate, virtual, deleted, system, "order", created_at, updated_at, meta, description) FROM stdin;
cr9281rkz5dpit0	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	ID	id	ID	int4	\N	\N	\N	\N	t	\N	t	t	\N	t	\N	\N	\N	\N	specificType	\N	\N	\N	\N	\N	\N	\N	1	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	\N	\N
cgvkav0m3p12am0	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	Nombre	nombre	SingleLineText	text	\N	\N	\N	\N	f	t	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	2	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	\N	\N
cp08sylckll5u64	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	Email	email	Email	character varying	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType	\N	\N	\N	{"func":["isEmail"],"args":[""],"msg":["Validation failed : isEmail"]}	\N	\N	\N	4	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	\N	\N
ctd95pigwvohwlr	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	Teléfono	telefono	PhoneNumber	character varying	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType	\N	\N	\N	{"func":["isMobilePhone"],"args":[""],"msg":["Validation failed : isMobilePhone"]}	\N	\N	\N	5	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	\N	\N
cuk8msv9e01r5qs	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	Tipo Empresa	tipo_empresa	SingleSelect	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType	Pyme,Agencia,Emprendedor,Startup	 	\N	\N	\N	\N	\N	6	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	\N	\N
chtewf19yconvxc	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m965eotz3l7hxbi	Id	Id	ID	int4	\N	\N	\N	\N	t	\N	t	t	\N	t	\N	\N	\N	\N	specificType	\N	\N	\N	\N	\N	\N	\N	1	2026-02-04 12:53:39+01	2026-02-04 12:53:39+01	\N	\N
c99gznqsho81qmc	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	Servicio	servicio	SingleSelect	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType	No lo tengo claro,Desarrollo web y software a medida,Cloud & DevOps,SRE / Observabilidad,Infraestructura gestionada,Integraciones / Automatización,Outsourcing IT / CAU	 	\N	\N	\N	\N	\N	8	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	\N	\N
cwvrczahkii68gx	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	Extra Información	extra_informacion	SingleLineText	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	9	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	\N	\N
cc9lfl109mgesga	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	Cómo nos conociste	como_nos_conociste	SingleSelect	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType	Google / Buscador,Google Ads,Bing Ads,LinkedIn,Recomendación de un conocido,Redes sociales,Directorio o listado,Ya habíamos trabajado antes,Otro	 	\N	\N	\N	\N	\N	10	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	\N	\N
cgw3j8nn4o6w285	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	Mensaje	mensaje	LongText	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	11	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	\N	\N
cmb9fgozmqj7j32	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	Origen Lead	origen_lead	SingleSelect	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	Formulario web	\N	\N	specificType	Formulario web,Llamada telefónica,Email directo,WhatsApp,Manual	 	\N	\N	\N	\N	\N	12	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	\N	\N
cc8mbs6beegxb27	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	Estado	estado	SingleSelect	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	Nuevo	\N	\N	specificType	Nuevo,En contacto,Presupuesto enviado,Ganado,Perdido	 	\N	\N	\N	\N	\N	13	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	{"options":[{"title":"Nuevo","color":"gray"},{"title":"En contacto","color":"blue"},{"title":"Presupuesto enviado","color":"orange"},{"title":"Ganado","color":"green"},{"title":"Perdido","color":"red"}]}	\N
cp2i3cj0wlu3nyj	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	Prioridad	prioridad	SingleSelect	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	Media	\N	\N	specificType	Alta,Media,Baja	 	\N	\N	\N	\N	\N	14	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	{"options":[{"title":"Alta","color":"red"},{"title":"Media","color":"yellow"},{"title":"Baja","color":"green"}]}	\N
cv46emwmskabko2	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	Notas Internas	notas_internas	LongText	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	15	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	\N	\N
c3qulrp5ivk3s7i	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	Lead Tag	lead_tag	SingleSelect	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType	Hot,Warm,Cold,Qualified,Unqualified	 	\N	\N	\N	\N	\N	16	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	\N	\N
c6i5br252s0bzjk	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	Next Action	next_action	SingleSelect	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	NO_ACTION	\N	\N	specificType	SEND_EMAIL,CALL,BOOK_MEETING,NO_ACTION	 	\N	\N	\N	\N	\N	17	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	{"options":[{"title":"SEND_EMAIL","color":"blue"},{"title":"CALL","color":"purple"},{"title":"BOOK_MEETING","color":"green"},{"title":"NO_ACTION","color":"gray"}]}	\N
cdld42bch58tzqh	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	Next Action Key	next_action_key	SingleLineText	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	18	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	\N	\N
cl3mje9g06ndmn2	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	Owner	owner	SingleSelect	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType	Sales Team,Support,Management	 	\N	\N	\N	\N	\N	19	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	\N	\N
cf4e69f6gwxlkoq	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	Next Followup At	next_followup_at	Date	date	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	21	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	\N	\N
cg9k96mozj92dk6	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	Lost Reason	lost_reason	SingleSelect	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType	Precio,Sin respuesta,Competencia,No cualificado,Timing,Otro	 	\N	\N	\N	\N	\N	22	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	\N	\N
cmbr44eh8sa4vqr	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	GDPR Consent	gdpr_consent	Checkbox	bool	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	false	\N	\N	specificType	\N	\N	\N	\N	\N	\N	\N	23	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	\N	\N
cet31zg1mkv51cp	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	CreatedAt	created_at	CreatedTime	timestamp	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	t	24	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	\N	\N
ccruq72xe2bhg9s	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	UpdatedAt	updated_at	LastModifiedTime	timestamp	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	t	25	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	\N	\N
cubtjoi22fwjko5	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	nc_created_by	created_by	CreatedBy	character varying	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType	\N	\N	\N	\N	\N	\N	t	26	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	\N	\N
c59z1eqsvpdl2os	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	nc_updated_by	updated_by	LastModifiedBy	character varying	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType	\N	\N	\N	\N	\N	\N	t	27	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	\N	\N
c5sbbie1xkxtt2i	bb4syuyu7fz1t03	pata00z3me9f1bz	meivlfimb46wep7	ID	id	ID	int4	\N	\N	\N	\N	t	\N	t	t	\N	t	\N	\N	\N	\N	specificType	\N	\N	\N	\N	\N	\N	\N	1	2026-01-06 20:52:52+01	2026-01-06 20:52:52+01	\N	\N
c9t1uu106dq5r8g	bb4syuyu7fz1t03	pata00z3me9f1bz	meivlfimb46wep7	Service	service	SingleSelect	text	\N	\N	\N	\N	f	t	f	f	\N	f	\N	\N	\N	\N	specificType	No lo tengo claro,Desarrollo web y software a medida,Cloud & DevOps,SRE / Observabilidad,Infraestructura gestionada,Integraciones / Automatización,Outsourcing IT / CAU	 	\N	\N	\N	\N	\N	2	2026-01-06 20:52:52+01	2026-01-06 20:52:52+01	\N	\N
crrv0yg28skccm7	bb4syuyu7fz1t03	pata00z3me9f1bz	meivlfimb46wep7	Question Label	question_label	SingleLineText	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	3	2026-01-06 20:52:52+01	2026-01-06 20:52:52+01	\N	\N
cl01772wjt5jlgc	bb4syuyu7fz1t03	pata00z3me9f1bz	meivlfimb46wep7	Input Type	input_type	SingleSelect	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType	select,text	 	\N	\N	\N	\N	\N	4	2026-01-06 20:52:52+01	2026-01-06 20:52:52+01	\N	\N
cw4yqjlz0a5ykcr	bb4syuyu7fz1t03	pata00z3me9f1bz	meivlfimb46wep7	Is Enabled	is_enabled	Checkbox	bool	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	true	\N	\N	specificType	\N	\N	\N	\N	\N	\N	\N	5	2026-01-06 20:52:52+01	2026-01-06 20:52:52+01	\N	\N
cmw4y8risbmn1do	bb4syuyu7fz1t03	pata00z3me9f1bz	meivlfimb46wep7	CreatedAt	created_at	CreatedTime	timestamp	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	t	6	2026-01-06 20:52:52+01	2026-01-06 20:52:52+01	\N	\N
c89acu3i27bt46g	bb4syuyu7fz1t03	pata00z3me9f1bz	meivlfimb46wep7	UpdatedAt	updated_at	LastModifiedTime	timestamp	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	t	7	2026-01-06 20:52:52+01	2026-01-06 20:52:52+01	\N	\N
cdbtq91lgdbjnbd	bb4syuyu7fz1t03	pata00z3me9f1bz	meivlfimb46wep7	nc_created_by	created_by	CreatedBy	character varying	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType	\N	\N	\N	\N	\N	\N	t	8	2026-01-06 20:52:52+01	2026-01-06 20:52:52+01	\N	\N
cu8xmyiq6x3rmfh	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	Entrada	entrada	Date	date	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N		\N	\N	\N	3	2026-01-06 20:52:25+01	2026-01-06 23:35:02+01	{"date_format":"MM-DD-YYYY","defaultViewColOrder":3}	\N
c8c370ltnjqswxz	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	Last Contact At	last_contact_at	Date	date	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N		\N	\N	\N	20	2026-01-06 20:52:25+01	2026-01-06 23:40:32+01	{"date_format":"MM-DD-YYYY","defaultViewColOrder":20}	\N
c33zx14ye4cipd5	bb4syuyu7fz1t03	pata00z3me9f1bz	meivlfimb46wep7	nc_updated_by	updated_by	LastModifiedBy	character varying	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType	\N	\N	\N	\N	\N	\N	t	9	2026-01-06 20:52:52+01	2026-01-06 20:52:52+01	\N	\N
cwp6ckygxgsesvz	bb4syuyu7fz1t03	pata00z3me9f1bz	myz6dmx69dbmfod	ID	id	ID	int4	\N	\N	\N	\N	t	\N	t	t	\N	t	\N	\N	\N	\N	specificType	\N	\N	\N	\N	\N	\N	\N	1	2026-01-06 20:53:13+01	2026-01-06 20:53:13+01	\N	\N
cay37dugmu28m2j	bb4syuyu7fz1t03	pata00z3me9f1bz	myz6dmx69dbmfod	Option Label	option_label	SingleLineText	text	\N	\N	\N	\N	f	t	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	2	2026-01-06 20:53:13+01	2026-01-06 20:53:13+01	\N	\N
c3da2q5oxv24clf	bb4syuyu7fz1t03	pata00z3me9f1bz	myz6dmx69dbmfod	Sort Order	sort_order	Number	bigint	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	3	2026-01-06 20:53:13+01	2026-01-06 20:53:13+01	\N	\N
cgy3oh2cpo9y9x5	bb4syuyu7fz1t03	pata00z3me9f1bz	myz6dmx69dbmfod	CreatedAt	created_at	CreatedTime	timestamp	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	t	4	2026-01-06 20:53:13+01	2026-01-06 20:53:13+01	\N	\N
cphzo0atiai403o	bb4syuyu7fz1t03	pata00z3me9f1bz	myz6dmx69dbmfod	UpdatedAt	updated_at	LastModifiedTime	timestamp	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	t	5	2026-01-06 20:53:13+01	2026-01-06 20:53:13+01	\N	\N
c7r51y404tyqcy3	bb4syuyu7fz1t03	pata00z3me9f1bz	myz6dmx69dbmfod	nc_created_by	created_by	CreatedBy	character varying	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType	\N	\N	\N	\N	\N	\N	t	6	2026-01-06 20:53:13+01	2026-01-06 20:53:13+01	\N	\N
caa2tqabxfuncxe	bb4syuyu7fz1t03	pata00z3me9f1bz	myz6dmx69dbmfod	nc_updated_by	updated_by	LastModifiedBy	character varying	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType	\N	\N	\N	\N	\N	\N	t	7	2026-01-06 20:53:13+01	2026-01-06 20:53:13+01	\N	\N
cgayrgpbjrz18bs	bb4syuyu7fz1t03	pata00z3me9f1bz	m2t8ts768utecu3	ID	id	ID	int4	\N	\N	\N	\N	t	\N	t	t	\N	t	\N	\N	\N	\N	specificType	\N	\N	\N	\N	\N	\N	\N	1	2026-01-06 20:53:28+01	2026-01-06 20:53:28+01	\N	\N
cvgd1zq61flnccx	bb4syuyu7fz1t03	pata00z3me9f1bz	m2t8ts768utecu3	Free Text Answer	free_text_answer	LongText	text	\N	\N	\N	\N	f	t	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	2	2026-01-06 20:53:28+01	2026-01-06 20:53:28+01	\N	\N
cuua1r8exqh953r	bb4syuyu7fz1t03	pata00z3me9f1bz	m2t8ts768utecu3	Captured At	captured_at	DateTime	timestamp	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	3	2026-01-06 20:53:28+01	2026-01-06 20:53:28+01	\N	\N
czfxtglmoaaopx3	bb4syuyu7fz1t03	pata00z3me9f1bz	m2t8ts768utecu3	CreatedAt	created_at	CreatedTime	timestamp	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	t	4	2026-01-06 20:53:28+01	2026-01-06 20:53:28+01	\N	\N
cddyxqajybhkcmc	bb4syuyu7fz1t03	pata00z3me9f1bz	m2t8ts768utecu3	UpdatedAt	updated_at	LastModifiedTime	timestamp	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	t	5	2026-01-06 20:53:28+01	2026-01-06 20:53:28+01	\N	\N
c6rmixllw4e8ycn	bb4syuyu7fz1t03	pata00z3me9f1bz	m2t8ts768utecu3	nc_created_by	created_by	CreatedBy	character varying	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType	\N	\N	\N	\N	\N	\N	t	6	2026-01-06 20:53:28+01	2026-01-06 20:53:28+01	\N	\N
c499tlvuswclzo6	bb4syuyu7fz1t03	pata00z3me9f1bz	m2t8ts768utecu3	nc_updated_by	updated_by	LastModifiedBy	character varying	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType	\N	\N	\N	\N	\N	\N	t	7	2026-01-06 20:53:28+01	2026-01-06 20:53:28+01	\N	\N
c934u2vpzrym0lj	bb4syuyu7fz1t03	pata00z3me9f1bz	myz6dmx69dbmfod	nc_fl6j___ServiceQuestions_id	nc_fl6j___ServiceQuestions_id	ForeignKey	int4	\N	\N	\N	\N	f	\N	f	t	\N	f	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	8	2026-01-06 20:54:00+01	2026-01-06 20:54:00+01	\N	\N
cvue26t4z7n6b1q	bb4syuyu7fz1t03	pata00z3me9f1bz	myz6dmx69dbmfod	Servicequestions	\N	LinkToAnotherRecord	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	\N	f	9	2026-01-06 20:54:00+01	2026-01-06 20:54:00+01	{"custom":false}	\N
cj43y361lmgcxkl	bb4syuyu7fz1t03	pata00z3me9f1bz	meivlfimb46wep7	Service Question	\N	LinkToAnotherRecord	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	\N	\N	10	2026-01-06 20:54:00+01	2026-01-06 20:54:00+01	{"plural":"Servicequestionoptions","singular":"Servicequestionoption","custom":false}	\N
ckrhmyg1j9o8fib	bb4syuyu7fz1t03	pata00z3me9f1bz	m2t8ts768utecu3	nc_fl6j___Leads_id	nc_fl6j___Leads_id	ForeignKey	int4	\N	\N	\N	\N	f	\N	f	t	\N	f	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	8	2026-01-06 20:54:15+01	2026-01-06 20:54:15+01	\N	\N
c465mwb9s8y839s	bb4syuyu7fz1t03	pata00z3me9f1bz	m2t8ts768utecu3	Leads	\N	LinkToAnotherRecord	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	\N	f	9	2026-01-06 20:54:15+01	2026-01-06 20:54:15+01	{"custom":false}	\N
cgt60wb5h0npnoo	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	Lead	\N	LinkToAnotherRecord	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	\N	\N	28	2026-01-06 20:54:15+01	2026-01-06 20:54:15+01	{"plural":"Leadanswers","singular":"Leadanswer","custom":false}	\N
c4gfmfo60vtwsg0	bb4syuyu7fz1t03	pata00z3me9f1bz	m2t8ts768utecu3	nc_fl6j___ServiceQuestions_id	nc_fl6j___ServiceQuestions_id	ForeignKey	int4	\N	\N	\N	\N	f	\N	f	t	\N	f	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	10	2026-01-06 20:54:34+01	2026-01-06 20:54:34+01	\N	\N
c6td8i4yv4e4w17	bb4syuyu7fz1t03	pata00z3me9f1bz	m2t8ts768utecu3	Servicequestions	\N	LinkToAnotherRecord	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	\N	f	11	2026-01-06 20:54:35+01	2026-01-06 20:54:35+01	{"custom":false}	\N
cuzqnnl9qiyhlk3	bb4syuyu7fz1t03	pata00z3me9f1bz	meivlfimb46wep7	Service Question1	\N	LinkToAnotherRecord	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	\N	\N	11	2026-01-06 20:54:35+01	2026-01-06 20:54:35+01	{"plural":"Leadanswers","singular":"Leadanswer","custom":false}	\N
cjc1wrl7dln3hk7	bb4syuyu7fz1t03	pata00z3me9f1bz	m2t8ts768utecu3	nc_fl6j___ServiceQuestionOptions_id	nc_fl6j___ServiceQuestionOptions_id	ForeignKey	int4	\N	\N	\N	\N	f	\N	f	t	\N	f	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	12	2026-01-06 20:55:02+01	2026-01-06 20:55:02+01	\N	\N
c8un30eflpsel7t	bb4syuyu7fz1t03	pata00z3me9f1bz	m2t8ts768utecu3	Servicequestionoptions	\N	LinkToAnotherRecord	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	\N	f	13	2026-01-06 20:55:02+01	2026-01-06 20:55:02+01	{"custom":false}	\N
c8z468hq9d6sy4x	bb4syuyu7fz1t03	pata00z3me9f1bz	myz6dmx69dbmfod	Selected Option	\N	LinkToAnotherRecord	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	\N	\N	10	2026-01-06 20:55:02+01	2026-01-06 20:55:02+01	{"plural":"Leadanswers","singular":"Leadanswer","custom":false}	\N
c1rmoj4wluax562	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	utm_source	utm_source	SingleLineText	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	f	29	2026-01-06 21:25:40+01	2026-01-06 21:25:40+01	\N	\N
c2knskjxbsyuljx	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	utm_medium	utm_medium	SingleLineText	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	f	30	2026-01-06 21:25:40+01	2026-01-06 21:25:40+01	\N	\N
cfnfdjfiyi4vies	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	utm_campaign	utm_campaign	SingleLineText	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	f	31	2026-01-06 21:25:40+01	2026-01-06 21:25:40+01	\N	\N
cnqxl5loaw6h3xz	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	utm_term	utm_term	SingleLineText	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	f	32	2026-01-06 21:25:40+01	2026-01-06 21:25:40+01	\N	\N
cp6v6s7mpznsjse	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	utm_content	utm_content	SingleLineText	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	f	33	2026-01-06 21:25:41+01	2026-01-06 21:25:41+01	\N	\N
cy1jeduocy059j3	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	landing_url	landing_url	LongText	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	f	34	2026-01-06 21:25:41+01	2026-01-06 21:25:41+01	\N	\N
cfbsuwgsoe9nx1n	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	referrer	referrer	LongText	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	f	35	2026-01-06 21:25:41+01	2026-01-06 21:25:41+01	\N	\N
clefdnmj083t05n	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	Bing Click ID (msclkid)	bing_click_id_msclkid	SingleLineText	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	f	36	2026-01-06 21:31:22+01	2026-01-06 21:31:22+01	\N	\N
cwcbx5xoqgjm86r	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	Google Click ID (gclid)	google_click_id_gclid	SingleLineText	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	f	37	2026-01-06 21:31:28+01	2026-01-06 21:31:28+01	\N	\N
c1xgr90k0s4t69a	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	Google Click ID (gbraid)	google_click_id_gbraid	SingleLineText	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	f	38	2026-01-06 21:31:42+01	2026-01-06 21:31:42+01	\N	\N
cirnniwr7fcaef7	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	Google Click ID (wbraid)	google_click_id_wbraid	SingleLineText	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	f	39	2026-01-06 21:31:42+01	2026-01-06 21:31:42+01	\N	\N
cnv13qo5wqisd5b	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	LinkedIn Click ID (li_fat_id)	linkedin_click_id_li_fat_id	SingleLineText	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	f	40	2026-01-06 21:31:50+01	2026-01-06 21:31:50+01	\N	\N
chxwfq82sa99mrg	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m965eotz3l7hxbi	PackKey	pack_key	SingleLineText	text	\N	\N	\N	\N	f	t	f	f	\N	f	t	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	2	2026-02-04 12:53:39+01	2026-02-04 12:53:39+01	\N	\N
cz2izt6bcyp6h7d	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m965eotz3l7hxbi	Name	name	SingleLineText	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	3	2026-02-04 12:53:39+01	2026-02-04 12:53:39+01	\N	\N
cos7orpu4oetkbs	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m965eotz3l7hxbi	PriceMin	price_min	Number	bigint	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	4	2026-02-04 12:53:39+01	2026-02-04 12:53:39+01	\N	\N
c4lf6uhrx3sad82	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	Entrada At	entrada_at	DateTime	timestamp	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	f	44	2026-01-07 00:03:20+01	2026-01-07 00:03:20+01	\N	\N
cyqfxh28r3vzadk	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m965eotz3l7hxbi	PriceMax	price_max	Number	bigint	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	5	2026-02-04 12:53:39+01	2026-02-04 12:53:39+01	\N	\N
c4ri76xdz18sf03	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m965eotz3l7hxbi	Description	description	LongText	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	6	2026-02-04 12:53:39+01	2026-02-04 12:53:39+01	\N	\N
cnqen1pd0e91qcn	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	Ads Platform	Ads_Platform	SingleLineText	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N		\N	\N	f	48	2026-01-07 00:41:07+01	2026-01-07 00:59:03+01	{"defaultViewColOrder":48}	\N
chkyo3iyn9af193	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	Ads Click ID Type	Ads_Click_ID_Type	SingleLineText	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N		\N	\N	f	49	2026-01-07 00:41:13+01	2026-01-07 00:59:13+01	{"defaultViewColOrder":49}	\N
c7maigexwjqamjl	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	Ads Click ID (unified)	Ads_Click_ID__unified_	SingleLineText	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N		\N	\N	f	45	2026-01-07 00:18:12+01	2026-01-07 00:59:51+01	{"defaultViewColOrder":45}	\N
c33kuznk7tpyq6o	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m965eotz3l7hxbi	IsActive	is_active	Checkbox	bool	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	true	\N	\N	specificType	\N	\N	\N	\N	\N	\N	\N	7	2026-02-04 12:53:39+01	2026-02-04 12:53:39+01	\N	\N
c1psfvqvod7rg33	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m965eotz3l7hxbi	IcpRules	icp_rules	LongText	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	8	2026-02-04 12:53:39+01	2026-02-04 12:53:39+01	\N	\N
c9igbdo5ukvhlvs	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m965eotz3l7hxbi	ScoringWeights	scoring_weights	LongText	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	9	2026-02-04 12:53:39+01	2026-02-04 12:53:39+01	\N	\N
cwdej5iqjcyf5lv	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m965eotz3l7hxbi	CreatedAt	created_at	DateTime	timestamp	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	10	2026-02-04 12:53:39+01	2026-02-04 12:53:39+01	\N	\N
cvuev7dhnbnkfzn	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m965eotz3l7hxbi	UpdatedAt	updated_at	DateTime	timestamp	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	11	2026-02-04 12:53:39+01	2026-02-04 12:53:39+01	\N	\N
ce9zgls0vldsyve	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m965eotz3l7hxbi	CreatedAt	created_at1	CreatedTime	timestamp	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	t	12	2026-02-04 12:53:39+01	2026-02-04 12:53:39+01	\N	\N
cdwl8z05mphf0vr	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m965eotz3l7hxbi	UpdatedAt	updated_at1	LastModifiedTime	timestamp	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	t	13	2026-02-04 12:53:39+01	2026-02-04 12:53:39+01	\N	\N
cckq6ux5vg1nlm9	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m965eotz3l7hxbi	nc_created_by	created_by	CreatedBy	character varying	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType	\N	\N	\N	\N	\N	\N	t	14	2026-02-04 12:53:39+01	2026-02-04 12:53:39+01	\N	\N
cjskjrzgu7zx12y	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m965eotz3l7hxbi	nc_updated_by	updated_by	LastModifiedBy	character varying	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType	\N	\N	\N	\N	\N	\N	t	15	2026-02-04 12:53:39+01	2026-02-04 12:53:39+01	\N	\N
cfvyp0oegs9kw7d	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	merj80wv3zr0yzl	Id	Id	ID	int4	\N	\N	\N	\N	t	\N	t	t	\N	t	\N	\N	\N	\N	specificType	\N	\N	\N	\N	\N	\N	\N	1	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
c3b48a3wrctuy1m	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	merj80wv3zr0yzl	Name	name	SingleLineText	text	\N	\N	\N	\N	f	t	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	2	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
cu8uid3p0wc1wgt	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	merj80wv3zr0yzl	Domain	domain	SingleLineText	text	\N	\N	\N	\N	f	\N	f	f	\N	f	t	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	3	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
co5taskc8jsow5v	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	merj80wv3zr0yzl	WebUrl	web_url	URL	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	{"func":["isURL"],"args":[""],"msg":["Validation failed : isURL"]}	\N	\N	\N	4	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
cb8doj0zxeltv44	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	merj80wv3zr0yzl	Industry	industry	SingleSelect	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType	\N	 	\N	\N	\N	\N	\N	5	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
cgp16aduu9lr9up	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	merj80wv3zr0yzl	LocationCity	location_city	SingleLineText	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	6	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
c1n0v11xcq44bzy	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	merj80wv3zr0yzl	LocationRegion	location_region	SingleLineText	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	7	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
c1mi3f7wfd8m9cj	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	merj80wv3zr0yzl	EmployeesRange	employees_range	SingleSelect	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	UNKNOWN	\N	\N	specificType	\N	 	\N	\N	\N	\N	\N	8	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
cwy90uck7umcg8k	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	merj80wv3zr0yzl	RevenueEstimateRange	revenue_estimate_range	SingleSelect	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	UNKNOWN	\N	\N	specificType	\N	 	\N	\N	\N	\N	\N	9	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
ca2ufyifpu1v2fa	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	merj80wv3zr0yzl	PlacesPlaceId	places_place_id	SingleLineText	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	10	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
cg8ebuo46nfptpp	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	merj80wv3zr0yzl	places_rating	places_rating	Decimal	decimal	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		2	\N	\N	\N	\N	\N	11	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
cyxd64nt2amqak1	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	merj80wv3zr0yzl	PlacesReviewsTotal	places_reviews_total	Number	bigint	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	12	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
com94fldw4t26od	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	merj80wv3zr0yzl	PlacesTypes	places_types	LongText	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	13	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
ca8odr9ckxtzc1r	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	merj80wv3zr0yzl	PlacesWebsite	places_website	URL	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	{"func":["isURL"],"args":[""],"msg":["Validation failed : isURL"]}	\N	\N	\N	14	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
ccrl2hzrdrhgua3	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	merj80wv3zr0yzl	PlacesPhone	places_phone	SingleLineText	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	15	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
c695hlrx7bsrkr7	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	merj80wv3zr0yzl	PlacesAddress	places_address	SingleLineText	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	16	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
cptyulm7rnp30v5	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	merj80wv3zr0yzl	PlacesLastCheckedAt	places_last_checked_at	DateTime	timestamp	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	17	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
cbzm4b8vyv41fjw	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	merj80wv3zr0yzl	PlacesSignalHash	places_signal_hash	SingleLineText	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	18	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
ca6kesjt4v2vxar	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	merj80wv3zr0yzl	WebSignalHash	web_signal_hash	SingleLineText	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	19	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
cgf4cpevkq073b4	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	merj80wv3zr0yzl	WebLastCheckedAt	web_last_checked_at	DateTime	timestamp	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	20	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
cw4qfyj6ewofuk2	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	merj80wv3zr0yzl	CreatedAt	created_at	CreatedTime	timestamp	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	t	21	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
c7niacluyb6u5ai	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	merj80wv3zr0yzl	UpdatedAt	updated_at	LastModifiedTime	timestamp	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	t	22	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
cf3b1jfiiaigzz9	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	merj80wv3zr0yzl	nc_created_by	created_by	CreatedBy	character varying	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType	\N	\N	\N	\N	\N	\N	t	23	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
clp9mlovpbpg5n3	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	merj80wv3zr0yzl	nc_updated_by	updated_by	LastModifiedBy	character varying	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType	\N	\N	\N	\N	\N	\N	t	24	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
cfx0hh3vvkr9yu9	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m4dhntou135vxm1	Id	Id	ID	int4	\N	\N	\N	\N	t	\N	t	t	\N	t	\N	\N	\N	\N	specificType	\N	\N	\N	\N	\N	\N	\N	1	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
cgmp5gcjcaqzkzw	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m4dhntou135vxm1	company	company	LinkToAnotherRecord	character varying	\N	\N	\N	\N	f	t	f	f	\N	f	\N	\N	\N	\N	specificType	\N	\N	\N	\N	\N	\N	\N	2	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
crghbrr65i2tlbu	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m7nt9pg5uw1e4h3	Id	Id	ID	int4	\N	\N	\N	\N	t	\N	t	t	\N	t	\N	\N	\N	\N	specificType	\N	\N	\N	\N	\N	\N	\N	1	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
cl4kbxvsw9jfho7	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m7nt9pg5uw1e4h3	SegmentKey	segment_key	SingleLineText	text	\N	\N	\N	\N	f	t	f	f	\N	f	t	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	2	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
ceui606d8jwe9ju	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m7nt9pg5uw1e4h3	pack	pack	LinkToAnotherRecord	character varying	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType	\N	\N	\N	\N	\N	\N	\N	3	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
c9k50d4m2330h0x	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m7nt9pg5uw1e4h3	Name	name	SingleLineText	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	4	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
cxgi277ii77m5fy	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m7nt9pg5uw1e4h3	Type	type	SingleSelect	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType	\N	 	\N	\N	\N	\N	\N	5	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
colbujailyyr19l	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m7nt9pg5uw1e4h3	Status	status	SingleSelect	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	RUNNING	\N	\N	specificType	\N	 	\N	\N	\N	\N	\N	6	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
cfmgudix0qksgsv	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m7nt9pg5uw1e4h3	Definition	definition	LongText	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	7	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
c0fosu85jg3s2jh	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m7nt9pg5uw1e4h3	DailyInviteCap	daily_invite_cap	Number	bigint	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	10	\N	\N	specificType		 	\N	\N	\N	\N	\N	8	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
cntg34pxhcn8fzp	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m7nt9pg5uw1e4h3	StartDate	start_date	Date	date	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	9	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
cocxr9dfmjsndgm	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m7nt9pg5uw1e4h3	EndDate	end_date	Date	date	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	10	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
co266doam53yl5p	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m7nt9pg5uw1e4h3	Notes	notes	LongText	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	11	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
ccoph5bl1lxzm62	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m7nt9pg5uw1e4h3	CreatedAt	created_at	CreatedTime	timestamp	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	t	12	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
calm53w3wy3ybmf	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m7nt9pg5uw1e4h3	UpdatedAt	updated_at	LastModifiedTime	timestamp	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	t	13	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
cmn8rsd9pe6xkis	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m7nt9pg5uw1e4h3	nc_created_by	created_by	CreatedBy	character varying	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType	\N	\N	\N	\N	\N	\N	t	14	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
cdv38fdll8o6up3	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m7nt9pg5uw1e4h3	nc_updated_by	updated_by	LastModifiedBy	character varying	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType	\N	\N	\N	\N	\N	\N	t	15	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
clya1e8vpxtnusj	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m4dhntou135vxm1	lead	lead	LinkToAnotherRecord	character varying	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType	\N	\N	\N	\N	\N	\N	\N	3	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
cgk7qg876t5xi2y	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m4dhntou135vxm1	Source	source	SingleSelect	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType	\N	 	\N	\N	\N	\N	\N	4	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
cn5nspgpm23vyzu	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m4dhntou135vxm1	Signals	signals	LongText	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	5	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
cg9dv5vw31plo6k	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m4dhntou135vxm1	SignalHash	signal_hash	SingleLineText	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	6	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
c0js689qcl0xhfh	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m4dhntou135vxm1	CreatedAt	created_at	DateTime	timestamp	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	7	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
c8aubq62ldh6a67	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m4dhntou135vxm1	CreatedAt	created_at1	CreatedTime	timestamp	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	t	8	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
c3dz4r7omn8lsg5	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m4dhntou135vxm1	UpdatedAt	updated_at	LastModifiedTime	timestamp	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	t	9	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
cnjp3jns5g15kz6	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m4dhntou135vxm1	nc_created_by	created_by	CreatedBy	character varying	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType	\N	\N	\N	\N	\N	\N	t	10	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
c51hueut49afrub	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m4dhntou135vxm1	nc_updated_by	updated_by	LastModifiedBy	character varying	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType	\N	\N	\N	\N	\N	\N	t	11	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
cn3oygm7rk9orhv	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m7d1wkpymm3kj7l	Id	Id	ID	int4	\N	\N	\N	\N	t	\N	t	t	\N	t	\N	\N	\N	\N	specificType	\N	\N	\N	\N	\N	\N	\N	1	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
c5cc6a1ct8zu9tl	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m7d1wkpymm3kj7l	TemplateKey	template_key	SingleLineText	text	\N	\N	\N	\N	f	t	f	f	\N	f	t	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	2	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
cymxw81qe37t06b	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m7d1wkpymm3kj7l	pack	pack	LinkToAnotherRecord	character varying	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType	\N	\N	\N	\N	\N	\N	\N	3	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
c6pmtlu10bgqi8e	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m7d1wkpymm3kj7l	segment	segment	LinkToAnotherRecord	character varying	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType	\N	\N	\N	\N	\N	\N	\N	4	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
cqvpzsa7muzvahe	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m7d1wkpymm3kj7l	Phase	phase	SingleSelect	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType	\N	 	\N	\N	\N	\N	\N	5	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
czufc759mmzmzte	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m7d1wkpymm3kj7l	Language	language	SingleSelect	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType	\N	 	\N	\N	\N	\N	\N	6	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
c7qd4ezf5mek9p3	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m7d1wkpymm3kj7l	TemplateText	template_text	LongText	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	7	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
c22psa2kc2792mn	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m7d1wkpymm3kj7l	Variables	variables	LongText	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	8	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
c6na7mjtdk6k7nl	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m7d1wkpymm3kj7l	Version	version	Number	bigint	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	1	\N	\N	specificType		 	\N	\N	\N	\N	\N	9	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
cqn6enmiw3mvggo	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m7d1wkpymm3kj7l	IsActive	is_active	Checkbox	bool	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	true	\N	\N	specificType	\N	\N	\N	\N	\N	\N	\N	10	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
cyw5f2ouyakeetl	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m7d1wkpymm3kj7l	Notes	notes	LongText	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	11	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
ck8mfufae0nwyg5	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m7d1wkpymm3kj7l	CreatedAt	created_at	CreatedTime	timestamp	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	t	12	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
c4mb01s5zwmwgn5	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m7d1wkpymm3kj7l	UpdatedAt	updated_at	LastModifiedTime	timestamp	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	t	13	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
cxvjuy1a4ly8mth	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m7d1wkpymm3kj7l	nc_created_by	created_by	CreatedBy	character varying	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType	\N	\N	\N	\N	\N	\N	t	14	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
c44jszl1hind848	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m7d1wkpymm3kj7l	nc_updated_by	updated_by	LastModifiedBy	character varying	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType	\N	\N	\N	\N	\N	\N	t	15	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
c1jaq7sruv48moq	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mx1ud1d86w1d4y6	Id	Id	ID	int4	\N	\N	\N	\N	t	\N	t	t	\N	t	\N	\N	\N	\N	specificType	\N	\N	\N	\N	\N	\N	\N	1	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
cp68n1hirgxg4ac	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mx1ud1d86w1d4y6	lead	lead	LinkToAnotherRecord	character varying	\N	\N	\N	\N	f	t	f	f	\N	f	\N	\N	\N	\N	specificType	\N	\N	\N	\N	\N	\N	\N	2	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
cl48g3sz3gwkigd	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mx1ud1d86w1d4y6	template	template	LinkToAnotherRecord	character varying	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType	\N	\N	\N	\N	\N	\N	\N	3	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
c69gbr33uorqy7r	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mx1ud1d86w1d4y6	Phase	phase	SingleSelect	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType	\N	 	\N	\N	\N	\N	\N	4	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
c3se5eac1nun01u	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mx1ud1d86w1d4y6	DraftMessage	draft_message	LongText	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	5	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
cn7t5jqfob1xqys	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mx1ud1d86w1d4y6	FinalMessage	final_message	LongText	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	6	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
cneon7k1vc1c1a3	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mx1ud1d86w1d4y6	Rationale	rationale	LongText	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	7	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
colzu9quxnxbnh8	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mx1ud1d86w1d4y6	AngleQuality	angle_quality	SingleSelect	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType	\N	 	\N	\N	\N	\N	\N	8	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
cjmxnucuwdti0ov	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mx1ud1d86w1d4y6	PainQuality	pain_quality	SingleSelect	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType	\N	 	\N	\N	\N	\N	\N	9	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
c5yhz2syzrcsd70	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mx1ud1d86w1d4y6	Note	note	SingleLineText	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	10	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
cf2u8yfbufgeweq	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mx1ud1d86w1d4y6	ApprovedBy	approved_by	SingleLineText	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	11	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
cv7kikt4k5dsj5f	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mx1ud1d86w1d4y6	ApprovedAt	approved_at	DateTime	timestamp	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	12	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
c395vprwrcmzl57	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mx1ud1d86w1d4y6	CreatedAt	created_at	CreatedTime	timestamp	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	t	13	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
cvyo6ytuiyrg9hl	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mx1ud1d86w1d4y6	UpdatedAt	updated_at	LastModifiedTime	timestamp	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	t	14	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
cxoeozdh0k34iyj	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mx1ud1d86w1d4y6	nc_created_by	created_by	CreatedBy	character varying	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType	\N	\N	\N	\N	\N	\N	t	15	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
ckmcuh9od42kkvb	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mx1ud1d86w1d4y6	nc_updated_by	updated_by	LastModifiedBy	character varying	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType	\N	\N	\N	\N	\N	\N	t	16	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
cdwm83qqvh18y4u	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mc5itfivoyx2rp5	Id	Id	ID	int4	\N	\N	\N	\N	t	\N	t	t	\N	t	\N	\N	\N	\N	specificType	\N	\N	\N	\N	\N	\N	\N	1	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
c7lbximf46oj2og	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mc5itfivoyx2rp5	LinkedinUrl	linkedin_url	URL	text	\N	\N	\N	\N	f	t	f	f	\N	f	t	\N	\N	\N	specificType		 	\N	{"func":["isURL"],"args":[""],"msg":["Validation failed : isURL"]}	\N	\N	\N	2	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
c4zk9sg1vu6rhag	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mc5itfivoyx2rp5	FullName	full_name	SingleLineText	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	3	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
c1tcdy8u6nv8yn3	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mc5itfivoyx2rp5	Title	title	SingleLineText	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	4	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
czcjput7b3iz3qu	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mc5itfivoyx2rp5	RoleType	role_type	SingleSelect	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	UNKNOWN	\N	\N	specificType	\N	 	\N	\N	\N	\N	\N	5	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
co9utg0xsmr47wg	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mc5itfivoyx2rp5	LocationCity	location_city	SingleLineText	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	6	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
cn8plh9xmxlf1sd	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mc5itfivoyx2rp5	Language	language	SingleSelect	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	UNKNOWN	\N	\N	specificType	\N	 	\N	\N	\N	\N	\N	7	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
cljj6490e5wy0z1	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mc5itfivoyx2rp5	Source	source	SingleSelect	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType	\N	 	\N	\N	\N	\N	\N	8	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
c8a52kfs7igesr6	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mc5itfivoyx2rp5	company	company	LinkToAnotherRecord	character varying	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType	\N	\N	\N	\N	\N	\N	\N	9	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
c0b6kxkcmknrmbz	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mc5itfivoyx2rp5	pack_candidate	pack_candidate	LinkToAnotherRecord	character varying	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType	\N	\N	\N	\N	\N	\N	\N	10	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
c74e36i29wlgw2m	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mc5itfivoyx2rp5	segment	segment	LinkToAnotherRecord	character varying	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType	\N	\N	\N	\N	\N	\N	\N	11	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
c6w114nfydog3o6	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mc5itfivoyx2rp5	Status	status	SingleSelect	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	NEW	\N	\N	specificType	\N	 	\N	\N	\N	\N	\N	12	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
cef82lzbg01fuhc	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mc5itfivoyx2rp5	Priority	priority	SingleSelect	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	MEDIUM	\N	\N	specificType	\N	 	\N	\N	\N	\N	\N	13	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
cr3uyexth3769aw	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mc5itfivoyx2rp5	LeadScore	lead_score	Number	bigint	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	0	\N	\N	specificType		 	\N	\N	\N	\N	\N	14	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
ce89e2ckcs82hw4	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mc5itfivoyx2rp5	ScoreBreakdown	score_breakdown	LongText	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	15	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
cunxivw0lk2ggok	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mc5itfivoyx2rp5	ScoringVersion	scoring_version	SingleLineText	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	16	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
cmsq89vdiunny56	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mc5itfivoyx2rp5	CreatedAt	created_at	DateTime	timestamp	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	17	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
cafac19aq8grbva	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mc5itfivoyx2rp5	InviteSentAt	invite_sent_at	DateTime	timestamp	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	18	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
cv8aty28f6dix2h	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mc5itfivoyx2rp5	AcceptedAt	accepted_at	DateTime	timestamp	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	19	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
cd72o3xbmwy9vm9	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mc5itfivoyx2rp5	NextActionAt	next_action_at	DateTime	timestamp	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	20	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
c8dgod9cg6pq0kf	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mc5itfivoyx2rp5	WaitWindowDays	wait_window_days	Number	bigint	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	14	\N	\N	specificType		 	\N	\N	\N	\N	\N	21	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
crgafrxjp0gbki1	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mc5itfivoyx2rp5	LastSignalCheckedAt	last_signal_checked_at	DateTime	timestamp	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	22	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
cmphy9c5imxsip2	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mc5itfivoyx2rp5	SignalChanged	signal_changed	Checkbox	bool	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	false	\N	\N	specificType	\N	\N	\N	\N	\N	\N	\N	23	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
ch22n49kbwy5vp3	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mc5itfivoyx2rp5	DoNotContact	do_not_contact	Checkbox	bool	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	false	\N	\N	specificType	\N	\N	\N	\N	\N	\N	\N	24	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
c31inzncoxixf84	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mc5itfivoyx2rp5	DoNotContactReason	do_not_contact_reason	SingleLineText	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	25	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
ckmv7lmbdc07flu	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mc5itfivoyx2rp5	Email	email	SingleLineText	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	26	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
cmhc1q0rc8x8lxc	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mc5itfivoyx2rp5	Phone	phone	SingleLineText	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	27	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
cktu46042n4dcxo	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mc5itfivoyx2rp5	CreatedAt	created_at1	CreatedTime	timestamp	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	t	28	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
cka3l1xthtrxhck	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mc5itfivoyx2rp5	UpdatedAt	updated_at	LastModifiedTime	timestamp	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	t	29	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
chaii833qzvnl34	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mc5itfivoyx2rp5	nc_created_by	created_by	CreatedBy	character varying	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType	\N	\N	\N	\N	\N	\N	t	30	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
c8szo2aomn5hhsp	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mc5itfivoyx2rp5	nc_updated_by	updated_by	LastModifiedBy	character varying	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType	\N	\N	\N	\N	\N	\N	t	31	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
cft17n3bxvzco6n	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mp45w6rbyjyh6ks	Id	Id	ID	int4	\N	\N	\N	\N	t	\N	t	t	\N	t	\N	\N	\N	\N	specificType	\N	\N	\N	\N	\N	\N	\N	1	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	\N	\N
c2gc3o7nudv7tb8	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mp45w6rbyjyh6ks	lead	lead	LinkToAnotherRecord	character varying	\N	\N	\N	\N	f	t	f	f	\N	f	\N	\N	\N	\N	specificType	\N	\N	\N	\N	\N	\N	\N	2	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	\N	\N
cv1vkbto1cqgg13	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mp45w6rbyjyh6ks	CallBookedAt	call_booked_at	DateTime	timestamp	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	3	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	\N	\N
c7rupva2bbsd942	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mp45w6rbyjyh6ks	CallHeldAt	call_held_at	DateTime	timestamp	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	4	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	\N	\N
chwey76orqjoarm	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mp45w6rbyjyh6ks	Outcome	outcome	SingleSelect	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType	\N	 	\N	\N	\N	\N	\N	5	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	\N	\N
chahes6qex1hndj	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mp45w6rbyjyh6ks	package_recommended	package_recommended	LinkToAnotherRecord	character varying	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType	\N	\N	\N	\N	\N	\N	\N	6	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	\N	\N
cu2b8rj8vkl3nf0	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mp45w6rbyjyh6ks	ValueEstimate	value_estimate	Number	bigint	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	7	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	\N	\N
crh0cx4kyxg85sa	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mp45w6rbyjyh6ks	Notes	notes	LongText	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	8	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	\N	\N
c3u2lv026zljxoz	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mp45w6rbyjyh6ks	CreatedAt	created_at	CreatedTime	timestamp	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	t	9	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	\N	\N
ca8lrrfqlnzcm26	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mp45w6rbyjyh6ks	UpdatedAt	updated_at	LastModifiedTime	timestamp	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	t	10	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	\N	\N
c5wgcib9tpnzcr6	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mp45w6rbyjyh6ks	nc_created_by	created_by	CreatedBy	character varying	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType	\N	\N	\N	\N	\N	\N	t	11	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	\N	\N
c033hx4s3pwntgh	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mp45w6rbyjyh6ks	nc_updated_by	updated_by	LastModifiedBy	character varying	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType	\N	\N	\N	\N	\N	\N	t	12	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	\N	\N
cc4mkzpmgh9vrp2	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mcyckhd2a05m772	Id	Id	ID	int4	\N	\N	\N	\N	t	\N	t	t	\N	t	\N	\N	\N	\N	specificType	\N	\N	\N	\N	\N	\N	\N	1	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
co17kfo1sg603dy	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mcyckhd2a05m772	lead	lead	LinkToAnotherRecord	character varying	\N	\N	\N	\N	f	t	f	f	\N	f	\N	\N	\N	\N	specificType	\N	\N	\N	\N	\N	\N	\N	2	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
ca4lddk146v74zd	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mcyckhd2a05m772	AttemptType	attempt_type	SingleSelect	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType	\N	 	\N	\N	\N	\N	\N	3	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
ciar62fx5ef6659	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mcyckhd2a05m772	Phase	phase	SingleSelect	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType	\N	 	\N	\N	\N	\N	\N	4	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
c6uwnbjl1r5mju0	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mcyckhd2a05m772	Result	result	SingleSelect	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType	\N	 	\N	\N	\N	\N	\N	5	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
c1g5wjmqu5d668i	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mcyckhd2a05m772	Reason	reason	SingleLineText	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	6	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
cn448us2zt8yitp	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mcyckhd2a05m772	Metadata	metadata	LongText	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	7	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
cyf6y1aedi2zm2w	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mcyckhd2a05m772	AttemptAt	attempt_at	DateTime	timestamp	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	8	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
cqsd7qq1yjvu3u6	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mcyckhd2a05m772	CreatedAt	created_at	CreatedTime	timestamp	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	t	9	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
cpkt9wuu4sozth6	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mcyckhd2a05m772	UpdatedAt	updated_at	LastModifiedTime	timestamp	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	t	10	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
cg0z4k44cktp7po	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mcyckhd2a05m772	nc_created_by	created_by	CreatedBy	character varying	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType	\N	\N	\N	\N	\N	\N	t	11	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
c7xu8j452nqmfnh	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mcyckhd2a05m772	nc_updated_by	updated_by	LastModifiedBy	character varying	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType	\N	\N	\N	\N	\N	\N	t	12	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
crtkv2hik413x5a	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mzvwidn4z544pas	Id	Id	ID	int4	\N	\N	\N	\N	t	\N	t	t	\N	t	\N	\N	\N	\N	specificType	\N	\N	\N	\N	\N	\N	\N	1	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	\N	\N
chbafyj23t8h3t8	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mzvwidn4z544pas	lead	lead	LinkToAnotherRecord	character varying	\N	\N	\N	\N	f	t	f	f	\N	f	\N	\N	\N	\N	specificType	\N	\N	\N	\N	\N	\N	\N	2	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	\N	\N
c2nn1lgezk2u5xy	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mzvwidn4z544pas	State	state	SingleSelect	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	NOT_STARTED	\N	\N	specificType	\N	 	\N	\N	\N	\N	\N	3	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	\N	\N
cpbdi22opzkv8du	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mzvwidn4z544pas	LastInboundAt	last_inbound_at	DateTime	timestamp	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	4	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	\N	\N
cnn1slzb4g8a9ae	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mzvwidn4z544pas	LastOutboundAt	last_outbound_at	DateTime	timestamp	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	5	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	\N	\N
cnn563xrm5wws3c	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mzvwidn4z544pas	InterestLevel	interest_level	SingleSelect	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	COLD	\N	\N	specificType	\N	 	\N	\N	\N	\N	\N	6	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	\N	\N
chinmfbl9u3sww2	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mzvwidn4z544pas	CtaSentAt	cta_sent_at	DateTime	timestamp	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	7	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	\N	\N
c58qbvmi535hl8f	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mzvwidn4z544pas	CalLink	cal_link	URL	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	{"func":["isURL"],"args":[""],"msg":["Validation failed : isURL"]}	\N	\N	\N	8	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	\N	\N
chzsfpz1xcf0dgw	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mzvwidn4z544pas	Notes	notes	LongText	text	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	\N	9	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	\N	\N
cb6pm56nja53kw9	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mzvwidn4z544pas	CreatedAt	created_at	CreatedTime	timestamp	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	t	10	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	\N	\N
c2xbmipf3pmn2og	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mzvwidn4z544pas	UpdatedAt	updated_at	LastModifiedTime	timestamp	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType		 	\N	\N	\N	\N	t	11	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	\N	\N
ccp11g3e72iil1u	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mzvwidn4z544pas	nc_created_by	created_by	CreatedBy	character varying	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType	\N	\N	\N	\N	\N	\N	t	12	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	\N	\N
chz2hzuhhfsjwhl	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mzvwidn4z544pas	nc_updated_by	updated_by	LastModifiedBy	character varying	\N	\N	\N	\N	f	\N	f	f	\N	f	\N	\N	\N	\N	specificType	\N	\N	\N	\N	\N	\N	t	13	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	\N	\N
\.


--
-- Data for Name: nc_comment_reactions; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public.nc_comment_reactions (id, row_id, comment_id, source_id, fk_model_id, base_id, reaction, created_by, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: nc_comments; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public.nc_comments (id, row_id, comment, created_by, created_by_email, resolved_by, resolved_by_email, parent_comment_id, source_id, base_id, fk_model_id, is_deleted, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: nc_disabled_models_for_role_v2; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public.nc_disabled_models_for_role_v2 (id, source_id, base_id, fk_view_id, role, disabled, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: nc_extensions; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public.nc_extensions (id, base_id, fk_user_id, extension_id, title, kv_store, meta, "order", created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: nc_file_references; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public.nc_file_references (id, storage, file_url, file_size, fk_user_id, fk_workspace_id, base_id, source_id, fk_model_id, fk_column_id, is_external, deleted, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: nc_filter_exp_v2; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public.nc_filter_exp_v2 (id, source_id, base_id, fk_view_id, fk_hook_id, fk_column_id, fk_parent_id, logical_op, comparison_op, value, is_group, "order", created_at, updated_at, comparison_sub_op, fk_link_col_id, fk_value_col_id) FROM stdin;
\.


--
-- Data for Name: nc_fl6j___LeadAnswers; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public."nc_fl6j___LeadAnswers" (id, free_text_answer, captured_at, created_at, updated_at, created_by, updated_by, "nc_fl6j___Leads_id", "nc_fl6j___ServiceQuestions_id", "nc_fl6j___ServiceQuestionOptions_id") FROM stdin;
1	\N	2026-01-06 18:30:00	2026-01-06 20:02:36	\N	us8g4rajnw6fzr9r	\N	\N	\N	\N
2	Zapier, Slack, Google Sheets, HubSpot	2026-01-06 19:00:00	2026-01-06 20:02:55	\N	us8g4rajnw6fzr9r	\N	\N	\N	\N
\.


--
-- Data for Name: nc_fl6j___Leads; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public."nc_fl6j___Leads" (id, nombre, entrada, email, telefono, tipo_empresa, servicio, extra_informacion, como_nos_conociste, mensaje, origen_lead, estado, prioridad, notas_internas, lead_tag, next_action, next_action_key, owner, last_contact_at, next_followup_at, lost_reason, gdpr_consent, created_at, updated_at, created_by, updated_by, utm_source, utm_medium, utm_campaign, utm_term, utm_content, landing_url, referrer, bing_click_id_msclkid, google_click_id_gclid, google_click_id_gbraid, google_click_id_wbraid, linkedin_click_id_li_fat_id, entrada_at, "Ads_Click_ID__unified_", "Ads_Platform", "Ads_Click_ID_Type") FROM stdin;
18	PROD ENV FIX OK	2026-01-07	prod.env.fix@test.com	\N	Pyme	\N	\N	Google / Buscador	Confirmación variables entorno Lambda	Formulario web	Nuevo	Media	\N	Qualified	SEND_EMAIL	REPLY_WITH_NEXT_STEPS	\N	\N	\N	\N	t	2026-01-07 02:45:41	\N	us8g4rajnw6fzr9r	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-01-07 02:45:41	\N	\N	\N
21	apiEnv PROD test	2026-01-07	apienv.prod@test.com	\N	Pyme	\N	\N	Google / Buscador	apiEnv check	Formulario web	Nuevo	Media	\N	Cold	SEND_EMAIL	ASK_FOR_DETAILS	\N	\N	\N	\N	t	2026-01-07 11:05:34	\N	us8g4rajnw6fzr9r	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-01-07 11:05:34	\N	\N	\N
19	test prod-lov 2	2026-01-07	info@comovivirdeltrading.com	+34631230488	Emprendedor	Infraestructura gestionada	Hosting / servidores	Redes sociales	pueden llamarme urgente	Formulario web	Nuevo	Alta	\N	Hot	CALL	URGENT_CALL_NOW	\N	\N	\N	\N	t	2026-01-07 03:30:45	\N	us8g4rajnw6fzr9r	\N	\N	\N	\N	\N	\N	https://www.nucleotecnologico.es/contacto	\N	\N	\N	\N	\N	\N	2026-01-07 03:30:44	\N	\N	\N
22	apiEnv PROD final test	2026-01-07	api.env.final@test.com	\N	Pyme	\N	\N	Google / Buscador	Final apiEnv verification	Formulario web	Nuevo	Media	\N	Qualified	SEND_EMAIL	REPLY_WITH_NEXT_STEPS	\N	\N	\N	\N	t	2026-01-07 11:17:00	\N	us8g4rajnw6fzr9r	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-01-07 11:16:59	\N	\N	\N
37	test	2026-01-23	nu@nu.es	+34631230488	Pyme	Desarrollo web y software a medida	Web profesional / landing	Google Ads	prueba conversion	Formulario web	Nuevo	Media	\N	Qualified	SEND_EMAIL	REPLY_WITH_NEXT_STEPS	\N	\N	\N	\N	t	2026-01-23 19:40:23	\N	us8g4rajnw6fzr9r	\N	\N	\N	\N	\N	\N	https://www.nucleotecnologico.es/contacto#form	https://tagassistant.google.com/	\N	\N	\N	\N	\N	2026-01-23 19:41:24	\N	\N	\N
20	edu test 07-01-2026	2026-01-07	info@comovivirdeltrading.com	+34631230488	Agencia	Desarrollo web y software a medida	MVP para validar idea	Google / Buscador	nuevo producto que estamos por lanzar 	Formulario web	Nuevo	Media	\N	Qualified	SEND_EMAIL	REPLY_WITH_NEXT_STEPS	\N	\N	\N	\N	t	2026-01-07 09:35:12	2026-01-07 12:51:42	us8g4rajnw6fzr9r	us8g4rajnw6fzr9r	\N	\N	\N	\N	\N	https://www.nucleotecnologico.es/contacto	\N	\N	\N	\N	\N	\N	2026-01-07 09:35:12	\N	\N	\N
23	Marimar	2026-01-07	info@help.es	+34625667655	Pyme	Desarrollo web y software a medida	CRM o sistema interno	Google Ads	No lo se 	Formulario web	Nuevo	Media	\N	Cold	SEND_EMAIL	ASK_FOR_DETAILS	\N	\N	\N	\N	t	2026-01-07 18:26:57	\N	us8g4rajnw6fzr9r	\N	\N	\N	\N	\N	\N	https://www.nucleotecnologico.es/contacto	\N	\N	\N	\N	\N	\N	2026-01-07 18:26:56	\N	\N	\N
24	YASMELI MARIA	2026-01-08	yasme@yasme.es	+34613705216	Pyme	Integraciones / Automatización	AUTOMATIZAR CONTROL DE ASISTENCIAS, FACTURAS Y TRABAJOS REALIZADOS 	Otro	TODA ESA VERGA	Formulario web	Nuevo	Media	\N	Cold	SEND_EMAIL	ASK_FOR_DETAILS	\N	\N	\N	\N	t	2026-01-08 16:54:46	\N	us8g4rajnw6fzr9r	\N	\N	\N	\N	\N	\N	https://www.nucleotecnologico.es/contacto#form	\N	\N	\N	\N	\N	\N	2026-01-08 16:54:46	\N	\N	\N
25	web test	2026-01-08	info@comovivirdeltrading.com	+34631230488	Agencia	SRE / Observabilidad	No tenemos alertas o llegan tarde	LinkedIn	necesito ayuda urgente	Formulario web	Nuevo	Alta	\N	Hot	CALL	URGENT_CALL_NOW	\N	\N	\N	\N	t	2026-01-08 20:41:33	\N	us8g4rajnw6fzr9r	\N	\N	\N	\N	\N	\N	https://www.nucleotecnologico.es/contacto	\N	\N	\N	\N	\N	\N	2026-01-08 20:41:32	\N	\N	\N
26	eduardo	2026-01-08	nu@nu.es	+34631230488	Emprendedor	Cloud & DevOps	AWS	Directorio o listado	necesito revisar un servidor 	Formulario web	Nuevo	Alta	\N	Hot	CALL	HIGH_VALUE_WITH_PHONE	\N	\N	\N	\N	t	2026-01-08 20:50:18	\N	us8g4rajnw6fzr9r	\N	\N	\N	\N	\N	\N	https://www.nucleotecnologico.es/contacto	\N	\N	\N	\N	\N	\N	2026-01-08 20:50:18	\N	\N	\N
27	eduardo	2026-01-08	nu@nu.es	+34631230488	Emprendedor	Cloud & DevOps	Google Cloud	Google / Buscador	necesito urtgene ee 	Formulario web	Nuevo	Alta	\N	Hot	CALL	HIGH_VALUE_WITH_PHONE	\N	\N	\N	\N	t	2026-01-08 20:51:53	\N	us8g4rajnw6fzr9r	\N	\N	\N	\N	\N	\N	https://www.nucleotecnologico.es/contacto	\N	\N	\N	\N	\N	\N	2026-01-08 20:51:53	\N	\N	\N
28	datarows	2026-01-08	info@comovivirdeltrading.com	+34631230488	Agencia	Cloud & DevOps	Servidor tradicional (sin cloud)	Google / Buscador	esto es un ejemplo 	Formulario web	Nuevo	Alta	\N	Hot	CALL	HIGH_VALUE_WITH_PHONE	\N	\N	\N	\N	t	2026-01-08 20:56:47	\N	us8g4rajnw6fzr9r	\N	\N	\N	\N	\N	\N	https://www.nucleotecnologico.es/contacto	\N	\N	\N	\N	\N	\N	2026-01-08 20:56:47	\N	\N	\N
29	claude	2026-01-08	claude@claude.es	+34631230488	Emprendedor	Infraestructura gestionada	Hosting / servidores	Google / Buscador	hola necesito servicio para hoy 	Formulario web	Nuevo	Alta	\N	Hot	CALL	URGENT_CALL_NOW	\N	\N	\N	\N	t	2026-01-08 21:08:19	\N	us8g4rajnw6fzr9r	\N	\N	\N	\N	\N	\N	https://www.nucleotecnologico.es/contacto	\N	\N	\N	\N	\N	\N	2026-01-08 21:08:18	\N	\N	\N
30	claude	2026-01-08	claude@claude.es	+34631230488	Emprendedor	Desarrollo web y software a medida	Web profesional / landing	Google Ads	Version A: Without brackets for spaced fields (try this first)\nKey changes:\nChanged rows.[0] to rows.0 (without brackets on the array index)\nLeft field names with spaces as-is: Tipo Empresa instead of [Tipo Empresa]	Formulario web	Nuevo	Media	\N	Qualified	SEND_EMAIL	REPLY_WITH_NEXT_STEPS	\N	\N	\N	\N	t	2026-01-08 21:12:32	\N	us8g4rajnw6fzr9r	\N	\N	\N	\N	\N	\N	https://www.nucleotecnologico.es/contacto	\N	\N	\N	\N	\N	\N	2026-01-08 21:12:32	\N	\N	\N
31	eduardo	2026-01-08	eduardo@ew.es	+34631230488	Agencia	SRE / Observabilidad	No sabemos qué pasa en producción	Google / Buscador	Version B: If Version A doesn't work, try quoted field names	Formulario web	Nuevo	Alta	\N	Hot	CALL	HIGH_VALUE_WITH_PHONE	\N	\N	\N	\N	t	2026-01-08 21:14:54	\N	us8g4rajnw6fzr9r	\N	\N	\N	\N	\N	\N	https://www.nucleotecnologico.es/contacto	\N	\N	\N	\N	\N	\N	2026-01-08 21:14:54	\N	\N	\N
32	test	2026-01-08	test@test.es	+34631230488	Pyme	Cloud & DevOps	Azure	Google Ads	testingf 	Formulario web	Nuevo	Alta	\N	Hot	CALL	HIGH_VALUE_WITH_PHONE	\N	\N	\N	\N	t	2026-01-08 21:21:40	\N	us8g4rajnw6fzr9r	\N	\N	\N	\N	\N	\N	https://www.nucleotecnologico.es/contacto	\N	\N	\N	\N	\N	\N	2026-01-08 21:21:39	\N	\N	\N
33	test	2026-01-08	test@test.es	+34631230488	Emprendedor	Desarrollo web y software a medida	CRM o sistema interno	Google Ads	test te fgdghdshñlbsdf dhfsghfghsdhsfh	Formulario web	Nuevo	Media	\N	Qualified	SEND_EMAIL	REPLY_WITH_NEXT_STEPS	\N	\N	\N	\N	t	2026-01-08 21:26:10	\N	us8g4rajnw6fzr9r	\N	\N	\N	\N	\N	\N	https://www.nucleotecnologico.es/contacto	\N	\N	\N	\N	\N	\N	2026-01-08 21:26:10	\N	\N	\N
34	chatgpt	2026-01-08	eduardo@ew.es	+34631230488	Pyme	Desarrollo web y software a medida	CRM o sistema interno	Google / Buscador	probando, probando, probando 	Formulario web	Nuevo	Media	\N	Qualified	SEND_EMAIL	REPLY_WITH_NEXT_STEPS	\N	\N	\N	\N	t	2026-01-08 21:33:15	\N	us8g4rajnw6fzr9r	\N	\N	\N	\N	\N	\N	https://www.nucleotecnologico.es/contacto	\N	\N	\N	\N	\N	\N	2026-01-08 21:33:14	\N	\N	\N
35	eduardo	2026-01-08	eduardo@ew.es	+34631230488	Pyme	SRE / Observabilidad	No tenemos alertas o llegan tarde	Google / Buscador	The json helper is used to safely serialize values into valid JSON, whether they’re strings, objects, or arrays. It ensures proper quoting and escaping, preventing common errors with quotes, newlines, or special characters. For example, {{ json event }} outputs the full event object, while {{ json event.data.rows.[0].Title }} safely inserts a single field as a JSON string. This makes it the most reliable way to embed dynamic values in webhook paylo	Formulario web	Nuevo	Alta	\N	Hot	CALL	HIGH_VALUE_WITH_PHONE	\N	\N	\N	\N	t	2026-01-08 21:41:06	\N	us8g4rajnw6fzr9r	\N	\N	\N	\N	\N	\N	https://www.nucleotecnologico.es/contacto	\N	\N	\N	\N	\N	\N	2026-01-08 21:41:05	\N	\N	\N
36	gemini	2026-01-08	gemini@gemini.es	+34631230488	Agencia	Cloud & DevOps	Servidor tradicional (sin cloud)	Google Ads	Great news! The diagnostic test confirms that for your NocoDB setup, the correct data path is {{data.ColumnName}}. It also confirms that for columns with spaces, the correct format is {{data.[Column Name]}}.	Formulario web	Nuevo	Alta	\N	Hot	CALL	HIGH_VALUE_WITH_PHONE	\N	\N	\N	\N	t	2026-01-08 21:46:30	\N	us8g4rajnw6fzr9r	\N	\N	\N	\N	\N	\N	https://www.nucleotecnologico.es/contacto	\N	\N	\N	\N	\N	\N	2026-01-08 21:46:29	\N	\N	\N
\.


--
-- Data for Name: nc_fl6j___ServiceQuestionOptions; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public."nc_fl6j___ServiceQuestionOptions" (id, option_label, sort_order, created_at, updated_at, created_by, updated_by, "nc_fl6j___ServiceQuestions_id") FROM stdin;
1	Web profesional / landing	1	2026-01-06 19:59:38	\N	us8g4rajnw6fzr9r	\N	\N
2	CRM o sistema interno	2	2026-01-06 19:59:38	\N	us8g4rajnw6fzr9r	\N	\N
3	App móvil o PWA	3	2026-01-06 19:59:38	\N	us8g4rajnw6fzr9r	\N	\N
4	E-commerce / tienda online	4	2026-01-06 19:59:38	\N	us8g4rajnw6fzr9r	\N	\N
5	MVP para validar idea	5	2026-01-06 19:59:38	\N	us8g4rajnw6fzr9r	\N	\N
6	Otro	6	2026-01-06 19:59:39	\N	us8g4rajnw6fzr9r	\N	\N
7	Servidor tradicional (sin cloud)	1	2026-01-06 19:59:47	\N	us8g4rajnw6fzr9r	\N	\N
8	AWS	2	2026-01-06 19:59:47	\N	us8g4rajnw6fzr9r	\N	\N
9	Azure	3	2026-01-06 19:59:48	\N	us8g4rajnw6fzr9r	\N	\N
10	Google Cloud	4	2026-01-06 19:59:48	\N	us8g4rajnw6fzr9r	\N	\N
11	Varios proveedores mezclados	5	2026-01-06 19:59:48	\N	us8g4rajnw6fzr9r	\N	\N
12	No lo sé / lo gestiona otro	6	2026-01-06 19:59:48	\N	us8g4rajnw6fzr9r	\N	\N
13	Caídas frecuentes sin saber por qué	1	2026-01-06 19:59:58	\N	us8g4rajnw6fzr9r	\N	\N
14	No tenemos alertas o llegan tarde	2	2026-01-06 19:59:58	\N	us8g4rajnw6fzr9r	\N	\N
15	Rendimiento lento sin diagnóstico	3	2026-01-06 19:59:58	\N	us8g4rajnw6fzr9r	\N	\N
16	No sabemos qué pasa en producción	4	2026-01-06 19:59:58	\N	us8g4rajnw6fzr9r	\N	\N
17	Queremos definir SLOs/SLAs	5	2026-01-06 19:59:59	\N	us8g4rajnw6fzr9r	\N	\N
18	Otro	6	2026-01-06 19:59:59	\N	us8g4rajnw6fzr9r	\N	\N
19	Hosting / servidores	1	2026-01-06 20:00:54	\N	us8g4rajnw6fzr9r	\N	\N
20	Dominios y DNS	2	2026-01-06 20:00:54	\N	us8g4rajnw6fzr9r	\N	\N
21	Certificados SSL	3	2026-01-06 20:00:54	\N	us8g4rajnw6fzr9r	\N	\N
22	Backups y recuperación	4	2026-01-06 20:00:54	\N	us8g4rajnw6fzr9r	\N	\N
23	Todo lo anterior	5	2026-01-06 20:00:54	\N	us8g4rajnw6fzr9r	\N	\N
24	Otro	6	2026-01-06 20:00:54	\N	us8g4rajnw6fzr9r	\N	\N
25	Soporte a usuarios (incidencias)	1	2026-01-06 20:01:04	\N	us8g4rajnw6fzr9r	\N	\N
26	Mantenimiento de equipos/sistemas	2	2026-01-06 20:01:04	\N	us8g4rajnw6fzr9r	\N	\N
27	Cobertura fuera de horario	3	2026-01-06 20:01:04	\N	us8g4rajnw6fzr9r	\N	\N
28	Refuerzo temporal del equipo IT	4	2026-01-06 20:01:04	\N	us8g4rajnw6fzr9r	\N	\N
29	Externalización completa IT	5	2026-01-06 20:01:04	\N	us8g4rajnw6fzr9r	\N	\N
30	Otro	6	2026-01-06 20:01:04	\N	us8g4rajnw6fzr9r	\N	\N
\.


--
-- Data for Name: nc_fl6j___ServiceQuestions; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public."nc_fl6j___ServiceQuestions" (id, service, question_label, input_type, is_enabled, created_at, updated_at, created_by, updated_by) FROM stdin;
1	Desarrollo web y software a medida	¿Qué tipo de solución necesitas?	select	t	2026-01-06 19:57:03	\N	us8g4rajnw6fzr9r	\N
2	Cloud & DevOps	¿Cuál es tu situación actual de infraestructura?	select	t	2026-01-06 19:57:34	\N	us8g4rajnw6fzr9r	\N
3	SRE / Observabilidad	¿Qué problema de fiabilidad o visibilidad tienes?	select	t	2026-01-06 19:57:53	\N	us8g4rajnw6fzr9r	\N
4	Infraestructura gestionada	¿Qué parte de la infraestructura necesitas gestionar?	select	t	2026-01-06 19:58:15	\N	us8g4rajnw6fzr9r	\N
5	Integraciones / Automatización	¿Qué herramientas o sistemas quieres conectar?	text	t	2026-01-06 19:58:33	\N	us8g4rajnw6fzr9r	\N
6	Outsourcing IT / CAU	¿Qué tipo de soporte necesitas?	select	t	2026-01-06 19:58:55	\N	us8g4rajnw6fzr9r	\N
7	No lo tengo claro	Sin pregunta adicional	select	f	2026-01-06 19:59:25	\N	us8g4rajnw6fzr9r	\N
\.


--
-- Data for Name: nc_form_view_columns_v2; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public.nc_form_view_columns_v2 (id, source_id, base_id, fk_view_id, fk_column_id, uuid, label, help, description, required, show, "order", created_at, updated_at, meta, enable_scanner) FROM stdin;
\.


--
-- Data for Name: nc_form_view_v2; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public.nc_form_view_v2 (source_id, base_id, fk_view_id, heading, subheading, success_msg, redirect_url, redirect_after_secs, email, submit_another_form, show_blank_form, uuid, banner_image_url, logo_url, created_at, updated_at, meta) FROM stdin;
\.


--
-- Data for Name: nc_gallery_view_columns_v2; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public.nc_gallery_view_columns_v2 (id, source_id, base_id, fk_view_id, fk_column_id, uuid, label, help, show, "order", created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: nc_gallery_view_v2; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public.nc_gallery_view_v2 (source_id, base_id, fk_view_id, next_enabled, prev_enabled, cover_image_idx, fk_cover_image_col_id, cover_image, restrict_types, restrict_size, restrict_number, public, dimensions, responsive_columns, created_at, updated_at, meta) FROM stdin;
\.


--
-- Data for Name: nc_grid_view_columns_v2; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public.nc_grid_view_columns_v2 (id, fk_view_id, fk_column_id, source_id, base_id, uuid, label, help, width, show, "order", created_at, updated_at, group_by, group_by_order, group_by_sort, aggregation) FROM stdin;
nc6kk1v5a40i5sss	vwpgmxxz13357xvo	crrv0yg28skccm7	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	439px	t	3	2026-01-06 20:52:52+01	2026-01-06 21:08:45+01	\N	\N	\N	none
ncyzimoufrfu8k5o	vws4819bc08ixvxj	c1rmoj4wluax562	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	180px	t	29	2026-01-06 21:25:40+01	2026-01-06 21:25:40+01	\N	\N	\N	\N
nc0m2tk8kh0oqmx8	vws4819bc08ixvxj	c2knskjxbsyuljx	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	180px	t	30	2026-01-06 21:25:40+01	2026-01-06 21:25:40+01	\N	\N	\N	\N
ncks2f1ev16idu6x	vws4819bc08ixvxj	cfnfdjfiyi4vies	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	180px	t	31	2026-01-06 21:25:40+01	2026-01-06 21:25:40+01	\N	\N	\N	\N
ncihulb07huz4z74	vws4819bc08ixvxj	cnqxl5loaw6h3xz	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	180px	t	32	2026-01-06 21:25:40+01	2026-01-06 21:25:40+01	\N	\N	\N	\N
ncg2y6s0xzzy0jh0	vws4819bc08ixvxj	cp6v6s7mpznsjse	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	180px	t	33	2026-01-06 21:25:41+01	2026-01-06 21:25:41+01	\N	\N	\N	\N
nclx2lfe67og2kid	vws4819bc08ixvxj	clefdnmj083t05n	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	180px	t	36	2026-01-06 21:31:22+01	2026-01-06 21:31:22+01	\N	\N	\N	\N
ncr5sbg7dv2ifj9c	vws4819bc08ixvxj	cwcbx5xoqgjm86r	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	180px	t	37	2026-01-06 21:31:28+01	2026-01-06 21:31:28+01	\N	\N	\N	\N
ncpfsxxpw0bplbfd	vws4819bc08ixvxj	c1xgr90k0s4t69a	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	180px	t	38	2026-01-06 21:31:42+01	2026-01-06 21:31:42+01	\N	\N	\N	\N
ncyv06x0apnxqct8	vws4819bc08ixvxj	cirnniwr7fcaef7	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	180px	t	39	2026-01-06 21:31:42+01	2026-01-06 21:31:42+01	\N	\N	\N	\N
ncddkep5x9m091fz	vws4819bc08ixvxj	cnv13qo5wqisd5b	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	180px	t	40	2026-01-06 21:31:50+01	2026-01-06 21:31:50+01	\N	\N	\N	\N
ncjic6zp88tdomlf	vwpyj1825rdljhp4	chtewf19yconvxc	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	1	2026-02-04 12:53:39+01	2026-02-04 12:53:39+01	\N	\N	\N	none
nc3fqwzadztidfqm	vwpyj1825rdljhp4	chxwfq82sa99mrg	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	2	2026-02-04 12:53:39+01	2026-02-04 12:53:39+01	\N	\N	\N	none
nccurgpwx6unvy78	vwpyj1825rdljhp4	cz2izt6bcyp6h7d	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	3	2026-02-04 12:53:39+01	2026-02-04 12:53:39+01	\N	\N	\N	none
ncp22t2xcappdk1j	vws4819bc08ixvxj	cy1jeduocy059j3	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	336px	t	34	2026-01-06 21:25:41+01	2026-01-06 23:34:36+01	\N	\N	\N	\N
nc48e7t6x6vhtrhi	vws4819bc08ixvxj	cfbsuwgsoe9nx1n	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	258px	t	35	2026-01-06 21:25:41+01	2026-01-06 23:34:41+01	\N	\N	\N	\N
ncostki3sk8g2yi5	vws4819bc08ixvxj	c4lf6uhrx3sad82	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	180px	t	44	2026-01-07 00:03:20+01	2026-01-07 00:03:20+01	\N	\N	\N	\N
ncdhbgn9q0598nf2	vwpyj1825rdljhp4	cos7orpu4oetkbs	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	4	2026-02-04 12:53:39+01	2026-02-04 12:53:39+01	\N	\N	\N	none
nc6q2sktn805w397	vwpyj1825rdljhp4	cyqfxh28r3vzadk	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	5	2026-02-04 12:53:39+01	2026-02-04 12:53:39+01	\N	\N	\N	none
ncvlv6nv2kg5ktei	vws4819bc08ixvxj	c7maigexwjqamjl	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	264px	t	45	2026-01-07 00:18:12+01	2026-01-07 00:37:15+01	\N	\N	\N	\N
ncch1bqgkq9s9jdg	vwpyj1825rdljhp4	c4ri76xdz18sf03	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	6	2026-02-04 12:53:39+01	2026-02-04 12:53:39+01	\N	\N	\N	none
ncagbw7yhd9fg1nl	vws4819bc08ixvxj	cnqen1pd0e91qcn	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	180px	t	48	2026-01-07 00:41:07+01	2026-01-07 00:41:07+01	\N	\N	\N	\N
nc5i4q6s7gawpsoc	vwpyj1825rdljhp4	c33kuznk7tpyq6o	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	7	2026-02-04 12:53:39+01	2026-02-04 12:53:39+01	\N	\N	\N	none
ncoultbco9aggik6	vwpyj1825rdljhp4	c1psfvqvod7rg33	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	8	2026-02-04 12:53:39+01	2026-02-04 12:53:39+01	\N	\N	\N	none
ncqhhhhq5mscn0pm	vws4819bc08ixvxj	chkyo3iyn9af193	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	232px	t	49	2026-01-07 00:41:13+01	2026-01-07 00:57:06+01	\N	\N	\N	\N
ncpuwzv4x6kxluah	vwpyj1825rdljhp4	c9igbdo5ukvhlvs	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	9	2026-02-04 12:53:39+01	2026-02-04 12:53:39+01	\N	\N	\N	none
ncdvz0cz0oy010a8	vwpyj1825rdljhp4	cwdej5iqjcyf5lv	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	10	2026-02-04 12:53:39+01	2026-02-04 12:53:39+01	\N	\N	\N	none
nc5ifa4rvk9l3zl1	vwpyj1825rdljhp4	cvuev7dhnbnkfzn	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	11	2026-02-04 12:53:39+01	2026-02-04 12:53:39+01	\N	\N	\N	none
ncshm58gw4sn01vs	vwpyj1825rdljhp4	ce9zgls0vldsyve	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	12	2026-02-04 12:53:39+01	2026-02-04 12:53:39+01	\N	\N	\N	none
nc53wwsddl1dsj8c	vwpyj1825rdljhp4	cdwl8z05mphf0vr	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	13	2026-02-04 12:53:39+01	2026-02-04 12:53:39+01	\N	\N	\N	none
nch2wu2p9zdgcv63	vwpyj1825rdljhp4	cckq6ux5vg1nlm9	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	14	2026-02-04 12:53:39+01	2026-02-04 12:53:39+01	\N	\N	\N	none
ncmectn61ad3r9nl	vwpyj1825rdljhp4	cjskjrzgu7zx12y	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	15	2026-02-04 12:53:39+01	2026-02-04 12:53:39+01	\N	\N	\N	none
nc7cvdjwa34b2ojj	vw1znarynk7fk1oe	cfvyp0oegs9kw7d	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	1	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncrs2hvnq1397rmn	vw1znarynk7fk1oe	c3b48a3wrctuy1m	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	2	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncs8drfyiha1wtue	vw1znarynk7fk1oe	cu8uid3p0wc1wgt	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	3	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
nc1iktghjmflqgfg	vw1znarynk7fk1oe	co5taskc8jsow5v	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	4	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
nclbpncz7f9ih5py	vw1znarynk7fk1oe	cb8doj0zxeltv44	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	5	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncym3rgrlkvpk4ik	vw1znarynk7fk1oe	cgp16aduu9lr9up	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	6	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
nc3sich0366ub4nl	vw1znarynk7fk1oe	c1n0v11xcq44bzy	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	7	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
nc1n85jz04wvskex	vw1znarynk7fk1oe	c1mi3f7wfd8m9cj	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	8	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncd759h0kkal9afh	vw1znarynk7fk1oe	cwy90uck7umcg8k	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	9	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncy69msczynjiird	vws4819bc08ixvxj	cgvkav0m3p12am0	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	200px	t	1	2026-01-06 20:52:25+01	2026-01-06 20:54:16+01	\N	\N	\N	none
ncc1lh1s8pth719e	vws4819bc08ixvxj	cr9281rkz5dpit0	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	200px	t	2	2026-01-06 20:52:25+01	2026-01-06 20:54:16+01	\N	\N	\N	none
nc4pfg6ahuae1s3f	vws4819bc08ixvxj	cu8xmyiq6x3rmfh	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	200px	t	3	2026-01-06 20:52:25+01	2026-01-06 20:54:16+01	\N	\N	\N	none
nc7c4ffg9vt5owlp	vws4819bc08ixvxj	cp08sylckll5u64	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	200px	t	4	2026-01-06 20:52:25+01	2026-01-06 20:54:16+01	\N	\N	\N	none
ncsj306wulc2jfaq	vws4819bc08ixvxj	ctd95pigwvohwlr	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	200px	t	5	2026-01-06 20:52:25+01	2026-01-06 20:54:16+01	\N	\N	\N	none
ncls9w0f1fk7oyxw	vws4819bc08ixvxj	cuk8msv9e01r5qs	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	200px	t	6	2026-01-06 20:52:25+01	2026-01-06 20:54:16+01	\N	\N	\N	none
ncg3320wkqak54mj	vws4819bc08ixvxj	c99gznqsho81qmc	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	200px	t	8	2026-01-06 20:52:25+01	2026-01-06 20:54:16+01	\N	\N	\N	none
ncnhb5x7qasxxx26	vws4819bc08ixvxj	cwvrczahkii68gx	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	200px	t	9	2026-01-06 20:52:25+01	2026-01-06 20:54:16+01	\N	\N	\N	none
nc3ytpq68198186g	vws4819bc08ixvxj	cc9lfl109mgesga	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	200px	t	10	2026-01-06 20:52:25+01	2026-01-06 20:54:16+01	\N	\N	\N	none
ncjmzhznwls2ohk5	vws4819bc08ixvxj	cgw3j8nn4o6w285	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	200px	t	11	2026-01-06 20:52:25+01	2026-01-06 20:54:16+01	\N	\N	\N	none
ncgaflblpse8q6p7	vw1znarynk7fk1oe	ca2ufyifpu1v2fa	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	10	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncb5i71qmas5jsci	vwnatjh1ee7fnrko	cay37dugmu28m2j	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	200px	t	1	2026-01-06 20:53:13+01	2026-01-06 20:54:00+01	\N	\N	\N	none
nc1lfnhjuj83xzhd	vwnatjh1ee7fnrko	cwp6ckygxgsesvz	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	200px	t	2	2026-01-06 20:53:13+01	2026-01-06 20:54:00+01	\N	\N	\N	none
nc71qij0867z6iac	vwnatjh1ee7fnrko	c3da2q5oxv24clf	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	200px	t	3	2026-01-06 20:53:13+01	2026-01-06 20:54:00+01	\N	\N	\N	none
nc5u7lf66wli5oxb	vwnatjh1ee7fnrko	cgy3oh2cpo9y9x5	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	200px	t	4	2026-01-06 20:53:13+01	2026-01-06 20:54:00+01	\N	\N	\N	none
nctnf1ruv89xoj5f	vwnatjh1ee7fnrko	cphzo0atiai403o	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	200px	t	5	2026-01-06 20:53:13+01	2026-01-06 20:54:00+01	\N	\N	\N	none
ncdqco20oa12sikk	vwnatjh1ee7fnrko	c7r51y404tyqcy3	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	200px	t	6	2026-01-06 20:53:13+01	2026-01-06 20:54:00+01	\N	\N	\N	none
nc1frn9strpm6c1m	vwnatjh1ee7fnrko	caa2tqabxfuncxe	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	200px	t	7	2026-01-06 20:53:13+01	2026-01-06 20:54:00+01	\N	\N	\N	none
ncicadkblg0drs6p	vwnatjh1ee7fnrko	c934u2vpzrym0lj	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	180px	t	8	2026-01-06 20:54:00+01	2026-01-06 20:54:00+01	\N	\N	\N	\N
nc5qcfko7ncy37e6	vwnatjh1ee7fnrko	cvue26t4z7n6b1q	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	180px	t	9	2026-01-06 20:54:00+01	2026-01-06 20:54:00+01	\N	\N	\N	\N
nc1sbk90yt13l6tl	vwpgmxxz13357xvo	c9t1uu106dq5r8g	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	200px	t	1	2026-01-06 20:52:52+01	2026-01-06 20:54:00+01	\N	\N	\N	none
nc7p679bhigeo5h9	vwpgmxxz13357xvo	c5sbbie1xkxtt2i	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	200px	t	2	2026-01-06 20:52:52+01	2026-01-06 20:54:00+01	\N	\N	\N	none
nccwrjbhv961wzhk	vwpgmxxz13357xvo	cl01772wjt5jlgc	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	200px	t	4	2026-01-06 20:52:52+01	2026-01-06 20:54:00+01	\N	\N	\N	none
nc5kt0xe0yia16fz	vwpgmxxz13357xvo	cw4yqjlz0a5ykcr	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	200px	t	5	2026-01-06 20:52:52+01	2026-01-06 20:54:00+01	\N	\N	\N	none
ncls0xzqmysu2n1e	vwpgmxxz13357xvo	cmw4y8risbmn1do	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	200px	t	6	2026-01-06 20:52:52+01	2026-01-06 20:54:00+01	\N	\N	\N	none
nc3rac25hv0fjr3e	vwpgmxxz13357xvo	c89acu3i27bt46g	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	200px	t	7	2026-01-06 20:52:52+01	2026-01-06 20:54:00+01	\N	\N	\N	none
nczkqg6snolfmhe5	vwpgmxxz13357xvo	cdbtq91lgdbjnbd	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	200px	t	8	2026-01-06 20:52:52+01	2026-01-06 20:54:00+01	\N	\N	\N	none
ncud013647rnwplq	vwpgmxxz13357xvo	c33zx14ye4cipd5	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	200px	t	9	2026-01-06 20:52:52+01	2026-01-06 20:54:00+01	\N	\N	\N	none
nc4xorl1g4xle50c	vwpgmxxz13357xvo	cj43y361lmgcxkl	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	180px	t	10	2026-01-06 20:54:00+01	2026-01-06 20:54:00+01	\N	\N	\N	\N
nc9jgrgxmek6iql3	vwb863vj0bh71lgi	cvgd1zq61flnccx	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	200px	t	1	2026-01-06 20:53:28+01	2026-01-06 20:54:15+01	\N	\N	\N	none
nchv7mih4i1a0gz3	vwb863vj0bh71lgi	cgayrgpbjrz18bs	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	200px	t	2	2026-01-06 20:53:28+01	2026-01-06 20:54:15+01	\N	\N	\N	none
ncr6d9mopc6urazg	vwb863vj0bh71lgi	cuua1r8exqh953r	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	200px	t	3	2026-01-06 20:53:28+01	2026-01-06 20:54:15+01	\N	\N	\N	none
ncrfwnunuqonlnil	vwb863vj0bh71lgi	czfxtglmoaaopx3	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	200px	t	4	2026-01-06 20:53:28+01	2026-01-06 20:54:15+01	\N	\N	\N	none
ncvp6k97menw5gw6	vwb863vj0bh71lgi	cddyxqajybhkcmc	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	200px	t	5	2026-01-06 20:53:28+01	2026-01-06 20:54:15+01	\N	\N	\N	none
nc4djx5cjaq6fw2c	vwb863vj0bh71lgi	c6rmixllw4e8ycn	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	200px	t	6	2026-01-06 20:53:28+01	2026-01-06 20:54:15+01	\N	\N	\N	none
nch4he58ub2hck0j	vwb863vj0bh71lgi	c499tlvuswclzo6	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	200px	t	7	2026-01-06 20:53:28+01	2026-01-06 20:54:15+01	\N	\N	\N	none
nc7m6anccndz4tys	vwb863vj0bh71lgi	ckrhmyg1j9o8fib	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	180px	t	8	2026-01-06 20:54:15+01	2026-01-06 20:54:15+01	\N	\N	\N	\N
ncxisqtgtnumd7lz	vwb863vj0bh71lgi	c465mwb9s8y839s	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	180px	t	9	2026-01-06 20:54:15+01	2026-01-06 20:54:15+01	\N	\N	\N	\N
ncuilpsiwcn2z1rp	vws4819bc08ixvxj	cmb9fgozmqj7j32	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	200px	t	12	2026-01-06 20:52:25+01	2026-01-06 20:54:16+01	\N	\N	\N	none
ncr7rongomuek137	vws4819bc08ixvxj	cc8mbs6beegxb27	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	200px	t	13	2026-01-06 20:52:25+01	2026-01-06 20:54:16+01	\N	\N	\N	none
ncsubwlaly3jy0u1	vws4819bc08ixvxj	cp2i3cj0wlu3nyj	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	200px	t	14	2026-01-06 20:52:25+01	2026-01-06 20:54:16+01	\N	\N	\N	none
ncip9h1312gr4dzs	vws4819bc08ixvxj	cv46emwmskabko2	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	200px	t	15	2026-01-06 20:52:25+01	2026-01-06 20:54:16+01	\N	\N	\N	none
ncmlrltnxqbiw884	vws4819bc08ixvxj	c3qulrp5ivk3s7i	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	200px	t	16	2026-01-06 20:52:25+01	2026-01-06 20:54:16+01	\N	\N	\N	none
ncptm59i1s1115va	vws4819bc08ixvxj	c6i5br252s0bzjk	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	200px	t	17	2026-01-06 20:52:25+01	2026-01-06 20:54:16+01	\N	\N	\N	none
ncdw9gosvuiwiz4n	vws4819bc08ixvxj	cdld42bch58tzqh	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	200px	t	18	2026-01-06 20:52:25+01	2026-01-06 20:54:16+01	\N	\N	\N	none
nc1tzuikzdy5963o	vws4819bc08ixvxj	cl3mje9g06ndmn2	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	200px	t	19	2026-01-06 20:52:25+01	2026-01-06 20:54:16+01	\N	\N	\N	none
nc8q6ij1mfjl943w	vws4819bc08ixvxj	c8c370ltnjqswxz	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	200px	t	20	2026-01-06 20:52:25+01	2026-01-06 20:54:16+01	\N	\N	\N	none
ncthuw5yc05d2uz7	vws4819bc08ixvxj	cf4e69f6gwxlkoq	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	200px	t	21	2026-01-06 20:52:25+01	2026-01-06 20:54:16+01	\N	\N	\N	none
nczxrhfrozeq7b44	vws4819bc08ixvxj	cg9k96mozj92dk6	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	200px	t	22	2026-01-06 20:52:25+01	2026-01-06 20:54:16+01	\N	\N	\N	none
ncooc1fz59ifz7yl	vws4819bc08ixvxj	cmbr44eh8sa4vqr	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	200px	t	23	2026-01-06 20:52:25+01	2026-01-06 20:54:16+01	\N	\N	\N	none
ncpt2u9xgmke9vop	vws4819bc08ixvxj	cet31zg1mkv51cp	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	200px	t	24	2026-01-06 20:52:25+01	2026-01-06 20:54:16+01	\N	\N	\N	none
nc92w4b5h7b8u0yv	vws4819bc08ixvxj	ccruq72xe2bhg9s	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	200px	t	25	2026-01-06 20:52:25+01	2026-01-06 20:54:16+01	\N	\N	\N	none
ncs22g5k0k420s62	vws4819bc08ixvxj	cubtjoi22fwjko5	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	200px	t	26	2026-01-06 20:52:25+01	2026-01-06 20:54:16+01	\N	\N	\N	none
nco1qcme43wdnr8n	vws4819bc08ixvxj	c59z1eqsvpdl2os	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	200px	t	27	2026-01-06 20:52:25+01	2026-01-06 20:54:16+01	\N	\N	\N	none
ncmgf3y2qqjsl12y	vws4819bc08ixvxj	cgt60wb5h0npnoo	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	180px	t	28	2026-01-06 20:54:15+01	2026-01-06 20:54:16+01	\N	\N	\N	\N
ncj309v5gfzmbhlr	vwb863vj0bh71lgi	c4gfmfo60vtwsg0	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	180px	t	10	2026-01-06 20:54:34+01	2026-01-06 20:54:34+01	\N	\N	\N	\N
ncgq32ji94tzs6f9	vwb863vj0bh71lgi	c6td8i4yv4e4w17	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	180px	t	11	2026-01-06 20:54:35+01	2026-01-06 20:54:35+01	\N	\N	\N	\N
nc96ysr35xxcm1gz	vwpgmxxz13357xvo	cuzqnnl9qiyhlk3	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	180px	t	11	2026-01-06 20:54:35+01	2026-01-06 20:54:35+01	\N	\N	\N	\N
ncvdr9peh4r1p3ks	vwb863vj0bh71lgi	cjc1wrl7dln3hk7	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	180px	t	12	2026-01-06 20:55:02+01	2026-01-06 20:55:02+01	\N	\N	\N	\N
ncya4huoeu9e353k	vwb863vj0bh71lgi	c8un30eflpsel7t	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	180px	t	13	2026-01-06 20:55:02+01	2026-01-06 20:55:02+01	\N	\N	\N	\N
ncv0ar5jtgiy0kv9	vwnatjh1ee7fnrko	c8z468hq9d6sy4x	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	\N	\N	180px	t	10	2026-01-06 20:55:02+01	2026-01-06 20:55:02+01	\N	\N	\N	\N
ncn0681uzjrwn7ob	vw1znarynk7fk1oe	cg8ebuo46nfptpp	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	11	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
nc20w5bpwy6m6sf8	vw1znarynk7fk1oe	cyxd64nt2amqak1	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	12	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncl0yawox1bjjcl5	vw1znarynk7fk1oe	com94fldw4t26od	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	13	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
nc5tr9wad4rzuywu	vw1znarynk7fk1oe	ca8odr9ckxtzc1r	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	14	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncx4cbsj7dneeezh	vw1znarynk7fk1oe	ccrl2hzrdrhgua3	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	15	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncuqb7ukh2iyzihp	vw1znarynk7fk1oe	c695hlrx7bsrkr7	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	16	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncluaoq3tw85qs85	vw1znarynk7fk1oe	cptyulm7rnp30v5	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	17	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
nchdomfz5xa8787q	vw1znarynk7fk1oe	cbzm4b8vyv41fjw	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	18	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
nc9c23nhpavduf26	vw1znarynk7fk1oe	ca6kesjt4v2vxar	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	19	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
nc60mrtp6atq2wvf	vw1znarynk7fk1oe	cgf4cpevkq073b4	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	20	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
nca6dr82c2w8mqtm	vw1znarynk7fk1oe	cw4qfyj6ewofuk2	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	21	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncxlfg2fg8mvbjoa	vw1znarynk7fk1oe	c7niacluyb6u5ai	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	22	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
nc12qxc9wheodg4q	vw1znarynk7fk1oe	cf3b1jfiiaigzz9	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	23	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncx14b1tcy5a8m8e	vw1znarynk7fk1oe	clp9mlovpbpg5n3	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	24	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncrich3s1jubdo1h	vwhgdl1fodz1dstx	ckmv7lmbdc07flu	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	26	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncfaeyslceil93w2	vwhgdl1fodz1dstx	cmhc1q0rc8x8lxc	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	27	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncajpfs8y09vx0dt	vwhgdl1fodz1dstx	cktu46042n4dcxo	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	28	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncpot9wcntndeudg	vwhgdl1fodz1dstx	cka3l1xthtrxhck	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	29	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncz63mzfrri0l8ew	vwhgdl1fodz1dstx	chaii833qzvnl34	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	30	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncoz71td0t51oonj	vwhgdl1fodz1dstx	c8szo2aomn5hhsp	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	31	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncuj9oyqh0iqr1m3	vw9rlol15y37u5ok	c1jaq7sruv48moq	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	1	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncyspj5k7un2ilhs	vw9rlol15y37u5ok	cp68n1hirgxg4ac	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	2	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncfz5zroa3dy24v3	vw9rlol15y37u5ok	cl48g3sz3gwkigd	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	3	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncvvg3rh9h462tcw	vw9rlol15y37u5ok	c69gbr33uorqy7r	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	4	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncwupi1yh17i44lk	vw9rlol15y37u5ok	c3se5eac1nun01u	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	5	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
nc4guu4ytmcjpdlb	vw9rlol15y37u5ok	cn7t5jqfob1xqys	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	6	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncj59f7m9tg847pr	vw9rlol15y37u5ok	cneon7k1vc1c1a3	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	7	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncohu1l8jat95buj	vw9rlol15y37u5ok	colzu9quxnxbnh8	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	8	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncm05lzt3wufdzep	vw9rlol15y37u5ok	cjmxnucuwdti0ov	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	9	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
nchhbkv0oamv7f59	vw9rlol15y37u5ok	c5yhz2syzrcsd70	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	10	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
nchhab7xweegccbc	vw9rlol15y37u5ok	cf2u8yfbufgeweq	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	11	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
nch4d0nt87oxhab7	vw9rlol15y37u5ok	cv7kikt4k5dsj5f	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	12	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncajz7rgj6p7j649	vw9rlol15y37u5ok	c395vprwrcmzl57	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	13	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncrox2i574rxlnz7	vw9rlol15y37u5ok	cvyo6ytuiyrg9hl	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	14	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncux8wsdgh2zprbj	vw9rlol15y37u5ok	cxoeozdh0k34iyj	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	15	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncqx21h4ebuz4kxj	vw9rlol15y37u5ok	ckmcuh9od42kkvb	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	16	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
nczi4y30cv2nq6f4	vw8zitic4fndcxgh	cft17n3bxvzco6n	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	1	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	\N	\N	\N	none
nc3u00p5fhu7buj5	vw8zitic4fndcxgh	c2gc3o7nudv7tb8	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	2	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	\N	\N	\N	none
nct6vtjh03l4745m	vw8zitic4fndcxgh	cv1vkbto1cqgg13	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	3	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	\N	\N	\N	none
ncvranl0wyqwn060	vw8zitic4fndcxgh	c7rupva2bbsd942	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	4	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	\N	\N	\N	none
ncpi0kj3x3p99vda	vw8zitic4fndcxgh	chwey76orqjoarm	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	5	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	\N	\N	\N	none
ncv6ohca6sd9l7dp	vw8zitic4fndcxgh	chahes6qex1hndj	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	6	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	\N	\N	\N	none
ncjxwy1z3bylb5rq	vw8zitic4fndcxgh	cu2b8rj8vkl3nf0	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	7	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	\N	\N	\N	none
ncq99j6kiqv85vis	vw8zitic4fndcxgh	crh0cx4kyxg85sa	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	8	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	\N	\N	\N	none
ncrat47e9fe555io	vw8zitic4fndcxgh	c3u2lv026zljxoz	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	9	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	\N	\N	\N	none
nca7az2flps869rw	vw8zitic4fndcxgh	ca8lrrfqlnzcm26	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	10	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	\N	\N	\N	none
nccq0xyeo47qg1wi	vw8zitic4fndcxgh	c5wgcib9tpnzcr6	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	11	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	\N	\N	\N	none
nc3afefpq2tuyn5w	vw8zitic4fndcxgh	c033hx4s3pwntgh	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	12	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	\N	\N	\N	none
ncg9c29e1ht04wma	vwn0c9s1zlncaz5d	crghbrr65i2tlbu	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	1	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
nch2u6m5xxe4qyeb	vwn0c9s1zlncaz5d	cl4kbxvsw9jfho7	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	2	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncxv6j0mjyacelbn	vwn0c9s1zlncaz5d	ceui606d8jwe9ju	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	3	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncpp3o0zjb82dkjk	vwn0c9s1zlncaz5d	c9k50d4m2330h0x	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	4	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
nc3y1fy69tu513a3	vwn0c9s1zlncaz5d	cxgi277ii77m5fy	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	5	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncuh7mlbrky0aype	vwn0c9s1zlncaz5d	colbujailyyr19l	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	6	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncn0ur1dno4gtv7j	vwn0c9s1zlncaz5d	cfmgudix0qksgsv	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	7	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
nc9oco176zzd960t	vwn0c9s1zlncaz5d	c0fosu85jg3s2jh	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	8	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncliof047sfmv29z	vwn0c9s1zlncaz5d	cntg34pxhcn8fzp	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	9	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
nc4u0z6mp11kit57	vwn0c9s1zlncaz5d	cocxr9dfmjsndgm	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	10	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncurt9czqq9p72ag	vwn0c9s1zlncaz5d	co266doam53yl5p	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	11	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
nc27ii0036ab884p	vwn0c9s1zlncaz5d	ccoph5bl1lxzm62	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	12	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
nc7ptity3v8nwiy4	vwn0c9s1zlncaz5d	calm53w3wy3ybmf	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	13	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
nctseg6j8gxrnq62	vwn0c9s1zlncaz5d	cmn8rsd9pe6xkis	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	14	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncmmr9zmffok9itb	vwn0c9s1zlncaz5d	cdv38fdll8o6up3	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	15	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncejjie0wdi787ua	vwh0uq249e5i5hbh	cc4mkzpmgh9vrp2	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	1	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncojmzdcuoq6rrjo	vwh0uq249e5i5hbh	co17kfo1sg603dy	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	2	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncl9e14iax0po10g	vwh0uq249e5i5hbh	ca4lddk146v74zd	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	3	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
nco0va4uyien2zu1	vwh0uq249e5i5hbh	ciar62fx5ef6659	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	4	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
nctcb4s4zvvong2x	vwh0uq249e5i5hbh	c6uwnbjl1r5mju0	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	5	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
nce37xram29ogzzo	vwh0uq249e5i5hbh	c1g5wjmqu5d668i	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	6	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
nc0lutavnguc7qsb	vwh0uq249e5i5hbh	cn448us2zt8yitp	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	7	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
nca500qo7o307u4n	vwh0uq249e5i5hbh	cyf6y1aedi2zm2w	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	8	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncttpki6mpiys6td	vwh0uq249e5i5hbh	cqsd7qq1yjvu3u6	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	9	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
nc7nf7vxnp83ssde	vwh0uq249e5i5hbh	cpkt9wuu4sozth6	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	10	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
nce6glst4sw61v0h	vwh0uq249e5i5hbh	cg0z4k44cktp7po	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	11	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncliyb10f7uftu6f	vwh0uq249e5i5hbh	c7xu8j452nqmfnh	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	12	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncf3r686k06jtrlr	vw8u9se8bzhmx7z9	crtkv2hik413x5a	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	1	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	\N	\N	\N	none
nc4xn3486mqfegx6	vw8u9se8bzhmx7z9	chbafyj23t8h3t8	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	2	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	\N	\N	\N	none
nc5cg8sxlw8oevby	vw8u9se8bzhmx7z9	c2nn1lgezk2u5xy	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	3	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	\N	\N	\N	none
ncrv7l2aphdl2n35	vw8u9se8bzhmx7z9	cpbdi22opzkv8du	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	4	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	\N	\N	\N	none
nczidrcmyzucon5j	vw8u9se8bzhmx7z9	cnn1slzb4g8a9ae	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	5	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	\N	\N	\N	none
ncga2ylt3qfgm1mo	vw8u9se8bzhmx7z9	cnn563xrm5wws3c	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	6	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	\N	\N	\N	none
ncu9h78y1896qwxo	vw8u9se8bzhmx7z9	chinmfbl9u3sww2	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	7	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	\N	\N	\N	none
ncje2nfs1cczzz69	vw8u9se8bzhmx7z9	c58qbvmi535hl8f	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	8	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	\N	\N	\N	none
ncwxczbli9fikra0	vw8u9se8bzhmx7z9	chzsfpz1xcf0dgw	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	9	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	\N	\N	\N	none
ncv0f7jbt7unsmpe	vw8u9se8bzhmx7z9	cb6pm56nja53kw9	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	10	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	\N	\N	\N	none
ncmpopdovgiqunah	vw8u9se8bzhmx7z9	c2xbmipf3pmn2og	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	11	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	\N	\N	\N	none
ncl6noad07n5kxtw	vw8u9se8bzhmx7z9	ccp11g3e72iil1u	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	12	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	\N	\N	\N	none
ncuzbyfaqy1xg71y	vwg79nefrwr8d3qt	cn3oygm7rk9orhv	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	1	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncqafqdwm1lqslaa	vwg79nefrwr8d3qt	c5cc6a1ct8zu9tl	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	2	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncqx5wz57rzir7ky	vwg79nefrwr8d3qt	cymxw81qe37t06b	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	3	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
nc3dfluk5eazwycf	vwg79nefrwr8d3qt	c6pmtlu10bgqi8e	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	4	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
nc1ebeweigg6fksa	vwg79nefrwr8d3qt	cqvpzsa7muzvahe	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	5	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncnamhkf80kq0rxu	vwg79nefrwr8d3qt	czufc759mmzmzte	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	6	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
nctk3j0p85ezk55a	vwg79nefrwr8d3qt	c7qd4ezf5mek9p3	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	7	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
nccr5b50xdo5vnva	vwg79nefrwr8d3qt	c22psa2kc2792mn	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	8	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
nc7xkeua5dl6gx4d	vwg79nefrwr8d3qt	c6na7mjtdk6k7nl	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	9	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncx2fxl8q2zrasvf	vwg79nefrwr8d3qt	cqn6enmiw3mvggo	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	10	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
nc152s2rle5hfry3	vwg79nefrwr8d3qt	cyw5f2ouyakeetl	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	11	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
nc34b2y7b95yx82e	vwg79nefrwr8d3qt	ck8mfufae0nwyg5	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	12	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncr7u7dp80lke8gw	vwg79nefrwr8d3qt	c4mb01s5zwmwgn5	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	13	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncfz1vuj2kr7i4hu	vwg79nefrwr8d3qt	cxvjuy1a4ly8mth	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	14	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
nclx392jb1fi77q3	vwg79nefrwr8d3qt	c44jszl1hind848	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	15	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncut99zs9aqqdrqh	vwi6eravj3la901y	cfx0hh3vvkr9yu9	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	1	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
nc4wrnm28wiomvai	vwi6eravj3la901y	cgmp5gcjcaqzkzw	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	2	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
nc4yr4gd2ikw688q	vwi6eravj3la901y	clya1e8vpxtnusj	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	3	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncnn1zlca6aoul0q	vwi6eravj3la901y	cgk7qg876t5xi2y	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	4	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
nccec7ey32038slq	vwi6eravj3la901y	cn5nspgpm23vyzu	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	5	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
nc0mpqzojr6wsxn9	vwi6eravj3la901y	cg9dv5vw31plo6k	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	6	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
nc6063zr8df55tug	vwi6eravj3la901y	c0js689qcl0xhfh	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	7	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
nc4t0btsf05mj817	vwi6eravj3la901y	c8aubq62ldh6a67	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	8	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
nchrva7bduz07yeo	vwi6eravj3la901y	c3dz4r7omn8lsg5	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	9	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
nc4gslfb62w9f0m4	vwi6eravj3la901y	cnjp3jns5g15kz6	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	10	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncrd8mdqeh4qiz0n	vwi6eravj3la901y	c51hueut49afrub	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	11	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncttb45ouhvtwjpw	vw8u9se8bzhmx7z9	chz2hzuhhfsjwhl	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	13	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	\N	\N	\N	none
ncdozslnw435jm26	vweic5xpl8rlg7t6	cd6rsrrhru7matc	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	1	2026-02-04 11:50:48+01	2026-02-04 11:50:48+01	\N	\N	\N	none
nck0znpek6vk5twc	vweic5xpl8rlg7t6	cb4bj5d7yotaijx	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	2	2026-02-04 11:50:48+01	2026-02-04 11:50:48+01	\N	\N	\N	none
ncb3xcwvd46eb3j6	vweic5xpl8rlg7t6	ce4hpj7p4zq8948	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	3	2026-02-04 11:50:48+01	2026-02-04 11:50:48+01	\N	\N	\N	none
ncv08ihymbxp1qmx	vweic5xpl8rlg7t6	che6swle0jywsdr	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	4	2026-02-04 11:50:48+01	2026-02-04 11:50:48+01	\N	\N	\N	none
nc4wfgx7foqqquau	vweic5xpl8rlg7t6	ciwcwek7fgr8lbu	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	5	2026-02-04 11:50:48+01	2026-02-04 11:50:48+01	\N	\N	\N	none
ncl18aiik037eyd6	vwhgdl1fodz1dstx	cdwm83qqvh18y4u	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	1	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncs11thdb8v7eitj	vwhgdl1fodz1dstx	c7lbximf46oj2og	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	2	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
nce2e87gvvcvjcba	vwhgdl1fodz1dstx	c4zk9sg1vu6rhag	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	3	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncrkyaqzua98nqhc	vwhgdl1fodz1dstx	c1tcdy8u6nv8yn3	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	4	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncydno11bg8cdzuf	vwhgdl1fodz1dstx	czcjput7b3iz3qu	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	5	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
nc5dqfpvasgpvbuq	vwhgdl1fodz1dstx	co9utg0xsmr47wg	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	6	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncfzrh40axi0k0in	vwhgdl1fodz1dstx	cn8plh9xmxlf1sd	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	7	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncegv5m4l8qfa7ha	vwhgdl1fodz1dstx	cljj6490e5wy0z1	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	8	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
nc40qxdwtpwquhrs	vwhgdl1fodz1dstx	c8a52kfs7igesr6	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	9	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
nca2sqyvvh5dccfu	vwhgdl1fodz1dstx	c0b6kxkcmknrmbz	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	10	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncn75w3zyqdacvrr	vwhgdl1fodz1dstx	c74e36i29wlgw2m	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	11	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
nc8eh7a42vdvz838	vwhgdl1fodz1dstx	c6w114nfydog3o6	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	12	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
nci3zfqtf565s8aj	vwhgdl1fodz1dstx	cef82lzbg01fuhc	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	13	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
nc23i31y9wm8nx16	vwhgdl1fodz1dstx	cr3uyexth3769aw	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	14	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncm3g4rv7q9tv6x7	vwhgdl1fodz1dstx	ce89e2ckcs82hw4	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	15	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncn3y1l888x4fude	vwhgdl1fodz1dstx	cunxivw0lk2ggok	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	16	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncqf3ce7knxo0wtc	vwhgdl1fodz1dstx	cmsq89vdiunny56	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	17	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncg79rk2qb9egjak	vwhgdl1fodz1dstx	cafac19aq8grbva	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	18	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncc4b878azypexuw	vwhgdl1fodz1dstx	cv8aty28f6dix2h	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	19	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
nc1cgrr78lcar6wq	vwhgdl1fodz1dstx	cd72o3xbmwy9vm9	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	20	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncmpx6ccn06ys3bo	vwhgdl1fodz1dstx	c8dgod9cg6pq0kf	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	21	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncuuny8r856rxozc	vwhgdl1fodz1dstx	crgafrxjp0gbki1	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	22	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncbe0rtd0unasxwi	vwhgdl1fodz1dstx	cmphy9c5imxsip2	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	23	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
ncjtlpaeuph2yxxo	vwhgdl1fodz1dstx	ch22n49kbwy5vp3	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	24	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
nc6dvgu952w3wb6x	vwhgdl1fodz1dstx	c31inzncoxixf84	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	\N	\N	200px	t	25	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N	\N	none
\.


--
-- Data for Name: nc_grid_view_v2; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public.nc_grid_view_v2 (fk_view_id, source_id, base_id, uuid, created_at, updated_at, meta, row_height) FROM stdin;
vweic5xpl8rlg7t6	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	2026-02-04 11:50:48+01	2026-02-04 11:50:48+01	\N	\N
vwpyj1825rdljhp4	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	2026-02-04 12:53:39+01	2026-02-04 12:53:39+01	\N	\N
vw1znarynk7fk1oe	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
vwn0c9s1zlncaz5d	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
vws4819bc08ixvxj	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	\N	\N
vwpgmxxz13357xvo	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	2026-01-06 20:52:52+01	2026-01-06 20:52:52+01	\N	\N
vwnatjh1ee7fnrko	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	2026-01-06 20:53:13+01	2026-01-06 20:53:13+01	\N	\N
vwb863vj0bh71lgi	bb4syuyu7fz1t03	pata00z3me9f1bz	\N	2026-01-06 20:53:28+01	2026-01-06 20:53:28+01	\N	\N
vwg79nefrwr8d3qt	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
vwhgdl1fodz1dstx	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
vwh0uq249e5i5hbh	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
vwi6eravj3la901y	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
vw9rlol15y37u5ok	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N	\N
vw8u9se8bzhmx7z9	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	\N	\N
vw8zitic4fndcxgh	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	\N	\N
\.


--
-- Data for Name: nc_hook_logs_v2; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public.nc_hook_logs_v2 (id, source_id, base_id, fk_hook_id, type, event, operation, test_call, payload, conditions, notification, error_code, error_message, error, execution_time, response, triggered_by, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: nc_hooks_v2; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public.nc_hooks_v2 (id, source_id, base_id, fk_model_id, title, description, env, type, event, operation, async, payload, url, headers, condition, notification, retries, retry_interval, timeout, active, created_at, updated_at, version) FROM stdin;
hk046suf7mfhn8pt	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	Notificación: Envío Email - Nuevo Lead	\N	all	\N	after	insert	f	t	\N	\N	f	{"type":"Email","payload":{"to":"Eduardovl5@hotmail.com, marimarpalacios25@hotmail.com","subject":"¡Yujuuu! Nuevo partner potencial en la lista: {{data.Nombre}}","body":"<div style=\\"font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #333; line-height: 1.6; max-width: 600px; margin: 0 auto; border: 1px solid #f0f0f0; padding: 20px; border-radius: 8px;\\">\\n    \\n    <p style=\\"font-size: 18px; margin-bottom: 25px;\\">🚀 <strong>¡Un nuevo socio tecnológico en camino!</strong> Mira quién ha escrito.</p>\\n\\n    <div style=\\"background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin-bottom: 20px;\\">\\n        <p style=\\"margin: 0; border-bottom: 1px solid #ddd; padding-bottom: 5px; font-weight: bold; color: #555;\\">DATOS DEL CONTACTO</p>\\n        <ul style=\\"list-style: none; padding: 0; margin-top: 10px;\\">\\n            <li><strong>Nombre:</strong> {{data.Nombre}}</li>\\n            <li><strong>Email:</strong> {{data.Email}}</li>\\n            <li><strong>Teléfono:</strong> {{data.Teléfono}}</li>\\n        </ul>\\n    </div>\\n\\n    <div style=\\"margin-bottom: 20px;\\">\\n        <p style=\\"margin: 0; border-bottom: 1px solid #ddd; padding-bottom: 5px; font-weight: bold; color: #555;\\">PERFIL DEL CLIENTE</p>\\n        <ul style=\\"list-style: none; padding: 0; margin-top: 10px;\\">\\n            <li><strong>Tipo de Empresa:</strong> {{data.[Tipo Empresa]}}</li>\\n            <li><strong>Servicio solicitado:</strong> {{data.Servicio}}</li>\\n            <li><strong>Mensaje:</strong> {{data.Mensaje}}</li>\\n        </ul>\\n    </div>\\n\\n    <p style=\\"padding: 10px; background-color: #e8f5e9; border-left: 4px solid #4caf50;\\">\\n        <strong>Estado:</strong> {{data.Estado}} | <strong>Prioridad:</strong> {{data.Prioridad}}\\n    </p>\\n\\n    <p style=\\"margin-top: 20px; font-size: 15px; color: #d81b60; font-weight: bold;\\">\\n        ¡A por ello! Un paso más cerca de nuestra meta. ❤️ 🛠️\\n    </p>\\n\\n    <hr style=\\"border: 0; border-top: 1px solid #eee; margin: 30px 0 20px 0;\\">\\n\\n    <table style=\\"width: 100%; border-collapse: collapse;\\">\\n        <tr>\\n            <td style=\\"width: 120px; vertical-align: middle;\\">\\n                <img src=\\"https://www.nucleotecnologico.es/assets/og/og-nucleo-tecnologico.png\\" alt=\\"Núcleo Tecnológico\\" style=\\"width: 100px; height: auto; display: block;\\">\\n            </td>\\n            <td style=\\"vertical-align: middle; padding-left: 15px;\\">\\n                <p style=\\"margin: 0; font-size: 12px; color: #888; font-style: italic;\\">\\n                    \\"Este email fue generado por un bot que trabaja para ti 24/7\\"\\n                </p>\\n                <p style=\\"margin: 0; font-size: 11px; color: #bbb; letter-spacing: 1px;\\">\\n                    NÚCLEO TECNOLÓGICO • PARTNER IT\\n                </p>\\n            </td>\\n        </tr>\\n    </table>\\n</div>"}}	0	60000	60000	t	2026-01-07 21:51:59+01	2026-01-08 22:44:32+01	v2
\.


--
-- Data for Name: nc_integrations_v2; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public.nc_integrations_v2 (id, title, config, meta, type, sub_type, is_private, deleted, created_by, "order", created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: nc_jmsd___Approval; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public."nc_jmsd___Approval" ("Id", lead, template, phase, draft_message, final_message, rationale, angle_quality, pain_quality, note, approved_by, approved_at, created_at, updated_at, created_by, updated_by) FROM stdin;
2	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-02-04 13:28:12	\N	us8g4rajnw6fzr9r	\N
\.


--
-- Data for Name: nc_jmsd___Attempt; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public."nc_jmsd___Attempt" ("Id", lead, attempt_type, phase, result, reason, metadata, attempt_at, created_at, updated_at, created_by, updated_by) FROM stdin;
1	\N	INVITE	INVITE	SUCCESS	Invitación enviada sin problemas	{"linkedin_status": "sent"}	\N	2026-02-04 11:59:44	\N	us5ceritq5sgzoni	\N
\.


--
-- Data for Name: nc_jmsd___Company; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public."nc_jmsd___Company" ("Id", name, domain, web_url, industry, location_city, location_region, employees_range, revenue_estimate_range, places_place_id, places_rating, places_reviews_total, places_types, places_website, places_phone, places_address, places_last_checked_at, places_signal_hash, web_signal_hash, web_last_checked_at, created_at, updated_at, created_by, updated_by) FROM stdin;
\.


--
-- Data for Name: nc_jmsd___Conversation; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public."nc_jmsd___Conversation" ("Id", lead, state, last_inbound_at, last_outbound_at, interest_level, cta_sent_at, cal_link, notes, created_at, updated_at, created_by, updated_by) FROM stdin;
1	\N	ACTIVE	\N	\N	WARM	\N	\N	Conversación de test activa	2026-02-04 11:59:44	\N	us5ceritq5sgzoni	\N
\.


--
-- Data for Name: nc_jmsd___Lead; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public."nc_jmsd___Lead" ("Id", linkedin_url, full_name, title, role_type, location_city, language, source, company, pack_candidate, segment, status, priority, lead_score, score_breakdown, scoring_version, created_at, invite_sent_at, accepted_at, next_action_at, wait_window_days, last_signal_checked_at, signal_changed, do_not_contact, do_not_contact_reason, email, phone, created_at1, updated_at, created_by, updated_by) FROM stdin;
1	https://linkedin.com/in/carlos-garcia-test-001	Carlos García [TEST]	Owner	OWNER	Barcelona	ES	SALES_NAV	\N	\N	\N	NEW	HIGH	78	{"fit": 40, "maps": 28, "web": 10}	v1.0	\N	\N	\N	\N	14	\N	f	f	\N	carlos@talleresgarcia-test.com	+34 93 987 65 43	2026-02-04 11:59:44	\N	us5ceritq5sgzoni	\N
\.


--
-- Data for Name: nc_jmsd___Message_Template; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public."nc_jmsd___Message_Template" ("Id", template_key, pack, segment, phase, language, template_text, variables, version, is_active, notes, created_at, updated_at, created_by, updated_by) FROM stdin;
1	GUARDIAN_FIRST_TEST	\N	\N	FIRST_MESSAGE	ES	Hola {{name}}, vi tu taller y me pareció {{signal}}.	["name", "signal"]	1	t	Template de test	2026-02-04 11:59:44	\N	us5ceritq5sgzoni	\N
\.


--
-- Data for Name: nc_jmsd___Outcome; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public."nc_jmsd___Outcome" ("Id", lead, call_booked_at, call_held_at, outcome, package_recommended, value_estimate, notes, created_at, updated_at, created_by, updated_by) FROM stdin;
1	\N	\N	\N	QUALIFIED	\N	650	Test outcome — qualified lead	2026-02-04 11:59:44	\N	us5ceritq5sgzoni	\N
\.


--
-- Data for Name: nc_jmsd___Pack; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public."nc_jmsd___Pack" ("Id", pack_key, name, price_min, price_max, description, is_active, icp_rules, scoring_weights, created_at, updated_at, created_at1, updated_at1, created_by, updated_by) FROM stdin;
\.


--
-- Data for Name: nc_jmsd___Research_Snapshot; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public."nc_jmsd___Research_Snapshot" ("Id", company, lead, source, signals, signal_hash, created_at, created_at1, updated_at, created_by, updated_by) FROM stdin;
1	\N	\N	MIXED	{"web": "modern_tech", "places": "high_rating"}	sha256:snapshot_test_001	\N	2026-02-04 11:59:44	\N	us5ceritq5sgzoni	\N
\.


--
-- Data for Name: nc_jmsd___Segment; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public."nc_jmsd___Segment" ("Id", segment_key, pack, name, type, status, definition, daily_invite_cap, start_date, end_date, notes, created_at, updated_at, created_by, updated_by) FROM stdin;
1	BCN_A_LT50REV_GUARDIAN_TEST	\N	BCN A <50 reviews [TEST]	AB_TEST	RUNNING	{"city": "Barcelona", "reviews_bucket": "LT50", "test": true}	10	\N	\N	Segmento de test — se puede eliminar.	2026-02-04 11:59:43	\N	us5ceritq5sgzoni	\N
\.


--
-- Data for Name: nc_jobs; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public.nc_jobs (id, job, status, result, fk_user_id, fk_workspace_id, base_id, created_at, updated_at) FROM stdin;
jobxc3v65uifez5c5	init-migration-jobs	completed	\N	\N	\N	\N	2025-12-29 20:35:13+01	2025-12-29 20:35:13+01
jobo3yibf5btxkkte	init-migration-jobs	completed	\N	\N	\N	\N	2026-02-04 14:45:34+01	2026-02-04 14:45:34+01
jobmsr838m59d0v1z	handle-webhook	completed	\N	us8g4rajnw6fzr9r	\N	pata00z3me9f1bz	2026-01-08 17:54:46+01	2026-01-08 17:54:47+01
job1n5vuqlogmwuki	handle-webhook	completed	\N	us8g4rajnw6fzr9r	\N	pata00z3me9f1bz	2026-01-08 21:41:33+01	2026-01-08 21:41:33+01
jobdx6uohnezitcty	handle-webhook	completed	\N	us8g4rajnw6fzr9r	\N	pata00z3me9f1bz	2026-01-08 21:50:18+01	2026-01-08 21:50:19+01
job0eznyv4fbfjend	init-migration-jobs	completed	\N	\N	\N	\N	2026-02-04 14:50:45+01	2026-02-04 14:50:45+01
jobq60sveswn5hy0i	handle-webhook	completed	\N	us8g4rajnw6fzr9r	\N	pata00z3me9f1bz	2026-01-08 21:51:53+01	2026-01-08 21:51:54+01
job6zye1npx3y14ba	handle-webhook	completed	\N	us8g4rajnw6fzr9r	\N	pata00z3me9f1bz	2026-01-08 21:56:47+01	2026-01-08 21:56:47+01
jobv2biico40vtb8y	handle-webhook	completed	\N	us8g4rajnw6fzr9r	\N	pata00z3me9f1bz	2026-01-08 22:08:19+01	2026-01-08 22:08:20+01
job8uopl086m5mmud	init-migration-jobs	completed	\N	\N	\N	\N	2026-02-04 15:17:48+01	2026-02-04 15:17:48+01
job8hzqumr6l8zoi1	handle-webhook	completed	\N	us8g4rajnw6fzr9r	\N	pata00z3me9f1bz	2026-01-08 22:12:32+01	2026-01-08 22:12:33+01
jobjnt1ymm2zlc46f	handle-webhook	completed	\N	us8g4rajnw6fzr9r	\N	pata00z3me9f1bz	2026-01-08 22:14:54+01	2026-01-08 22:14:54+01
jobjeyojsbh3w4cfh	handle-webhook	completed	\N	us8g4rajnw6fzr9r	\N	pata00z3me9f1bz	2026-01-08 22:21:40+01	2026-01-08 22:21:40+01
job9vgm3gsnibe0yp	init-migration-jobs	completed	\N	\N	\N	\N	2026-02-04 15:24:38+01	2026-02-04 15:24:38+01
joblmryh84s5uzn8p	handle-webhook	completed	\N	us8g4rajnw6fzr9r	\N	pata00z3me9f1bz	2026-01-08 22:26:10+01	2026-01-08 22:26:11+01
jobega5j22fd3fyxt	handle-webhook	completed	\N	us8g4rajnw6fzr9r	\N	pata00z3me9f1bz	2026-01-08 22:33:15+01	2026-01-08 22:33:15+01
job355oglrqpzkk3g	handle-webhook	completed	\N	us8g4rajnw6fzr9r	\N	pata00z3me9f1bz	2026-01-08 22:41:06+01	2026-01-08 22:41:06+01
jobh1ja8c4inkxt7k	init-migration-jobs	completed	\N	\N	\N	\N	2026-02-04 15:31:41+01	2026-02-04 15:31:41+01
job0ajwv5xvi26hyg	handle-webhook	completed	\N	us8g4rajnw6fzr9r	\N	pata00z3me9f1bz	2026-01-08 22:46:30+01	2026-01-08 22:46:31+01
job17ysdcksmv9721	init-migration-jobs	completed	\N	\N	\N	\N	2026-01-22 11:02:50+01	2026-01-22 11:02:50+01
joblveoi2wjwtttpd	handle-webhook	completed	\N	us8g4rajnw6fzr9r	\N	pata00z3me9f1bz	2026-01-23 20:40:23+01	2026-01-23 20:40:23+01
jobxemirq2e2m6u98	init-migration-jobs	completed	\N	\N	\N	\N	2026-02-04 15:36:37+01	2026-02-04 15:36:37+01
job7m45xvbcxaof8h	init-migration-jobs	completed	\N	\N	\N	\N	2026-02-04 14:00:40+01	2026-02-04 14:00:40+01
jobx1efyjmkuue7cx	init-migration-jobs	completed	\N	\N	\N	\N	2026-02-04 14:24:31+01	2026-02-04 14:24:31+01
job1gzi84962bitn2	init-migration-jobs	completed	\N	\N	\N	\N	2026-02-04 14:30:59+01	2026-02-04 14:30:59+01
job1z277bw13hvd2q	init-migration-jobs	completed	\N	\N	\N	\N	2026-02-04 14:35:07+01	2026-02-04 14:35:07+01
\.


--
-- Data for Name: nc_kanban_view_columns_v2; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public.nc_kanban_view_columns_v2 (id, source_id, base_id, fk_view_id, fk_column_id, uuid, label, help, show, "order", created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: nc_kanban_view_v2; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public.nc_kanban_view_v2 (fk_view_id, source_id, base_id, show, "order", uuid, title, public, password, show_all_fields, created_at, updated_at, fk_grp_col_id, fk_cover_image_col_id, meta) FROM stdin;
\.


--
-- Data for Name: nc_map_view_columns_v2; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public.nc_map_view_columns_v2 (id, base_id, project_id, fk_view_id, fk_column_id, uuid, label, help, show, "order", created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: nc_map_view_v2; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public.nc_map_view_v2 (fk_view_id, source_id, base_id, uuid, title, fk_geo_data_col_id, meta, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: nc_models_v2; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public.nc_models_v2 (id, source_id, base_id, table_name, title, type, meta, schema, enabled, mm, tags, pinned, deleted, "order", created_at, updated_at, description) FROM stdin;
m2t8ts768utecu3	bb4syuyu7fz1t03	pata00z3me9f1bz	nc_fl6j___LeadAnswers	Leadanswers	table	{"hasNonDefaultViews":false}	\N	t	f	\N	\N	\N	4	2026-01-06 20:53:28+01	2026-01-06 20:53:28+01	\N
mcyckhd2a05m772	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	nc_jmsd___Attempt	Attempt	table	{"hasNonDefaultViews":false}	\N	t	f	\N	\N	\N	18	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N
m4dhntou135vxm1	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	nc_jmsd___Research_Snapshot	ResearchSnapshot	table	{"hasNonDefaultViews":false}	\N	t	f	\N	\N	\N	19	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N
mx1ud1d86w1d4y6	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	nc_jmsd___Approval	Approval	table	{"hasNonDefaultViews":false}	\N	t	f	\N	\N	\N	20	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N
mzvwidn4z544pas	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	nc_jmsd___Conversation	Conversation	table	{"hasNonDefaultViews":false}	\N	t	f	\N	\N	\N	21	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	\N
mp45w6rbyjyh6ks	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	nc_jmsd___Outcome	Outcome	table	{"hasNonDefaultViews":false}	\N	t	f	\N	\N	\N	22	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	\N
m965eotz3l7hxbi	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	nc_jmsd___Pack	Pack	table	{"hasNonDefaultViews":false}	\N	t	f	\N	\N	\N	13	2026-02-04 12:53:39+01	2026-02-04 12:53:39+01	\N
merj80wv3zr0yzl	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	nc_jmsd___Company	Company	table	{"hasNonDefaultViews":false}	\N	t	f	\N	\N	\N	14	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N
m7nt9pg5uw1e4h3	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	nc_jmsd___Segment	Segment	table	{"hasNonDefaultViews":false}	\N	t	f	\N	\N	\N	15	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N
m7d1wkpymm3kj7l	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	nc_jmsd___Message_Template	MessageTemplate	table	{"hasNonDefaultViews":false}	\N	t	f	\N	\N	\N	16	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N
mc5itfivoyx2rp5	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	nc_jmsd___Lead	Lead	table	{"hasNonDefaultViews":false}	\N	t	f	\N	\N	\N	17	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	\N
mn7w22ahohc9ngr	bb4syuyu7fz1t03	pata00z3me9f1bz	nc_fl6j___Leads	Leads	table	{"hasNonDefaultViews":false}	\N	t	f	\N	\N	\N	1	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	\N
meivlfimb46wep7	bb4syuyu7fz1t03	pata00z3me9f1bz	nc_fl6j___ServiceQuestions	Servicequestions	table	{"hasNonDefaultViews":false}	\N	t	f	\N	\N	\N	2	2026-01-06 20:52:52+01	2026-01-06 20:52:52+01	\N
myz6dmx69dbmfod	bb4syuyu7fz1t03	pata00z3me9f1bz	nc_fl6j___ServiceQuestionOptions	Servicequestionoptions	table	{"hasNonDefaultViews":false}	\N	t	f	\N	\N	\N	3	2026-01-06 20:53:13+01	2026-01-06 20:53:13+01	\N
\.


--
-- Data for Name: nc_orgs_v2; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public.nc_orgs_v2 (id, title, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: nc_plugins_v2; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public.nc_plugins_v2 (id, title, description, active, rating, version, docs, status, status_details, logo, icon, tags, category, input_schema, input, creator, creator_website, price, created_at, updated_at) FROM stdin;
ncm15fqq4dhsy2tx	Slack	Slack brings team communication and collaboration into one place so you can get more work done, whether you belong to a large enterprise or a small business. 	f	\N	0.0.1	\N	install	\N	plugins/slack.webp	\N	Chat	Chat	{"title":"Configure Slack","array":true,"items":[{"key":"channel","label":"Channel Name","placeholder":"Channel Name","type":"SingleLineText","required":true},{"key":"webhook_url","label":"Webhook URL","placeholder":"Webhook URL","type":"Password","required":true}],"actions":[{"label":"Test","placeholder":"Test","key":"test","actionType":"TEST","type":"Button"},{"label":"Save","placeholder":"Save","key":"save","actionType":"SUBMIT","type":"Button"}],"msgOnInstall":"Successfully installed and Slack is enabled for notification.","msgOnUninstall":""}	\N	\N	\N	\N	2025-12-29 20:35:13+01	2025-12-29 20:35:13+01
nc6f84x4al6ycvnu	Microsoft Teams	Microsoft Teams is for everyone · Instantly go from group chat to video call with the touch of a button.	f	\N	0.0.1	\N	install	\N	plugins/teams.ico	\N	Chat	Chat	{"title":"Configure Microsoft Teams","array":true,"items":[{"key":"channel","label":"Channel Name","placeholder":"Channel Name","type":"SingleLineText","required":true},{"key":"webhook_url","label":"Webhook URL","placeholder":"Webhook URL","type":"Password","required":true}],"actions":[{"label":"Test","placeholder":"Test","key":"test","actionType":"TEST","type":"Button"},{"label":"Save","placeholder":"Save","key":"save","actionType":"SUBMIT","type":"Button"}],"msgOnInstall":"Successfully installed and Microsoft Teams is enabled for notification.","msgOnUninstall":""}	\N	\N	\N	\N	2025-12-29 20:35:13+01	2025-12-29 20:35:13+01
nclqflbt9m4xuy6s	Discord	Discord is the easiest way to talk over voice, video, and text. Talk, chat, hang out, and stay close with your friends and communities.	f	\N	0.0.1	\N	install	\N	plugins/discord.png	\N	Chat	Chat	{"title":"Configure Discord","array":true,"items":[{"key":"channel","label":"Channel Name","placeholder":"Channel Name","type":"SingleLineText","required":true},{"key":"webhook_url","label":"Webhook URL","type":"Password","placeholder":"Webhook URL","required":true}],"actions":[{"label":"Test","placeholder":"Test","key":"test","actionType":"TEST","type":"Button"},{"label":"Save","placeholder":"Save","key":"save","actionType":"SUBMIT","type":"Button"}],"msgOnInstall":"Successfully installed and Discord is enabled for notification.","msgOnUninstall":""}	\N	\N	\N	\N	2025-12-29 20:35:13+01	2025-12-29 20:35:13+01
nc6x7i12gszzdpd9	Whatsapp Twilio	With Twilio, unite communications and strengthen customer relationships across your business – from marketing and sales to customer service and operations.	f	\N	0.0.1	\N	install	\N	plugins/whatsapp.png	\N	Chat	Twilio	{"title":"Configure Twilio","items":[{"key":"sid","label":"Account SID","placeholder":"Account SID","type":"SingleLineText","required":true},{"key":"token","label":"Auth Token","placeholder":"Auth Token","type":"Password","required":true},{"key":"from","label":"From Phone Number","placeholder":"From Phone Number","type":"SingleLineText","required":true}],"actions":[{"label":"Test","placeholder":"Test","key":"test","actionType":"TEST","type":"Button"},{"label":"Save","placeholder":"Save","key":"save","actionType":"SUBMIT","type":"Button"}],"msgOnInstall":"Successfully installed and Whatsapp Twilio is enabled for notification.","msgOnUninstall":""}	\N	\N	\N	\N	2025-12-29 20:35:13+01	2025-12-29 20:35:13+01
nc3f9zh8ycs24soh	Twilio	With Twilio, unite communications and strengthen customer relationships across your business – from marketing and sales to customer service and operations.	f	\N	0.0.1	\N	install	\N	plugins/twilio.png	\N	Chat	Twilio	{"title":"Configure Twilio","items":[{"key":"sid","label":"Account SID","placeholder":"Account SID","type":"SingleLineText","required":true},{"key":"token","label":"Auth Token","placeholder":"Auth Token","type":"Password","required":true},{"key":"from","label":"From Phone Number","placeholder":"From Phone Number","type":"SingleLineText","required":true}],"actions":[{"label":"Test","placeholder":"Test","key":"test","actionType":"TEST","type":"Button"},{"label":"Save","placeholder":"Save","key":"save","actionType":"SUBMIT","type":"Button"}],"msgOnInstall":"Successfully installed and Twilio is enabled for notification.","msgOnUninstall":""}	\N	\N	\N	\N	2025-12-29 20:35:13+01	2025-12-29 20:35:13+01
ncbovyuyu1yo0m3w	S3	Amazon Simple Storage Service (Amazon S3) is an object storage service that offers industry-leading scalability, data availability, security, and performance.	f	\N	0.0.5	\N	install	\N	plugins/s3.png	\N	Storage	Storage	{"title":"Configure Amazon S3","items":[{"key":"bucket","label":"Bucket Name","placeholder":"Bucket Name","type":"SingleLineText","required":true},{"key":"region","label":"Region","placeholder":"Region","type":"SingleLineText","required":true},{"key":"endpoint","label":"Endpoint","placeholder":"Endpoint","type":"SingleLineText","required":false},{"key":"access_key","label":"Access Key","placeholder":"Access Key","type":"SingleLineText","required":true},{"key":"access_secret","label":"Access Secret","placeholder":"Access Secret","type":"Password","required":true},{"key":"acl","label":"Access Control Lists (ACL)","placeholder":"","type":"SingleLineText","required":false},{"key":"force_path_style","label":"Force Path Style","placeholder":"Default set to false","type":"Checkbox","required":false}],"actions":[{"label":"Test","placeholder":"Test","key":"test","actionType":"TEST","type":"Button"},{"label":"Save","placeholder":"Save","key":"save","actionType":"SUBMIT","type":"Button"}],"msgOnInstall":"Successfully installed and attachment will be stored in AWS S3","msgOnUninstall":""}	\N	\N	\N	\N	2025-12-29 20:35:13+01	2025-12-29 20:35:13+01
ncgln87wv077b0qe	Minio	MinIO is a High Performance Object Storage released under Apache License v2.0. It is API compatible with Amazon S3 cloud storage service.	f	\N	0.0.3	\N	install	\N	plugins/minio.png	\N	Storage	Storage	{"title":"Configure Minio","items":[{"key":"endPoint","label":"Minio Endpoint","placeholder":"Minio Endpoint","type":"SingleLineText","required":true},{"key":"port","label":"Port","placeholder":"Port","type":"Number","required":true},{"key":"bucket","label":"Bucket Name","placeholder":"Bucket Name","type":"SingleLineText","required":true},{"key":"access_key","label":"Access Key","placeholder":"Access Key","type":"SingleLineText","required":true},{"key":"access_secret","label":"Access Secret","placeholder":"Access Secret","type":"Password","required":true},{"key":"ca","label":"Ca","placeholder":"Ca","type":"LongText"},{"key":"useSSL","label":"Use SSL","placeholder":"Use SSL","type":"Checkbox","required":false}],"actions":[{"label":"Test","placeholder":"Test","key":"test","actionType":"TEST","type":"Button"},{"label":"Save","placeholder":"Save","key":"save","actionType":"SUBMIT","type":"Button"}],"msgOnInstall":"Successfully installed and attachment will be stored in Minio","msgOnUninstall":""}	\N	\N	\N	\N	2025-12-29 20:35:13+01	2025-12-29 20:35:13+01
ncwqc4cpxqni85k4	GCS	Google Cloud Storage is a RESTful online file storage web service for storing and accessing data on Google Cloud Platform infrastructure.	f	\N	0.0.2	\N	install	\N	plugins/gcs.png	\N	Storage	Storage	{"title":"Configure Google Cloud Storage","items":[{"key":"bucket","label":"Bucket Name","placeholder":"Bucket Name","type":"SingleLineText","required":true},{"key":"client_email","label":"Client Email","placeholder":"Client Email","type":"SingleLineText","required":true},{"key":"private_key","label":"Private Key","placeholder":"Private Key","type":"Password","required":true},{"key":"project_id","label":"Project ID","placeholder":"Project ID","type":"SingleLineText","required":false}],"actions":[{"label":"Test","placeholder":"Test","key":"test","actionType":"TEST","type":"Button"},{"label":"Save","placeholder":"Save","key":"save","actionType":"SUBMIT","type":"Button"}],"msgOnInstall":"Successfully installed and attachment will be stored in Google Cloud Storage","msgOnUninstall":""}	\N	\N	\N	\N	2025-12-29 20:35:13+01	2025-12-29 20:35:13+01
ncjr8ealuxf8nfhv	Mattermost	Mattermost brings all your team communication into one place, making it searchable and accessible anywhere.	f	\N	0.0.1	\N	install	\N	plugins/mattermost.png	\N	Chat	Chat	{"title":"Configure Mattermost","array":true,"items":[{"key":"channel","label":"Channel Name","placeholder":"Channel Name","type":"SingleLineText","required":true},{"key":"webhook_url","label":"Webhook URL","placeholder":"Webhook URL","type":"Password","required":true}],"actions":[{"label":"Test","placeholder":"Test","key":"test","actionType":"TEST","type":"Button"},{"label":"Save","placeholder":"Save","key":"save","actionType":"SUBMIT","type":"Button"}],"msgOnInstall":"Successfully installed and Mattermost is enabled for notification.","msgOnUninstall":""}	\N	\N	\N	\N	2025-12-29 20:35:13+01	2025-12-29 20:35:13+01
ncdby5tyqathc4bc	Spaces	Store & deliver vast amounts of content with a simple architecture.	f	\N	0.0.1	\N	install	\N	plugins/spaces.png	\N	Storage	Storage	{"title":"DigitalOcean Spaces","items":[{"key":"bucket","label":"Bucket Name","placeholder":"Bucket Name","type":"SingleLineText","required":true},{"key":"region","label":"Region","placeholder":"Region","type":"SingleLineText","required":true},{"key":"access_key","label":"Access Key","placeholder":"Access Key","type":"SingleLineText","required":true},{"key":"access_secret","label":"Access Secret","placeholder":"Access Secret","type":"Password","required":true},{"key":"acl","label":"Access Control Lists (ACL)","placeholder":"Default set to public-read","type":"SingleLineText","required":false}],"actions":[{"label":"Test","placeholder":"Test","key":"test","actionType":"TEST","type":"Button"},{"label":"Save","placeholder":"Save","key":"save","actionType":"SUBMIT","type":"Button"}],"msgOnInstall":"Successfully installed and attachment will be stored in DigitalOcean Spaces","msgOnUninstall":""}	\N	\N	\N	\N	2025-12-29 20:35:13+01	2025-12-29 20:35:13+01
nc1i8d9bs233rps5	Backblaze B2	Backblaze B2 is enterprise-grade, S3 compatible storage that companies around the world use to store and serve data while improving their cloud OpEx vs. Amazon S3 and others.	f	\N	0.0.3	\N	install	\N	plugins/backblaze.jpeg	\N	Storage	Storage	{"title":"Configure Backblaze B2","items":[{"key":"bucket","label":"Bucket Name","placeholder":"Bucket Name","type":"SingleLineText","required":true},{"key":"region","label":"Region","placeholder":"e.g. us-west-001","type":"SingleLineText","required":true},{"key":"access_key","label":"Access Key","placeholder":"i.e. keyID in App Keys","type":"SingleLineText","required":true},{"key":"access_secret","label":"Access Secret","placeholder":"i.e. applicationKey in App Keys","type":"Password","required":true},{"key":"acl","label":"Access Control Lists (ACL)","placeholder":"Default set to public-read","type":"SingleLineText","required":false}],"actions":[{"label":"Test","placeholder":"Test","key":"test","actionType":"TEST","type":"Button"},{"label":"Save","placeholder":"Save","key":"save","actionType":"SUBMIT","type":"Button"}],"msgOnInstall":"Successfully installed and attachment will be stored in Backblaze B2","msgOnUninstall":""}	\N	\N	\N	\N	2025-12-29 20:35:13+01	2025-12-29 20:35:13+01
ncdwgpieef006ee3	Vultr Object Storage	Using Vultr Object Storage can give flexibility and cloud storage that allows applications greater flexibility and access worldwide.	f	\N	0.0.3	\N	install	\N	plugins/vultr.png	\N	Storage	Storage	{"title":"Configure Vultr Object Storage","items":[{"key":"bucket","label":"Bucket Name","placeholder":"Bucket Name","type":"SingleLineText","required":true},{"key":"hostname","label":"Host Name","placeholder":"e.g.: ewr1.vultrobjects.com","type":"SingleLineText","required":true},{"key":"access_key","label":"Access Key","placeholder":"Access Key","type":"SingleLineText","required":true},{"key":"access_secret","label":"Access Secret","placeholder":"Access Secret","type":"Password","required":true},{"key":"acl","label":"Access Control Lists (ACL)","placeholder":"Default set to public-read","type":"SingleLineText","required":false}],"actions":[{"label":"Test","placeholder":"Test","key":"test","actionType":"TEST","type":"Button"},{"label":"Save","placeholder":"Save","key":"save","actionType":"SUBMIT","type":"Button"}],"msgOnInstall":"Successfully installed and attachment will be stored in Vultr Object Storage","msgOnUninstall":""}	\N	\N	\N	\N	2025-12-29 20:35:13+01	2025-12-29 20:35:13+01
nc6tfqxkq9u3l82p	OvhCloud Object Storage	Upload your files to a space that you can access via HTTPS using the OpenStack Swift API, or the S3 API. 	f	\N	0.0.2	\N	install	\N	plugins/ovhCloud.png	\N	Storage	Storage	{"title":"Configure OvhCloud Object Storage","items":[{"key":"bucket","label":"Bucket Name","placeholder":"Bucket Name","type":"SingleLineText","required":true},{"key":"region","label":"Region","placeholder":"Region","type":"SingleLineText","required":true},{"key":"access_key","label":"Access Key","placeholder":"Access Key","type":"SingleLineText","required":true},{"key":"access_secret","label":"Access Secret","placeholder":"Access Secret","type":"Password","required":true},{"key":"acl","label":"Access Control Lists (ACL)","placeholder":"Default set to public-read","type":"SingleLineText","required":false}],"actions":[{"label":"Test","placeholder":"Test","key":"test","actionType":"TEST","type":"Button"},{"label":"Save","placeholder":"Save","key":"save","actionType":"SUBMIT","type":"Button"}],"msgOnInstall":"Successfully installed and attachment will be stored in OvhCloud Object Storage","msgOnUninstall":""}	\N	\N	\N	\N	2025-12-29 20:35:13+01	2025-12-29 20:35:13+01
ncb7ytx25sc9m23y	Linode Object Storage	S3-compatible Linode Object Storage makes it easy and more affordable to manage unstructured data such as content assets, as well as sophisticated and data-intensive storage challenges around artificial intelligence and machine learning.	f	\N	0.0.2	\N	install	\N	plugins/linode.svg	\N	Storage	Storage	{"title":"Configure Linode Object Storage","items":[{"key":"bucket","label":"Bucket Name","placeholder":"Bucket Name","type":"SingleLineText","required":true},{"key":"region","label":"Region","placeholder":"Region","type":"SingleLineText","required":true},{"key":"access_key","label":"Access Key","placeholder":"Access Key","type":"SingleLineText","required":true},{"key":"access_secret","label":"Access Secret","placeholder":"Access Secret","type":"Password","required":true},{"key":"acl","label":"Access Control Lists (ACL)","placeholder":"Default set to public-read","type":"SingleLineText","required":false}],"actions":[{"label":"Test","placeholder":"Test","key":"test","actionType":"TEST","type":"Button"},{"label":"Save","placeholder":"Save","key":"save","actionType":"SUBMIT","type":"Button"}],"msgOnInstall":"Successfully installed and attachment will be stored in Linode Object Storage","msgOnUninstall":""}	\N	\N	\N	\N	2025-12-29 20:35:13+01	2025-12-29 20:35:13+01
nctmrc9o957t6h37	UpCloud Object Storage	The perfect home for your data. Thanks to the S3-compatible programmable interface,\nyou have a host of options for existing tools and code implementations.\n	f	\N	0.0.2	\N	install	\N	plugins/upcloud.png	\N	Storage	Storage	{"title":"Configure UpCloud Object Storage","items":[{"key":"bucket","label":"Bucket Name","placeholder":"Bucket Name","type":"SingleLineText","required":true},{"key":"endpoint","label":"Endpoint","placeholder":"Endpoint","type":"SingleLineText","required":true},{"key":"access_key","label":"Access Key","placeholder":"Access Key","type":"SingleLineText","required":true},{"key":"access_secret","label":"Access Secret","placeholder":"Access Secret","type":"Password","required":true},{"key":"acl","label":"Access Control Lists (ACL)","placeholder":"Default set to public-read","type":"SingleLineText","required":false}],"actions":[{"label":"Test","placeholder":"Test","key":"test","actionType":"TEST","type":"Button"},{"label":"Save","placeholder":"Save","key":"save","actionType":"SUBMIT","type":"Button"}],"msgOnInstall":"Successfully installed and attachment will be stored in UpCloud Object Storage","msgOnUninstall":""}	\N	\N	\N	\N	2025-12-29 20:35:13+01	2025-12-29 20:35:13+01
nc1mhvvh5sa7rdhb	MailerSend	MailerSend email client	f	\N	0.0.1	\N	install	\N	plugins/mailersend.svg	\N	Email	Email	{"title":"Configure MailerSend","items":[{"key":"api_key","label":"API KEy","placeholder":"eg: ***************","type":"Password","required":true},{"key":"from","label":"From","placeholder":"eg: admin@run.com","type":"SingleLineText","required":true},{"key":"from_name","label":"From Name","placeholder":"eg: Adam","type":"SingleLineText","required":true}],"actions":[{"label":"Test","key":"test","actionType":"TEST","type":"Button"},{"label":"Save","key":"save","actionType":"SUBMIT","type":"Button"}],"msgOnInstall":"Successfully installed and email notification will use MailerSend configuration","msgOnUninstall":""}	\N	\N	\N	\N	2025-12-29 20:35:13+01	2025-12-29 20:35:13+01
nc63qz3kpv4ao0lk	Scaleway Object Storage	Scaleway Object Storage is an S3-compatible object store from Scaleway Cloud Platform.	f	\N	0.0.2	\N	install	\N	plugins/scaleway.png	\N	Storage	Storage	{"title":"Setup Scaleway","items":[{"key":"bucket","label":"Bucket name","placeholder":"Bucket name","type":"SingleLineText","required":true},{"key":"region","label":"Region of bucket","placeholder":"Region of bucket","type":"SingleLineText","required":true},{"key":"access_key","label":"Access Key","placeholder":"Access Key","type":"SingleLineText","required":true},{"key":"access_secret","label":"Access Secret","placeholder":"Access Secret","type":"Password","required":true},{"key":"acl","label":"Access Control Lists (ACL)","placeholder":"Default set to public-read","type":"SingleLineText","required":false}],"actions":[{"label":"Test","placeholder":"Test","key":"test","actionType":"TEST","type":"Button"},{"label":"Save","placeholder":"Save","key":"save","actionType":"SUBMIT","type":"Button"}],"msgOnInstall":"Successfully installed Scaleway Object Storage","msgOnUninstall":""}	\N	\N	\N	\N	2025-12-29 20:35:13+01	2025-12-29 20:35:13+01
ncv6ackqxolyboid	SES	Amazon Simple Email Service (SES) is a cost-effective, flexible, and scalable email service that enables developers to send mail from within any application.	f	\N	0.0.1	\N	install	\N	plugins/aws.png	\N	Email	Email	{"title":"Configure Amazon Simple Email Service (SES)","items":[{"key":"from","label":"From","placeholder":"From","type":"SingleLineText","required":true},{"key":"region","label":"Region","placeholder":"Region","type":"SingleLineText","required":true},{"key":"access_key","label":"Access Key","placeholder":"Access Key","type":"SingleLineText","required":true},{"key":"access_secret","label":"Access Secret","placeholder":"Access Secret","type":"Password","required":true}],"actions":[{"label":"Test","placeholder":"Test","key":"test","actionType":"TEST","type":"Button"},{"label":"Save","placeholder":"Save","key":"save","actionType":"SUBMIT","type":"Button"}],"msgOnInstall":"Successfully installed and email notification will use Amazon SES","msgOnUninstall":""}	\N	\N	\N	\N	2025-12-29 20:35:13+01	2025-12-29 20:35:13+01
ncji5jlg8r35psj5	Cloudflare R2 Storage	Cloudflare R2 is an S3-compatible, zero egress-fee, globally distributed object storage.	f	\N	0.0.1	\N	install	\N	plugins/r2.png	\N	Storage	Storage	{"title":"Configure Cloudflare R2 Storage","items":[{"key":"bucket","label":"Bucket Name","placeholder":"Bucket Name","type":"SingleLineText","required":true},{"key":"hostname","label":"Host Name","placeholder":"e.g.: *****.r2.cloudflarestorage.com","type":"SingleLineText","required":true},{"key":"access_key","label":"Access Key","placeholder":"Access Key","type":"SingleLineText","required":true},{"key":"access_secret","label":"Access Secret","placeholder":"Access Secret","type":"Password","required":true}],"actions":[{"label":"Test","placeholder":"Test","key":"test","actionType":"TEST","type":"Button"},{"label":"Save","placeholder":"Save","key":"save","actionType":"SUBMIT","type":"Button"}],"msgOnInstall":"Successfully installed and attachment will be stored in Cloudflare R2 Storage","msgOnUninstall":""}	\N	\N	\N	\N	2025-12-29 20:35:13+01	2025-12-29 20:35:13+01
nczvtwyc8jz4vm8v	SMTP	SMTP email client	t	\N	0.0.3	\N	install	\N	\N	\N	Email	Email	{"title":"Configure Email SMTP","items":[{"key":"from","label":"From Address","placeholder":"admin@run.com","type":"SingleLineText","required":true},{"key":"host","label":"SMTP Server","placeholder":"smtp.run.com","type":"SingleLineText","required":true},{"key":"name","label":"From Domain","placeholder":"your-domain.com","type":"SingleLineText","required":true},{"key":"port","label":"SMTP Port","placeholder":"Port","type":"SingleLineText","required":true},{"key":"secure","label":"Use Secure Connection","placeholder":"Secure","type":"Checkbox","required":false},{"key":"ignoreTLS","label":"Ignore TLS Errors","placeholder":"Ignore TLS","type":"Checkbox","required":false},{"key":"rejectUnauthorized","label":"Reject Unauthorized","placeholder":"Reject Unauthorized","type":"Checkbox","required":false},{"key":"username","label":"Username","placeholder":"Username","type":"SingleLineText","required":false},{"key":"password","label":"Password","placeholder":"Password","type":"Password","required":false}],"actions":[{"label":"Test","key":"test","actionType":"TEST","type":"Button"},{"label":"Save","key":"save","actionType":"SUBMIT","type":"Button"}],"msgOnInstall":"Successfully installed and email notification will use SMTP configuration","msgOnUninstall":""}	{"from":"team@nucleotecnologico.es","host":"authsmtp.securemail.pro","port":"465","username":"team@nucleotecnologico.es","password":"64qIP&Cd^2DhJDJLgY^%","secure":"true"}	\N	\N	\N	2025-12-29 20:35:13+01	2026-02-04 15:36:36+01
\.


--
-- Data for Name: nc_shared_bases; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public.nc_shared_bases (id, project_id, db_alias, roles, shared_base_id, enabled, password, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: nc_shared_views_v2; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public.nc_shared_views_v2 (id, fk_view_id, meta, query_params, view_id, show_all_fields, allow_copy, password, deleted, "order", created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: nc_sort_v2; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public.nc_sort_v2 (id, source_id, base_id, fk_view_id, fk_column_id, direction, "order", created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: nc_sources_v2; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public.nc_sources_v2 (id, base_id, alias, config, meta, is_meta, type, inflection_column, inflection_table, created_at, updated_at, enabled, "order", description, erd_uuid, deleted, is_schema_readonly, is_data_readonly, fk_integration_id) FROM stdin;
bb4syuyu7fz1t03	pata00z3me9f1bz	\N	U2FsdGVkX19CxgIYnitGeiUV77Jnt6RzwJWgxyGNVQI=	\N	t	pg	camelize	camelize	2025-12-30 17:27:36+01	2025-12-30 17:27:36+01	t	1	\N	\N	f	f	f	\N
b5f5jtriymzfd5p	pbydkvvvbvv4pdf	\N	U2FsdGVkX1+07uTxKL/AT22FFu+fNaeeE/6TmdRM/4g=	\N	t	pg	camelize	camelize	2026-02-03 10:56:38+01	2026-02-03 10:56:38+01	t	1	\N	\N	f	f	f	\N
\.


--
-- Data for Name: nc_store; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public.nc_store (id, base_id, db_alias, key, value, type, env, tag, created_at, updated_at) FROM stdin;
1	\N		NC_DEBUG	{"nc:app":false,"nc:api:rest":false,"nc:api:source":false,"nc:api:gql":false,"nc:api:grpc":false,"nc:migrator":false,"nc:datamapper":false}	\N	\N	\N	\N	\N
2	\N		NC_PROJECT_COUNT	0	\N	\N	\N	\N	\N
3	\N	db	NC_MIGRATION_JOBS	{"version":"1","stall_check":1767036910078,"locked":false,"instance":"6ee64037-9bf5-452c-b83d-b599ad1e8071"}	\N	\N	\N	2025-12-29 20:35:13+01	2025-12-29 20:35:13+01
4	\N	db	nc_server_id	3a2896caaed427f2915beb696a2013102805f6a0bf76a23cb3d5facf5f468ce7	\N	\N	\N	2025-12-29 20:35:13+01	2025-12-29 20:35:13+01
5	\N	db	NC_CONFIG_MAIN	{"version":"0111005"}	\N	\N	\N	2025-12-29 20:35:13+01	2025-12-29 20:35:13+01
\.


--
-- Data for Name: nc_sync_logs_v2; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public.nc_sync_logs_v2 (id, base_id, fk_sync_source_id, time_taken, status, status_details, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: nc_sync_source_v2; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public.nc_sync_source_v2 (id, title, type, details, deleted, enabled, "order", base_id, fk_user_id, created_at, updated_at, source_id) FROM stdin;
\.


--
-- Data for Name: nc_team_users_v2; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public.nc_team_users_v2 (org_id, user_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: nc_teams_v2; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public.nc_teams_v2 (id, title, org_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: nc_user_comment_notifications_preference; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public.nc_user_comment_notifications_preference (id, row_id, user_id, fk_model_id, source_id, base_id, preferences, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: nc_user_refresh_tokens; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public.nc_user_refresh_tokens (fk_user_id, token, meta, expires_at, created_at, updated_at) FROM stdin;
usf4zleee8lkaehw	11b47cf7281ab5a445ba416987a5d3fc9f806fbb8c472c61f53f5999bb64bb67ec848a10b9ce16eb	\N	2026-03-31 11:30:30.57+02	2025-12-31 11:30:30+01	2025-12-31 11:30:30+01
us8g4rajnw6fzr9r	f59751d6fad4db5cb4e5406891031beaf667d09345e3f089003a8eb85d3844e945150d34311750e9	\N	2026-05-05 10:19:24.62+02	2026-02-04 10:19:24+01	2026-02-04 10:19:24+01
\.


--
-- Data for Name: nc_users_v2; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public.nc_users_v2 (id, email, password, salt, invite_token, invite_token_expires, reset_password_expires, reset_password_token, email_verification_token, email_verified, roles, created_at, updated_at, token_version, display_name, user_name, blocked, blocked_reason) FROM stdin;
us8g4rajnw6fzr9r	team@mailerblend.com	$2a$10$LyPjpRurcMMSb3jwV0FVSOCPAnFcODX1OAi.VaKHZF5Xhn7dWmmJq	$2a$10$LyPjpRurcMMSb3jwV0FVSO	\N	\N	\N	\N	29262e2b-a2d9-46e3-b87f-266e2fb22bbc	\N	org-level-creator,super	2025-12-30 17:27:36+01	2026-02-04 10:19:24+01	0ab71458e5b29e7cfd7fa593d10ad83c3694a9d7e640328a60ff89a584a96ac78034d6536a948cf3	\N	\N	f	\N
us5ceritq5sgzoni	gestionads15.21@gmail.com	$2a$10$L51pGBFK2gLdA4WKGvF3he0maF/D5EBMJV0MuupRvmQchATWxdf4S	$2a$10$L51pGBFK2gLdA4WKGvF3he	\N	\N	\N	\N	13205b2a-531d-4d08-866f-9bf87e135667	\N	org-level-creator	2026-02-03 10:43:58+01	2026-02-04 11:28:34+01	fcccfa140d11bdd8708eaab3dbfd1a40d0c1d36085c20a10c60946f80c85f59a0f1b4df612897453	\N	\N	f	\N
\.


--
-- Data for Name: nc_views_v2; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public.nc_views_v2 (id, source_id, base_id, fk_model_id, title, type, is_default, show_system_fields, lock_type, uuid, password, show, "order", created_at, updated_at, meta, description) FROM stdin;
vweic5xpl8rlg7t6	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mc01xvnub0qtm7n	tabla_test_id	3	t	\N	collaborative	\N	\N	t	1	2026-02-04 11:50:48+01	2026-02-04 11:50:48+01	{}	\N
vwpyj1825rdljhp4	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m965eotz3l7hxbi	Pack	3	t	\N	collaborative	\N	\N	t	1	2026-02-04 12:53:39+01	2026-02-04 12:53:39+01	{}	\N
vw1znarynk7fk1oe	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	merj80wv3zr0yzl	Company	3	t	\N	collaborative	\N	\N	t	1	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	{}	\N
vwn0c9s1zlncaz5d	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m7nt9pg5uw1e4h3	Segment	3	t	\N	collaborative	\N	\N	t	1	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	{}	\N
vws4819bc08ixvxj	bb4syuyu7fz1t03	pata00z3me9f1bz	mn7w22ahohc9ngr	Leads	3	t	\N	collaborative	\N	\N	t	1	2026-01-06 20:52:25+01	2026-01-06 20:52:25+01	{}	\N
vwpgmxxz13357xvo	bb4syuyu7fz1t03	pata00z3me9f1bz	meivlfimb46wep7	Servicequestions	3	t	\N	collaborative	\N	\N	t	1	2026-01-06 20:52:52+01	2026-01-06 20:52:52+01	{}	\N
vwnatjh1ee7fnrko	bb4syuyu7fz1t03	pata00z3me9f1bz	myz6dmx69dbmfod	Servicequestionoptions	3	t	\N	collaborative	\N	\N	t	1	2026-01-06 20:53:13+01	2026-01-06 20:53:13+01	{}	\N
vwb863vj0bh71lgi	bb4syuyu7fz1t03	pata00z3me9f1bz	m2t8ts768utecu3	Leadanswers	3	t	\N	collaborative	\N	\N	t	1	2026-01-06 20:53:28+01	2026-01-06 20:53:28+01	{}	\N
vwg79nefrwr8d3qt	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m7d1wkpymm3kj7l	MessageTemplate	3	t	\N	collaborative	\N	\N	t	1	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	{}	\N
vwhgdl1fodz1dstx	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mc5itfivoyx2rp5	Lead	3	t	\N	collaborative	\N	\N	t	1	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	{}	\N
vwh0uq249e5i5hbh	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mcyckhd2a05m772	Attempt	3	t	\N	collaborative	\N	\N	t	1	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	{}	\N
vwi6eravj3la901y	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	m4dhntou135vxm1	ResearchSnapshot	3	t	\N	collaborative	\N	\N	t	1	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	{}	\N
vw9rlol15y37u5ok	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mx1ud1d86w1d4y6	Approval	3	t	\N	collaborative	\N	\N	t	1	2026-02-04 12:53:40+01	2026-02-04 12:53:40+01	{}	\N
vw8u9se8bzhmx7z9	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mzvwidn4z544pas	Conversation	3	t	\N	collaborative	\N	\N	t	1	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	{}	\N
vw8zitic4fndcxgh	b5f5jtriymzfd5p	pbydkvvvbvv4pdf	mp45w6rbyjyh6ks	Outcome	3	t	\N	collaborative	\N	\N	t	1	2026-02-04 12:53:41+01	2026-02-04 12:53:41+01	{}	\N
\.


--
-- Data for Name: notification; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public.notification (id, type, body, is_read, is_deleted, fk_user_id, created_at, updated_at) FROM stdin;
ncmq634k7i9lt5f9	app.welcome	{}	f	f	us8g4rajnw6fzr9r	2025-12-30 17:27:36+01	2025-12-30 17:27:36+01
nc04u735wlldk9av	app.welcome	{}	f	f	usf4zleee8lkaehw	2025-12-31 11:30:30+01	2025-12-31 11:30:30+01
ncox47t8gcxx624d	base.invite	{"base":{"id":"pata00z3me9f1bz","title":"Getting Started"},"user":{"id":"us8g4rajnw6fzr9r","email":"team@mailerblend.com","displayName":null}}	f	f	usf4zleee8lkaehw	2026-01-02 00:51:12+01	2026-01-02 00:51:12+01
ncvkkrmowdmb8209	base.invite	{"base":{"id":"pata00z3me9f1bz","title":"Getting Started"},"user":{"id":"us8g4rajnw6fzr9r","email":"team@mailerblend.com","displayName":null}}	f	f	usz8al5yknabajkj	2026-01-05 21:48:43+01	2026-01-05 21:48:43+01
nconu93wxrmck5yy	base.invite	{"base":{"id":"pata00z3me9f1bz","title":"Getting Started"},"user":{"id":"us8g4rajnw6fzr9r","email":"team@mailerblend.com","displayName":null}}	f	f	ushvxy1yf9wrgo8c	2026-01-06 09:26:37+01	2026-01-06 09:26:37+01
ncjwf2jdkj0cq3ew	app.welcome	{}	f	f	us5ceritq5sgzoni	2026-02-03 10:48:26+01	2026-02-03 10:48:26+01
nckor5uazlgmh2zj	base.invite	{"base":{"id":"pbydkvvvbvv4pdf","title":"LinkedIn Stealth Sourcing"},"user":{"id":"us8g4rajnw6fzr9r","email":"team@mailerblend.com","displayName":null}}	f	f	us5ceritq5sgzoni	2026-02-03 10:57:27+01	2026-02-03 10:57:27+01
\.


--
-- Data for Name: xc_knex_migrations; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public.xc_knex_migrations (id, name, batch, migration_time) FROM stdin;
1	project	1	2025-12-29 20:35:10.733+01
2	m2m	1	2025-12-29 20:35:10.736+01
3	fkn	1	2025-12-29 20:35:10.737+01
4	viewType	1	2025-12-29 20:35:10.739+01
5	viewName	1	2025-12-29 20:35:10.74+01
6	nc_006_alter_nc_shared_views	1	2025-12-29 20:35:10.743+01
7	nc_007_alter_nc_shared_views_1	1	2025-12-29 20:35:10.744+01
8	nc_008_add_nc_shared_bases	1	2025-12-29 20:35:10.759+01
9	nc_009_add_model_order	1	2025-12-29 20:35:10.768+01
10	nc_010_add_parent_title_column	1	2025-12-29 20:35:10.769+01
11	nc_011_remove_old_ses_plugin	1	2025-12-29 20:35:10.772+01
12	nc_012_cloud_cleanup	1	2025-12-29 20:35:10.866+01
\.


--
-- Data for Name: xc_knex_migrations_lock; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public.xc_knex_migrations_lock (index, is_locked) FROM stdin;
1	0
\.


--
-- Data for Name: xc_knex_migrationsv2; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public.xc_knex_migrationsv2 (id, name, batch, migration_time) FROM stdin;
1	nc_011	1	2025-12-29 20:35:11.325+01
2	nc_012_alter_column_data_types	1	2025-12-29 20:35:11.333+01
3	nc_013_sync_source	1	2025-12-29 20:35:11.355+01
4	nc_014_alter_column_data_types	1	2025-12-29 20:35:11.37+01
5	nc_015_add_meta_col_in_column_table	1	2025-12-29 20:35:11.371+01
6	nc_016_alter_hooklog_payload_types	1	2025-12-29 20:35:11.387+01
7	nc_017_add_user_token_version_column	1	2025-12-29 20:35:11.388+01
8	nc_018_add_meta_in_view	1	2025-12-29 20:35:11.39+01
9	nc_019_add_meta_in_meta_tables	1	2025-12-29 20:35:11.4+01
10	nc_020_kanban_view	1	2025-12-29 20:35:11.406+01
11	nc_021_add_fields_in_token	1	2025-12-29 20:35:11.414+01
12	nc_022_qr_code_column_type	1	2025-12-29 20:35:11.427+01
13	nc_023_multiple_source	1	2025-12-29 20:35:11.435+01
14	nc_024_barcode_column_type	1	2025-12-29 20:35:11.449+01
15	nc_025_add_row_height	1	2025-12-29 20:35:11.451+01
16	nc_026_map_view	1	2025-12-29 20:35:11.483+01
17	nc_027_add_comparison_sub_op	1	2025-12-29 20:35:11.484+01
18	nc_028_add_enable_scanner_in_form_columns_meta_table	1	2025-12-29 20:35:11.488+01
19	nc_029_webhook	1	2025-12-29 20:35:11.492+01
20	nc_030_add_description_field	1	2025-12-29 20:35:11.496+01
21	nc_031_remove_fk_and_add_idx	1	2025-12-29 20:35:11.899+01
22	nc_033_add_group_by	1	2025-12-29 20:35:11.901+01
23	nc_034_erd_filter_and_notification	1	2025-12-29 20:35:11.935+01
24	nc_035_add_username_to_users	1	2025-12-29 20:35:11.941+01
25	nc_036_base_deleted	1	2025-12-29 20:35:11.945+01
26	nc_037_rename_project_and_base	1	2025-12-29 20:35:12.277+01
27	nc_038_formula_parsed_tree_column	1	2025-12-29 20:35:12.279+01
28	nc_039_sqlite_alter_column_types	1	2025-12-29 20:35:12.28+01
29	nc_040_form_view_alter_column_types	1	2025-12-29 20:35:12.291+01
30	nc_041_calendar_view	1	2025-12-29 20:35:12.31+01
31	nc_042_user_block	1	2025-12-29 20:35:12.312+01
32	nc_043_user_refresh_token	1	2025-12-29 20:35:12.332+01
33	nc_044_view_column_index	1	2025-12-29 20:35:12.361+01
34	nc_045_extensions	1	2025-12-29 20:35:12.372+01
35	nc_046_comment_mentions	1	2025-12-29 20:35:12.429+01
36	nc_047_comment_migration	1	2025-12-29 20:35:12.435+01
37	nc_048_view_links	1	2025-12-29 20:35:12.458+01
38	nc_049_clear_notifications	1	2025-12-29 20:35:12.46+01
39	nc_050_tenant_isolation	1	2025-12-29 20:35:12.729+01
40	nc_051_source_readonly_columns	1	2025-12-29 20:35:12.732+01
41	nc_052_field_aggregation	1	2025-12-29 20:35:12.733+01
42	nc_053_jobs	1	2025-12-29 20:35:12.744+01
43	nc_054_id_length	1	2025-12-29 20:35:13.346+01
44	nc_055_junction_pk	1	2025-12-29 20:35:13.35+01
45	nc_056_integration	1	2025-12-29 20:35:13.385+01
46	nc_057_file_references	1	2025-12-29 20:35:13.403+01
47	nc_058_button_colum	1	2025-12-29 20:35:13.409+01
48	nc_059_invited_by	1	2025-12-29 20:35:13.413+01
\.


--
-- Data for Name: xc_knex_migrationsv2_lock; Type: TABLE DATA; Schema: public; Owner: nocodb
--

COPY public.xc_knex_migrationsv2_lock (index, is_locked) FROM stdin;
1	0
\.


--
-- Name: nc_api_tokens_id_seq; Type: SEQUENCE SET; Schema: public; Owner: nocodb
--

SELECT pg_catalog.setval('public.nc_api_tokens_id_seq', 4, true);


--
-- Name: nc_fl6j___LeadAnswers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: nocodb
--

SELECT pg_catalog.setval('public."nc_fl6j___LeadAnswers_id_seq"', 2, true);


--
-- Name: nc_fl6j___Leads_id_seq; Type: SEQUENCE SET; Schema: public; Owner: nocodb
--

SELECT pg_catalog.setval('public."nc_fl6j___Leads_id_seq"', 37, true);


--
-- Name: nc_fl6j___ServiceQuestionOptions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: nocodb
--

SELECT pg_catalog.setval('public."nc_fl6j___ServiceQuestionOptions_id_seq"', 30, true);


--
-- Name: nc_fl6j___ServiceQuestions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: nocodb
--

SELECT pg_catalog.setval('public."nc_fl6j___ServiceQuestions_id_seq"', 7, true);


--
-- Name: nc_jmsd___Approval_Id_seq; Type: SEQUENCE SET; Schema: public; Owner: nocodb
--

SELECT pg_catalog.setval('public."nc_jmsd___Approval_Id_seq"', 2, true);


--
-- Name: nc_jmsd___Attempt_Id_seq; Type: SEQUENCE SET; Schema: public; Owner: nocodb
--

SELECT pg_catalog.setval('public."nc_jmsd___Attempt_Id_seq"', 1, true);


--
-- Name: nc_jmsd___Company_Id_seq; Type: SEQUENCE SET; Schema: public; Owner: nocodb
--

SELECT pg_catalog.setval('public."nc_jmsd___Company_Id_seq"', 1, true);


--
-- Name: nc_jmsd___Conversation_Id_seq; Type: SEQUENCE SET; Schema: public; Owner: nocodb
--

SELECT pg_catalog.setval('public."nc_jmsd___Conversation_Id_seq"', 1, true);


--
-- Name: nc_jmsd___Lead_Id_seq; Type: SEQUENCE SET; Schema: public; Owner: nocodb
--

SELECT pg_catalog.setval('public."nc_jmsd___Lead_Id_seq"', 1, true);


--
-- Name: nc_jmsd___Message_Template_Id_seq; Type: SEQUENCE SET; Schema: public; Owner: nocodb
--

SELECT pg_catalog.setval('public."nc_jmsd___Message_Template_Id_seq"', 1, true);


--
-- Name: nc_jmsd___Outcome_Id_seq; Type: SEQUENCE SET; Schema: public; Owner: nocodb
--

SELECT pg_catalog.setval('public."nc_jmsd___Outcome_Id_seq"', 1, true);


--
-- Name: nc_jmsd___Pack_Id_seq; Type: SEQUENCE SET; Schema: public; Owner: nocodb
--

SELECT pg_catalog.setval('public."nc_jmsd___Pack_Id_seq"', 4, true);


--
-- Name: nc_jmsd___Research_Snapshot_Id_seq; Type: SEQUENCE SET; Schema: public; Owner: nocodb
--

SELECT pg_catalog.setval('public."nc_jmsd___Research_Snapshot_Id_seq"', 1, true);


--
-- Name: nc_jmsd___Segment_Id_seq; Type: SEQUENCE SET; Schema: public; Owner: nocodb
--

SELECT pg_catalog.setval('public."nc_jmsd___Segment_Id_seq"', 2, true);


--
-- Name: nc_shared_bases_id_seq; Type: SEQUENCE SET; Schema: public; Owner: nocodb
--

SELECT pg_catalog.setval('public.nc_shared_bases_id_seq', 1, false);


--
-- Name: nc_store_id_seq; Type: SEQUENCE SET; Schema: public; Owner: nocodb
--

SELECT pg_catalog.setval('public.nc_store_id_seq', 5, true);


--
-- Name: xc_knex_migrations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: nocodb
--

SELECT pg_catalog.setval('public.xc_knex_migrations_id_seq', 12, true);


--
-- Name: xc_knex_migrations_lock_index_seq; Type: SEQUENCE SET; Schema: public; Owner: nocodb
--

SELECT pg_catalog.setval('public.xc_knex_migrations_lock_index_seq', 1, true);


--
-- Name: xc_knex_migrationsv2_id_seq; Type: SEQUENCE SET; Schema: public; Owner: nocodb
--

SELECT pg_catalog.setval('public.xc_knex_migrationsv2_id_seq', 48, true);


--
-- Name: xc_knex_migrationsv2_lock_index_seq; Type: SEQUENCE SET; Schema: public; Owner: nocodb
--

SELECT pg_catalog.setval('public.xc_knex_migrationsv2_lock_index_seq', 1, true);


--
-- Name: nc_api_tokens nc_api_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.nc_api_tokens
    ADD CONSTRAINT nc_api_tokens_pkey PRIMARY KEY (id);


--
-- Name: nc_audit_v2 nc_audit_v2_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.nc_audit_v2
    ADD CONSTRAINT nc_audit_v2_pkey PRIMARY KEY (id);


--
-- Name: nc_base_users_v2 nc_base_users_v2_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.nc_base_users_v2
    ADD CONSTRAINT nc_base_users_v2_pkey PRIMARY KEY (base_id, fk_user_id);


--
-- Name: nc_sources_v2 nc_bases_v2_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.nc_sources_v2
    ADD CONSTRAINT nc_bases_v2_pkey PRIMARY KEY (id);


--
-- Name: nc_calendar_view_columns_v2 nc_calendar_view_columns_v2_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.nc_calendar_view_columns_v2
    ADD CONSTRAINT nc_calendar_view_columns_v2_pkey PRIMARY KEY (id);


--
-- Name: nc_calendar_view_range_v2 nc_calendar_view_range_v2_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.nc_calendar_view_range_v2
    ADD CONSTRAINT nc_calendar_view_range_v2_pkey PRIMARY KEY (id);


--
-- Name: nc_calendar_view_v2 nc_calendar_view_v2_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.nc_calendar_view_v2
    ADD CONSTRAINT nc_calendar_view_v2_pkey PRIMARY KEY (fk_view_id);


--
-- Name: nc_col_barcode_v2 nc_col_barcode_v2_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.nc_col_barcode_v2
    ADD CONSTRAINT nc_col_barcode_v2_pkey PRIMARY KEY (id);


--
-- Name: nc_col_formula_v2 nc_col_formula_v2_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.nc_col_formula_v2
    ADD CONSTRAINT nc_col_formula_v2_pkey PRIMARY KEY (id);


--
-- Name: nc_col_lookup_v2 nc_col_lookup_v2_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.nc_col_lookup_v2
    ADD CONSTRAINT nc_col_lookup_v2_pkey PRIMARY KEY (id);


--
-- Name: nc_col_qrcode_v2 nc_col_qrcode_v2_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.nc_col_qrcode_v2
    ADD CONSTRAINT nc_col_qrcode_v2_pkey PRIMARY KEY (id);


--
-- Name: nc_col_relations_v2 nc_col_relations_v2_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.nc_col_relations_v2
    ADD CONSTRAINT nc_col_relations_v2_pkey PRIMARY KEY (id);


--
-- Name: nc_col_rollup_v2 nc_col_rollup_v2_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.nc_col_rollup_v2
    ADD CONSTRAINT nc_col_rollup_v2_pkey PRIMARY KEY (id);


--
-- Name: nc_col_select_options_v2 nc_col_select_options_v2_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.nc_col_select_options_v2
    ADD CONSTRAINT nc_col_select_options_v2_pkey PRIMARY KEY (id);


--
-- Name: nc_columns_v2 nc_columns_v2_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.nc_columns_v2
    ADD CONSTRAINT nc_columns_v2_pkey PRIMARY KEY (id);


--
-- Name: nc_comment_reactions nc_comment_reactions_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.nc_comment_reactions
    ADD CONSTRAINT nc_comment_reactions_pkey PRIMARY KEY (id);


--
-- Name: nc_comments nc_comments_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.nc_comments
    ADD CONSTRAINT nc_comments_pkey PRIMARY KEY (id);


--
-- Name: nc_disabled_models_for_role_v2 nc_disabled_models_for_role_v2_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.nc_disabled_models_for_role_v2
    ADD CONSTRAINT nc_disabled_models_for_role_v2_pkey PRIMARY KEY (id);


--
-- Name: nc_extensions nc_extensions_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.nc_extensions
    ADD CONSTRAINT nc_extensions_pkey PRIMARY KEY (id);


--
-- Name: nc_file_references nc_file_references_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.nc_file_references
    ADD CONSTRAINT nc_file_references_pkey PRIMARY KEY (id);


--
-- Name: nc_filter_exp_v2 nc_filter_exp_v2_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.nc_filter_exp_v2
    ADD CONSTRAINT nc_filter_exp_v2_pkey PRIMARY KEY (id);


--
-- Name: nc_fl6j___LeadAnswers nc_fl6j___LeadAnswers_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public."nc_fl6j___LeadAnswers"
    ADD CONSTRAINT "nc_fl6j___LeadAnswers_pkey" PRIMARY KEY (id);


--
-- Name: nc_fl6j___Leads nc_fl6j___Leads_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public."nc_fl6j___Leads"
    ADD CONSTRAINT "nc_fl6j___Leads_pkey" PRIMARY KEY (id);


--
-- Name: nc_fl6j___ServiceQuestionOptions nc_fl6j___ServiceQuestionOptions_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public."nc_fl6j___ServiceQuestionOptions"
    ADD CONSTRAINT "nc_fl6j___ServiceQuestionOptions_pkey" PRIMARY KEY (id);


--
-- Name: nc_fl6j___ServiceQuestions nc_fl6j___ServiceQuestions_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public."nc_fl6j___ServiceQuestions"
    ADD CONSTRAINT "nc_fl6j___ServiceQuestions_pkey" PRIMARY KEY (id);


--
-- Name: nc_form_view_columns_v2 nc_form_view_columns_v2_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.nc_form_view_columns_v2
    ADD CONSTRAINT nc_form_view_columns_v2_pkey PRIMARY KEY (id);


--
-- Name: nc_form_view_v2 nc_form_view_v2_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.nc_form_view_v2
    ADD CONSTRAINT nc_form_view_v2_pkey PRIMARY KEY (fk_view_id);


--
-- Name: nc_gallery_view_columns_v2 nc_gallery_view_columns_v2_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.nc_gallery_view_columns_v2
    ADD CONSTRAINT nc_gallery_view_columns_v2_pkey PRIMARY KEY (id);


--
-- Name: nc_gallery_view_v2 nc_gallery_view_v2_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.nc_gallery_view_v2
    ADD CONSTRAINT nc_gallery_view_v2_pkey PRIMARY KEY (fk_view_id);


--
-- Name: nc_grid_view_columns_v2 nc_grid_view_columns_v2_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.nc_grid_view_columns_v2
    ADD CONSTRAINT nc_grid_view_columns_v2_pkey PRIMARY KEY (id);


--
-- Name: nc_grid_view_v2 nc_grid_view_v2_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.nc_grid_view_v2
    ADD CONSTRAINT nc_grid_view_v2_pkey PRIMARY KEY (fk_view_id);


--
-- Name: nc_hook_logs_v2 nc_hook_logs_v2_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.nc_hook_logs_v2
    ADD CONSTRAINT nc_hook_logs_v2_pkey PRIMARY KEY (id);


--
-- Name: nc_hooks_v2 nc_hooks_v2_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.nc_hooks_v2
    ADD CONSTRAINT nc_hooks_v2_pkey PRIMARY KEY (id);


--
-- Name: nc_integrations_v2 nc_integrations_v2_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.nc_integrations_v2
    ADD CONSTRAINT nc_integrations_v2_pkey PRIMARY KEY (id);


--
-- Name: nc_jmsd___Approval nc_jmsd___Approval_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public."nc_jmsd___Approval"
    ADD CONSTRAINT "nc_jmsd___Approval_pkey" PRIMARY KEY ("Id");


--
-- Name: nc_jmsd___Attempt nc_jmsd___Attempt_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public."nc_jmsd___Attempt"
    ADD CONSTRAINT "nc_jmsd___Attempt_pkey" PRIMARY KEY ("Id");


--
-- Name: nc_jmsd___Company nc_jmsd___Company_domain_key; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public."nc_jmsd___Company"
    ADD CONSTRAINT "nc_jmsd___Company_domain_key" UNIQUE (domain);


--
-- Name: nc_jmsd___Company nc_jmsd___Company_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public."nc_jmsd___Company"
    ADD CONSTRAINT "nc_jmsd___Company_pkey" PRIMARY KEY ("Id");


--
-- Name: nc_jmsd___Conversation nc_jmsd___Conversation_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public."nc_jmsd___Conversation"
    ADD CONSTRAINT "nc_jmsd___Conversation_pkey" PRIMARY KEY ("Id");


--
-- Name: nc_jmsd___Lead nc_jmsd___Lead_linkedin_url_key; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public."nc_jmsd___Lead"
    ADD CONSTRAINT "nc_jmsd___Lead_linkedin_url_key" UNIQUE (linkedin_url);


--
-- Name: nc_jmsd___Lead nc_jmsd___Lead_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public."nc_jmsd___Lead"
    ADD CONSTRAINT "nc_jmsd___Lead_pkey" PRIMARY KEY ("Id");


--
-- Name: nc_jmsd___Message_Template nc_jmsd___Message_Template_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public."nc_jmsd___Message_Template"
    ADD CONSTRAINT "nc_jmsd___Message_Template_pkey" PRIMARY KEY ("Id");


--
-- Name: nc_jmsd___Message_Template nc_jmsd___Message_Template_template_key_key; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public."nc_jmsd___Message_Template"
    ADD CONSTRAINT "nc_jmsd___Message_Template_template_key_key" UNIQUE (template_key);


--
-- Name: nc_jmsd___Outcome nc_jmsd___Outcome_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public."nc_jmsd___Outcome"
    ADD CONSTRAINT "nc_jmsd___Outcome_pkey" PRIMARY KEY ("Id");


--
-- Name: nc_jmsd___Pack nc_jmsd___Pack_pack_key_key; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public."nc_jmsd___Pack"
    ADD CONSTRAINT "nc_jmsd___Pack_pack_key_key" UNIQUE (pack_key);


--
-- Name: nc_jmsd___Pack nc_jmsd___Pack_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public."nc_jmsd___Pack"
    ADD CONSTRAINT "nc_jmsd___Pack_pkey" PRIMARY KEY ("Id");


--
-- Name: nc_jmsd___Research_Snapshot nc_jmsd___Research_Snapshot_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public."nc_jmsd___Research_Snapshot"
    ADD CONSTRAINT "nc_jmsd___Research_Snapshot_pkey" PRIMARY KEY ("Id");


--
-- Name: nc_jmsd___Segment nc_jmsd___Segment_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public."nc_jmsd___Segment"
    ADD CONSTRAINT "nc_jmsd___Segment_pkey" PRIMARY KEY ("Id");


--
-- Name: nc_jmsd___Segment nc_jmsd___Segment_segment_key_key; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public."nc_jmsd___Segment"
    ADD CONSTRAINT "nc_jmsd___Segment_segment_key_key" UNIQUE (segment_key);


--
-- Name: nc_jobs nc_jobs_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.nc_jobs
    ADD CONSTRAINT nc_jobs_pkey PRIMARY KEY (id);


--
-- Name: nc_kanban_view_columns_v2 nc_kanban_view_columns_v2_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.nc_kanban_view_columns_v2
    ADD CONSTRAINT nc_kanban_view_columns_v2_pkey PRIMARY KEY (id);


--
-- Name: nc_kanban_view_v2 nc_kanban_view_v2_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.nc_kanban_view_v2
    ADD CONSTRAINT nc_kanban_view_v2_pkey PRIMARY KEY (fk_view_id);


--
-- Name: nc_map_view_columns_v2 nc_map_view_columns_v2_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.nc_map_view_columns_v2
    ADD CONSTRAINT nc_map_view_columns_v2_pkey PRIMARY KEY (id);


--
-- Name: nc_map_view_v2 nc_map_view_v2_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.nc_map_view_v2
    ADD CONSTRAINT nc_map_view_v2_pkey PRIMARY KEY (fk_view_id);


--
-- Name: nc_models_v2 nc_models_v2_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.nc_models_v2
    ADD CONSTRAINT nc_models_v2_pkey PRIMARY KEY (id);


--
-- Name: nc_orgs_v2 nc_orgs_v2_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.nc_orgs_v2
    ADD CONSTRAINT nc_orgs_v2_pkey PRIMARY KEY (id);


--
-- Name: nc_plugins_v2 nc_plugins_v2_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.nc_plugins_v2
    ADD CONSTRAINT nc_plugins_v2_pkey PRIMARY KEY (id);


--
-- Name: nc_bases_v2 nc_projects_v2_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.nc_bases_v2
    ADD CONSTRAINT nc_projects_v2_pkey PRIMARY KEY (id);


--
-- Name: nc_shared_bases nc_shared_bases_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.nc_shared_bases
    ADD CONSTRAINT nc_shared_bases_pkey PRIMARY KEY (id);


--
-- Name: nc_shared_views_v2 nc_shared_views_v2_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.nc_shared_views_v2
    ADD CONSTRAINT nc_shared_views_v2_pkey PRIMARY KEY (id);


--
-- Name: nc_sort_v2 nc_sort_v2_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.nc_sort_v2
    ADD CONSTRAINT nc_sort_v2_pkey PRIMARY KEY (id);


--
-- Name: nc_store nc_store_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.nc_store
    ADD CONSTRAINT nc_store_pkey PRIMARY KEY (id);


--
-- Name: nc_sync_logs_v2 nc_sync_logs_v2_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.nc_sync_logs_v2
    ADD CONSTRAINT nc_sync_logs_v2_pkey PRIMARY KEY (id);


--
-- Name: nc_sync_source_v2 nc_sync_source_v2_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.nc_sync_source_v2
    ADD CONSTRAINT nc_sync_source_v2_pkey PRIMARY KEY (id);


--
-- Name: nc_teams_v2 nc_teams_v2_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.nc_teams_v2
    ADD CONSTRAINT nc_teams_v2_pkey PRIMARY KEY (id);


--
-- Name: nc_user_comment_notifications_preference nc_user_comment_notifications_preference_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.nc_user_comment_notifications_preference
    ADD CONSTRAINT nc_user_comment_notifications_preference_pkey PRIMARY KEY (id);


--
-- Name: nc_users_v2 nc_users_v2_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.nc_users_v2
    ADD CONSTRAINT nc_users_v2_pkey PRIMARY KEY (id);


--
-- Name: nc_views_v2 nc_views_v2_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.nc_views_v2
    ADD CONSTRAINT nc_views_v2_pkey PRIMARY KEY (id);


--
-- Name: notification notification_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.notification
    ADD CONSTRAINT notification_pkey PRIMARY KEY (id);


--
-- Name: xc_knex_migrations_lock xc_knex_migrations_lock_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.xc_knex_migrations_lock
    ADD CONSTRAINT xc_knex_migrations_lock_pkey PRIMARY KEY (index);


--
-- Name: xc_knex_migrations xc_knex_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.xc_knex_migrations
    ADD CONSTRAINT xc_knex_migrations_pkey PRIMARY KEY (id);


--
-- Name: xc_knex_migrationsv2_lock xc_knex_migrationsv2_lock_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.xc_knex_migrationsv2_lock
    ADD CONSTRAINT xc_knex_migrationsv2_lock_pkey PRIMARY KEY (index);


--
-- Name: xc_knex_migrationsv2 xc_knex_migrationsv2_pkey; Type: CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.xc_knex_migrationsv2
    ADD CONSTRAINT xc_knex_migrationsv2_pkey PRIMARY KEY (id);


--
-- Name: nc_api_tokens_fk_user_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_api_tokens_fk_user_id_index ON public.nc_api_tokens USING btree (fk_user_id);


--
-- Name: nc_audit_v2_base_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_audit_v2_base_id_index ON public.nc_audit_v2 USING btree (base_id);


--
-- Name: nc_audit_v2_fk_model_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_audit_v2_fk_model_id_index ON public.nc_audit_v2 USING btree (fk_model_id);


--
-- Name: nc_audit_v2_row_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_audit_v2_row_id_index ON public.nc_audit_v2 USING btree (row_id);


--
-- Name: nc_base_users_v2_base_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_base_users_v2_base_id_index ON public.nc_base_users_v2 USING btree (base_id);


--
-- Name: nc_base_users_v2_invited_by_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_base_users_v2_invited_by_index ON public.nc_base_users_v2 USING btree (invited_by);


--
-- Name: nc_calendar_view_columns_v2_base_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_calendar_view_columns_v2_base_id_index ON public.nc_calendar_view_columns_v2 USING btree (base_id);


--
-- Name: nc_calendar_view_columns_v2_fk_view_id_fk_column_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_calendar_view_columns_v2_fk_view_id_fk_column_id_index ON public.nc_calendar_view_columns_v2 USING btree (fk_view_id, fk_column_id);


--
-- Name: nc_calendar_view_range_v2_base_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_calendar_view_range_v2_base_id_index ON public.nc_calendar_view_range_v2 USING btree (base_id);


--
-- Name: nc_calendar_view_v2_base_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_calendar_view_v2_base_id_index ON public.nc_calendar_view_v2 USING btree (base_id);


--
-- Name: nc_col_barcode_v2_base_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_col_barcode_v2_base_id_index ON public.nc_col_barcode_v2 USING btree (base_id);


--
-- Name: nc_col_barcode_v2_fk_column_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_col_barcode_v2_fk_column_id_index ON public.nc_col_barcode_v2 USING btree (fk_column_id);


--
-- Name: nc_col_formula_v2_base_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_col_formula_v2_base_id_index ON public.nc_col_formula_v2 USING btree (base_id);


--
-- Name: nc_col_formula_v2_fk_column_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_col_formula_v2_fk_column_id_index ON public.nc_col_formula_v2 USING btree (fk_column_id);


--
-- Name: nc_col_lookup_v2_base_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_col_lookup_v2_base_id_index ON public.nc_col_lookup_v2 USING btree (base_id);


--
-- Name: nc_col_lookup_v2_fk_column_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_col_lookup_v2_fk_column_id_index ON public.nc_col_lookup_v2 USING btree (fk_column_id);


--
-- Name: nc_col_lookup_v2_fk_lookup_column_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_col_lookup_v2_fk_lookup_column_id_index ON public.nc_col_lookup_v2 USING btree (fk_lookup_column_id);


--
-- Name: nc_col_lookup_v2_fk_relation_column_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_col_lookup_v2_fk_relation_column_id_index ON public.nc_col_lookup_v2 USING btree (fk_relation_column_id);


--
-- Name: nc_col_qrcode_v2_base_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_col_qrcode_v2_base_id_index ON public.nc_col_qrcode_v2 USING btree (base_id);


--
-- Name: nc_col_qrcode_v2_fk_column_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_col_qrcode_v2_fk_column_id_index ON public.nc_col_qrcode_v2 USING btree (fk_column_id);


--
-- Name: nc_col_relations_v2_base_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_col_relations_v2_base_id_index ON public.nc_col_relations_v2 USING btree (base_id);


--
-- Name: nc_col_relations_v2_fk_child_column_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_col_relations_v2_fk_child_column_id_index ON public.nc_col_relations_v2 USING btree (fk_child_column_id);


--
-- Name: nc_col_relations_v2_fk_column_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_col_relations_v2_fk_column_id_index ON public.nc_col_relations_v2 USING btree (fk_column_id);


--
-- Name: nc_col_relations_v2_fk_mm_child_column_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_col_relations_v2_fk_mm_child_column_id_index ON public.nc_col_relations_v2 USING btree (fk_mm_child_column_id);


--
-- Name: nc_col_relations_v2_fk_mm_model_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_col_relations_v2_fk_mm_model_id_index ON public.nc_col_relations_v2 USING btree (fk_mm_model_id);


--
-- Name: nc_col_relations_v2_fk_mm_parent_column_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_col_relations_v2_fk_mm_parent_column_id_index ON public.nc_col_relations_v2 USING btree (fk_mm_parent_column_id);


--
-- Name: nc_col_relations_v2_fk_parent_column_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_col_relations_v2_fk_parent_column_id_index ON public.nc_col_relations_v2 USING btree (fk_parent_column_id);


--
-- Name: nc_col_relations_v2_fk_related_model_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_col_relations_v2_fk_related_model_id_index ON public.nc_col_relations_v2 USING btree (fk_related_model_id);


--
-- Name: nc_col_relations_v2_fk_target_view_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_col_relations_v2_fk_target_view_id_index ON public.nc_col_relations_v2 USING btree (fk_target_view_id);


--
-- Name: nc_col_rollup_v2_base_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_col_rollup_v2_base_id_index ON public.nc_col_rollup_v2 USING btree (base_id);


--
-- Name: nc_col_rollup_v2_fk_column_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_col_rollup_v2_fk_column_id_index ON public.nc_col_rollup_v2 USING btree (fk_column_id);


--
-- Name: nc_col_rollup_v2_fk_relation_column_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_col_rollup_v2_fk_relation_column_id_index ON public.nc_col_rollup_v2 USING btree (fk_relation_column_id);


--
-- Name: nc_col_rollup_v2_fk_rollup_column_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_col_rollup_v2_fk_rollup_column_id_index ON public.nc_col_rollup_v2 USING btree (fk_rollup_column_id);


--
-- Name: nc_col_select_options_v2_base_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_col_select_options_v2_base_id_index ON public.nc_col_select_options_v2 USING btree (base_id);


--
-- Name: nc_col_select_options_v2_fk_column_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_col_select_options_v2_fk_column_id_index ON public.nc_col_select_options_v2 USING btree (fk_column_id);


--
-- Name: nc_columns_v2_base_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_columns_v2_base_id_index ON public.nc_columns_v2 USING btree (base_id);


--
-- Name: nc_columns_v2_fk_model_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_columns_v2_fk_model_id_index ON public.nc_columns_v2 USING btree (fk_model_id);


--
-- Name: nc_comment_reactions_base_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_comment_reactions_base_id_index ON public.nc_comment_reactions USING btree (base_id);


--
-- Name: nc_comment_reactions_comment_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_comment_reactions_comment_id_index ON public.nc_comment_reactions USING btree (comment_id);


--
-- Name: nc_comment_reactions_row_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_comment_reactions_row_id_index ON public.nc_comment_reactions USING btree (row_id);


--
-- Name: nc_comments_base_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_comments_base_id_index ON public.nc_comments USING btree (base_id);


--
-- Name: nc_comments_row_id_fk_model_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_comments_row_id_fk_model_id_index ON public.nc_comments USING btree (row_id, fk_model_id);


--
-- Name: nc_disabled_models_for_role_v2_base_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_disabled_models_for_role_v2_base_id_index ON public.nc_disabled_models_for_role_v2 USING btree (base_id);


--
-- Name: nc_disabled_models_for_role_v2_fk_view_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_disabled_models_for_role_v2_fk_view_id_index ON public.nc_disabled_models_for_role_v2 USING btree (fk_view_id);


--
-- Name: nc_extensions_base_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_extensions_base_id_index ON public.nc_extensions USING btree (base_id);


--
-- Name: nc_file_references_temp; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_file_references_temp ON public.nc_file_references USING btree (file_url, storage);


--
-- Name: nc_filter_exp_v2_base_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_filter_exp_v2_base_id_index ON public.nc_filter_exp_v2 USING btree (base_id);


--
-- Name: nc_filter_exp_v2_fk_column_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_filter_exp_v2_fk_column_id_index ON public.nc_filter_exp_v2 USING btree (fk_column_id);


--
-- Name: nc_filter_exp_v2_fk_hook_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_filter_exp_v2_fk_hook_id_index ON public.nc_filter_exp_v2 USING btree (fk_hook_id);


--
-- Name: nc_filter_exp_v2_fk_link_col_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_filter_exp_v2_fk_link_col_id_index ON public.nc_filter_exp_v2 USING btree (fk_link_col_id);


--
-- Name: nc_filter_exp_v2_fk_parent_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_filter_exp_v2_fk_parent_id_index ON public.nc_filter_exp_v2 USING btree (fk_parent_id);


--
-- Name: nc_filter_exp_v2_fk_value_col_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_filter_exp_v2_fk_value_col_id_index ON public.nc_filter_exp_v2 USING btree (fk_value_col_id);


--
-- Name: nc_filter_exp_v2_fk_view_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_filter_exp_v2_fk_view_id_index ON public.nc_filter_exp_v2 USING btree (fk_view_id);


--
-- Name: nc_fl6j___leadanswers_nc_fl6j___leads_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_fl6j___leadanswers_nc_fl6j___leads_id_index ON public."nc_fl6j___LeadAnswers" USING btree ("nc_fl6j___Leads_id");


--
-- Name: nc_fl6j___leadanswers_nc_fl6j___servicequestionoptions_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_fl6j___leadanswers_nc_fl6j___servicequestionoptions_id_index ON public."nc_fl6j___LeadAnswers" USING btree ("nc_fl6j___ServiceQuestionOptions_id");


--
-- Name: nc_fl6j___leadanswers_nc_fl6j___servicequestions_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_fl6j___leadanswers_nc_fl6j___servicequestions_id_index ON public."nc_fl6j___LeadAnswers" USING btree ("nc_fl6j___ServiceQuestions_id");


--
-- Name: nc_fl6j___servicequestionoptions_nc_fl6j___servicequestions_id_; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_fl6j___servicequestionoptions_nc_fl6j___servicequestions_id_ ON public."nc_fl6j___ServiceQuestionOptions" USING btree ("nc_fl6j___ServiceQuestions_id");


--
-- Name: nc_form_view_columns_v2_base_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_form_view_columns_v2_base_id_index ON public.nc_form_view_columns_v2 USING btree (base_id);


--
-- Name: nc_form_view_columns_v2_fk_column_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_form_view_columns_v2_fk_column_id_index ON public.nc_form_view_columns_v2 USING btree (fk_column_id);


--
-- Name: nc_form_view_columns_v2_fk_view_id_fk_column_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_form_view_columns_v2_fk_view_id_fk_column_id_index ON public.nc_form_view_columns_v2 USING btree (fk_view_id, fk_column_id);


--
-- Name: nc_form_view_columns_v2_fk_view_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_form_view_columns_v2_fk_view_id_index ON public.nc_form_view_columns_v2 USING btree (fk_view_id);


--
-- Name: nc_form_view_v2_base_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_form_view_v2_base_id_index ON public.nc_form_view_v2 USING btree (base_id);


--
-- Name: nc_form_view_v2_fk_view_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_form_view_v2_fk_view_id_index ON public.nc_form_view_v2 USING btree (fk_view_id);


--
-- Name: nc_gallery_view_columns_v2_base_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_gallery_view_columns_v2_base_id_index ON public.nc_gallery_view_columns_v2 USING btree (base_id);


--
-- Name: nc_gallery_view_columns_v2_fk_column_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_gallery_view_columns_v2_fk_column_id_index ON public.nc_gallery_view_columns_v2 USING btree (fk_column_id);


--
-- Name: nc_gallery_view_columns_v2_fk_view_id_fk_column_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_gallery_view_columns_v2_fk_view_id_fk_column_id_index ON public.nc_gallery_view_columns_v2 USING btree (fk_view_id, fk_column_id);


--
-- Name: nc_gallery_view_columns_v2_fk_view_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_gallery_view_columns_v2_fk_view_id_index ON public.nc_gallery_view_columns_v2 USING btree (fk_view_id);


--
-- Name: nc_gallery_view_v2_base_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_gallery_view_v2_base_id_index ON public.nc_gallery_view_v2 USING btree (base_id);


--
-- Name: nc_gallery_view_v2_fk_view_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_gallery_view_v2_fk_view_id_index ON public.nc_gallery_view_v2 USING btree (fk_view_id);


--
-- Name: nc_grid_view_columns_v2_base_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_grid_view_columns_v2_base_id_index ON public.nc_grid_view_columns_v2 USING btree (base_id);


--
-- Name: nc_grid_view_columns_v2_fk_column_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_grid_view_columns_v2_fk_column_id_index ON public.nc_grid_view_columns_v2 USING btree (fk_column_id);


--
-- Name: nc_grid_view_columns_v2_fk_view_id_fk_column_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_grid_view_columns_v2_fk_view_id_fk_column_id_index ON public.nc_grid_view_columns_v2 USING btree (fk_view_id, fk_column_id);


--
-- Name: nc_grid_view_columns_v2_fk_view_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_grid_view_columns_v2_fk_view_id_index ON public.nc_grid_view_columns_v2 USING btree (fk_view_id);


--
-- Name: nc_grid_view_v2_base_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_grid_view_v2_base_id_index ON public.nc_grid_view_v2 USING btree (base_id);


--
-- Name: nc_grid_view_v2_fk_view_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_grid_view_v2_fk_view_id_index ON public.nc_grid_view_v2 USING btree (fk_view_id);


--
-- Name: nc_hook_logs_v2_base_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_hook_logs_v2_base_id_index ON public.nc_hook_logs_v2 USING btree (base_id);


--
-- Name: nc_hooks_v2_base_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_hooks_v2_base_id_index ON public.nc_hooks_v2 USING btree (base_id);


--
-- Name: nc_hooks_v2_fk_model_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_hooks_v2_fk_model_id_index ON public.nc_hooks_v2 USING btree (fk_model_id);


--
-- Name: nc_integrations_v2_created_by_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_integrations_v2_created_by_index ON public.nc_integrations_v2 USING btree (created_by);


--
-- Name: nc_integrations_v2_type_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_integrations_v2_type_index ON public.nc_integrations_v2 USING btree (type);


--
-- Name: nc_kanban_view_columns_v2_base_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_kanban_view_columns_v2_base_id_index ON public.nc_kanban_view_columns_v2 USING btree (base_id);


--
-- Name: nc_kanban_view_columns_v2_fk_column_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_kanban_view_columns_v2_fk_column_id_index ON public.nc_kanban_view_columns_v2 USING btree (fk_column_id);


--
-- Name: nc_kanban_view_columns_v2_fk_view_id_fk_column_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_kanban_view_columns_v2_fk_view_id_fk_column_id_index ON public.nc_kanban_view_columns_v2 USING btree (fk_view_id, fk_column_id);


--
-- Name: nc_kanban_view_columns_v2_fk_view_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_kanban_view_columns_v2_fk_view_id_index ON public.nc_kanban_view_columns_v2 USING btree (fk_view_id);


--
-- Name: nc_kanban_view_v2_base_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_kanban_view_v2_base_id_index ON public.nc_kanban_view_v2 USING btree (base_id);


--
-- Name: nc_kanban_view_v2_fk_grp_col_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_kanban_view_v2_fk_grp_col_id_index ON public.nc_kanban_view_v2 USING btree (fk_grp_col_id);


--
-- Name: nc_kanban_view_v2_fk_view_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_kanban_view_v2_fk_view_id_index ON public.nc_kanban_view_v2 USING btree (fk_view_id);


--
-- Name: nc_map_view_columns_v2_base_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_map_view_columns_v2_base_id_index ON public.nc_map_view_columns_v2 USING btree (base_id);


--
-- Name: nc_map_view_columns_v2_fk_column_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_map_view_columns_v2_fk_column_id_index ON public.nc_map_view_columns_v2 USING btree (fk_column_id);


--
-- Name: nc_map_view_columns_v2_fk_view_id_fk_column_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_map_view_columns_v2_fk_view_id_fk_column_id_index ON public.nc_map_view_columns_v2 USING btree (fk_view_id, fk_column_id);


--
-- Name: nc_map_view_columns_v2_fk_view_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_map_view_columns_v2_fk_view_id_index ON public.nc_map_view_columns_v2 USING btree (fk_view_id);


--
-- Name: nc_map_view_v2_base_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_map_view_v2_base_id_index ON public.nc_map_view_v2 USING btree (base_id);


--
-- Name: nc_map_view_v2_fk_geo_data_col_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_map_view_v2_fk_geo_data_col_id_index ON public.nc_map_view_v2 USING btree (fk_geo_data_col_id);


--
-- Name: nc_map_view_v2_fk_view_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_map_view_v2_fk_view_id_index ON public.nc_map_view_v2 USING btree (fk_view_id);


--
-- Name: nc_models_v2_base_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_models_v2_base_id_index ON public.nc_models_v2 USING btree (base_id);


--
-- Name: nc_models_v2_source_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_models_v2_source_id_index ON public.nc_models_v2 USING btree (source_id);


--
-- Name: nc_project_users_v2_fk_user_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_project_users_v2_fk_user_id_index ON public.nc_base_users_v2 USING btree (fk_user_id);


--
-- Name: nc_shared_views_v2_fk_view_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_shared_views_v2_fk_view_id_index ON public.nc_shared_views_v2 USING btree (fk_view_id);


--
-- Name: nc_sort_v2_base_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_sort_v2_base_id_index ON public.nc_sort_v2 USING btree (base_id);


--
-- Name: nc_sort_v2_fk_column_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_sort_v2_fk_column_id_index ON public.nc_sort_v2 USING btree (fk_column_id);


--
-- Name: nc_sort_v2_fk_view_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_sort_v2_fk_view_id_index ON public.nc_sort_v2 USING btree (fk_view_id);


--
-- Name: nc_sources_v2_base_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_sources_v2_base_id_index ON public.nc_sources_v2 USING btree (base_id);


--
-- Name: nc_sources_v2_fk_integration_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_sources_v2_fk_integration_id_index ON public.nc_sources_v2 USING btree (fk_integration_id);


--
-- Name: nc_store_key_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_store_key_index ON public.nc_store USING btree (key);


--
-- Name: nc_sync_logs_v2_base_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_sync_logs_v2_base_id_index ON public.nc_sync_logs_v2 USING btree (base_id);


--
-- Name: nc_sync_source_v2_base_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_sync_source_v2_base_id_index ON public.nc_sync_source_v2 USING btree (base_id);


--
-- Name: nc_sync_source_v2_source_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_sync_source_v2_source_id_index ON public.nc_sync_source_v2 USING btree (source_id);


--
-- Name: nc_user_comment_notifications_preference_base_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_user_comment_notifications_preference_base_id_index ON public.nc_user_comment_notifications_preference USING btree (base_id);


--
-- Name: nc_user_refresh_tokens_expires_at_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_user_refresh_tokens_expires_at_index ON public.nc_user_refresh_tokens USING btree (expires_at);


--
-- Name: nc_user_refresh_tokens_fk_user_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_user_refresh_tokens_fk_user_id_index ON public.nc_user_refresh_tokens USING btree (fk_user_id);


--
-- Name: nc_user_refresh_tokens_token_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_user_refresh_tokens_token_index ON public.nc_user_refresh_tokens USING btree (token);


--
-- Name: nc_views_v2_base_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_views_v2_base_id_index ON public.nc_views_v2 USING btree (base_id);


--
-- Name: nc_views_v2_fk_model_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX nc_views_v2_fk_model_id_index ON public.nc_views_v2 USING btree (fk_model_id);


--
-- Name: notification_created_at_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX notification_created_at_index ON public.notification USING btree (created_at);


--
-- Name: notification_fk_user_id_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX notification_fk_user_id_index ON public.notification USING btree (fk_user_id);


--
-- Name: user_comments_preference_index; Type: INDEX; Schema: public; Owner: nocodb
--

CREATE INDEX user_comments_preference_index ON public.nc_user_comment_notifications_preference USING btree (user_id, row_id, fk_model_id);


--
-- Name: nc_team_users_v2 nc_team_users_v2_org_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.nc_team_users_v2
    ADD CONSTRAINT nc_team_users_v2_org_id_foreign FOREIGN KEY (org_id) REFERENCES public.nc_orgs_v2(id);


--
-- Name: nc_team_users_v2 nc_team_users_v2_user_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.nc_team_users_v2
    ADD CONSTRAINT nc_team_users_v2_user_id_foreign FOREIGN KEY (user_id) REFERENCES public.nc_users_v2(id);


--
-- Name: nc_teams_v2 nc_teams_v2_org_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: nocodb
--

ALTER TABLE ONLY public.nc_teams_v2
    ADD CONSTRAINT nc_teams_v2_org_id_foreign FOREIGN KEY (org_id) REFERENCES public.nc_orgs_v2(id);


--
-- PostgreSQL database dump complete
--

\unrestrict Y8ylmnfLByCW0QNSm7awAmw6bEziZU4HlLwVPvnyIdUi2qGpHDzIfjvDfVI3vHr

