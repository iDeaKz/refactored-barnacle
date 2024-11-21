# tests/test_api.py

import pytest
from fastapi.testclient import TestClient
from app.api.__init__ import app
from unittest.mock import patch

client = TestClient(app)


@patch('app.utils.monetization.verify_api_key')
def test_create_payment_session_success(mock_verify):
    mock_verify.return_value = True
    with patch('app.utils.monetization.PaymentProvider.create_payment_session') as mock_create_session:
        mock_create_session.return_value = "https://stripe.com/pay/session123"
        response = client.post("/api/create-payment-session", json={"amount": 50.0}, headers={"api_key": "valid_key"})
        assert response.status_code == 200
        assert "payment_url" in response.json()
        assert response.json()["payment_url"] == "https://stripe.com/pay/session123"


@patch('app.utils.monetization.verify_api_key')
def test_create_payment_session_invalid_key(mock_verify):
    mock_verify.return_value = False
    response = client.post("/api/create-payment-session", json={"amount": 50.0}, headers={"api_key": "invalid_key"})
    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid API Key"


@patch('app.utils.monetization.PaymentProvider.handle_stripe_webhook')
def test_stripe_webhook_success(mock_handle_webhook):
    mock_handle_webhook.return_value = {"type": "checkout.session.completed", "data": {"object": {"customer": "cust_123"}}}
    response = client.post("/api/stripe-webhook", data=b"{}", headers={"stripe-signature": "valid_signature"})
    assert response.status_code == 200
    assert response.json()["status"] == "success"


@patch('app.utils.monetization.PaymentProvider.handle_stripe_webhook')
def test_stripe_webhook_invalid_signature(mock_handle_webhook):
    mock_handle_webhook.return_value = None
    response = client.post("/api/stripe-webhook", data=b"{}", headers={"stripe-signature": "invalid_signature"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid webhook"
