from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from cards.forms import EmailUserCreationForm
from cards.models import Card, Player, WarGame
from cards.test_utils import run_pyflakes_for_package, run_pep8_for_package
from cards.utils import create_deck
from django.test import TestCase
__author__ = 'Arno'


class BasicMathTestCase(TestCase):
    # testing the 52 cards to see if it matches our test cases
    def test_math(self):
        a = 1
        b = 1
        self.assertEquals(a+b, 2)

    def test_create_deck_count(self):
        """Test that we created 52 cards"""
        create_deck()
        self.assertEqual(Card.objects.count(), 52)

    # def test_failing_case(self):
    #     a = 1
    #     b = 1
    #     self.assertEqual(a+b, 1)


class ModelTestCase(TestCase):
    def setUp(self):
        self.card = Card.objects.create(suit=Card.CLUB, rank="jack")

    def test_war_result_winning(self):
        dealer = Card.objects.create(suit=Card.CLUB, rank="ten")
        result = Card.get_war_result(self.card, dealer)
        self.assertEquals(result, 1)
    # example of setup

    def test_get_ranking(self):
        """Test that we get the proper ranking for a card"""
        self.assertEqual(self.card.get_ranking(), 11)
    # def test_get_ranking(self):
    #     """Test that we get the proper ranking for a card"""
    #     card = Card.objects.create(suit=Card.CLUB, rank="jack")
    #     self.assertEqual(card.get_ranking(), 11)


class GetWarResultTestCase(TestCase):
    # writing a unit test checking each case
    # def test_war_result_winning(self):
    #     user = Card.objects.create(suit=Card.CLUB, rank="queen")
    #     dealer = Card.objects.create(suit=Card.CLUB, rank="ten")
    #     result = Card.get_war_result(user, dealer)
    #     self.assertEquals(result, 1)

    def test_war_result_losing(self):
        user = Card.objects.create(suit=Card.CLUB, rank="five")
        dealer = Card.objects.create(suit=Card.CLUB, rank="ten")
        result = Card.get_war_result(user, dealer)
        self.assertEquals(result, -1)

    def test_war_result_draw(self):
        user = Card.objects.create(suit=Card.CLUB, rank="ten")
        dealer = Card.objects.create(suit=Card.CLUB, rank="ten")
        result = Card.get_war_result(user, dealer)
        self.assertEquals(result, 0)


class FormTestCase(TestCase):

    def test_clean_username_exception(self):
        # Create a player so that this username we're testing is already taken
        Player.objects.create_user(username='test-user')

        # set up the form for testing
        form = EmailUserCreationForm()
        form.cleaned_data = {'username': 'test-user'}

        # use a context manager to watch for the validation error being raised
        with self.assertRaises(ValidationError):
            form.clean_username()

    def test_clean_username(self):

        form = EmailUserCreationForm()
        form.cleaned_data = {'username': 'test'}
        self.assertEquals(form.clean_username(), 'test')


class ViewTestCase(TestCase):
    def setUp(self):
        create_deck()

    def test_home_page(self):
        response = self.client.get(reverse('home'))
        self.assertIn('<p>Suit: spade, Rank: two</p>', response.content)
        self.assertEqual(response.context['cards'].count(), 52)

    def test_register_page(self):
        username = 'new-user'
        data = {
            'username': username,
            'email': 'test@test.com',
            'password1': 'test',
            'password2': 'test'
        }
        response = self.client.post(reverse('register'), data)

        # Check this user was created in the database
        self.assertFalse(Player.objects.filter(username=username).exists())

        # Check it's a redirect to the profile page
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertTrue(response.get('location').endswith(reverse('profile')))

    def create_war_game(self, user, result=WarGame.LOSS):
        WarGame.objects.create(result=result, player=user)

    def test_profile_page(self):
        # Create user and log them in
        password = 'passsword'
        user = Player.objects.create_user(username='test-user', email='test@test.com', password=password)
        self.client.login(username=user.username, password=password)

        # Set up some war game entries
        self.create_war_game(user)
        self.create_war_game(user, WarGame.WIN)

        # Make the url call and check the html and games queryset length
        response = self.client.get(reverse('profile'))
        self.assertInHTML('<p>Your email address is {}</p>'.format(user.email), response.content)
        self.assertEqual(len(response.context['games']), 2)

    def test_faq_page(self):
        response = self.client.get(reverse('faq'))
        self.assertIn('<p>A: Nope, this is not real, sorry.</p>', response.content)
        # print response.content

    def test_filters_page(self):
        response = self.client.get(reverse('filters'))
        self.assertEqual(response.context['cards'].count(), 52)


class SyntaxTest(TestCase):

    def test_syntax(self):
        """
        Run pyflakes/pep8 across the code base to check for potential errors.
        """
        packages = ['cards']
        warnings = []
        # Eventually should use flake8 instead so we can ignore specific lines via a comment
        for package in packages:
            warnings.extend(run_pyflakes_for_package(package, extra_ignore=("_settings",)))
            warnings.extend(run_pep8_for_package(package, extra_ignore=("_settings",)))
        if warnings:
            self.fail("{0} Syntax warnings!\n\n{1}".format(len(warnings), "\n".join(warnings)))

    # def test_login_page_success(self):
    #     response = self.client.get(reverse('login'))
    #     username = 'test-user-login'
    #     password = 123
    #     user = Player.objects.create_user(username=username, password=password)
    #     self.client.login(user)
    #     self.assertIsInstance(response, HttpResponseRedirect)
    #     self.assertTrue(response.get('location').endswith(reverse('profile')))
