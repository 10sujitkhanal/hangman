import random
import string
from django.shortcuts import render, redirect
from .models import Word
from .forms import UploadCSVForm
from io import TextIOWrapper
import csv

MAX_GUESSES = 6

def initialize_game(session):
    available_words = list(Word.objects.filter(is_solved=False))

    if not available_words:
        session['word_text'] = None
        session['game_over'] = True
        session['message'] = "All words have been solved! Please ask an administrator to reset words."
        return
    
    word_obj = random.choice(available_words)
    word_text = word_obj.text.upper()

    session['word_id'] = word_obj.id
    session['word_text'] = word_text
    session['guessed_letters'] = []
    session['guesses_left'] = MAX_GUESSES
    session['display_word'] = ['_'] * len(word_text)
    session['game_over'] = False
    session['message'] = "Guess a letter!"
    session['win'] = False
    session['word_suggestions'] = word_obj.suggestions

def hangman_game(request):
    if 'word_text' not in request.session or request.GET.get('reset'):
        initialize_game(request.session)

    word_id = request.session.get('word_id')
    word_text = request.session.get('word_text')
    guessed_letters = request.session.get('guessed_letters', [])
    guesses_left = request.session.get('guesses_left', MAX_GUESSES)
    display_word = request.session.get('display_word', [])
    game_over = request.session.get('game_over', False)
    message = request.session.get('message', "Guess a letter!")
    win = request.session.get('win', False)
    word_suggestions = request.session.get('word_suggestions', '')
    

    if word_text is None and game_over:
        context = {
            'game_over': True,
            'message': message,
            'alphabet': string.ascii_uppercase,
            'guessed_letters': guessed_letters,
            'guesses_left_image_idx': MAX_GUESSES - guesses_left,
            'word_suggestions': word_suggestions
        }
        return render(request, 'game/hangman.html', context)

    if request.method == 'POST' and not game_over:
        guess = request.POST.get('guess', '').upper()

        if not guess.isalpha() or len(guess) != 1:
            message = "Please enter a single letter (A-Z)."
        elif guess in guessed_letters:
            message = f"You already guessed '{guess}'. Try another."
        else:
            guessed_letters.append(guess)
            request.session['guessed_letters'] = guessed_letters

            if guess in word_text:
                message = f"'{guess}' is correct!"
                for i, char in enumerate(word_text):
                    if char == guess:
                        display_word[i] = guess
                request.session['display_word'] = display_word
                

                if '_' not in display_word:
                    message = f"Congratulations! You've guessed the word: {word_text}!"
                    game_over = True
                    win = True

                    if word_id:
                        try:
                            solved_word_obj = Word.objects.get(id=word_id)
                            solved_word_obj.is_solved = True
                            solved_word_obj.save()
                        except Word.DoesNotExist:
                            pass
            else:
                guesses_left -= 1
                request.session['guesses_left'] = guesses_left
                message = f"'{guess}' is not in the word."

                if guesses_left == 0:
                    message = f"Game Over! The word was '{word_text}'."
                    game_over = True
                    win = False
        
        request.session['game_over'] = game_over
        request.session['message'] = message
        request.session['win'] = win

    context = {
        'display_word': " ".join(display_word),
        'guesses_left': guesses_left,
        'max_guesses': MAX_GUESSES,
        'guessed_letters': guessed_letters,
        'message': message,
        'game_over': game_over,
        'win': win,
        'alphabet': string.ascii_uppercase,
        'word': word_text if game_over else None,
        'guesses_left_image_idx': MAX_GUESSES - guesses_left ,
        'incorrect_guesses_count': MAX_GUESSES - guesses_left,
        'word_suggestions': word_suggestions
    }
    return render(request, 'game/hangman.html', context)

def reset_game(request):
    request.session.clear()
    return redirect('hangman_game')


def upload_csv(request):
    Word.objects.all().delete()

    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('hangman_game')

    if request.method == "POST":
        form = UploadCSVForm(request.POST, request.FILES)
        if form.is_valid():
            file = TextIOWrapper(request.FILES['file'].file, encoding='utf-8')
            reader = csv.DictReader(file)

            for row in reader:
                text = row['text'].strip().lower()  # Normalize input
                # Skip if the word already exists (case-insensitive)
                if not Word.objects.filter(text__iexact=text).exists():
                    Word.objects.create(
                        text=text,
                        suggestions=row['suggestions']
                    )

            return redirect('upload_success')
    else:
        form = UploadCSVForm()

    return render(request, 'upload_csv.html', {'form': form})

def upload_success(request):
    return render(request, 'upload_success.html')