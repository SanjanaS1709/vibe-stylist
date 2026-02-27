-- FIX: Update item_type constraint for virtual_wardrobe and outfit_catalog
-- This will ensure 'dress', 'shirt', 'kurta', etc. are all allowed.

BEGIN;

-- 1. Fix virtual_wardrobe
ALTER TABLE virtual_wardrobe 
DROP CONSTRAINT IF EXISTS virtual_wardrobe_item_type_check;

ALTER TABLE virtual_wardrobe 
ADD CONSTRAINT virtual_wardrobe_item_type_check 
CHECK (item_type IN ('top', 'pant', 'shoes', 'accessory', 'shirt', 'suit', 'kurta', 'kurti', 'saree', 'dress'));

-- 2. Fix outfit_catalog (just in case)
ALTER TABLE outfit_catalog 
DROP CONSTRAINT IF EXISTS outfit_catalog_item_type_check;

ALTER TABLE outfit_catalog 
ADD CONSTRAINT outfit_catalog_item_type_check 
CHECK (item_type IN ('top', 'pant', 'shoes', 'accessory', 'shirt', 'suit', 'kurta', 'kurti', 'saree', 'dress'));

COMMIT;
