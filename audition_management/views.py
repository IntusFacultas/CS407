from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.views import View
from audition_management.models import Role, AuditionAccount, CastingAccount
from audition_management.forms import SettingsForm
from difflib import SequenceMatcher
from nltk.corpus import wordnet
# Create your views here.
from audition_management.forms import RoleCreationForm
from audition_management.forms import EditRoleForm

class DashboardView(LoginRequiredMixin, View):

    def handle_request(self, request):
        if request.GET:
            return DashboardView.get(request)

    def get(self, request):
        roles = Role.objects.all()
        dictionaries = [obj.as_dict() for obj in roles]
        return render(request, 'audition_management/dashboard.html', {
            "roles": dictionaries
        })


class AccountDelete(LoginRequiredMixin, View):
    def post(self, request, pk):
        user = User.objects.get(pk=pk)
        if request.user != user:
            messages.error(request, "You cannot delete this account.")
            return HttpResponseRedirect(
                reverse("audition_management:settings"))
        else:
            user.delete()
            messages.success(request, "Account deleted.")
            return HttpResponseRedirect(reverse("session:login"))


class SettingsView(LoginRequiredMixin, View):

    def handle_request(self, request):
        if request.GET:
            return SettingsView.get(request)
        else:
            return SettingsView.post(request)

    def get_user(self, current_user):
        user = None
        try:
            user = current_user.audition_account
        except AuditionAccount.DoesNotExist:
            try:
                user = current_user.casting_account
            except CastingAccount.DoesNotExist:
                pass
        return user

    def get(self, request):
        user = self.get_user(request.user)
        form = SettingsForm(instance=request.user)
        change_password_form = PasswordChangeForm(request.user)
        return render(request, 'session/settings.html', {
            'form': form,
            "change_password_form": change_password_form,
        })

    def post(self, request):
        user = self.get_user(request.user)
        if request.POST.get("form_type") == 'account_form':
            form = SettingsForm(request.POST)
            if form.is_valid():
                form.save()
                user.profile.set_password(form.password1)
                messages.success(request, "Account updated successfully.")
                return HttpResponseRedirect(
                    reverse("audition_management:settings"))
        else:
            form = PasswordChangeForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Password changed successfully.")
                return HttpResponseRedirect(
                    reverse("audition_management:settings"))


class RoleView(LoginRequiredMixin, View):

    def get(self, request, pk):
        dictionary = object
        dates = object
        try:
            role = Role.objects.get(id=pk)
            dictionary = role.as_dict()
            dates = role.dates.all()
        except Role.DoesNotExist:
            dictionary = None
            dates = None
        return render(request, 'audition_management/role.html', {
            "role": dictionary,
            "dates": dates
        })

class RoleCreationView(LoginRequiredMixin, View):

    def get(self, request):
        form = RoleCreationForm()
        return render(
            request,
            'audition_management/create.html',
            {'form': form}
        )

    def post(self, request):
        form = RoleCreationForm(request.POST)
        print(form.name)
        if form.is_valid():
            role = Role(
                name=form.name,
                description=form.description,
                domain=form.domain.current(),
                studio_address=form.studio_address
            )
            role.save()
            return render(request, 'audition_management/role.html', {
                'role': role.as_dict()
            })
        else:
            return render(
                request,
                'audition_management/create.html',
                {'form': form}
            )
class EditRoleView(LoginRequiredMixin, View):

    def get(self, request, pk):
        form = EditRoleForm()
        dictionary = object
        dates = object
        try:
            role = Role.objects.get(id=pk)
            dictionary = role.as_dict()
            dates = role.dates.all()
        except Role.DoesNotExist:
            dictionary = None
            dates = None
        return render(request, 'audition_management/editRole.html', {
            "role": dictionary,
            "dates": dates,
            'form': form
        })

    def post(self, request):
        form = EditRoleForm(request.POST)
        if form.is_valid():
            role = Role.objects.get(pk="NEED TO FIGURE THIS OUT")
            role.name=form.name,
            role.description=form.description,
            role.domain=form.domain.current(),
            role.studio_address=form.studio_address
            role.save()
            return render(request, 'audition_management/role.html', {
                'role': role.as_dict()
            })
        else:
            return render(
                request,
                'audition_management/EditRole.html',
                {'form': form}
            )

"""
    def similar(a, b):
        return SequenceMatcher(None, a, b).ratio()

    def get_word_synonyms_from_tags(role_tag, user_tags):
        role_tag_synonyms = []
        for synset in role_tagnet.synsets(role_tag.name):
            for lemma in synset.lemma_names():
                for tag in user_tags:
                    if tag.name == lemma:
                        role_tag_synonyms.append(lemma)
        return word_synonyms

    # fuzzy search algorithm
    roles = Role.objects.all()
    account = request.user.audition_account
    tags = account.tags.all()
    matching_roles = []
    for tag in tags:
        for role in roles:
            for role_tag in role.tags.all():
                similarity_index = similar(tag.name, role_tag.name)
                # confidence threshold of 80% chosen arbitrarily
                if similarity > .8:
                    matching_roles.append(role)
                    break
                else:
                    tag_synonyms = get_word_synonyms_from_tags(word, sent)
                    if len(tag_synonyms) > 0:
                        # synonym found.
                        matching_roles.append(role)
                        break
"""
