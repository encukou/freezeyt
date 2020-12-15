from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return HttpResponse("""
    <html>
        <head>
            <title>Hello world</title>
        </head>
        <body>
            Hello world!
            <br>
            <a href='/second_page.html'>LINK</a> to second page.
        </body>
    </html>
    """)


def second_page(request):
    return HttpResponse("""
    <html>
        <head>
            <title>Hello world second page</title>
        </head>
        <body>
            Second page !!!
        </body>
    </html>
    """)
