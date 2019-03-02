from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django import template
from sorl.thumbnail.templatetags.thumbnail import ThumbnailNode


register = template.Library()


class StaticThumbnailStorage(FileSystemStorage):
    def __init__(self, *args, **kw):
        super(StaticThumbnailStorage, self).__init__(
            *args, location=settings.STATIC_ROOT, base_url=settings.STATIC_URL, **kw
        )


storage = StaticThumbnailStorage()


class StaticThumbnailNode(ThumbnailNode):
    def _get_thumbnail(self, file_, geometry, **options):
        options["storage"] = storage
        return super(StaticThumbnailNode, self)._get_thumbnail(
            file_, geometry, **options
        )


@register.tag
def static_thumbnail(parser, token):
    return StaticThumbnailNode(parser, token)
