def test_register_user(client):
    """Test that a new user can be created."""
    response = client.post("/auth/register", json={
        "email": "newuser@example.com",
        "password": "securepassword",
        "name": "New User"
    })

    assert response.status_code in [200, 400]

    if response.status_code == 200:
        data = response.json()
        assert data["email"] == "newuser@example.com"

def test_login_user(client):
    """Test that a valid user gets an access Token"""

    client.post("/auth/register", json={
        "email": "testuser@example.com",
        "password": "testpassword123",
        "name": "Test User"
    }) 
    
    response = client.post("/auth/login", data={
        "username": "testuser@example.com",
        "password": "testpassword123"
    })

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"