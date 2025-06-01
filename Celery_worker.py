from celery import Celery
from config import app  # Import your existing app from config

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend='redis://localhost:6379/0',
        broker='redis://localhost:6379/0'
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():  # Ensure DB and Flask context is available
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

celery = make_celery(app)
