def transform_posts(raw_data: list) -> list:
    """Transform raw post records from the external API.

    Normalises field names, trims whitespace, title-cases the title, and
    appends a word-count metric derived from the post body.

    Args:
        raw_data: List of raw post dicts as returned by the external API.

    Returns:
        List of transformed post dicts ready for storage or response.
    """
    transformed = []
    for post in raw_data:
        body = post.get("body", "").strip()
        transformed.append(
            {
                "external_id": post["id"],
                "user_id": post["userId"],
                "title": post.get("title", "").strip().title(),
                "body": body,
                "word_count": len(body.split()) if body else 0,
            }
        )
    return transformed
