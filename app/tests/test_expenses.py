def test_create_expense(client, auth_token):
    """Test creating a new expense using a valid JWT token."""
    response = client.post(
        "/expense/",
        headers=auth_token,
        json={
            "title": "Groceries",
            "amount": 150.50,
            "transaction_date": "2026-09-28",
            "category": "Food",
            "notes": "Weekly shopping"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Groceries"
    assert data["amount"] == 150.50
    assert "id" in data


def test_get_expenses(client, auth_token):
    """Test retrieving a list of expenses for the authenticated user."""
    # 1. Create a dummy expense first
    client.post(
        "/expense/",
        headers=auth_token,
        json={
            "title": "Internet Bill",
            "amount": 60.00,
            "transaction_date": "2026-09-28",
            "category": "Utilities"
        }
    )
    
    # 2. Fetch the expenses
    response = client.get("/expense/", headers=auth_token)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["title"] == "Internet Bill"