from datetime import date, timedelta

from django.test import TestCase
from django.urls import reverse

from .models import Todo


class TodoViewTests(TestCase):
    def test_home_groups_pending_and_completed(self):
        pending = Todo.objects.create(title='Pending', due_date=date.today())
        completed = Todo.objects.create(title='Done', is_resolved=True)

        response = self.client.get(reverse('home'))

        self.assertTemplateUsed(response, 'home.html')
        self.assertQuerySetEqual(
            response.context['pending_todos'],
            [pending],
            transform=lambda x: x,
        )
        self.assertQuerySetEqual(
            response.context['completed_todos'],
            [completed],
            transform=lambda x: x,
        )

    def test_create_todo_via_post(self):
        payload = {
            'title': 'Write tests',
            'description': 'Cover CRUD flows',
            'due_date': (date.today() + timedelta(days=1)).isoformat(),
            'is_resolved': '',
        }

        response = self.client.post(reverse('home'), payload, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Todo.objects.count(), 1)
        todo = Todo.objects.get()
        self.assertEqual(todo.title, 'Write tests')
        self.assertEqual(todo.description, 'Cover CRUD flows')

    def test_invalid_create_shows_errors(self):
        response = self.client.post(reverse('home'), {'title': ''})

        self.assertEqual(Todo.objects.count(), 0)
        self.assertContains(response, 'This field is required', status_code=200)

    def test_update_todo(self):
        todo = Todo.objects.create(title='Old title')
        payload = {
            'title': 'Updated',
            'description': 'New description',
            'due_date': '',
            'is_resolved': 'on',
        }

        response = self.client.post(reverse('todo_edit', args=[todo.pk]), payload, follow=True)

        self.assertEqual(response.status_code, 200)
        todo.refresh_from_db()
        self.assertEqual(todo.title, 'Updated')
        self.assertTrue(todo.is_resolved)

    def test_toggle_resolved_changes_status(self):
        todo = Todo.objects.create(title='Toggle me')

        response = self.client.post(reverse('todo_toggle', args=[todo.pk]), follow=True)

        self.assertEqual(response.status_code, 200)
        todo.refresh_from_db()
        self.assertTrue(todo.is_resolved)

    def test_delete_todo(self):
        todo = Todo.objects.create(title='Delete me')

        response = self.client.post(reverse('todo_delete', args=[todo.pk]), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Todo.objects.count(), 0)
