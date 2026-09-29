from src.models import Listing
from src.scoring import distance_km, fast_score


def test_distance_is_reasonable():
    assert 9.5 <= distance_km(48.8566, 2.3522, 48.9466, 2.3522) <= 10.5


def test_good_deal_scores_higher():
    listing = Listing(title="Produit précis excellent état", url="https://www.leboncoin.fr/ad/x", price_eur=250, description="Facture, très bon état, remise en main propre", latitude=48.90, longitude=2.35, image_urls=["x"])
    search = {"keywords": ["produit précis"], "max_price_eur": 500, "reference_price_eur": 450, "must_have": ["facture"], "avoid": ["HS"]}
    result = fast_score(listing, search, {"latitude": 48.8566, "longitude": 2.3522, "max_distance_km": 50})
    assert result["fast_score"] >= 60
    assert result["risk_score"] < 20
