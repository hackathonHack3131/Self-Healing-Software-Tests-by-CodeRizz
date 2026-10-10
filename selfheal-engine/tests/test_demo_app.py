"""Unit tests for the Flask demo shop application."""

import re
from html.parser import HTMLParser
import pytest
from demo_app.app import create_app


@pytest.fixture
def client():
    """Create a Flask test client."""
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


def test_health_check(client):
    """Verify /health returns HTTP 200 with ok status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data is not None
    assert data.get("status") == "ok"


def test_index_page(client):
    """Verify index page lists versions and returns 200."""
    response = client.get("/")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "/v/a/" in html
    assert "/v/b/" in html
    assert "/v/c/" in html
    assert "/v/d/" in html


def test_every_page_of_every_version_returns_200(client):
    """Verify GET on every standard page of all 4 versions returns 200."""
    pages_to_test = [
        # Version A
        "/v/a/",
        "/v/a/confirmation",
        # Version B
        "/v/b/",
        "/v/b/shipping",
        "/v/b/payment",
        "/v/b/review",
        "/v/b/confirmation",
        # Version C (pre-failure pages)
        "/v/c/",
        "/v/c/shipping",
        "/v/c/payment",
        "/v/c/review",
        # Version D
        "/v/d/",
        "/v/d/shipping",
        "/v/d/payment",
        "/v/d/review",
        "/v/d/confirmation",
    ]

    for page in pages_to_test:
        response = client.get(page)
        assert response.status_code == 200, f"Page {page} returned status {response.status_code}"


def test_version_a_and_b_confirmations(client):
    """Verify A and B confirmations contain 'Order confirmed', order id QA-[0-9]+ and total 36.50."""
    for path in ("/v/a/confirmation", "/v/b/confirmation"):
        response = client.get(path)
        assert response.status_code == 200
        html = response.get_data(as_text=True)

        assert "Order confirmed" in html, f"Missing 'Order confirmed' in {path}"
        assert re.search(r"QA-[0-9]+", html), f"Missing order id matching QA-[0-9]+ in {path}"
        assert "36.50" in html, f"Missing total 36.50 in {path}"


def test_version_c_place_returns_500_with_alert(client):
    """Verify POST /v/c/place returns HTTP 500 with role=alert text and no 'Order confirmed'."""
    response = client.post("/v/c/place")
    assert response.status_code == 500
    html = response.get_data(as_text=True)

    assert 'role="alert"' in html
    assert "Payment service unavailable. Please try again later." in html
    assert "Order confirmed" not in html


def test_version_d_confirmation_has_wrong_total(client):
    """Verify Version D confirmation displays wrong total (not 36.50)."""
    response = client.get("/v/d/confirmation")
    assert response.status_code == 200
    html = response.get_data(as_text=True)

    assert "Order confirmed" in html
    assert re.search(r"QA-[0-9]+", html)
    assert "36.50" not in html
    assert "32.50" in html


class LabelInputParser(HTMLParser):
    """Parser to collect input IDs and label 'for' attributes."""

    def __init__(self):
        super().__init__()
        self.inputs = []
        self.labels = set()

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        if tag == "input":
            input_type = attr_dict.get("type", "text")
            if input_type not in ("hidden", "submit", "button"):
                input_id = attr_dict.get("id")
                if input_id:
                    self.inputs.append(input_id)
        elif tag == "label":
            label_for = attr_dict.get("for")
            if label_for:
                self.labels.add(label_for)


def test_every_input_has_associated_label(client):
    """Verify every text/email input across all form pages has a corresponding label."""
    form_pages = [
        "/v/a/",
        "/v/b/shipping",
        "/v/b/payment",
        "/v/c/shipping",
        "/v/c/payment",
        "/v/d/shipping",
        "/v/d/payment",
    ]

    for path in form_pages:
        response = client.get(path)
        assert response.status_code == 200
        html = response.get_data(as_text=True)

        parser = LabelInputParser()
        parser.feed(html)

        assert len(parser.inputs) > 0, f"No inputs found on {path}"
        for input_id in parser.inputs:
            assert input_id in parser.labels, f"Input '{input_id}' on {path} has no associated label"


def test_multi_step_flow_session_persistence(client):
    """Verify multi-step form data persists across session steps in Version B."""
    # Step 1: Cart -> Shipping
    client.get("/v/b/")

    # Step 2: Shipping POST
    shipping_data = {
        "full_name": "Alice Tester",
        "email_address": "alice@example.com",
        "street_address": "456 Automation Way",
    }
    resp_ship = client.post("/v/b/shipping", data=shipping_data, follow_redirects=True)
    assert resp_ship.status_code == 200
    assert "Payment Method" in resp_ship.get_data(as_text=True)

    # Step 3: Payment POST
    payment_data = {
        "card_number": "4111222233334444",
        "expiry": "11/29",
        "cvc": "789",
    }
    resp_pay = client.post("/v/b/payment", data=payment_data, follow_redirects=True)
    assert resp_pay.status_code == 200
    review_html = resp_pay.get_data(as_text=True)
    assert "Review &amp; Confirm" in review_html or "Review & Confirm" in review_html
    assert "Alice Tester" in review_html
    assert "4444" in review_html

    # Step 4: Place order POST
    resp_place = client.post("/v/b/place", follow_redirects=True)
    assert resp_place.status_code == 200
    confirm_html = resp_place.get_data(as_text=True)
    assert "Order confirmed" in confirm_html
    assert "36.50" in confirm_html
