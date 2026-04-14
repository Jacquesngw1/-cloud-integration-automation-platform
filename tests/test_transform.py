"""Tests for the data-transformation layer."""
import pytest

from app.transform import transform_posts


def test_transform_posts_basic():
    raw = [
        {"id": 1, "userId": 10, "title": "hello world", "body": "some body text here"}
    ]
    result = transform_posts(raw)
    assert len(result) == 1
    post = result[0]
    assert post["external_id"] == 1
    assert post["user_id"] == 10
    assert post["title"] == "Hello World"
    assert post["body"] == "some body text here"
    assert post["word_count"] == 4


def test_transform_posts_word_count():
    raw = [{"id": 2, "userId": 1, "title": "t", "body": "one two three four five"}]
    result = transform_posts(raw)
    assert result[0]["word_count"] == 5


def test_transform_posts_strips_whitespace():
    raw = [{"id": 3, "userId": 1, "title": "  padded  ", "body": "  body  "}]
    result = transform_posts(raw)
    assert result[0]["title"] == "Padded"
    assert result[0]["body"] == "body"


def test_transform_posts_empty_body():
    raw = [{"id": 4, "userId": 1, "title": "t", "body": ""}]
    result = transform_posts(raw)
    assert result[0]["word_count"] == 0


def test_transform_posts_multiple():
    raw = [
        {"id": i, "userId": 1, "title": f"title {i}", "body": "x y z"}
        for i in range(1, 6)
    ]
    result = transform_posts(raw)
    assert len(result) == 5
    for i, post in enumerate(result, start=1):
        assert post["external_id"] == i
        assert post["word_count"] == 3
