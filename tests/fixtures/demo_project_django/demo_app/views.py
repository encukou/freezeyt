from django.http import HttpResponse
from django.conf.urls import url
from django.template import Context, Template
# from django.shortcuts import render


def index(request):
    return HttpResponse("""
    <html>
        <head>
            <title>Hello world</title>
        </head>
        <body>
            <h3>Hello world! This is a home page of app.</h3>
            <div>
            <a href='/second_page.html'>LINK</a> to second page.
            </div>
        </body>
    </html>
    """)


def second_page(request):
    template = Template("""
    <html>
        <head>
            <title>Hello world second page</title>
        </head>
        <body>
            <h3>Second page !!!</h3>
            <div>
            <a href="{% url 'third_page' %}">LINK</a> to third page.
            </div>
        </body>
    </html>
    """)
    context = Context({"url": url})
    return HttpResponse(template.render(context=context))


def third_page(request):
    return HttpResponse("""
    <html>
        <head>
            <title>Hello world third page</title>
        </head>
        <body>
            <h3>Third page !!!</h3>
            <div>
            <a href='/'>LINK</a> to home page.
            </div>
        </body>
    </html>
    """)
