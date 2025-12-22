CREATE TABLE lists (
    id SERIAL PRIMARY KEY,
    title text NOT NULL UNIQUE 
);


CREATE TABLE todos (
    id SERIAL PRIMARY KEY,
    title text NOT NULL,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    list_id integer NOT NULL
                    REFERENCES lists (id)
                    ON DELETE CASCADE
);