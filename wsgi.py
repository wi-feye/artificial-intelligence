"""
This file is the entry point for
Artificial Intelligence microservice.
"""
# from src import create_app
from src import create_app

# application instance
app = create_app()

if __name__ == '__main__':
    app.run()