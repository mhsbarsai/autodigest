"""Tests for Bluesky AT Protocol thread dispatcher."""
from unittest.mock import MagicMock, patch
from src.distribution.bluesky_poster import create_bluesky_session, dispatch_bluesky_thread


def test_create_bluesky_session_missing_credentials():
    assert create_bluesky_session("", "") is None
    assert create_bluesky_session("user", "") is None


@patch("src.distribution.bluesky_poster.requests.post")
def test_create_bluesky_session_success(mock_post):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "accessJwt": "fake_jwt_token",
        "did": "did:plc:12345678",
        "handle": "creavora.bsky.social",
    }
    mock_post.return_value = mock_resp

    session = create_bluesky_session("creavora.bsky.social", "secret_app_pw")
    assert session is not None
    assert session["accessJwt"] == "fake_jwt_token"
    assert session["did"] == "did:plc:12345678"


@patch("src.distribution.bluesky_poster.create_bluesky_session")
@patch("src.distribution.bluesky_poster.requests.post")
def test_dispatch_bluesky_thread_success(mock_post, mock_session):
    mock_session.return_value = {
        "accessJwt": "fake_jwt_token",
        "did": "did:plc:12345678",
        "handle": "creavora.bsky.social",
    }

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.side_effect = [
        {"uri": "at://did:plc:12345678/app.bsky.feed.post/1", "cid": "cid_1"},
        {"uri": "at://did:plc:12345678/app.bsky.feed.post/2", "cid": "cid_2"},
    ]
    mock_post.return_value = mock_resp

    posts = ["First tweet hook", "Second tweet technical analysis"]
    results = dispatch_bluesky_thread("creavora.bsky.social", "secret_pw", posts)

    assert len(results) == 2
    assert results[0]["uri"] == "at://did:plc:12345678/app.bsky.feed.post/1"
    assert results[1]["uri"] == "at://did:plc:12345678/app.bsky.feed.post/2"
