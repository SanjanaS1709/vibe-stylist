from supabase_client import supabase

class EngagementEngine:
    def update_score(self, user_id, increment):
        """
        Updates the user's engagement score in the users table.
        """
        try:
            # Get current score
            res = supabase.table('users').select('engagement_score').eq('id', user_id).execute()
            current_score = res.data[0].get('engagement_score', 0) if res.data else 0
            
            new_score = current_score + increment
            
            # Update score
            supabase.table('users').update({"engagement_score": new_score}).eq('id', user_id).execute()
            return new_score
        except Exception as e:
            print(f"Error updating engagement score: {e}")
            return 0

engagement_engine = EngagementEngine()
