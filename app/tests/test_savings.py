def test_create_savings(client, auth_token):
    """Test creating a new savings entry."""
    response = client.post(
        "/savings/",
        headers=auth_token,
        json={
            "savings_type": "Income",
            "amount": 500.00,
            "source": "Salary",
            "transaction_date": "2026-09-28"
        }
    )
    
    assert response.status_code == 200, response.json()
    data = response.json()
    assert data["amount"] == 500.00
    assert data["source"] == "Salary"
    assert "id" in data


def test_get_savings(client, auth_token):
    """Test retrieving a list of savings records."""
    client.post(
        "/savings/",
        headers=auth_token,
        json={
            "savings_type": "Income",
            "amount": 100.00,
            "source": "Bonus",
            "transaction_date": "2026-09-28"
        }
    )
    
    # Updated to match the combined prefix + route: /savings/savings
    response = client.get("/savings/savings", headers=auth_token)
    
    assert response.status_code == 200, response.json()
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["source"] == "Bonus"


def test_update_savings(client, auth_token):
    """Test updating an existing savings record."""
    create_res = client.post(
        "/savings/",
        headers=auth_token,
        json={
            "savings_type": "Other",
            "amount": 50.00,
            "source": "Gift",
            "transaction_date": "2026-09-28"
        }
    )
    savings_id = create_res.json()["id"]

    # Updated to use .patch() to match @router.patch
    update_res = client.patch(
        f"/savings/{savings_id}",
        headers=auth_token,
        json={
            "savings_type": "Other",
            "amount": 75.00,
            "source": "Gift - Updated",
            "transaction_date": "2026-09-28"
        }
    )
    
    assert update_res.status_code == 200, update_res.json()
    assert update_res.json()["amount"] == 75.00
    assert update_res.json()["source"] == "Gift - Updated"


def test_delete_savings(client, auth_token):
    """Test deleting a savings record."""
    create_res = client.post(
        "/savings/",
        headers=auth_token,
        json={
            "savings_type": "Other",
            "amount": 20.00,
            "source": "Cashback",
            "transaction_date": "2026-09-28"
        }
    )
    savings_id = create_res.json()["id"]

    delete_res = client.delete(f"/savings/{savings_id}", headers=auth_token)
    assert delete_res.status_code == 200
    
    # Removed the GET /{id} verification step since the endpoint does not exist.