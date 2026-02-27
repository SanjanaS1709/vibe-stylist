-- NUCLEAR FIX: Reset all check constraints on virtual_wardrobe
-- This ensures that 'dress' and all other categories work perfectly.

BEGIN;

-- 1. Drop the specific constraint if it exists
ALTER TABLE virtual_wardrobe 
DROP CONSTRAINT IF EXISTS virtual_wardrobe_item_type_check;

-- 2. Drop any other potential item_type check constraints that might have been created
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

-- 3. Add the complete, updated constraint
ALTER TABLE virtual_wardrobe 
ADD CONSTRAINT virtual_wardrobe_item_type_check 
CHECK (item_type IN ('top', 'pant', 'shoes', 'accessory', 'shirt', 'suit', 'kurta', 'kurti', 'saree', 'dress'));

-- 4. Do the same for outfit_catalog just to be safe
ALTER TABLE outfit_catalog 
DROP CONSTRAINT IF EXISTS outfit_catalog_item_type_check;

ALTER TABLE outfit_catalog 
ADD CONSTRAINT outfit_catalog_item_type_check 
CHECK (item_type IN ('top', 'pant', 'shoes', 'accessory', 'shirt', 'suit', 'kurta', 'kurti', 'saree', 'dress'));

COMMIT;
