# Supabase SQL Schema for Phase 1

Create these tables in your Supabase SQL Editor to support the updated application.

## 1. Enable UUID Extension
Ensure the UUID extension is enabled (usually on by default).

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

## 2. Create Users Table
This table stores basic user information and hashed passwords.

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    skin_tone_result TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

## 3. Create User Preferences Table
This table stores user-specific style preferences linked to their account.

```sql
CREATE TABLE user_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    style_tags JSONB,
    color_preferences JSONB,
    vibe_type TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```
