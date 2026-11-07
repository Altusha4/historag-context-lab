CREATE TABLE IF NOT EXISTS weather (
 location TEXT NOT NULL, time TEXT NOT NULL, temperature REAL NOT NULL,
 humidity REAL NOT NULL, fetched_at TEXT NOT NULL, source TEXT NOT NULL,
 PRIMARY KEY(location,time)
);
CREATE TABLE IF NOT EXISTS collection_runs (
 id INTEGER PRIMARY KEY, fetched_at TEXT NOT NULL, received INTEGER NOT NULL,
 inserted INTEGER NOT NULL, source TEXT NOT NULL
);
