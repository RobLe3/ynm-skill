def test_retry_limit(client):
    assert client.retry_limit == 3
