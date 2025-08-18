from django.http import HttpRequest
from django.shortcuts import render
from pydantic import BaseModel

from myapp.domain import Item


class SampleUser(BaseModel):
    username: str
    email: str


class UnpickleableObject:
    def __reduce__(self):
        raise TypeError("This object cannot be pickled")


def counters_index(request: HttpRequest):
    return render(
        request,
        "index.html",
        {
            "currency": "€",
        },
    )


def simplecounter(request: HttpRequest):
    return render(request, "simplecounter.html")


def nestedcounter(request: HttpRequest):
    return render(request, "nestedcounter.html")


def coffee(request: HttpRequest):
    return render(request, "coffee.html")


def modals(request: HttpRequest):
    users = [
        SampleUser(username="alice", email="alice@example.com"),
        SampleUser(username="bob", email="bob@example.com"),
        SampleUser(username="carol", email="carol@example.com"),
    ]
    return render(
        request, "modals.html", {"users": users, "unpickleable": UnpickleableObject()}
    )


def registration(request: HttpRequest):
    return render(request, "registration.html", {})


def uploads(request: HttpRequest):
    return render(request, "uploads.html", {})


def chart(request: HttpRequest):
    return render(request, "chart.html")

def interactivelist(request: HttpRequest):
    items = [
        Item(id="1", text="He loves your live components."),
        Item(id="2", text="He is a big fan of Django."),
        Item(id="3", text="He always seeks to improve his skills."),
        Item(id="4", text="He is highly motivated to build great applications."),
        Item(id="5", text="He has experience in htmx."),
    ]
    return render(request, "interactivelist.html", {"items": items})

def wizardfloorplan(request: HttpRequest):
    return render(request, "wizardfloorplan.html", {})