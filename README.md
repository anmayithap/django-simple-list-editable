# Django. Simple list editable

> [!IMPORTANT]
> This project is intended only for the management of routine work with django admin,
> often wanted to manage list_editable attribute based on a request or self context,
> I hope this project can help you

## Content

- [Django. Simple list editable](#django-simple-list-editable)
  - [Content](#content)
  - [Install](#install)
  - [Using](#using)
    - [Using mixin](#using-mixin)
    - [Using admin instance](#using-admin-instance)

## Install

```bash
pip install django-simple-list-editable
```

## Using

### Using mixin

```python
from typing import Self, Sequence

from django.contrib.admin import ModelAdmin as StandaloneModelAdmin
from django.http.request import HttpRequest

from simple_list_editable.admin import ModelAdminMixin


class ModelAdmin(ModelAdminMixin, StandaloneModelAdmin):

    list_editable = ('some_field',)

    def get_list_editable(self: Self, request: HttpRequest) -> Sequence[str]:
        if not request.user.is_superuser:
            return ()
        return self.list_editable
```

### Using admin instance

```python
from typing import Self, Sequence

from django.http.request import HttpRequest

from simple_list_editable.admin import ModelAdmin as StandaloneModelAdmin


class ModelAdmin(StandaloneModelAdmin):

    list_editable = ('some_field',)

    def get_list_editable(self: Self, request: HttpRequest) -> Sequence[str]:
        if not request.user.is_superuser:
            return ()
        return self.list_editable
```
