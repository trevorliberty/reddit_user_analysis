'''
imports all the models from the .models package
'''
from .Users import Users


def init():
    """
    Initalizes the Users
    """
    return Users()
