import os
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.contenttypes.models import ContentType

from comments.forms import CommentForm
from .models import Post
from comments.models import Comment
from .forms import PostForm


# Create your views here.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def post_list(request):
    today = timezone.now().date()
    queryset_list = Post.objects.active()
    if request.user.is_staff or request.user.is_superuser:
        queryset_list = Post.objects.all()

    query = request.GET.get("q")
    # request.GET is a dictonnary and we get the value of element with index q
    # values of request.GET come from the form q in post_list
    if query:
        queryset_list = queryset_list.filter(
                    Q(title__icontains=query) |
                    Q(content__icontains=query) |
                    Q(user__first_name__icontains=query) |
                    Q(user__last_name__icontains=query)
                    ).distinct()
    paginator = Paginator(queryset_list, 5)  # Show 5 contacts per page
    page_request_var = "page"
    page = request.GET.get(page_request_var)
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        queryset = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        queryset = paginator.page(paginator.num_pages)

    context = {
        "title": "MeinTitle",
        "objects_list": queryset,
        "page_request_var": page_request_var,
        "today": today,
    }
    return render(request, "post_list.html", context)


def post_create(request):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    # if not request.user.is_authenticated:
    #    raise Http404
    form = PostForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        # messages.success(request, "Successfully created")
        print("test 1")
        messages.add_message(request, messages.SUCCESS, "Successfully created")

        return HttpResponseRedirect(instance.get_absolute_url())
    context = {
        "form": form,
    }
    return render(request, "post_form.html", context)


# def post_detail(request, id):
def post_detail(request, slug):
    instance = get_object_or_404(Post, slug=slug)
    if instance.publish > timezone.now().date() or instance.draft:
        if not request.user.is_staff or not request.user.is_superuser:
            raise Http404

    """ we define the initial_data to be set in the form """
    initial_data = {
                    "content_type": instance.get_content_type,
                    "object_id": instance.id
    }

    """ request.POST handles the case HttpPost contains values meaning the
    form is filled | None refers to the case where the form is empty """
    form = CommentForm(request.POST or None, initial=initial_data)
    if form.is_valid() and request.user.is_authenticated():
        # we get the content type name
        c_type = form.cleaned_data.get("content_type")

        # we get the  ContentType object based on the content type name (c_type)
        content_type = ContentType.objects.get(model=c_type)
        obj_id = form.cleaned_data.get("object_id")
        content_data = form.cleaned_data.get("content")

        # we define the parent object
        parent_obj = None
        # we get the value of the parent ID from the POST from the detail_view
        try:
            parent_id = int(request.POST.get("parent_id"))
        except:
            parent_id = None
        # if parent_id has a value
        if parent_id:
            # we get a queryset with the comment with this parent_id
            parent_qs = Comment.objects.filter(id=parent_id)
            # we make sure it exists and contains only one record
            if parent_qs.exists() and parent_qs.count() == 1:
                parent_obj = parent_qs.first()  # we select the parent

        #  create the new comment, return true if comment created
        new_comment, created = Comment.objects.get_or_create(
                                user=request.user,
                                content_type=content_type,
                                object_id=obj_id,
                                parent=parent_obj,
                                content=content_data)

        """ this is equivalent to new_comment.Posts.get_absolute_url and
        it redirects to the Post via the absolute URL """
        return HttpResponseRedirect(new_comment.content_object.get_absolute_url())

    """ comments is a proprety of class Post - it gets all comments associated
    to the Post instance """
    comments = instance.comments

    """ context is the dictonnary we send to the template. it contains
    all the values  """
    context = {
        "title": "MeinDetail",
        "instance": instance,
        "comments": comments,
        "comment_form": form,
    }
    return render(request, "post_detail.html", context)


# we look for the object based on the slug (slug is unique identifier)
def post_update(request, slug=None):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    instance = get_object_or_404(Post, slug=slug)
    form = PostForm(request.POST or None, request.FILES or None,
                    instance=instance)
    if form.is_valid():
        instance = form.save(commit=False or None)
        instance.save()
        messages.success(request, "Item Saved")
        return HttpResponseRedirect(instance.get_absolute_url())
    context = {
        "form": form,
        "title": instance.title,
        "instance": instance
    }
    return render(request, "post_form.html", context)


# def post_delete(request, id=None):
# instance = get_object_or_404(Post, id=id)
def post_delete(request, slug=None):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    instance = get_object_or_404(Post, slug=slug)
    instance.delete()
    messages.add_message(request, messages.SUCCESS, "Successfully deleted")
    return redirect("posts:list")
