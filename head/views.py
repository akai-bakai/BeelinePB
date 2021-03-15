from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.forms import modelformset_factory
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, DetailView, DeleteView

from .forms import ImageForm, PersonForm
from .models import *
from .permissions import UserHasPermissionMixin


class HomePageView(ListView):
    model = Person
    template_name = 'index.html'
    context_object_name = 'persons'
    paginate_by = 2

    def get_template_names(self):
        template_name = super(HomePageView, self).get_template_names()
        search = self.request.GET.get('q')
        filter = self.request.GET.get('filter')
        if search:
            template_name = 'search.html'
        elif filter:
            template_name = 'new.html'
        return template_name

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        search = self.request.GET.get('q')
        filter = self.request.GET.get('filter')
        if search:
            context['persons'] = Person.objects.filter(Q(contact__icontains=search) |
                                                       Q(description__icontains=search))
        elif filter:
            start_date = timezone.now() - timedelta(days=1)
            context['persons'] = Person.objects.filter(created__gte=start_date)
        else:
            context['persons'] = Person.objects.all()
        return context


class CategoryDetailView(DetailView):
    model = Category
    template_name = 'category-detail.html'
    context_object_name = 'category'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.slug = kwargs.get('slug', None)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['persons'] = Person.objects.filter(category_id=self.slug)
        return context


class PersonDetailView(DetailView):
    model = Person
    template_name = 'person-detail.html'
    context_object_name = 'person'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        image = self.get_object().get_image
        if isinstance(image, type(Image)):
            context['images'] = self.get_object().images.exclude(id=image.id)
        return context

# Add Contact

@login_required(login_url='login')
def add_person(request):
    ImageFormSet = modelformset_factory(Image, form=ImageForm, max_num=5)
    if request.method == 'POST':
        person_form = PersonForm(request.POST)
        formset = ImageFormSet(request.POST or None, request.FILES or None, queryset=Image.objects.none())
        if person_form.is_valid() and formset.is_valid():
            person = person_form.save(commit=False)
            person.user = request.user
            person.save()

            for form in formset.cleaned_data:
                image = form['image']
                Image.objects.create(image=image, person=person)
            return redirect(person.get_absolute_url())
    else:
        person_form = PersonForm()
        formset = ImageFormSet(queryset=Image.objects.none())
    return render(request, 'add-person.html', locals())

def update_person(request, pk):
    person = get_object_or_404(Person, pk=pk)
    if request.user == person.user:
        ImageFormSet = modelformset_factory(Image, form=ImageForm, max_num=5)
        person_form = PersonForm(request.POST or None, instance=person)
        formset = ImageFormSet(request.POST or None, request.FILES or None,
                               queryset=Image.objects.filter(person=person))
        if person_form.is_valid() and formset.is_valid():
            person = person_form.save()
            images = formset.save(commit=False)
            for image in images:
                image.person = person
                image.save()
            return redirect(person.get_absolute_url())
        return render(request, 'update-person.html', locals())
    else:
        return HttpResponse('<h1>403 Forbidden</h1>')


class DeletePersonView(UserHasPermissionMixin, DeleteView):
    model = Person
    template_name = 'delete-person.html'
    success_url = reverse_lazy('home')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        messages.add_message(request, messages.SUCCESS, 'Person is deleted!')
        return HttpResponseRedirect(success_url)