from sources.routing import classify_claim, route_claim, score_evidence, fuse_scores

def test_claim_routes_by_domain():
    assert classify_claim("What causes malaria?") == "MEDICAL"
    assert "who" in route_claim("What causes malaria?")
    assert "world_bank" in route_claim("What is India's GDP?")

def test_evidence_score_is_transparent_and_bounded():
    score = score_evidence("government", 1.0, .8, .9)
    assert score.reliability == .95
    assert 0 <= score.score <= 1

def test_fusion_rewards_independent_sources_without_duplicate_inflation():
    one = score_evidence("wikipedia", 1, 1, .8)
    two = score_evidence("government", 1, 1, .9)
    assert fuse_scores([one, two]) > one.score
    assert fuse_scores([one, one]) == fuse_scores([one])
