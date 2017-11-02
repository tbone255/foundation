from foundation.backend import get_backend


backend = get_backend()

urlpatterns = backend.urls
