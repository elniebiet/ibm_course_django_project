from django.contrib import admin
# <HINT> Import any new Models here
from .models import Course, Lesson, Instructor, Learner, Question, Choice, Submission

# <HINT> Register QuestionInline and ChoiceInline classes here
class QuestionInline(admin.StackedInline):
    model = Question

class ChoiceInline(admin.StackedInline):
    model = Choice

class SubmissionInline(admin.StackedInline):
    model = Submission

class LessonInline(admin.StackedInline):
    model = Lesson
    extra = 5


# Register your models here.
class CourseAdmin(admin.ModelAdmin):
    inlines = [LessonInline]
    list_display = ('name', 'pub_date')
    list_filter = ['pub_date']
    search_fields = ['name', 'description']


class LessonAdmin(admin.ModelAdmin):
    list_display = ['title']
    search_fields = ['title', 'content']

class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text']
    search_fields = ['question_text']

class ChoiceAdmin(admin.ModelAdmin):
    list_display = ['choice_text']
    search_fields = ['choice_text']

class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['enrollment_id']
    search_fields = ['enrollment_id']

# <HINT> Register Question and Choice models here

admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Instructor)
admin.site.register(Learner)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice, ChoiceAdmin)
admin.site.register(Submission, SubmissionAdmin)


