from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic import DeleteView, ListView, UpdateView
from django.views.generic.edit import FormMixin

from .forms import TodoForm
from .models import Todo


class TodoListView(FormMixin, ListView):
    model = Todo
    template_name = 'home.html'
    context_object_name = 'todos'
    form_class = TodoForm

    def get_success_url(self):
        return reverse_lazy('home')

    def get_queryset(self):
        return Todo.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault('form', self.get_form())
        context['pending_todos'] = context['todos'].filter(is_resolved=False)
        context['completed_todos'] = context['todos'].filter(is_resolved=True)
        return context

    def post(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        form = self.get_form()
        if form.is_valid():
            form.save()
            return redirect(self.get_success_url())
        return self.render_to_response(self.get_context_data(form=form))


@method_decorator(require_POST, name='dispatch')
class TodoDeleteView(DeleteView):
    model = Todo
    success_url = reverse_lazy('home')
    template_name = 'todos/todo_confirm_delete.html'


class TodoUpdateView(UpdateView):
    model = Todo
    form_class = TodoForm
    template_name = 'todos/todo_form.html'
    success_url = reverse_lazy('home')


@require_POST
def toggle_resolved(request, pk):
    todo = get_object_or_404(Todo, pk=pk)
    todo.is_resolved = not todo.is_resolved
    todo.save(update_fields=['is_resolved', 'updated_at'])
    return redirect('home')
