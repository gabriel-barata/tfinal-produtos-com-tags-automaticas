from pydantic import BaseModel

from app.models.tag_vocabulary import TagGroup


class TagCountResponse(BaseModel):
    """Uma tag do índice, em quantos produtos aparece e a qual grupo pertence."""

    tag: str
    count: int
    group: TagGroup
