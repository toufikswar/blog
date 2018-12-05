from django.shortcuts import render, get_object_or_404
from .models import Comment
from .forms import CommentForm
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, Http404
# Create your views here.


# login URL defined in Settings in LOGIN_URL
@login_required
def comment_delete(request, id):
    # obj = get_object_or_404(Comment, id=id)
    try:
        obj = Comment.objects.get(id=id)
    except:
        raise Http404

    if obj.user != request.user:
        response = HttpResponse("You cannot see that...")
        response.status_code = 403
        return response

    """ if POST request means tat the delete button has been clicked on the view
    we delete the post and return to the absolute URL of the Post """
    if request.method == "POST":
        parent_obj_url = obj.content_object.get_absolute_url()
        obj.delete()
        messages.add_message(request, messages.SUCCESS, "Successfully deleted")
        return HttpResponseRedirect(parent_obj_url)
    context = {
                "object": obj,
    }
    """ if does not come from the Post then we render the confirm_delete view
     """
    return render(request, "confirm_delete.html", context)


def comment_thread(request, id):
    # obj = get_object_or_404(Comment, id=id)
    try:
        obj = Comment.objects.get(id=id)
    except:
        raise Http404

    # we make sure we only display the parent comment
    if not obj.is_parent:
        obj = obj.parent

    initial_data = {
                "content_type": obj.content_type,
                "object_id": obj.object_id
    }
    form = CommentForm(request.POST or None, initial=initial_data)
    print(form.errors)

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
        it redirects to the parent_obj meaning the parent comment page"""
        return HttpResponseRedirect(parent_obj.get_absolute_url())

    context = {
                "comment": obj,
                "form": form,
                "id": id,
    }
    return render(request, "comment_thread.html", context)
