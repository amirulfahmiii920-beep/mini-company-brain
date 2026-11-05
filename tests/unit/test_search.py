"""Tests for search input checks and role mapping (no database or model needed)."""

import pytest

from mini_company_brain.search import MAX_K, allowed_access, search


def test_employee_sees_only_all():
    assert allowed_access("employee") == ("all",)


def test_hr_sees_all_and_hr():
    assert allowed_access("hr") == ("all", "hr")


@pytest.mark.parametrize("role", ["admin", "HR", "", None])
def test_unknown_role_raises(role):
    # Fail closed: a typo must never fall back to some default access.
    with pytest.raises(ValueError, match="role"):
        allowed_access(role)


@pytest.mark.parametrize("query", ["", "   ", "\n"])
def test_empty_query_raises(query):
    # Checked before the database or the model is touched, so None is fine here.
    with pytest.raises(ValueError, match="query"):
        search(None, None, query, role="employee")


@pytest.mark.parametrize("k", [0, -1, MAX_K + 1])
def test_k_out_of_range_raises(k):
    with pytest.raises(ValueError, match="k"):
        search(None, None, "leave", role="employee", k=k)


def test_unknown_role_raises_in_search_before_any_query():
    with pytest.raises(ValueError, match="role"):
        search(None, None, "leave", role="admin")
