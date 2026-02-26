from supabase_client import supabase
from datetime import date, timedelta
from services.engagement_engine import engagement_engine

class StreakEngine:
    def record_activity(self, user_id):
        """
        Records daily login and checks for a 7-day streak.
        """
        today = date.today().isoformat()
        try:
            # Check if already recorded today
            res = supabase.table('user_activity').select('*').eq('user_id', user_id).eq('activity_date', today).execute()
            if not res.data:
                # Insert today's activity
                supabase.table('user_activity').insert({"user_id": user_id, "activity_date": today}).execute()
                # Award login points
                engagement_engine.update_score(user_id, 2)
                
                # Check streak
                return self.check_streak(user_id)
            return False
        except Exception as e:
            print(f"Error recording activity: {e}")
            return False

    def check_streak(self, user_id):
        """
        Checks if the user has logged in for 7 consecutive days.
        """
        try:
            # Get last 7 unique activity dates
            res = supabase.table('user_activity').select('activity_date').eq('user_id', user_id).order('activity_date', desc=True).limit(7).execute()
            dates = [d['activity_date'] for d in res.data]
            
            if len(dates) < 7:
                return False
            
            # Verify consecutiveness
            for i in range(1, 7):
                current = date.fromisoformat(dates[i-1])
                prev = date.fromisoformat(dates[i])
                if (current - prev).days != 1:
                    return False
            return True # 7-day streak confirmed
        except Exception as e:
            print(f"Error checking streak: {e}")
            return False

streak_engine = StreakEngine()
