import re
import time
import uuid

from django.conf import settings
from django.contrib.sessions.backends.base import UpdateError
from django.contrib.sessions.exceptions import SessionInterrupted
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpResponseRedirect
from django.urls import get_script_prefix, set_script_prefix
from django.utils.cache import patch_vary_headers
from django.utils.deprecation import MiddlewareMixin
from django.utils.http import http_date


_WINDOW_PATH = re.compile(r'^/_window/([0-9a-f]{32})(?P<path>/.*)?$')
_NEW_WINDOW_PATH = '/__new-window__/'


class WindowRoutingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.path_info == _NEW_WINDOW_PATH:
            window_id = uuid.uuid4().hex
            return HttpResponseRedirect(f'/_window/{window_id}/login/')

        match = _WINDOW_PATH.fullmatch(request.path_info)
        if not match:
            return None

        window_id = match.group(1)
        script_name = f'/_window/{window_id}'
        path_info = match.group('path') or '/'
        request.window_session_id = window_id
        request.window_session_cookie_name = (
            f'{settings.SESSION_COOKIE_NAME}_window_{window_id}'
        )
        request.window_session_cookie_path = f'{script_name}/'
        request._window_script_prefix = get_script_prefix()
        request.META['SCRIPT_NAME'] = script_name
        request.META['PATH_INFO'] = path_info
        request.path = f'{script_name}{path_info}'
        request.path_info = path_info
        set_script_prefix(f'{script_name}/')
        return None

    def process_response(self, request, response):
        previous_prefix = getattr(request, '_window_script_prefix', None)
        if previous_prefix is not None:
            set_script_prefix(previous_prefix)
        return response


class WindowSessionMiddleware(SessionMiddleware):
    def process_request(self, request):
        cookie_name = getattr(request, 'window_session_cookie_name', None)
        if cookie_name is None:
            return super().process_request(request)
        request._default_session = request.session
        request.session = self.SessionStore(request.COOKIES.get(cookie_name))
        request.COOKIES.pop(settings.SESSION_COOKIE_NAME, None)

    def process_response(self, request, response):
        cookie_name = getattr(request, 'window_session_cookie_name', None)
        if cookie_name is None:
            return super().process_response(request, response)

        try:
            try:
                accessed = request.session.accessed
                modified = request.session.modified
                empty = request.session.is_empty()
            except AttributeError:
                return response

            cookie_path = request.window_session_cookie_path
            if cookie_name in request.COOKIES and empty:
                response.delete_cookie(
                    cookie_name,
                    path=cookie_path,
                    domain=settings.SESSION_COOKIE_DOMAIN,
                    samesite=settings.SESSION_COOKIE_SAMESITE,
                )
                need_vary_cookie = True
            else:
                need_vary_cookie = accessed
                if (modified or settings.SESSION_SAVE_EVERY_REQUEST) and not empty:
                    if request.session.get_expire_at_browser_close():
                        max_age = None
                        expires = None
                    else:
                        max_age = request.session.get_expiry_age()
                        expires = http_date(time.time() + max_age)
                    if response.status_code < 500:
                        try:
                            request.session.save()
                        except UpdateError as error:
                            raise SessionInterrupted(
                                'The request session was deleted before the request completed.'
                            ) from error
                        response.set_cookie(
                            cookie_name,
                            request.session.session_key,
                            max_age=max_age,
                            expires=expires,
                            domain=settings.SESSION_COOKIE_DOMAIN,
                            path=cookie_path,
                            secure=settings.SESSION_COOKIE_SECURE or None,
                            httponly=settings.SESSION_COOKIE_HTTPONLY or None,
                            samesite=settings.SESSION_COOKIE_SAMESITE,
                        )
                        need_vary_cookie = True

            if need_vary_cookie:
                patch_vary_headers(response, ('Cookie',))
            return response
        finally:
            request.session = request._default_session
