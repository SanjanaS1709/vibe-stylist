-- Create the Saved Looks table
CREATE TABLE saved_looks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    outfit_data JSONB NOT NULL,
    vibe TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for performance
CREATE INDEX idx_saved_looks_user_id ON saved_looks(user_id);
