from typing import Any, ClassVar, Protocol, Self, Sequence

from django.contrib.admin.options import ModelAdmin as StandaloneModelAdmin
from django.contrib.admin.views.main import ChangeList
from django.forms.models import BaseModelFormSet
from django.forms.widgets import MediaDefiningClass
from django.http.request import HttpRequest


class ModelAdminProtocol(Protocol):
    """Request based list_editable interface for ModelAdmin.

    :cvar Sequence[str] _list_editable: Protected attribute for list_editable
    """

    _list_editable: ClassVar[Sequence[str]]

    @property
    def list_editable(self: Self) -> Sequence[str]:
        """Public getter to get _list_editable."""
        ...

    @list_editable.setter
    def list_editable(self: Self, value: Sequence[str]) -> None:
        """Public setter to set new _list_editable items."""
        ...

    def get_list_editable(
        self: Self,
        request: HttpRequest,
    ) -> Sequence[str]:
        """Modify or return a new list_editable object.

        Сan be modified based on request or self context.

        :param django.http.request.HttpRequest request: Http request instance.
        """
        ...


def _getter(self: ModelAdminProtocol) -> Sequence[str]:
    return self._list_editable


def _setter(self: ModelAdminProtocol, value: Sequence[str]) -> None:
    self._list_editable = value


class ModelAdminMeta(MediaDefiningClass):
    """Model admin metaclass.

    Necessary to replace the public attribute list_editable with its protected version.
    """

    def __new__(  # noqa: D102
        metaclass: type[Self],  # noqa: N804
        name: str,
        bases: Sequence[type],
        namespace: dict[str, Any],
    ) -> type[ModelAdminProtocol]:
        cls: type[ModelAdminProtocol] = super().__new__(
            metaclass,
            name,
            bases,
            namespace,
        )

        if hasattr(cls, 'list_editable') and not isinstance(cls.list_editable, property):
            public = cls.list_editable
        else:
            public = ()

        if not public:
            for base in cls.__mro__[-1:0:-1]:
                list_editable = getattr(base, '_list_editable', None)
                if list_editable is not None:
                    cls._list_editable = list_editable
                else:
                    cls._list_editable = public
        else:
            cls._list_editable = public

        cls.list_editable = property(
            fget=_getter,
            fset=_setter,
        )

        return cls


class BaseModelAdminMixin(metaclass=ModelAdminMeta):
    """Base mixin which overrides the standard list_editable."""

    @property
    def list_editable(self: Self) -> Sequence[str]:  # noqa: D102
        return self._list_editable

    @list_editable.setter
    def list_editable(self: Self, value: Sequence[str]) -> None:
        self._list_editable = value

    def get_list_editable(self: Self, request: HttpRequest) -> Sequence[str]:  # noqa: ARG002, D102
        return self.list_editable


class ModelAdminMixin(BaseModelAdminMixin):
    """Mixin which overrides the necessary methods to implement the new list_editable logic."""

    def get_changelist_instance(self: Self, request: HttpRequest) -> ChangeList:
        """Return change list instance.

        Overrides list_editable based on request and self contexts.

        :param django.http.request.HttpRequest request: Http request instance

        :return: Change list instance
        :rtype: ChangeList
        """
        self.list_editable = self.get_list_editable(request)
        return super().get_changelist_instance(request)

    def get_changelist_formset(self: Self, request: HttpRequest, **kwargs: Any) -> BaseModelFormSet:
        """Return formset for changelist.

        Overrides list_editable based on request and self contexts.

        :param django.http.request.HttpRequest request: Http request instance
        :param typing.Any kwargs: Necessary context

        :return: Model formset
        :rtype: BaseModelFormSet
        """
        self.list_editable = self.get_list_editable(request)
        return super().get_changelist_formset(request, **kwargs)


class ModelAdmin(ModelAdminMixin, StandaloneModelAdmin):
    """Model admin class."""

    pass
