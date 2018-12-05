from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class CommentManager(models.Manager):

    """used in tuto "Advancing the Blog: 16 - Reply to Comments" but not
    sure where needed"""
    """def all(self):
        qs = super(CommentManager, self).filter(parent=None)
        return qs"""
    #  we redefine the filter class

    def filter_by_instance(self, instance):
            """use of contentype to stay generic - here we select the model Post
            __class__ calls the class of the instance in that case Post"""
            content_type = ContentType.objects.get_for_model(
                                                        instance.__class__)
            obj_id = instance.id

            # super() calls the filter of the Mother class of CommentManager
            qs = super(CommentManager, self).filter(content_type=content_type,
                                                    object_id=obj_id).filter(
                                                    parent=None)
            """ => in the end with the content_type it is as doing
            Post.objects.get(id=instance.id) """

            # we add .filter(parent=None) to keep only comments without parents
            return qs


class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, default=1)
    """ ContentType allow comment to be Generic
    Generic Model : comment is not linked to a post and can be implemented
    in any other app """
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    parent = models.ForeignKey("self", null=True, blank=True)

    # needed to link CommentManager to Comment
    objects = CommentManager()

    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return str(self.user.username)

    """ we return list of children of the current parent instance """
    def children(self):  # replies
        return Comment.objects.filter(parent=self)

    def get_absolute_url(self):
        return reverse("comments:thread", kwargs={"id": self.id})

    def get_delete_url(self):
        return reverse("comments:delete", kwargs={"id": self.id})

    @property
    def is_parent(self):
        """ if parent is not None then there is a parent
        so it has a parent then it is a child """
        if self.parent is not None:
            return False
        return True
