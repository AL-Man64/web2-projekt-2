from http import HTTPStatus

from django.core.exceptions import BadRequest
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_safe

from w2p2_app import csrf_utils, vulnerability
from w2p2_app.models import BookmarkedAlbum, User


@require_POST
def set_vulnerable(req: HttpRequest) -> HttpResponse:
    if 'value' not in req.POST or req.POST['value'] not in ('true', 'false'):
        raise BadRequest
    vulnerability.set_app_is_vulnerable(req.POST['value'] == 'true')
    return redirect(reverse('index'))


@require_POST
def login(req: HttpRequest) -> HttpResponse:
    if not all(key in req.POST for key in ['username', 'password']):
        raise BadRequest

    username = req.POST['username']
    password = req.POST['password']

    user = User.find_by_username_and_password(username, password)
    if not user:
        return HttpResponse('Incorrect username or password.', status=HTTPStatus.UNAUTHORIZED)

    req.session['user_id'] = user.id
    req.session.cycle_key()

    return redirect(reverse('index'))


@require_POST
def logout(req: HttpRequest) -> HttpResponse:
    req.session.flush()
    return redirect(reverse('index'))


@csrf_exempt
@require_POST
def bookmark_album(req: HttpRequest) -> HttpResponse:
    if 'user_id' not in req.session:
        return HttpResponse('Unauthorized', status=HTTPStatus.UNAUTHORIZED)

    if not vulnerability.app_is_vulnerable() and not csrf_utils.validate_token(
        req, req.POST.get('csrf_token')
    ):
        return HttpResponseForbidden('Invalid CSRF token')
    if not all(key in req.POST for key in ['album_title', 'album_author']):
        raise BadRequest

    album_title = req.POST['album_title']
    album_author = req.POST['album_author']

    BookmarkedAlbum.objects.create(
        user_id=req.session['user_id'], album_title=album_title, album_author=album_author
    )

    return redirect(reverse('index'))


@csrf_exempt
@require_POST
def delete_bookmarked_album(req: HttpRequest, id: int) -> HttpResponse:
    if 'user_id' not in req.session:
        return HttpResponse('Unauthorized', status=HTTPStatus.UNAUTHORIZED)
    if not vulnerability.app_is_vulnerable() and not csrf_utils.validate_token(
        req, req.POST.get('csrf_token')
    ):
        return HttpResponseForbidden('Invalid CSRF token')

    try:
        bookmark = get_object_or_404(BookmarkedAlbum, id=id, user_id=req.session['user_id'])
    except BookmarkedAlbum.DoesNotExist as e:
        raise Http404 from e

    bookmark.delete()

    return redirect(reverse('index'))


@require_safe
def index(req: HttpRequest) -> HttpResponse:
    user_info = None
    bookmarked_albums = []

    if user_id := req.session.get('user_id'):
        user = User.objects.get(id=user_id)
        user_info = {'username': user.username}
        bookmarked_albums = list(BookmarkedAlbum.objects.filter(user_id=user_id))

    csrf_token = csrf_utils.issue_token(req)

    return render(
        req,
        'index.html',
        {
            'vulnerable': vulnerability.app_is_vulnerable(),
            'custom_csrf_token': csrf_token,
            'user': user_info,
            'bookmarked_albums': bookmarked_albums,
        },
    )
