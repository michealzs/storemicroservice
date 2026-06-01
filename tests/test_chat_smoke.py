import pytest


@pytest.mark.asyncio
async def test_chat_ingest_and_recommend(seeded_client):
    ingest = await seeded_client.post("/ingest")
    assert ingest.status_code == 200
    assert ingest.json()["products_indexed"] >= 2

    resp = await seeded_client.post(
        "/chat", json={"message": "noise cancelling headphones for travel"}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "LLM provider not configured" in body["reply"]
    assert "headphones" in body["sources"]
