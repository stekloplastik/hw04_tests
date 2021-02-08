from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

from .models import Post, Group
from .forms import PostForm

User = get_user_model()


def index(request):
    post_list = Post.objects.all()
    # Показывать по 10 записей на странице.
    paginator = Paginator(post_list, 10)

    # Из URL извлекаем номер запрошенной страницы - это значение параметра page
    page_number = request.GET.get('page')

    # Получаем набор записей для страницы с запрошенным номером
    page = paginator.get_page(page_number)
    return render(
         request,
         'index.html',
         {'page': page, }
     )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    author = Group.objects.get(slug=slug)
    post_list = author.posts.all().order_by("-pub_date")
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    context = {
        "group": group,
        "page": page
    }
    return render(request, "group.html", context)


@login_required
def new_post(request):
    form = PostForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('index')
    return render(request, 'new.html', {'form': form})


def profile(request, username):
    user = User.objects.get(username=username)
    posts = user.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    context = {
        "page": page,
        "user": user
    }
    return render(request, 'profile.html', context)


def post_view(request, username, post_id):
    user = User.objects.get(username=username)
    number_post = Post.objects.get(id=post_id)
    context = {
        "user": user,
        "number_post": number_post
    }

    return render(request, 'post.html', context)


@login_required
def post_edit(request, username, post_id):
    author = User.objects.get(username=username)
    login_user = request.user
    if login_user != author:
        return redirect('post_view', username=author, post_id=post_id)
    post = get_object_or_404(Post, id=post_id, author=author)
    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        post = form.save()
        return redirect(
            'post_view',
            username=request.user.username,
            post_id=post_id
            )
    return render(request, 'new_post.html', {
        'form': form,
        'post': post
        })
