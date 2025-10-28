"""
Settings package for config project.
Import the appropriate settings module based on environment.
"""
import os

environment = os.environ.get('DJANGO_ENVIRONMENT', 'development')

if environment == 'production':
    from .production import *
elif environment == 'development':
    from .development import *
else:
    from .base import *
