import os
import json
from django.shortcuts import render
from django.conf import settings



def index(request):
    src = json.load(open(os.path.join(settings.BASE_DIR, 'webpack-stats.json')))
    vendor = json.load(open(os.path.join(settings.BASE_DIR, 'webpack-stats.json')))
    context = {
            "src": src['chunks']['app'][0]['name'],
            "vendor": vendor['chunks']['vendor'][0]['name'],
            "version": 'Tele Django',
            "buildDate": '2024'
        }
    return render(request, "index.html", context)