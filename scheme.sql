CREATE TABLE Messages
(
    user_id INTEGER,
    chat_id INTEGER,
    message_id INTEGER,
    time_stamp INTEGER,

    is_deleted INTEGER DEFAULT 0,

    json TEXT,
    PRIMARY KEY(chat_id, user_id, message_id, time_stamp)

);