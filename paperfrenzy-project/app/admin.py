from django.contrib import admin
from app.models import papers
from app.models import markscheme
from app.models import feedbacks
from app.models import NEETpapers
from app.models import NEETmarkscheme
from app.models import SamplePapers10
from app.models import class10samplemarkscheme
from app.models import IGCSE,IGCSEMarkscheme,IGCSEInsert

admin.site.register(papers)
admin.site.register(markscheme)
admin.site.register(NEETpapers)
admin.site.register(NEETmarkscheme)
admin.site.register(feedbacks)
admin.site.register(SamplePapers10)
admin.site.register(class10samplemarkscheme)
admin.site.register(IGCSE)
admin.site.register(IGCSEMarkscheme)
admin.site.register(IGCSEInsert)