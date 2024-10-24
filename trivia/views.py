from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from .models import Question, Leaderboard
import random


def home(request):
    return render(request, 'trivia/home.html')


def instructions(request):
    return render(request, 'trivia/instructions.html')


# Vista para el login (login.html)
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


# Vista para el registro (register.html)
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirige al login después del registro exitoso
    else:
        form = UserCreationForm()
    return render(request, 'trivia/register.html', {'form': form})


@login_required
def trivia_game(request):
    if 'lives' not in request.session:
        request.session['lives'] = 3
        request.session['score'] = 0
        request.session['questions_answered'] = 0

    if request.method == 'POST':
        selected_answer = request.POST.get(
            'answer').strip().lower()  # Respuesta seleccionada (ahora es "a", "b", "c" o "d")
        question_id = request.POST.get('question_id')
        question = Question.objects.get(id=question_id)

        correct_answer = question.correct_answer.strip().lower()  # La respuesta correcta almacenada en la base de datos ("a", "b", "c" o "d")

        # Depuración: Ver qué respuestas estamos comparando
        print(f"Selected answer: {selected_answer}")
        print(f"Correct answer: {correct_answer}")

        if selected_answer == correct_answer:
            request.session['score'] += question.points
            request.session['questions_answered'] += 1
            print("Respuesta correcta")
        else:
            request.session['lives'] -= 1
            print("Respuesta incorrecta")

        if request.session['lives'] <= 0:
            return redirect('trivia:end_game')

    # Obtener una pregunta aleatoria
    questions = Question.objects.all()
    question = random.choice(questions)

    context = {
        'question': question,
    }
    return render(request, 'trivia/game.html', context)


@login_required
def end_game(request):
    # Guardar el puntaje en el ranking
    leaderboard_entry = Leaderboard.objects.create(
        user=request.user,
        score=request.session['score'],
        correct_answers=request.session['questions_answered'],
        incorrect_answers=3 - request.session['lives']
    )
    # Resetear sesión
    del request.session['lives']
    del request.session['score']
    del request.session['questions_answered']

    return render(request, 'trivia/end_game.html', {'leaderboard_entry': leaderboard_entry})


@login_required
def leaderboard(request):
    leaderboard_entries = Leaderboard.objects.order_by('-score')[:10]
    return render(request, 'trivia/leaderboard.html', {'leaderboard_entries': leaderboard_entries})
