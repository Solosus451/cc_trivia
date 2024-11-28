# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Question, Answer, Game
import random


def home(   request):
    return render(request, 'trivia/home.html')


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)  # Inicia sesión automáticamente después de registrarse
            return redirect('trivia:trivia')  # Redirigir directamente a la parte de trivia
    else:
        form = UserCreationForm()
    return render(request, 'trivia/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('trivia:trivia')  # Redirigir a trivia después de iniciar sesión
    else:
        form = AuthenticationForm()
    return render(request, 'trivia/login.html', {'form': form})

@login_required(login_url='login')
def instructions_view(request):
    if request.method == 'POST':
        user = request.user
        # El juego empieza con puntaje 0 y 3 vidas
        game = Game.objects.create(user=user, score=0, lives=3)
        return redirect('trivia:play_game', game_id=game.id)
    return render(request, 'trivia/instructions.html')


@login_required(login_url='login')
def start_game(request):
    # El juego empieza con puntaje 0 y 3 vidas
    user = request.user
    game = Game.objects.create(user=user, score=0, lives=3)
    return redirect('trivia:play_game', game_id=game.id)

# Inicia el juego
@login_required(login_url='login')
def play_game(request, game_id):
    game = get_object_or_404(Game, id=game_id, user=request.user)

    # Ordena las preguntas que todavia no se respoden
    answered_question_ids = game.answers.values_list('question__id', flat=True)
    question = Question.objects.exclude(id__in=answered_question_ids).order_by('?').first()

    # para cuando se acaben las preguntas te tira a la pantalla principal
    if not question or game.lives <= 0:
        return redirect('trivia:game_over', game_id=game.id)

    if request.method == 'POST':
        selected_option = request.POST.get('option')

        if not selected_option:
            messages.error(request, 'Por favor selecciona una respuesta antes de continuar.')
            return redirect('trivia:play_game', game_id=game.id)

        if selected_option == question.correct_answer:
            game.score += 1  # puntaje+ pregunta buena
        else:
            game.lives -= 1  # puntaje- pregunta mala (medio obvio)
        game.save()

        # guarda la respuesta en la tabla de preguntas
        Answer.objects.create(game=game, question=question, selected_answer=selected_option, user=request.user)


        return redirect('trivia:play_game', game_id=game.id)

    context = {
        'game': game,
        'question': question,
    }
    return render(request, 'trivia/game.html', context)


# Game Over
@login_required(login_url='login')
def game_over(request, game_id):
    game = get_object_or_404(Game, id=game_id, user=request.user)
    context = {
        'final_score': game.score,
        'total_questions': game.answers.count(),
    }
    return render(request, 'trivia/game_over.html', context)

