from supabase_client import supabase
from datetime import datetime, timedelta

class AnalyticsEngine:
    def get_user_stats(self, user_id):
        """
        Aggregates data for the user dashboard.
        """
        stats = {}
        
        # 1. Totals
        stats['total_outfits'] = supabase.table('approved_outfits').select('id', count='exact').eq('user_id', user_id).execute().count
        stats['total_swipes'] = supabase.table('swipe_history').select('id', count='exact').eq('user_id', user_id).execute().count
        stats['total_wardrobe'] = supabase.table('virtual_wardrobe').select('id', count='exact').eq('user_id', user_id).execute().count
        
        # 2. Favorite Color (Most Liked)
        swipes = supabase.table('swipe_history').select('color').eq('user_id', user_id).eq('swipe_type', 'like').execute().data
        if swipes:
            colors = [s['color'] for s in swipes if s.get('color')]
            stats['fav_color'] = max(set(colors), key=colors.count) if colors else "N/A"
        else:
            stats['fav_color'] = "N/A"
            
        # 3. Earned Badges
        badges = supabase.table('user_badges').select('badge_name').eq('user_id', user_id).execute().data
        stats['badges'] = [b['badge_name'] for b in badges]
        
        # 4. Best Outfit Logic
        stats['weekly_best'] = self.get_best_outfit(user_id, days=7)
        stats['best_ever'] = self.get_best_outfit(user_id, days=None)
        
        return stats

    def get_best_outfit(self, user_id, days=None):
        query = supabase.table('approved_outfits').select('*, top:outfit_catalog!top_id(*), pant:outfit_catalog!pant_id(*), shoes:outfit_catalog!shoes_id(*), accessory:outfit_catalog!accessory_id(*)').eq('user_id', user_id)
        
        if days:
            cutoff = (datetime.now() - timedelta(days=days)).isoformat()
            query = query.gte('timestamp', cutoff)
            
        res = query.order('swipe_count', desc=True).limit(1).execute()
        return res.data[0] if res.data else None

analytics_engine = AnalyticsEngine()
