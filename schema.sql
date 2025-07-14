-- Supabase chat_history table schema
-- Run this in your Supabase SQL Editor

-- Drop table if it exists (be careful with this in production!)
-- DROP TABLE IF EXISTS chat_history;

-- Create the chat_history table with correct structure
CREATE TABLE IF NOT EXISTS chat_history (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for faster queries by user_id
CREATE INDEX IF NOT EXISTS idx_chat_history_user_id ON chat_history(user_id);

-- Create index for faster queries by created_at (for ordering)
CREATE INDEX IF NOT EXISTS idx_chat_history_created_at ON chat_history(created_at);

-- Enable Row Level Security (RLS)
ALTER TABLE chat_history ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all operations (you can make this more restrictive later)
CREATE POLICY "Allow all operations on chat_history" ON chat_history
    FOR ALL USING (true);

-- Insert some test data (optional)
-- INSERT INTO chat_history (user_id, role, content) VALUES 
-- ('test_user_1', 'user', 'Hello, my name is Hamza'),
-- ('test_user_1', 'assistant', 'Nice to meet you, Hamza! I will remember your name.'),
-- ('test_user_1', 'user', 'I am from Pakistan'),
-- ('test_user_1', 'assistant', 'Great! I will remember you are from Pakistan.');

-- Verify the table structure
SELECT 
    column_name, 
    data_type, 
    is_nullable, 
    column_default
FROM information_schema.columns 
WHERE table_name = 'chat_history' 
ORDER BY ordinal_position; 