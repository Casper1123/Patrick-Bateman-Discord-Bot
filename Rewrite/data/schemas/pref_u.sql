-- User preferences
-- Stores:
-- PK: UID in table FEATNAME for supported features in ./../interfaces/pref.py (except sayings as they're low rate)
-- Keeping seperate just in case.

CREATE TABLE IF NOT EXISTS Text (
    UserID INTEGER NOT NULL PRIMARY KEY
) WITHOUT ROWID;

CREATE TABLE IF NOT EXISTS Letter (
    UserID INTEGER NOT NULL PRIMARY KEY
) WITHOUT ROWID;

CREATE TABLE IF NOT EXISTS Number (
    UserID INTEGER NOT NULL PRIMARY KEY
) WITHOUT ROWID;
