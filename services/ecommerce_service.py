class EcommerceService:
    def generate_product_suggestion(self, item_type, description, color, style_tag):
        """
        Generates descriptive search links for fashion items.
        """
        # Clean the description for search
        query = f"{description}" if description else f"{color} {style_tag} {item_type}"
        search_term = query.replace(" ", "%20")
        
        return {
            "product_name": description or f"{color} {style_tag} {item_type}",
            "reason": f"Matches your chosen theme and color palette.",
            "amazon_link": f"https://www.amazon.in/s?k={search_term}",
            "myntra_link": f"https://www.myntra.com/{search_term.replace('%20', '-')}",
            "flipkart_link": f"https://www.flipkart.com/search?q={search_term}"
        }

ecommerce_service = EcommerceService()
