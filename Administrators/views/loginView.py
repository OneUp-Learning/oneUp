'''
Last updated on Sep 12, 2016

'''
from django.template import RequestContext
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

def loginView(request):
    context_dict = { }
    
    context_dict["logged_in"]=request.user.is_authenticated
    if request.user.is_authenticated:
        user = request.user
        context_dict["username"]=user.username
                
        if user.groups.filter(name='Teachers').exists():
            context_dict["is_teacher"] = True
        elif user.groups.filter(name='Admins').exists():
            context_dict["is_admin"] = True
        else:
            context_dict["is_student"] = True
    return render(request, 'home.html', context_dict)

@csrf_exempt
def login_interconnect(request):
    from django.contrib.auth.views import LoginView
    from django.utils.decorators import method_decorator
    from django.views.decorators.cache import never_cache
    from django.views.decorators.csrf import csrf_exempt
    from django.views.decorators.debug import sensitive_post_parameters
    from django.http import HttpResponseRedirect

    class uncsrfLoginView(LoginView):
        @method_decorator(sensitive_post_parameters())
        @method_decorator(csrf_exempt)
        @method_decorator(never_cache)
        def dispatch(self, request, *args, **kwargs):
            if self.redirect_authenticated_user and self.request.user.is_authenticated:
                redirect_to = self.get_success_url()
                if redirect_to == self.request.path:
                    raise ValueError(
                        'Redirection loop for authenticated user detected. Check that '
                        'your LOGIN_REDIRECT_URL doesn\'t point to a login page.')
                return HttpResponseRedirect(redirect_to)
            return super(LoginView, self).dispatch(request, *args, **kwargs)
    lv = uncsrfLoginView.as_view(template_name='home.html')
    return lv(request)
