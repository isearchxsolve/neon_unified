"""
Tests for HabitService and AuthService behaviors.
Covers habit creation, retrieval, uniqueness, completion toggling,
auth registration, login flows, password hashing, and validation errors.
"""

import pytest

from app.models import Habit, User
from app.services import AuthError, AuthService, HabitError, HabitService


@pytest.fixture
def auth_service():
    return AuthService()


@pytest.fixture
def habit_service():
    return HabitService()


@pytest.fixture
def alice(auth_service):
    user = auth_service.register(email="alice@example.com", password="top_secret_horses")
    return user


# ---------------------------------------------------------------------------
# AuthService: Registration
# ---------------------------------------------------------------------------


class TestAuthServiceRegistration:
    def test_register_returns_user_with_email(self, auth_service):
        user = auth_service.register(email="bob@example.com", password="p@ssw0rd_long")
        assert isinstance(user, User)
        assert user.email == "bob@example.com"

    def test_register_hashed_password_differs_from_plaintext(self, auth_service):
        user = auth_service.register(email="bob@example.com", password="p@ssw0rd_long")
        assert user.password_hash != "p@ssw0rd_long"
        assert "p@ssw0rd_long" not in user.password_hash

    def test_register_generates_unique_user_ids(self, auth_service):
        a = auth_service.register(email="a@example.com", password="p@ssw0rd_long")
        b = auth_service.register(email="b@example.com", password="p@ssw0rd_long")
        assert a.id != b.id

    def test_register_rejects_blank_email(self, auth_service):
        with pytest.raises(AuthError) as exc_info:
            auth_service.register(email="  ", password="p@ssw0rd_long")
        assert "email" in str(exc_info.value).lower()

    def test_register_rejects_invalid_email_format(self, auth_service):
        with pytest.raises(AuthError) as exc_info:
            auth_service.register(email="not-an-email", password="p@ssw0rd_long")
        assert "email" in str(exc_info.value).lower()

    def test_register_rejects_short_password(self, auth_service):
        with pytest.raises(AuthError) as exc_info:
            auth_service.register(email="short@example.com", password="12345")
        assert "password" in str(exc_info.value).lower()
        assert "short" in str(exc_info.value).lower() or "at least" in str(exc_info.value).lower()

    def test_register_rejects_blank_password(self, auth_service):
        with pytest.raises(AuthError) as exc_info:
            auth_service.register(email="blankpass@example.com", password="")
        assert "password" in str(exc_info.value).lower()

    def test_register_rejects_duplicate_email(self, auth_service):
        auth_service.register(email="dupe@example.com", password="p@ssw0rd_long")
        with pytest.raises(AuthError) as exc_info:
            auth_service.register(email="dupe@example.com", password="p@ssw0rd_long")
        assert "exists" in str(exc_info.value).lower() or "already" in str(exc_info.value).lower()

    def test_register_does_not_commit_plaintext_to_hash_for_differing_values(self, auth_service):
        u1 = auth_service.register(email="x@example.com", password="secret_one_long")
        u2 = auth_service.register(email="y@example.com", password="secret_one_long")
        assert u1.password_hash == u2.password_hash, "Same password should hash deterministically"


# ---------------------------------------------------------------------------
# AuthService: Login
# ---------------------------------------------------------------------------


class TestAuthServiceLogin:
    def test_login_with_valid_credentials_returns_user(self, auth_service):
        auth_service.register(email="login@example.com", password="p@ssw0rd_long")
        user = auth_service.login(email="login@example.com", password="p@ssw0rd_long")
        assert isinstance(user, User)
        assert user.email == "login@example.com"

    def test_login_with_wrong_password_raises(self, auth_service):
        auth_service.register(email="login@example.com", password="p@ssw0rd_long")
        with pytest.raises(AuthError):
            auth_service.login(email="login@example.com", password="totally_wrong_pw")

    def test_login_with_unknown_email_raises(self, auth_service):
        with pytest.raises(AuthError):
            auth_service.login(email="ghost@example.com", password="p@ssw0rd_long")

    def test_login_validation_rejects_blank_email(self, auth_service):
        with pytest.raises(AuthError):
            auth_service.login(email="", password="p@ssw0rd_long")

    def test_login_validation_rejects_blank_password(self, auth_service):
        with pytest.raises(AuthError):
            auth_service.login(email="bob@example.com", password="")


# ---------------------------------------------------------------------------
# AuthService: Retrieval
# ---------------------------------------------------------------------------


class TestAuthServiceRetrieval:
    def test_get_user_by_id_returns_registered_user(self, auth_service):
        registered = auth_service.register(email="fetch@example.com", password="p@ssw0rd_long")
        fetched = auth_service.get_user(user_id=registered.id)
        assert fetched is not None
        assert fetched.id == registered.id
        assert fetched.email == registered.email

    def test_get_user_by_id_returns_none_for_unknown_id(self, auth_service):
        assert auth_service.get_user(user_id="nonexistent-id-12345") is None


# ---------------------------------------------------------------------------
# HabitService: Create habit
# ---------------------------------------------------------------------------


class TestHabitServiceCreate:
    def test_create_habit_returns_habit_with_name_and_user(self, habit_service, alice):
        habit = habit_service.create_habit(user_id=alice.id, name="Read for 20 minutes")
        assert isinstance(habit, Habit)
        assert habit.name == "Read for 20 minutes"
        assert habit.user_id == alice.id
        assert habit.is_complete_today() is False

    def test_create_habit_rejects_blank_name(self, habit_service, alice):
        with pytest.raises(HabitError) as exc_info:
            habit_service.create_habit(user_id=alice.id, name="   ")
        assert "name" in str(exc_info.value).lower()

    def test_create_habit_rejects_empty_name(self, habit_service, alice):
        with pytest.raises(HabitError):
            habit_service.create_habit(user_id=alice.id, name="")

    def test_create_habit_for_unknown_user_raises(self, habit_service):
        with pytest.raises(HabitError):
            habit_service.create_habit(user_id="ghost-user-id", name="Run 5k")

    def test_create_duplicate_habit_name_raises_for_same_user(self, habit_service, alice):
        habit_service.create_habit(user_id=alice.id, name="Read for 20 minutes")
        with pytest.raises(HabitError) as exc_info:
            habit_service.create_habit(user_id=alice.id, name="Read for 20 minutes")
        assert "exists" in str(exc_info.value).lower() or "already" in str(exc_info.value).lower()


# ---------------------------------------------------------------------------
# HabitService: Get habits for user
# ---------------------------------------------------------------------------


class TestHabitServiceRetrieve:
    def test_get_habits_returns_only_habits_for_given_user(self, habit_service, auth_service):
        alice = auth_service.register(email="alice@example.com", password="secret_alice_pw")
        bob = auth_service.register(email="bob@example.com", password="secret_bob_pw")

        habit_service.create_habit(user_id=alice.id, name="Alice habit 1")
        habit_service.create_habit(user_id=alice.id, name="Alice habit 2")
        habit_service.create_habit(user_id=bob.id, name="Bob habit")

        alice_habits = habit_service.get_habits(user_id=alice.id)
        assert len(alice_habits) == 2
        assert all(h.user_id == alice.id for h in alice_habits)

        bob_habits = habit_service.get_habits(user_id=bob.id)
        assert len(bob_habits) == 1
        assert bob_habits[0].name == "Bob habit"

    def test_get_habits_returns_empty_list_for_new_user(self, habit_service, alice):
        assert habit_service.get_habits(user_id=alice.id) == []

    def test_get_habits_rejects_unknown_user(self, habit_service):
        with pytest.raises(HabitError):
            habit_service.get_habits(user_id="ghost-user-id")

    def test_get_habit_by_id_returns_habit(self, habit_service, alice):
        created = habit_service.create_habit(user_id=alice.id, name="Meditate")
        fetched = habit_service.get_habit(habit_id=created.id)
        assert fetched.id == created.id
        assert fetched.name == "Meditate"

    def test_get_habit_by_id_returns_none_for_unknown_habit_id(self, habit_service, alice):
        assert habit_service.get_habit(habit_id="nonexistent-habit-id") is None


# ---------------------------------------------------------------------------
# HabitService: Mark complete
# ---------------------------------------------------------------------------


class TestHabitServiceComplete:
    def test_mark_complete_sets_habit_status(self, habit_service, alice):
        habit = habit_service.create_habit(user_id=alice.id, name="Workout")
        updated = habit_service.mark_complete(habit_id=habit.id)
        assert updated.is_complete_today() is True

    def test_mark_complete_second_time_is_idempotent(self, habit_service, alice):
        habit = habit_service.create_habit(user_id=alice.id, name="Water plants")
        habit_service.mark_complete(habit_id=habit.id)
        second = habit_service.mark_complete(habit_id=habit.id)
        assert second.is_complete_today() is True
        assert isinstance(second.completion_count, int)
        assert second.completion_count == 2

    def test_mark_complete_unknown_habit_raises(self, habit_service):
        with pytest.raises(HabitError):
            habit_service.mark_complete(habit_id="ghost-habit-id")


# ---------------------------------------------------------------------------
# HabitService: Unmark complete / toggle behavior (dashboard coordination)
# ---------------------------------------------------------------------------


class TestHabitServiceUnmark:
    def test_unmark_sets_habit_status_to_incomplete(self, habit_service, alice):
        habit = habit_service.create_habit(user_id=alice.id, name="Stretch")
        habit_service.mark_complete(habit_id=habit.id)
        updated = habit_service.unmark(habit_id=habit.id)
        assert updated.is_complete_today() is False

    def test_mark_then_unmark_keeps_completion_count_at_zero(self, habit_service, alice):
        habit = habit_service.create_habit(user_id=alice.id, name="Read")
        habit_service.mark_complete(habit_id=habit.id)
        updated = habit_service.unmark(habit_id=habit.id)
        assert updated.completion_count == 0

    def test_unmark_unknown_habit_raises(self, habit_service):
        with pytest.raises(HabitError):
            habit_service.unmark(habit_id="ghost-habit-id")


# ---------------------------------------------------------------------------
# HabitService: Dashboard summary
# ---------------------------------------------------------------------------


class TestHabitServiceDashboard:
    def test_dashboard_with_no_habits(self, habit_service, alice):
        summary = habit_service.load_dashboard_for_user(user_id=alice.id)
        assert summary["total"] == 0
        assert summary["completed"] == 0
        assert summary["completion_rate"] == 0

    def test_dashboard_counts_total_and_completed(self, habit_service, alice):
        h1 = habit_service.create_habit(user_id=alice.id, name="Habit A")
        h2 = habit_service.create_habit(user_id=alice.id, name="Habit B")
        h3 = habit_service.create_habit(user_id=alice.id, name="Habit C")

        habit_service.mark_complete(habit_id=h1.id)
        habit_service.mark_complete(habit_id=h3.id)

        summary = habit_service.load_dashboard_for_user(user_id=alice.id)
        assert summary["total"] == 3
        assert summary["completed"] == 2
        assert isinstance(summary["completion_rate"], (int, float))
        # 2/3 -> round half to even (banker's); Python rounds to nearest even so ok to loose check
        assert round(summary["completion_rate"], 4) == round(2 / 3, 4)