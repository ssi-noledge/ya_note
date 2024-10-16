import pytest

from http import HTTPStatus


from pytest_django.asserts import assertRedirects, assertFormError

from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note


def test_user_can_create_note(author_client, author, test_form_data):
    url = reverse('notes:add')
    response = author_client.post(url, data=test_form_data)
    assertRedirects(response, reverse('notes:success'))
    assert Note.objects.count() == 1
    new_note = Note.objects.get()
    assert new_note.title == test_form_data['title']
    assert new_note.text == test_form_data['text']
    assert new_note.slug == test_form_data['slug']
    assert new_note.author == author


@pytest.mark.django_db
def test_anonymous_user_cant_create_note(client, test_form_data):
    url = reverse('notes:add')
    response = client.post(url, data=test_form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Note.objects.count() == 0


def test_not_unique_slug(author_client, note, test_form_data):
    url = reverse('notes:add')
    test_form_data['slug'] = note.slug
    response = author_client.post(url, data=test_form_data)
    assertFormError(response, 'form', 'slug', errors=(note.slug + WARNING))
    assert Note.objects.count() == 1


def test_empty_slug(author_client, test_form_data):
    url = reverse('notes:add')
    test_form_data.pop('slug')
    response = author_client.post(url, data=test_form_data)
    assertRedirects(response, reverse('notes:success'))
    assert Note.objects.count() == 1
    new_note = Note.objects.get()
    expected_slug = slugify(test_form_data['title'])
    assert new_note.slug == expected_slug


def test_author_can_edit_note(author_client, test_form_data, note):
    url = reverse('notes:edit', args=(note.slug,))
    response = author_client.post(url, test_form_data)
    assertRedirects(response, reverse('notes:success'))
    note.refresh_from_db()
    assert note.title == test_form_data['title']
    assert note.text == test_form_data['text']
    assert note.slug == test_form_data['slug']


def test_other_user_cant_edit_note(not_author_client, test_form_data, note):
    url = reverse('notes:edit', args=(note.slug,))
    response = not_author_client.post(url, test_form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    note_from_db = Note.objects.get(id=note.id)
    assert note.title == note_from_db.title
    assert note.text == note_from_db.text
    assert note.slug == note_from_db.slug


def test_deletion_by_author_is_ok(author_client, test_note_slug):
    # Attempt to delete the note using the client of the note's author
    deletion_url = reverse('notes:delete', args=test_note_slug)
    response = author_client.post(deletion_url)
    assertRedirects(response, reverse('notes:success'))
    assert Note.objects.count() == 0


def test_deletion_by_non_author(not_author_client, test_note_slug):
    # Attempt to delete the note using a client that is not the author
    deletion_url = reverse('notes:delete', args=test_note_slug)
    response = not_author_client.post(deletion_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Note.objects.count() == 1
