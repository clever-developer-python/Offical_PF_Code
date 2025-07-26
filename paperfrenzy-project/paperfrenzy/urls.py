"""paperfrenzy URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path,include
import app.views
from django.conf.urls.static import static
from django.conf import settings

#JEEPPV

urlpatterns = [
    path('c@rr0^$', admin.site.urls),
    path('',app.views.home, name="home"),
    path('subjects_10/', app.views.subjects_x, name="class_10"),
    path('subjects_12/', app.views.subjects_12, name="class_12"),
    path('viewer/',app.views.subjectview10, name='subjectview'),
    path('viewer12/', app.views.subjectview12, name="sv12"),
    path('search/', app.views.search_view, name='search_view'),
    path('feedback/',app.views.feedback, name='feedback'),
    path('reieve/',app.views.recieve, name="r"),
    path('openms/',app.views.openms, name='openms'),
    path('openms12/',app.views.openms12, name='openms12'),
    path('neetpapers/',app.views.jeeviewer, name='jv'),
    path('neetviewer/',app.views.JEEADVVIEWER,name="JEEPPV"),
    path('openmsneet/',app.views.openmsjee,name="msjee"),
    path('class_10_sample/', app.views.subjects_10_sample, name='class_10_sample'),
    path('class10_sample_viewer/',app.views.subjectsview10, name="class_10_sample"),
    path('samplenewtabms/',app.views.openmsSample, name="newtabsample"),
    path('igcse/',app.views.igcse, name="igcse"),
    path('igcseview/',app.views.igcseview, name="igcseview"),
    path('igcsems/',app.views.igcsems, name="igcsems"),
    path('igcseinsert/',app.views.igcseinsert, name="igcseinsert"),
    path('ALevels/',app.views.ALevels, name="Alevels"),
    path('ALevelsview/',app.views.Alevelsview, name="Alevelsview"),
    path('ALevelsms/',app.views.ALevelsms, name="Alevelsms"),
    path('ALevelsinsert/',app.views.ALevelsinsert, name="Alevelsinsert"),
    path('questionai/',app.views.question_ai, name="qa"),
    path('generate/',app.views.generate, name="gen"),
    path('blog/',app.views.blog, name="blog"),
    path('resourcerep',app.views.Resourcerepo, name="dcinv"),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
