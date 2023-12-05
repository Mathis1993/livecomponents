from django.http import HttpRequest
from django.shortcuts import render


def index(request: HttpRequest):
    return render(
        request,
        "index.html",
        # Pass initial context to see if it's kept on partial rendering.
        {
            "currency": "€",
        },
    )
