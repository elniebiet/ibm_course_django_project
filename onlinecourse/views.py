from django.shortcuts import render
from django.http import HttpResponseRedirect
# <HINT> Import any new Models here
from .models import Course, Enrollment, Question, Choice, Submission
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth import login, logout, authenticate
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)
# Create your views here.


def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'onlinecourse/user_registration_bootstrap.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("onlinecourse:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'onlinecourse/user_registration_bootstrap.html', context)


def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('onlinecourse:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'onlinecourse/user_login_bootstrap.html', context)
    else:
        return render(request, 'onlinecourse/user_login_bootstrap.html', context)


def logout_request(request):
    logout(request)
    return redirect('onlinecourse:index')


def check_if_enrolled(user, course):
    is_enrolled = False
    if user.id is not None:
        # Check if user enrolled
        num_results = Enrollment.objects.filter(user=user, course=course).count()
        if num_results > 0:
            is_enrolled = True
    return is_enrolled


# CourseListView
class CourseListView(generic.ListView):
    template_name = 'onlinecourse/course_list_bootstrap.html'
    context_object_name = 'course_list'

    def get_queryset(self):
        user = self.request.user
        courses = Course.objects.order_by('-total_enrollment')[:10]
        for course in courses:
            if user.is_authenticated:
                course.is_enrolled = check_if_enrolled(user, course)
        return courses


class CourseDetailView(generic.DetailView):
    model = Course
    template_name = 'onlinecourse/course_detail_bootstrap.html'
    # def get_queryset(self):
    #     questions = Question.objects.order_by('lesson_id')
    #     print(questions)
    #     return questions


def enroll(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user

    is_enrolled = check_if_enrolled(user, course)
    if not is_enrolled and user.is_authenticated:
        # Create an enrollment
        Enrollment.objects.create(user=user, course=course, mode='honor')
        course.total_enrollment += 1
        course.save()

    return HttpResponseRedirect(reverse(viewname='onlinecourse:course_details', args=(course.id,)))


# <HINT> Create a submit view to create an exam submission record for a course enrollment,
# you may implement it based on following logic:
         # Get user and course object, then get the associated enrollment object created when the user enrolled the course
         # Create a submission object referring to the enrollment
         # Collect the selected choices from exam form
         # Add each selected choice object to the submission object
         # Redirect to show_exam_result with the submission id

def submit(request, course_id):
    user = request.user
    course = get_object_or_404(Course, pk=course_id)
    enrollment = Enrollment.objects.get(user=user, course=course_id)
    selected_choices = extract_answers(request)
    print("selected answers: ") 
    print(selected_choices)
    context = {}
    
    submission_obj = Submission.objects.create(enrollment=enrollment)
    for selected_choice in selected_choices:
        selected_choice = get_object_or_404(Choice, id=selected_choice)
        submission_obj.choices.add(selected_choice)
    
    submission_obj.save()
    print("submission saved: ID = ")
    print(submission_obj.id)
    print(submission_obj)
    print(submission_obj.choices)
    return HttpResponseRedirect(reverse(viewname='onlinecourse:exam_result', args=(course.id,submission_obj.id,)))


# <HINT> A example method to collect the selected choices from the exam form from the request object
def extract_answers(request):
   submitted_anwsers = []
   for key in request.POST:
       if key.startswith('choice'):
           value = request.POST[key]
           choice_id = int(value)
           submitted_anwsers.append(choice_id)
   return submitted_anwsers


# <HINT> Create an exam result view to check if learner passed exam and show their question results and result for each question,
# you may implement it based on the following logic:
        # Get course and submission based on their ids
        # Get the selected choice ids from the submission record
        # For each selected choice, check if it is a correct answer or not
        # Calculate the total score
def show_exam_result(request, course_id, submission_id):
    context = {}
    choice_id_with_status = {}
    score = {}
    print("course id and submission id")
    print(course_id)
    print(submission_id)
    course = get_object_or_404(Course, pk=course_id)
    submission = Submission.objects.get(id=submission_id)
    choiceids = submission.choices.all()
    user_score = 0
    total_score = 0

    print(choiceids)
    print(Submission.objects.all)

    questions = Question.objects.filter(course=course_id)
    for question in questions:
        passed_question = True
        choices = Choice.objects.filter(question=question.id)
        for choice in choices:
            if choice.is_correct: #choice is correct, check its in the list of submitted choices
                choice_found_in_submission = False
                for ch in choiceids:
                    if ch.id == choice.id:
                        choice_found_in_submission = True
                if False == choice_found_in_submission:
                    passed_question = False
                    # break
                choice_id_with_status[choice.id] = choice_found_in_submission
            else: #choice is not correct, check its not submitted
                choice_found_in_submission = False
                for ch in choiceids:
                    if ch.id == choice.id:
                        choice_found_in_submission = True
                if True == choice_found_in_submission:
                    passed_question = False
                    # break
                res = True 
                if choice_found_in_submission:
                    res = False
                choice_id_with_status[choice.id] = res
        if passed_question:
            question.grade = 1
            print("passed question - ")
            print(question.id)
            user_score += 1
        else:
            question.grade = 0
            print("failed question - ")
            print(question.id)
        total_score += 1

    score['user_score'] = user_score
    score['total_score'] = total_score


    # return HttpResponseRedirect(reverse(viewname='onlinecourse:course_details', args=(course_id,)))
    # return HttpResponseRedirect(reverse(viewname='onlinecourse:course_details', args=(course_id,)))
    context['course'] = course
    context['selected_ids'] = choiceids
    print(choice_id_with_status)
    context['choice_id_with_status'] = choice_id_with_status
    context['score'] = score
    print(score)


    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)


