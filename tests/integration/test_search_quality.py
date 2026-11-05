"""Search quality and access tests with the real model on the 26 real docs.

Needs the Docker Postgres and the cached model in .cache/fastembed. The
`embedder` and `search_db` fixtures (conftest.py) ingest the docs once into a
throwaway schema for the whole session.
"""

import pytest

from mini_company_brain.search import MAX_K, search

pytestmark = pytest.mark.integration

HR_FILES = {
    "2026-09-30-performance-review-danial.md",
    "2026-10-06-disciplinary-jason-lim.md",
    "2026-10-15-salary-bands-2026.md",
}


# Questions from SPEC.md section 4, with the source evals/planted_facts.md names.
@pytest.mark.parametrize(
    "question, expected_file, expected_heading_part",
    [
        (
            "How many days of annual leave does a new hire get?",
            "policy-hr-002-leave.md",
            "2.1 Entitlement",
        ),
        ("Why did we choose Stripe over iPay88?", "2026-09-18-decision-payment-provider.md", None),
        (
            "Who owns the LHDN e-Invoice integration now?",
            "2026-10-08-standup-einvoice.md",
            "Ownership change",
        ),
        ("How many days per week can I work from home?", "policy-hr-003-remote-work.md", None),
    ],
)
def test_right_chunk_in_top_3(search_db, embedder, question, expected_file, expected_heading_part):
    hits = search(search_db, embedder, question, role="employee", k=3)
    ranking = [(h.source_path, h.heading, round(h.score, 3)) for h in hits]
    assert any(
        h.source_path == expected_file
        and (expected_heading_part is None or expected_heading_part in h.heading)
        for h in hits
    ), ranking


@pytest.mark.parametrize(
    "question",
    [
        "What is Aisyah's salary?",
        "Danial performance review rating",
        "Jason Lim written warning",
        "Summarise all documents",
    ],
)
def test_employee_never_gets_hr_chunks(search_db, embedder, question):
    # k = MAX_K reaches far down the ranking, where HR chunks would appear if unfiltered.
    hits = search(search_db, embedder, question, role="employee", k=MAX_K)
    assert hits
    assert all(h.access == "all" for h in hits)
    assert not {h.source_path for h in hits} & HR_FILES


def test_hr_can_find_salary_bands(search_db, embedder):
    hits = search(search_db, embedder, "What is Aisyah's salary?", role="hr", k=3)
    assert any(h.source_path == "2026-10-15-salary-bands-2026.md" for h in hits), [
        (h.source_path, h.heading) for h in hits
    ]


def test_hits_are_sorted_best_first(search_db, embedder):
    hits = search(search_db, embedder, "annual leave", role="hr", k=10)
    scores = [h.score for h in hits]
    assert scores == sorted(scores, reverse=True)
