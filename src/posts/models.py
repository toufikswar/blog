from django.db import models
from django.conf import settings
from django.db.models.signals import pre_save
from django.core.urlresolvers import reverse
from django.utils.text import slugify
from django.utils import timezone
from markdown_deux import markdown
from django.utils.safestring import mark_safe
from django.contrib.contenttypes.models import ContentType
from .utils import get_read_time

from comments.models import Comment


# e.g : Post.objects.all() is a model Manager
class PostManager(models.Manager):
    def active(self, *args, **kwargs):
        return super(PostManager,
                     self).filter(
                                  draft=False).filter(
                                  publish__lte=timezone.now())


def upload_location(instance, filename):
    return "{}/{}".format(instance.id, filename)


class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, default=1)
    title = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to=upload_location, null=True, blank=True,
                              width_field="width_field",
                              height_field="height_field")
    height_field = models.IntegerField(default=0)
    width_field = models.IntegerField(default=0)
    content = models.TextField()
    draft = models.BooleanField(default=False)
    publish = models.DateField(auto_now=False, auto_now_add=False)
    read_time = models.IntegerField(default=0)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)
    # auto_now : field updated each time we update the entry in the DB
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)
    # auto_now_add : field only updated once (on the creation)
    tags = models.ManyToManyField("Tag")

    objects = PostManager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        # return reverse("posts:detail", kwargs={"id": self.id})
        return reverse("posts:detail", kwargs={"slug": self.slug})

    def get_markdown(self):
        content = self.content
        markdown_text = markdown(content)
        return mark_safe(markdown_text)

    class Meta:
        ordering = ["-timestamp", "-updated"]

    """ we define the property comments within the Post class to get all comments
    associated to a specific Post instance """
    @property
    def comments(self):
        instance = self
        qs = Comment.objects.filter_by_instance(instance)
        return qs

    """ return the ContentType of the current instance (Post) """
    @property
    def get_content_type(self):
        instance = self
        content_type = ContentType.objects.get_for_model(instance.__class__)
        return content_type


class Tag(models.Model):
    tagName = models.CharField(max_length=50, default='General')

    def __str__(self):
        return self.tagName


# function to create the slug
def create_slug(instance, new_slug=None):
    slug = slugify(instance.title)
    if new_slug is not None:
        slug = new_slug
    qs = Post.objects.filter(slug=slug).order_by("-id")
    exists = qs.exists()
    if exists:
        new_slug = "{}-{}".format(slug, qs.first().id)
        return create_slug(instance, new_slug=new_slug)
    return slug


""" Signal function executed before the save() method of the instance
used to create the slug and to calculate read_time before saving the
Post object """


def pre_save_post_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_slug(instance)

    if instance.content:
        print(instance.content)
        html_string = instance.get_markdown()
        read_time_var = get_read_time(html_string)
        instance.read_time = read_time_var


pre_save.connect(pre_save_post_receiver, sender=Post)
