# -*- coding: utf-8 -*-
from webtest import AppError
from django_webtest import WebTest
from django.contrib.auth.models import User


class GetRequestTest(WebTest):
    def test_get_request(self):
        response = self.app.get('/')
        self.assertEqual(response.status_int, 200)
        self.assertTrue('GET' in response)

class PostRequestTest(WebTest):
    csrf_checks = False

    def test_post_request(self):
        response = self.app.post('/')
        self.assertEqual(response.status_int, 200)
        self.assertTrue('POST' in response)

    def test_404_response(self):
        self.assertRaises(AppError, self.app.get, '/404/')


class CsrfProtectionTest(WebTest):
    def test_csrf_failed(self):
        response = self.app.post('/', expect_errors=True)
        self.assertEqual(response.status_int, 403)


class TemplateContextTest(WebTest):
    def test_rendered_templates(self):
        response = self.app.get('/template/index.html')
        self.assertTrue(hasattr(response, 'context'))
        self.assertTrue(hasattr(response, 'template'))

        self.assertEqual(response.template.name, 'index.html')
        self.assertEqual(response.context['bar'], True)
        self.assertEqual(response.context['spam'], None)
        self.assertRaises(KeyError, response.context.__getitem__, 'invalid')

    def test_multiple_templates(self):
        response = self.app.get('/template/complex.html')
        self.assertEqual(len(response.template), 4)
        self.assertEqual(response.template[0].name, 'complex.html')
        self.assertEqual(response.template[1].name, 'include.html')
        self.assertEqual(response.template[2].name, 'include.html')
        self.assertEqual(response.template[3].name, 'include.html')

        self.assertEqual(response.context['foo'], ('a', 'b', 'c'))
        self.assertEqual(response.context['bar'], True)
        self.assertEqual(response.context['spam'], None)


class AuthTest(WebTest):
    def setUp(self):
        self.user = User.objects.create_user('foo', 'example@example.com', '123')

    def test_not_logged_in(self):
        response = self.app.get('/template/index.html')
        user = response.context['user']
        assert not user.is_authenticated()

    def test_logged_using_username(self):
        response = self.app.get('/template/index.html', user='foo')
        user = response.context['user']
        assert user.is_authenticated()
        self.assertEqual(user, self.user)

    def test_logged_using_instance(self):
        response = self.app.get('/template/index.html', user=self.user)
        user = response.context['user']
        assert user.is_authenticated()
        self.assertEqual(user, self.user)

    def test_auth_is_enabled(self):
        from django.conf import settings
        assert 'django.contrib.auth.middleware.RemoteUserMiddleware' in settings.MIDDLEWARE_CLASSES
        assert 'django.contrib.auth.backends.RemoteUserBackend' in settings.AUTHENTICATION_BACKENDS


class DisableAuthSetupTest(WebTest):
    setup_auth = False

    def test_no_auth(self):
        from django.conf import settings
        assert 'django.contrib.auth.middleware.RemoteUserMiddleware' not in settings.MIDDLEWARE_CLASSES
        assert 'django.contrib.auth.backends.RemoteUserBackend' not in settings.AUTHENTICATION_BACKENDS
