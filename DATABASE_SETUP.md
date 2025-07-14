# Database Setup Guide

## Supabase Table Setup

Your project uses a `chat_history` table in Supabase to store all conversations. Here's how to set it up:

### 1. Create the Table

Go to your **Supabase Dashboard** → **SQL Editor** and run the SQL from `schema.sql`:

```sql
CREATE TABLE IF NOT EXISTS chat_history (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 2. Table Structure

| Column | Type | Description |
|--------|------|-------------|
| `id` | BIGSERIAL | Auto-incrementing primary key |
| `user_id` | TEXT | Unique identifier for each user |
| `role` | TEXT | Either 'user' or 'assistant' |
| `content` | TEXT | The actual message content |
| `created_at` | TIMESTAMP | When the message was created |

### 3. Enable Row Level Security (RLS)

```sql
ALTER TABLE chat_history ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow all operations on chat_history" ON chat_history
    FOR ALL USING (true);
```

### 4. Create Indexes (Optional but Recommended)

```sql
CREATE INDEX IF NOT EXISTS idx_chat_history_user_id ON chat_history(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_history_created_at ON chat_history(created_at);
```

### 5. Test the Setup

Run the test script to verify everything works:

```bash
cd backend
python test_supabase_fixed.py
```

### 6. How It Works

- **User sends message** → Saved as `role: "user"` in database
- **Agent responds** → Saved as `role: "assistant"` in database  
- **Agent recalls** → Reads full conversation history from database
- **No keywords** → Everything stored and recalled naturally

### 7. Environment Variables

Make sure your `.env` file has:

```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
```

### 8. Verify Setup

Check your table in Supabase Dashboard → Table Editor → chat_history

You should see columns: `id`, `user_id`, `role`, `content`, `created_at` 