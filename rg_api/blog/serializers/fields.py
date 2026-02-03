"""
Common serializer fields for Post model.
"""

# Common fields for Post serializers
POST_BASE_FIELDS = (
    "id",
    "url",
    "author",
    "title",
    "created_at",
    'image',
    'categories',
    'summary'
)
