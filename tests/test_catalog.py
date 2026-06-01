import pytest


@pytest.mark.asyncio
async def test_create_list_and_detail(seeded_client):
    listing = await seeded_client.get("/products")
    assert listing.status_code == 200
    slugs = [p["slug"] for p in listing.json()]
    assert "headphones" in slugs and "water-bottle" in slugs

    detail = await seeded_client.get("/products/headphones")
    assert detail.status_code == 200
    assert detail.json()["name"] == "Wireless Headphones"

    missing = await seeded_client.get("/products/nope")
    assert missing.status_code == 404


@pytest.mark.asyncio
async def test_featured_and_search(seeded_client):
    featured = await seeded_client.get("/featured-products")
    assert [p["slug"] for p in featured.json()] == ["headphones"]

    search = await seeded_client.get("/search", params={"q": "bottle"})
    assert [p["slug"] for p in search.json()] == ["water-bottle"]


@pytest.mark.asyncio
async def test_cart_and_checkout(seeded_client):
    add = await seeded_client.post(
        "/cart/add/headphones", json={"session": "abc", "quantity": 2}
    )
    assert add.status_code == 200
    body = add.json()
    assert body["total"] == pytest.approx(149.0 * 2)

    checkout = await seeded_client.post("/checkout/abc")
    assert checkout.status_code == 200
    assert checkout.json()["payment_status"] == "unpaid"  # no Stripe key


@pytest.mark.asyncio
async def test_review_creation(seeded_client):
    resp = await seeded_client.post(
        "/reviews/headphones", json={"author": "sam", "rating": 5, "content": "great"}
    )
    assert resp.status_code == 201
    assert resp.json()["rating"] == 5
