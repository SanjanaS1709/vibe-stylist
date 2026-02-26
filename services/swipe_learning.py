from supabase_client import supabase

class SwipeLearningService:
    def get_user_preferences(self, user_id):
        """
        Analyzes swipe history to find liked/rejected tags and colors.
        Returns a dictionary for prompt enrichment.
        """
        try:
            response = supabase.table('swipe_history').select('*').eq('user_id', user_id).execute()
            history = response.data
            
            likes = [h for h in history if h['swipe_type'] == 'like']
            rejections = [h for h in history if h['swipe_type'] == 'reject']
            
            pref = {
                "liked_tags": list(set([l['style_tag'] for l in likes if l.get('style_tag')])),
                "rejected_tags": list(set([r['style_tag'] for r in rejections if r.get('style_tag')])),
                "liked_colors": list(set([l['color'] for l in likes if l.get('color')])),
                "rejected_colors": list(set([r['color'] for r in rejections if r.get('color')]))
            }
            return pref
        except Exception as e:
            print(f"Error analyzing swipe history: {e}")
            return {"liked_tags": [], "rejected_tags": [], "liked_colors": [], "rejected_colors": []}

swipe_learning_service = SwipeLearningService()
