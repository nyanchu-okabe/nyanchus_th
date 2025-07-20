from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
from .models import Thread, Comment, User
from .forms import ThreadForm, UserCreationForm, LoginForm
import datetime

def index(request):
    threads = Thread.objects.all()
    username = ""  # デフォルト値

    # セッションから user_id を取得する場合
    user_id = request.session.get('user_id')
    if user_id:
        try:
            user = User.objects.get(id=user_id)
            username = user.username  # 変数名を統一
        except User.DoesNotExist:
            username = "Unknown"  # ユーザーが見つからない場合
            # オプション: 無効なセッションをクリア
            request.session.pop('user_id', None)

    # 代替: ログイン中のユーザーから取得（推奨）
    if request.user.is_authenticated:
        username = request.user.username

    return render(request, 'app/index.html', {
        'threads': threads,
        'username': username
    })


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful. You can now log in.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'app/signup.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            try:
                user = User.objects.get(username=username)
                if user.check_password(password):
                    request.session.flush() # Clear the old session data
                    request.session['user_id'] = user.id
                    messages.success(request, 'Logged in successfully.')
                    return redirect('index')
                else:
                    messages.error(request, 'Invalid username or password.')
            except User.DoesNotExist:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'app/login.html', {'form': form})

def user_logout(request):
    if 'user_id' in request.session:
        del request.session['user_id']
        messages.success(request, 'Logged out successfully.')
    return redirect('index')

def board_detail(request, slug):
    thread = get_object_or_404(Thread, slug=slug)

    # セッションで認証済みか確認
    authenticated_threads = request.session.get('authenticated_threads', [])
    if thread.id not in authenticated_threads:
        # パスワードが設定されているスレッドの場合、パスワード確認ページへ
        if thread.password:
            messages.error(request, "This board is password protected. Please enter the password.")
            return redirect('pass_check', slug=slug)

    # コメント投稿処理
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            user_id = request.session.get('user_id')
            if user_id:
                user = User.objects.get(id=user_id)
                comment = Comment.objects.create(thread=thread, content=content, user=user)
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
                        'content': comment.content,
                        'created_at': comment.created_at.strftime('%Y/%m/%d %H:%M:%S'),
                        'username': user.username
                    })
                return redirect('board_detail', slug=slug)
            else:
                messages.error(request, "You must be logged in to post a comment.")
                return redirect('login')

    comments = thread.comments.all()
    last_timestamp = comments.last().created_at.isoformat() if comments else None
    context = {
        'thread': thread,
        'comments': comments,
        'board_slug': slug,
        'last_timestamp': last_timestamp,
        'current_user': request.session.get('user_id')
    }
    return render(request, 'app/board.html', context)


def fetch_updates(request, slug):
    if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'error': 'Invalid request'}, status=400)

    thread = get_object_or_404(Thread, slug=slug)
    last_timestamp = request.GET.get('last_timestamp')

    if last_timestamp:
        try:
            last_timestamp = datetime.datetime.fromisoformat(last_timestamp)
            comments = thread.comments.filter(created_at__gt=last_timestamp)
        except ValueError:
            return JsonResponse({'error': 'Invalid timestamp format'}, status=400)
    else:
        comments = thread.comments.all()

    new_comments = [
        {
            'content': comment.content,
            'created_at': comment.created_at.strftime('%Y/%m/%d %H:%M:%S'),
            'username': comment.user.username if comment.user else 'Anonymous'
        }
        for comment in comments
    ]

    return JsonResponse({'comments': new_comments})


def create_board(request):
    if request.method == 'POST':
        form = ThreadForm(request.POST)
        if form.is_valid():
            thread = form.save()

            # パスワード付きで作成した場合、セッションに認証済みスレッドとして記録
            if thread.password:
                authenticated_threads = request.session.get('authenticated_threads', [])
                if thread.id not in authenticated_threads:
                    authenticated_threads.append(thread.id)
                    request.session['authenticated_threads'] = authenticated_threads

            return redirect('board_detail', slug=thread.slug)
    else:
        form = ThreadForm()

    context = {
        'form': form
    }
    return render(request, 'app/create_board.html', context)


def pass_check(request, slug):
    thread = get_object_or_404(Thread, slug=slug)
    if request.method == 'POST':
        password = request.POST.get('password', '')

        # パスワードを検証
        if check_password(password, thread.password):
            # セッションに認証済みスレッドIDを保存
            authenticated_threads = request.session.get('authenticated_threads', [])
            if thread.id not in authenticated_threads:
                authenticated_threads.append(thread.id)
                request.session['authenticated_threads'] = authenticated_threads
            return redirect('board_detail', slug=slug)
        else:
            messages.error(request, "Incorrect password.")

    return render(request, 'app/pass_check.html', {'slug': slug})
