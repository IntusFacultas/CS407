from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.views import View
from audition_management.models import Role, AuditionAccount, CastingAccount, Tag
from audition_management.forms import SettingsForm
from difflib import SequenceMatcher
from nltk.corpus import wordnet
import json
# Create your views here.
from audition_management.forms import (
    RoleCreationForm, EventForm, EventFormSet, EditRoleForm, TagFormSet, SkillsFormSet, PortfolioFormSet)


def is_casting_agent(current_user):
    user = None
    try:
        user = current_user.audition_account
        return False
    except AuditionAccount.DoesNotExist:
        try:
            user = current_user.casting_account
            return True
        except CastingAccount.DoesNotExist:
            pass
    return False


class DashboardView(LoginRequiredMixin, View):

    def handle_request(self, request):
        if request.GET:
            return DashboardView.get(request)

    def get(self, request):
        roles = Role.objects.all()
        dictionaries = [obj.as_dict() for obj in roles]
        return render(request, 'audition_management/dashboard.html', {
            "roles": dictionaries,
            "is_casting": is_casting_agent(request.user)
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

    def get_account_type(self, current_user):
        user = None
        try:
            user = current_user.audition_account
            return "Auditioner"
        except AuditionAccount.DoesNotExist:
            try:
                user = current_user.casting_account
                return "Casting Agent"
            except CastingAccount.DoesNotExist:
                pass
        return "None"

    def get(self, request):
        user = self.get_user(request.user)
        account_type = self.get_account_type(request.user)
        events = None
        if is_casting_agent(request.user):
            events = user.roles.all()
            events = [obj.as_dict() for obj in events]
        else:
            skillsformset = SkillsFormSet(prefix="form1")
            portfolioformset = PortfolioFormSet(prefix="form1")
        form = SettingsForm(instance=request.user)
        change_password_form = PasswordChangeForm(request.user)
        if is_casting_agent(request.user):
            return render(request, 'session/settings.html', {
                'form': form,
                "change_password_form": change_password_form,
                "account_type": account_type,
                "is_casting": is_casting_agent(request.user),
                "roles": events
            })
        else:
            return render(request, 'session/settings.html', {
                'form': form,
                "change_password_form": change_password_form,
                "account_type": account_type,
                "is_casting": is_casting_agent(request.user),
                "skill_form_set": skillsformset,
                "portfolio_form_set": portfolioformset
            })

    def post(self, request):
        if request.POST.get("form_type") == 'account_form':
            form = SettingsForm(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, "Account updated successfully.")
                return HttpResponseRedirect(
                    reverse("audition_management:settings"))
            else:
                account_type = self.get_account_type(request.user)
                change_password_form = PasswordChangeForm(request.user)
                return render(request, 'session/settings.html', {
                    'form': form,
                    "change_password_form": change_password_form,
                    "account_type": account_type,
                    "is_casting": is_casting_agent(request.user)
                })
        elif request.POST.get("form_type") == 'skill_form_set':
            form = SkillsFormSet(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, "Account updated successfully.")
                return HttpResponseRedirect(
                    reverse("audition_management:settings"))
            else:
                account_type = self.get_account_type(request.user)
                account_form = SettingsForm(instance=request.user)
                change_password_form = PasswordChangeForm(request.user)
                skillsformset = SkillsFormSet(prefix="form1")
                portfolioformset = PortfolioFormSet(prefix="form1")
                return render(request, 'session/settings.html', {
                    'form': account_form,
                    "change_password_form": change_password_form,
                    "account_type": account_type,
                    "is_casting": is_casting_agent(request.user),
                    "skill_form_set": form,
                    "portfolio_form_set": portfolioformset
                })
        elif request.POST.get("form_type") == 'portfolio_form_set':
            form = SkillsFormSet(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, "Account updated successfully.")
                return HttpResponseRedirect(
                    reverse("audition_management:settings"))
            else:
                account_type = self.get_account_type(request.user)
                account_form = SettingsForm(instance=request.user)
                change_password_form = PasswordChangeForm(request.user)
                skillsformset = SkillsFormSet(prefix="form1")
                return render(request, 'session/settings.html', {
                    'form': account_form,
                    "change_password_form": change_password_form,
                    "account_type": account_type,
                    "is_casting": is_casting_agent(request.user),
                    "skill_form_set": skillsformset,
                    "portfolio_form_set": form
                })
        else:
            form = PasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Password changed successfully.")
                return HttpResponseRedirect(
                    reverse("audition_management:settings"))
            else:
                account_type = self.get_account_type(request.user)
                account_form = SettingsForm(instance=request.user)
                return render(request, 'session/settings.html', {
                    'form': account_form,
                    "change_password_form": form,
                    "account_type": account_type,
                    "is_casting": is_casting_agent(request.user)
                })


class RoleView(LoginRequiredMixin, View):

    def get(self, request, pk):
        role = Role.objects.get(id=pk)
        return render(request, 'audition_management/role.html', {
            "role": role,
            "is_casting": is_casting_agent(request.user)
        })


class RoleCreationView(LoginRequiredMixin, View):

    def get(self, request):
        form = RoleCreationForm(prefix="form1")
        formset = EventFormSet(prefix="form2")
        return render(request, 'audition_management/create.html', {
            'form': form,
            "formset": formset
        })

    def post(self, request):
        form = RoleCreationForm(request.POST, prefix="form1")
        role = None
        if form.is_valid():
            role = form.save(commit=False)
            role.agent = request.user.casting_account
            role.save()
        else: 
            return render(request, 'audition_management/create.html', {
                'form': form,
                "formset": formset
            })
        formset = EventFormSet(request.POST, prefix="form2")
        if formset.is_valid() is False:
            messages.error(
                request, "Please review the forms and try again.")
            return render(request, 'audition_management/create.html', {
                'form': form,
                "formset": formset
            })
        else:
            for form in formset:
                if form.is_valid():
                    event = form.save(commit=False)
                    event.role = role
                    event.save()
            messages.success(
                request, "Role successfully created.")
            return HttpResponseRedirect(
                reverse("audition_management:tags", args=[role.id]))

class TagCreationView(LoginRequiredMixin, View):
    def get(self, request, pk):
        role = Role.objects.get(pk=pk)
        formset = TagFormSet(prefix="form1")
        return render(request, "audition_management/addTags.html", {
            "role": role,
            "formset": formset,
        })

    def post(self, request, pk):
        role = Role.objects.get(pk=pk)
        formset = TagFormSet(request.POST, prefix="form1")
        if formset.is_valid() is False:
            messages.error(
                request, "Please review the forms and try again.")
            return render(request, 'audition_management/addTags.html', {
                'role': role,
                "formset": formset
            })
        else:
            for form in formset:
                if form.is_valid():
                    tag = form.save(commit=False)
                    tag.role = role
                    tag.save()
            messages.success(
                request, "Tags successfully added to posting.")
            return HttpResponseRedirect(reverse("audition_management:settings"))

class EditRoleView(LoginRequiredMixin, View):

    def get(self, request, pk):
        role = Role.objects.get(pk=pk)
        form = EditRoleForm(instance=role, prefix="form1")
        formset = EventFormSet(instance=role, prefix="form2")
        return render(request, 'audition_management/editRole.html', {
            'role': role,
            'form': form,
            'formset': formset,
            "is_casting": is_casting_agent(request.user)
        })

    def post(self, request, pk):
        role = Role.objects.get(pk=pk)
        update_tags = json.loads(request.POST.get("update_tags"))
        form = EditRoleForm(request.POST, instance=role, prefix="form1")
        if form.is_valid():
            role = form.save()
            formset = EventFormSet(request.POST, instance=role, prefix="form2")
            for form in formset:
                if (form.is_valid() and
                        form.cleaned_data.get('DELETE') is False):
                    event = form.save(commit=False)
                    event.role = role
                    event.save()
                elif (form.cleaned_data.get('DELETE') is True):
                    form.cleaned_data.get('id').delete()
                elif form.is_valid() is False:
                    role = Role.objects.get(pk=pk)
                    form = EditRoleForm(instance=role, prefix="form1")
                    return render(request, 'audition_management/editRole.html', {
                        'role': role,
                        'form': form,
                        'formset': formset,
                        "is_casting": is_casting_agent(request.user)
                    })
            role.tags.all().delete()
            for tag in update_tags:
                Tag.objects.create(name=tag["tag"], role=role)
            messages.success(request, "Role successfully updated.")
            return HttpResponseRedirect(
                reverse("audition_management:edit-role", args=[pk]))
        else:
            role = Role.objects.get(pk=pk)
            formset = EventFormSet(instance=role, prefix="form2")
            return render(request, 'audition_management/editRole.html', {
                'role': role,
                'form': form,
                'formset': formset,
                "is_casting": is_casting_agent(request.user)
            })


"""
    This will be used in sprint 2
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
