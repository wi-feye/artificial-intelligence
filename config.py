import os 

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:

    
    TESTING = False
    DEBUG = False
        
    SECRET_KEY = os.getenv('APP_SECRET', os.urandom(24))