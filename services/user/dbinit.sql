CREATE TABLE user(
    user_id text primary key,
    user_name text,
    full_name text,
    email text,
    user_disabled boolean,
    double_hashed_password text
);

CREATE TABLE session(
    session_id text primary key,
    user_id text,
    lastest_refresh_token_exp text,
    device_context text
);
