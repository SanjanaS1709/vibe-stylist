from supabase_client import supabase
from services.engagement_engine import engagement_engine

class BadgeEngine:
    def check_and_award(self, user_id):
        """
        Checks all achievement conditions and awards new badges.
        """
        badges_to_check = [
            {"name": "Baddie Icon", "type": "style", "condition": lambda uid: self._check_outfit_count(uid, 'baddie', 5)},
            {"name": "Style Explorer", "type": "outfit", "condition": lambda uid: self._check_total_outfits(uid, 10)},
            {"name": "Wardrobe Master", "type": "wardrobe", "condition": lambda uid: self._check_wardrobe_count(uid, 20)},
            {"name": "Trend Lover", "type": "swipe", "condition": lambda uid: self._check_swipe_count(uid, 15)}
        ]
        
        awarded = []
        for badge in badges_to_check:
            if badge['condition'](user_id):
                if self._award_badge(user_id, badge['name'], badge['type']):
                    awarded.append(badge['name'])
        return awarded

    def _check_outfit_count(self, user_id, style_tag, count):
        # Implementation depends on how style_tags are stored (JSONB)
        # For simplicity, we check approved_outfits joined with historical tags
        return False # Placeholder until deeper logic integrated

    def _check_total_outfits(self, user_id, count):
        res = supabase.table('approved_outfits').select('id', count='exact').eq('user_id', user_id).execute()
        return res.count >= count

    def _check_wardrobe_count(self, user_id, count):
        res = supabase.table('virtual_wardrobe').select('id', count='exact').eq('user_id', user_id).execute()
        return res.count >= count

    def _check_swipe_count(self, user_id, count):
        res = supabase.table('swipe_history').select('id', count='exact').eq('user_id', user_id).execute()
        return res.count >= count

    def _award_badge(self, user_id, badge_name, badge_type):
        try:
            # Attempt to insert, UNIQUE constraint will handle duplicates
            supabase.table('user_badges').insert({
                "user_id": user_id,
                "badge_name": badge_name,
                "badge_type": badge_type
            }).execute()
            # Reward engagement score
            engagement_engine.update_score(user_id, 10)
            return True
        except Exception:
            return False # Badge already exists

badge_engine = BadgeEngine()
