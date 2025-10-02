CREATE TABLE BusinessConnection
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_business_connection_id TEXT,
    telegram_user_chat_id INTEGER,
    telegram_user_id INTEGER,
    telegram_date_created INTEGER,
    telegram_date_deleted INTEGER,
    is_enabled INTEGER DEFAULT 1

);


CREATE TABLE Messages
(
    business_conn_id INTEGER,
    telegram_chat_id INTEGER,
    telegram_message_id INTEGER,
    telegram_message_version INTEGER,

    telegram_date INTEGER,

    is_deleted INTEGER DEFAULT 0,
    json TEXT,

    FOREIGN KEY (business_conn_id)  REFERENCES BusinessConnection (id),

    PRIMARY KEY(telegram_chat_id, telegram_message_id, business_conn_id, telegram_message_version)

);



