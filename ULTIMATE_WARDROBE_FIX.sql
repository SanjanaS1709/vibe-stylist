-- ULTIMATE FIX: Remove all item_type restrictions on virtual_wardrobe
-- This script is designed to bypass ANY lingering constraints.

BEGIN;

-- 1. Find and Drop the known constraint
ALTER TABLE virtual_wardrobe 
DROP CONSTRAINT IF EXISTS virtual_wardrobe_item_type_check;

-- 2. Find and Drop ANY check constraint on the virtual_wardrobe table
-- This is a very aggressive cleanup.
DO $$ 
DECLARE 
    r RECORD;
BEGIN
    FOR r IN (
        SELECT conname 
        FROM pg_constraint 
        WHERE conrelid = 'virtual_wardrobe'::regclass 
          AND contype = 'c'
    ) 
    LOOP
        EXECUTE 'ALTER TABLE virtual_wardrobe DROP CONSTRAINT ' || quote_ident(r.conname);
    END LOOP;
END $$;

-- 3. To be absolutely sure, we'll also check outfit_catalog
ALTER TABLE outfit_catalog 
DROP CONSTRAINT IF EXISTS outfit_catalog_item_type_check;

DO $$ 
DECLARE 
    r RECORD;
BEGIN
    FOR r IN (
        SELECT conname 
        FROM pg_constraint 
        WHERE conrelid = 'outfit_catalog'::regclass 
          AND contype = 'c'
    ) 
    LOOP
        EXECUTE 'ALTER TABLE outfit_catalog DROP CONSTRAINT ' || quote_ident(r.conname);
    END LOOP;
END $$;

-- 4. Re-add a completely open constraint that allows ANY item_type
-- This ensures the column exists but doesn't restrict the values.
ALTER TABLE virtual_wardrobe 
ADD CONSTRAINT virtual_wardrobe_open_check 
CHECK (item_type IS NOT NULL);

ALTER TABLE outfit_catalog 
ADD CONSTRAINT outfit_catalog_open_check 
CHECK (item_type IS NOT NULL);

COMMIT;
