# agent/tools.py
# Built-ins
import difflib
import re

# Third-party / Django
from companies.models import Company
from langchain.tools import StructuredTool

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _clean(text: str) -> str:
    """Lower-case and strip non-alphanumerics so that 'Acme Corp.' ≈ 'acme corp'."""
    return re.sub(r"[^a-z0-9]", "", text.lower())

def _format_company(c: Company) -> str:
    """Return a concise multi-line description for the chatbot."""
    return (
        f"{c.name} — {c.description}\n"
        f"Sector: {c.sector}\n"
        f"Financials: {c.financials}"
    )

# ---------------------------------------------------------------------------
# Public tool function
# ---------------------------------------------------------------------------

def _get_company_by_name(name: str) -> str:
    """Return a company profile given *name*.

    The search strategy is:
    1. Exact case-insensitive match (fast).
    2. `icontains` fallback (partial substring).
    3. Fuzzy match using :pymod:`difflib` in case of typos like *Acme Crop*.
    """

    # --- 1. Exact (case-insensitive) --------------------------------------
    try:
        c = Company.objects.get(name__iexact=name)
        return _format_company(c)
    except Company.DoesNotExist:
        pass

    # --- 2. Sub-string fallback ------------------------------------------
    qs = Company.objects.filter(name__icontains=name).order_by("name")
    if qs.exists():
        return _format_company(qs.first())

    # --- 3. Fuzzy match ---------------------------------------------------
    cleaned_target = _clean(name)
    best_ratio = 0.0
    best_company = None
    for c in Company.objects.all():
        ratio = difflib.SequenceMatcher(None, cleaned_target, _clean(c.name)).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_company = c
    if best_company and best_ratio >= 0.75:  # 0.75 is permissive but avoids randoms
        return _format_company(best_company)

    # --- None found -------------------------------------------------------
    return "Company not found."

get_company_tool = StructuredTool.from_function(
    name        = "get_company_info",
    description = "Look up a company profile by name in the internal database.",
    func        = _get_company_by_name,
)