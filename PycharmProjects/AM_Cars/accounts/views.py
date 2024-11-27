from random import randint

from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import auth, messages
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic import CreateView
from django.core.mail import EmailMessage

from AM_Cars.settings import DEFAULT_FROM_EMAIL
from accounts.forms import UserForm
from contacts.models import Contact


class UserCreateView(CreateView):
    template_name = 'accounts/register.html'
    model = User
    form_class = UserForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        if form.is_valid():
            new_user = form.save(commit=False)

            new_user.first_name = new_user.first_name.title()

            new_user.last_name = new_user.last_name.title()

            new_user.username = f'{new_user.first_name[0].lower()}{new_user.last_name.lower().replace(" ", "")}_{randint(100000, 999999)}'

            new_user.is_active = False

            new_user.save()

            token = default_token_generator.make_token(new_user)
            uid = urlsafe_base64_encode(force_bytes(new_user.id))
            activation_url = self.request.build_absolute_uri(
                reverse_lazy('activate', kwargs={'uid64': uid, 'token': token})
            )
            subject = 'Activate your account!'

            details_user = {
                'fullname': f'{new_user.first_name} {new_user.last_name}',
                'username': new_user.username,
                'activation_url': activation_url
            }

            message = get_template('email.html').render(details_user)
            mail = EmailMessage(subject, message, DEFAULT_FROM_EMAIL, [new_user.email])
            mail.content_subtype = 'html'
            mail.send()

        return redirect('login')


def activate(request, uid64, token):
    try:
        uid = urlsafe_base64_decode(uid64).decode()
        user = get_object_or_404(User, pk=uid)

    except User.DoesNotExist:
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('login')
    else:
        return HttpResponse('NU EXISTA')


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, 'You are now logged in.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('login')
    return render(request, 'accounts/login.html')


@login_required(login_url='login')
def dashboard(request):
    user_inquiry = Contact.objects.order_by('-create_date').filter(user_id=request.user.id)
    # count = Contact.objects.order_by('-create_date').filter(user_id=request.user.id).count()

    data = {
        'inquiries': user_inquiry,
    }
    return render(request, 'accounts/dashboard.html', data)


def logout(request):
    if request.method == 'POST':
        auth.logout(request)
        return redirect('home')
    return redirect('home')
