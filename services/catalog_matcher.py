from supabase_client import supabase

class CatalogMatcher:
    def find_best_match(self, item_type, description, color=None, style_tag=None):
        """
        Finds the closest item in the outfit_catalog based on AI suggestion.
        Simple matching using filters; can be improved with vector search later.
        """
        try:
            query = supabase.table('outfit_catalog').select('*').eq('item_type', item_type)
            
            # Try to match by style_tag first
            if style_tag:
                tag_query = query.ilike('style_tag', f'%{style_tag}%').execute()
                if tag_query.data:
                    return tag_query.data[0]
            
            # Fallback to color
            if color:
                color_query = query.ilike('color', f'%{color}%').execute()
                if color_query.data:
                    return color_query.data[0]
                    
            # Absolute fallback: just return any item of that type
            final_query = query.limit(1).execute()
            return final_query.data[0] if final_query.data else None
            
        except Exception as e:
            print(f"Error matching catalog item: {e}")
            return None

catalog_matcher = CatalogMatcher()
