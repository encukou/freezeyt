from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return HttpResponse("""
    <html>
        <head>
            <title>Hello world</title>
        </head>
        <body>
            <h3>Hello world!</h3>

            This is index page of app - django demo_app.
        </body>
    </html>
    """)
