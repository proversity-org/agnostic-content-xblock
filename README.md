# Subscription Content XBlock


### Add URL patterns to edx-platform/lms/urls.py

```
# include URL patterns for subscription content views
urlpatterns += (
    url(r'^subscription/', include('agnosticcontentxblock.urls')),
)
```