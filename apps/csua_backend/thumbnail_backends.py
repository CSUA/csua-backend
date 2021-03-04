# from http://blog.yawd.eu/2012/seo-friendly-image-names-sorl-thumbnail-and-django/
import os
import re
from urllib.parse import urlparse

from django.conf import settings
from django.template.defaultfilters import slugify
from sorl.thumbnail.base import ThumbnailBackend


class SEOThumbnailBackend(ThumbnailBackend):
    """
    Custom backend for SEO-friendly thumbnail file names/urls.
    """

    def _get_thumbnail_filename(self, source, geometry_string, options):
        """
        Computes the destination filename.
        """
        try:
            basepath = source.storage.path("")
        except NotImplementedError:
            basepath = source.storage.url("")

        split_path = urlparse(source.name).path.split("/")
        split_path.insert(-1, geometry_string)

        # attempt to slugify the filename to make it SEO-friendly
        split_name = split_path[-1].split(".")
        try:
            split_path[-1] = "%s.%s" % (
                slugify(".".join(split_name[:-1])),
                split_name[-1],
            )
        except:
            # on fail keep the original filename
            pass

        path = os.sep.join(split_path)

        # if the path already starts with THUMBNAIL_PREFIX do not concatenate the PREFIX
        # this way we avoid ending up with a url like /images/images/120x120/my.png
        if not path.startswith(settings.THUMBNAIL_PREFIX):
            return "%s/%s" % (settings.THUMBNAIL_PREFIX, path)

        return path
