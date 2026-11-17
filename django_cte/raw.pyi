from collections.abc import Mapping, Sequence
from typing import Any

from django.db.models.fields import Field

# Each `raw_cte_sql()` call returns a new class named `RawCTEQuerySet`;
# this stub-only class stands for all of them. Import it for annotations
# under `if TYPE_CHECKING:` only, as it does not exist at module level.
class RawCTEQuerySet:
    """Opaque result of `raw_cte_sql()`, only usable as a `CTE` body"""

def raw_cte_sql(
    sql: str,
    params: Sequence[object],
    # `Field[Any, Any]` is django-stubs' "any field"
    refs: Mapping[str, Field[Any, Any]],  # pyright: ignore[reportExplicitAny]
) -> type[RawCTEQuerySet]: ...
