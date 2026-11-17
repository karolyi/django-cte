from collections.abc import Callable
from typing import Any, Generic, TypeVar, overload

from django.db.models import Manager, Q
from django.db.models.base import Model
from django.db.models.query import QuerySet
from django.db.models.sql import Query
from typing_extensions import Self, deprecated, override

from .meta import CTEColumns
from .raw import RawCTEQuerySet

__all__ = ["CTE", "with_cte"]

_ModelT = TypeVar("_ModelT", bound=Model)
_ModelT_co = TypeVar("_ModelT_co", bound=Model, covariant=True)
_RowT_co = TypeVar("_RowT_co", covariant=True)
# `object` rows: the row type of `QuerySet` is covariant, so
# `QuerySet[Model, object]` takes any queryset, no `Any` needed
_QuerySetT = TypeVar("_QuerySetT", bound=QuerySet[Model, object])
_QuerySetT_co = TypeVar(
    "_QuerySetT_co", bound=QuerySet[Model, object], covariant=True
)

@overload
def with_cte(*ctes: CTE[QuerySet[Model, object]], select: CTE[_QuerySetT]) -> _QuerySetT: ...
@overload
def with_cte(*ctes: CTE[QuerySet[Model, object]], select: _QuerySetT) -> _QuerySetT: ...
@overload
def with_cte(
    *ctes: CTE[QuerySet[Model, object]], select: type[_ModelT]
) -> QuerySet[_ModelT, _ModelT]: ...

class CTE(Generic[_QuerySetT_co]):
    """Common Table Expression

    The type parameter is the type of the queryset making up the body
    of the CTE, e.g. `CTE[QuerySet[Order, dict[str, Any]]]`.
    """

    query: Query | None
    name: str
    col: CTEColumns
    materialized: bool | None
    @overload
    def __init__(
        self,
        queryset: _QuerySetT_co | None,
        name: str = "cte",
        materialized: bool | None = None,
    ) -> None: ...
    @overload
    def __init__(
        # `Any` values: the row types of raw SQL are unknown
        self: CTE[QuerySet[Model, dict[str, Any]]],  # pyright: ignore[reportExplicitAny]
        queryset: type[RawCTEQuerySet],
        name: str = "cte",
        materialized: bool | None = None,
    ) -> None: ...
    @classmethod
    def recursive(
        cls,
        make_cte_queryset: Callable[[CTE[_QuerySetT]], _QuerySetT],
        name: str = "cte",
        materialized: bool | None = None,
    ) -> CTE[_QuerySetT]: ...
    @overload
    def join(
        self,
        model_or_queryset: _QuerySetT,
        *filter_q: Q,
        _join_type: str = ...,
        **filter_kw: object,
    ) -> _QuerySetT: ...
    @overload
    def join(
        self,
        model_or_queryset: type[_ModelT],
        *filter_q: Q,
        _join_type: str = ...,
        **filter_kw: object,
    ) -> QuerySet[_ModelT, _ModelT]: ...
    def queryset(self) -> _QuerySetT_co: ...
    def resolve_expression(self, *args: object, **kw: object) -> Self: ...

@deprecated("Use `django_cte.CTE` instead.")
class With(CTE[_QuerySetT_co]):
    @staticmethod
    @override
    @deprecated("Use `django_cte.CTE.recursive` instead.")
    def recursive(  # pyright: ignore[reportIncompatibleMethodOverride]
        make_cte_queryset: Callable[[CTE[_QuerySetT]], _QuerySetT],
        name: str = "cte",
        materialized: bool | None = None,
    ) -> CTE[_QuerySetT]: ...

# Message split as in cte.py, where the runtime message lives
@deprecated(
    "CTEQuerySet is deprecated. "  # pyright: ignore[reportImplicitStringConcatenation]
    "CTEs can now be applied to any queryset using `with_cte()`"
)
class CTEQuerySet(QuerySet[_ModelT_co, _RowT_co]):
    """QuerySet with support for Common Table Expressions"""

    @deprecated("Use `django_cte.with_cte(cte, select=...)` instead.")
    def with_cte(self, cte: CTE[QuerySet[Model, object]]) -> Self: ...

# The deprecated manager returns the deprecated queryset, hence the
# `reportDeprecated` ignores
class _CTEManagerBase(Manager[_ModelT_co]):
    @override
    def get_queryset(self) -> CTEQuerySet[_ModelT_co, _ModelT_co]: ...  # pyright: ignore[reportDeprecated]
    @override
    def all(self) -> CTEQuerySet[_ModelT_co, _ModelT_co]: ...  # pyright: ignore[reportDeprecated]
    @deprecated("Use `django_cte.with_cte(cte, select=...)` instead.")
    def with_cte(
        self, cte: CTE[QuerySet[Model, object]]
    ) -> CTEQuerySet[_ModelT_co, _ModelT_co]: ...  # pyright: ignore[reportDeprecated]

# Message split as in cte.py, where the runtime message lives
@deprecated(
    "CTEMAnager is deprecated. "  # pyright: ignore[reportImplicitStringConcatenation]
    "CTEs can now be applied to any queryset using `with_cte()`"
)
class CTEManager(_CTEManagerBase[_ModelT_co]):
    """Manager for models that perform CTE queries"""
