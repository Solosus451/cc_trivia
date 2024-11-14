from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from .models import Question, Leaderboard
from django.contrib import messages
import random


def home(request):
    return render(request, 'trivia/home.html')


def instructions(request):
    return render(request, 'trivia/instructions.html')



def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'trivia/login.html', {'error': 'Credenciales incorrectas'})
    return render(request, 'trivia/login.html')


def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'trivia/register.html', {'form': form})


@login_required
def trivia_game(request):
    if 'lives' not in request.session:
        request.session['lives'] = 3
        request.session['score'] = 0
        request.session['questions_answered'] = 0
        request.session['answered_questions'] = []

    remaining_questions = Question.objects.exclude(id__in=request.session['answered_questions'])
    if not remaining_questions.exists():
        # Finalizar la partida si no hay preguntas restantes
        return redirect('trivia:end_game')

    question = random.choice(remaining_questions)

    if request.method == 'POST':
        selected_answer = request.POST.get('answer')

        if not selected_answer:
            return render(request, 'trivia/game.html', {
                'question': question,
                'error_message': 'Por favor, selecciona una respuesta antes de enviar.'
            })

        selected_answer = selected_answer.strip().lower()
        question_id = int(request.POST.get('question_id'))
        question = Question.objects.get(id=question_id)
        correct_answer = question.correct_answer.strip().lower()

        print(f"Selected answer: {selected_answer}")
        print(f"Correct answer: {correct_answer}")

        if selected_answer == correct_answer:
            request.session['score'] += question.points
            request.session['questions_answered'] += 1
            print("Respuesta correcta")
        else:
            request.session['lives'] -= 1
            print("Respuesta incorrecta")

        if question.id not in request.session['answered_questions']:
            request.session['answered_questions'].append(question.id)
            request.session.modified = True

        print("Preguntas respondidas:", request.session['answered_questions'])

        if request.session['lives'] <= 0:
            return redirect('trivia:end_game')

        remaining_questions = Question.objects.exclude(id__in=request.session['answered_questions'])
        if not remaining_questions.exists():
            return redirect('trivia:end_game')

    context = {
        'question': question,
    }
    return render(request, 'trivia/game.html', context)


@login_required
def end_game(request):
    leaderboard_entry = Leaderboard.objects.create(
        user=request.user,
        score=request.session['score'],
        correct_answers=request.session['questions_answered'],
        incorrect_answers=3 - request.session['lives']
    )
    del request.session['lives']
    del request.session['score']
    del request.session['questions_answered']

    return render(request, 'trivia/end_game.html', {'leaderboard_entry': leaderboard_entry})


@login_required
def leaderboard(request):
    leaderboard_entries = Leaderboard.objects.order_by('-score')[:10]
    return render(request, 'trivia/leaderboard.html', {'leaderboard_entries': leaderboard_entries})
