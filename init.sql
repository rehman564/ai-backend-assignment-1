CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    done BOOLEAN DEFAULT FALSE
);

-- Seed/Initial data testing ke liye
INSERT INTO tasks (title, done) VALUES 
('Setup FastAPI project with Postgres', true),
('Learn Docker Compose', false)
ON CONFLICT DO NOTHING;