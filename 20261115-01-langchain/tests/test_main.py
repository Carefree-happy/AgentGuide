def test_read_root(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json() == {"hello": "world"}


def test_openapi_available(client):
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    assert "/" in resp.json()["paths"]
