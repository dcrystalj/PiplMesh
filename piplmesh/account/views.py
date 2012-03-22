import urllib

from django import http
from django.conf import settings
from django.contrib import auth
from django.core import urlresolvers
from django.views import generic as generic_views
from django.views.generic import simple, edit as edit_views

from piplmesh.account import forms

class RegistrationView(edit_views.FormView):
    """
    This view checks if form data are valid, saves new user.
    New user is authenticated, logged in and redirected to home page.
    """

    template_name = 'registration.html'
    form_class = forms.RegistrationForm

    # Have to do this because we don't have reverse_lazy() yet
    def get_success_url(self):
        return urlresolvers.reverse('home')

    def form_valid(self, form):
        username, password = form.save()
        new_user = auth.authenticate(username=username, password=password)
        auth.login(self.request, new_user)
        return super(RegistrationView, self).form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return simple.redirect_to(request, url=self.get_success_url(), permanent=False)
        return super(RegistrationView, self).dispatch(request, *args, **kwargs)

class FacebookLoginView(generic_views.RedirectView):
    """ 
    This view authenticates the user via Facebook. 
    """

    permanent = False
    url = 'https://www.facebook.com/dialog/oauth'

    def get_redirect_url(self, **kwargs):
        args = {
            'client_id': settings.FACEBOOK_APP_ID,
            'scope': settings.FACEBOOK_SCOPE,
            'redirect_uri': self.request.build_absolute_uri(urlresolvers.reverse('facebook_callback')),
        }
        if self.url:
            url = self.url % kwargs
            return "%s?%s" % (url, urllib.urlencode(args))
        else:
            return None
        
class FacebookLogoutView(generic_views.RedirectView):
    """ 
    Log user out of Facebook and redirect to FACEBOOK_LOGOUT_REDIRECT. 
    """

    permanent = False
    url = settings.FACEBOOK_LOGOUT_REDIRECT
    
    def get(self, request, *args, **kwargs):
        auth.logout(request)
        return super(FacebookLogoutView, self).get(request, *args, **kwargs)

class FacebookCallbackView(generic_views.RedirectView):
    """ 
    Authentication callback. Redirects user to LOGIN_REDIRECT_URL. 
    """

    permanent = False
    url = settings.FACEBOOK_LOGIN_REDIRECT
  
    def get(self, request, *args, **kwargs):
        try:
            token = request.GET['code']
        except KeyError:
            # If the user clicks cancel, they will be redirected back without logging in
            return super(FacebookCallbackView, self).get(request, *args, **kwargs)
        else:
            user = auth.authenticate(token=token, request=request)
            auth.login(request, user)
            return super(FacebookCallbackView, self).get(request, *args, **kwargs)