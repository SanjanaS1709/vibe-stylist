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
    style_archetype TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

## 4. Create Outfit Catalog Table
CREATE TABLE outfit_catalog (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    item_type TEXT CHECK (item_type IN ('top', 'pant', 'shoes', 'accessory')),
    name TEXT NOT NULL,
    image_url TEXT NOT NULL,
    style_tag TEXT,
    color TEXT,
    gender TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

## 5. Create Swipe History Table
CREATE TABLE swipe_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    item_type TEXT,
    item_name TEXT,
    style_tag TEXT,
    color TEXT,
    swipe_type TEXT CHECK (swipe_type IN ('like', 'reject')),
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

## 6. Create Approved Outfits Table
CREATE TABLE approved_outfits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    top_id UUID REFERENCES outfit_catalog(id),
    pant_id UUID REFERENCES outfit_catalog(id),
    shoes_id UUID REFERENCES outfit_catalog(id),
    accessory_id UUID REFERENCES outfit_catalog(id),
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

## 7. Create Virtual Wardrobe Table
CREATE TABLE virtual_wardrobe (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    item_type TEXT CHECK (item_type IN ('top', 'pant', 'shoes', 'accessory')),
    image_url TEXT NOT NULL,
    dominant_color TEXT,
    style_tag TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

## 8. Update Swipe History for Source Tracking
ALTER TABLE swipe_history ADD COLUMN source_type TEXT DEFAULT 'catalog';
-- source_type can be 'catalog', 'wardrobe', or 'ecommerce'

## 9. Create User Badges Table
CREATE TABLE user_badges (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    badge_name TEXT NOT NULL,
    badge_type TEXT,
    earned_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, badge_name)
);

## 10. Create User Activity Table
CREATE TABLE user_activity (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    activity_date DATE DEFAULT CURRENT_DATE,
    UNIQUE(user_id, activity_date)
);

## 11. Update Users Table for Engagement
ALTER TABLE users ADD COLUMN engagement_score INTEGER DEFAULT 0;

## 12. Update Approved Outfits for Scoring
ALTER TABLE approved_outfits ADD COLUMN approval_score INTEGER DEFAULT 0;
ALTER TABLE approved_outfits ADD COLUMN swipe_count INTEGER DEFAULT 0;
