CREATE TABLE IF NOT EXISTS translation_parameters (
    translation_parameters_id   INTEGER PRIMARY KEY,
    translation_tool_name       TEXT,
    translation_tool_commit     TEXT,
    translation_model           TEXT,
    translation_config_sha256   TEXT,
    translation_config          TEXT,
    UNIQUE(translation_tool_name, translation_tool_commit, translation_model, translation_config_sha256, translation_config)
);



CREATE TABLE IF NOT EXISTS message_translation (
    translation_id              INTEGER PRIMARY KEY,
    translation_parameters_id    INTEGER,
    message_id                  INTEGER,
    translation_text            TEXT,
    translation_timestamp       TIMESTAMPTZ(0),
    FOREIGN KEY (translation_parameters_id) REFERENCES translation_parameters(translation_parameters_id),
    FOREIGN KEY (message_id) REFERENCES messages(message_id)
);
