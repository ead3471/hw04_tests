from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from ..models import Group, Post
from django.urls import reverse

User = get_user_model()


class PostTestForms(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.new_group = Group.objects.create(
            slug="new_group_slug",
            description="new_group_description",
            title="new_group_title"
        )

        cls.auth_user = User.objects.create_user("auth_user")
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.auth_user)

        cls.new_post = Post.objects.create(
            text="New post",
            author=cls.auth_user
        )

    def test_post_create_with_and_without_group(self):
        forms = [
            {
                "text": "Post with group",
                "group": PostTestForms.new_group.id
            },
            {
                "text": "Post without group"
            }
        ]

        for form in forms:
            posts_count = Post.objects.count()

            response = (PostTestForms
                        .auth_client
                        .post(reverse('posts:post_create'),
                              data=form,
                              follow=True))

            self.assertRedirects(response,
                                 reverse(
                                     'posts:profile',
                                     args=(PostTestForms.auth_user.username,)))

            self.assertEquals(posts_count + 1, Post.objects.count())

            created_objects = (Post
                               .objects
                               .filter(text=form["text"],
                                       author=PostTestForms.auth_user)
                               )

            if "group" in form.keys():
                created_objects = created_objects.filter(group=form["group"])

            self.assertTrue(created_objects.exists())

    def test_post_edit(self):
        edit_post_data = {
            "text": "new_text",
            "group": PostTestForms.new_group.id,
        }
        response = (PostTestForms
                    .auth_client
                    .post(
                        reverse('posts:post_edit',
                                args=(PostTestForms.new_post.id,)),
                        data=edit_post_data,
                        follow=True))

        self.assertRedirects(
            response,
            reverse("posts:post_detail",
                    args=(PostTestForms.new_post.id,)))

        edited_post = Post.objects.filter(
            id=PostTestForms.new_post.id,
            text=edit_post_data["text"],
            group=PostTestForms.new_group.id,
        )
        self.assertTrue(edited_post.exists())
