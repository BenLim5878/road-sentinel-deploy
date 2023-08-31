"""
URL configuration for server project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, re_path
from core.views import process_image, upload_validity
from img_api.views import get_image
from sentinel_view.views import serve_html,serve_img,serve_css,serve_javascript,serve_geo_data, serve_geo_data_country, serve_geo_data_state, serve_system_configuration_setting,serve_annotation_data,serve_statistic_data,serve_login_page,logout_user,serve_public_html, create_user
from test_api.views import process_latlong, create_default_user
from django.shortcuts import redirect

handler404 = 'sentinel_view.views.page_not_found'

urlpatterns = [
    path('uploads', process_image, name='process_image'),
    path('uploads/valid', upload_validity, name='uplaod_validity'),
    path('api/img/result/<str:filename>', get_image, name='get_image'),
    re_path(r'^app/(?:(?P<path>.+)/)?$', serve_html, name='render_sentinel'),
    path('app/login', serve_login_page, name="login"),
    path('app/logout', logout_user, name="logout"),
    path('',lambda request: redirect('/app/')),
    path('api/user', create_user, name='create_user'),
    path('api/img/resource/<str:img_name>', serve_img, name='render_img'),
    path('api/css/<str:css_filename>', serve_css, name='render_css'),
    path('api/js/<str:js_filename>', serve_javascript, name='render_javascript'),
    path('api/geo/all', serve_geo_data, name="serve_compiled_data"),
    path('api/geo/country', serve_geo_data_country, name="serve_compiled_data_country"),
    path('api/geo/state', serve_geo_data_state, name="serve_compiled_data_state"),
    path('api/setting', serve_system_configuration_setting, name="serve_system_configuration_setting"),
    path('api/annotation',serve_annotation_data, name="serve_annotation_data"),
    path('api/annotation/<str:annotation_id>',serve_annotation_data, name="serve_annotation_data"),
    path('api/statistic',serve_statistic_data, name="serve_statistic_data"),
    path('api/test/coords/', process_latlong, name="test_coord_lat_lng"),
    path('api/test/user/default',create_default_user, name="test_create_default_user"),
    # public
    path('public',serve_public_html, name="render_public"),
]
