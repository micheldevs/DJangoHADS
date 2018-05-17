"""
Definition of views.
"""

from django.shortcuts import render,get_object_or_404
from django.http import HttpRequest
from django.template import RequestContext
from datetime import datetime
from django.http.response import HttpResponse, Http404
from django.http import HttpResponseRedirect, HttpResponse
from .models import Question,Choice,User
from django.template import loader
from django.core.urlresolvers import reverse
from app.forms import QuestionForm, ChoiceForm,UserForm
from django.shortcuts import redirect
import json


def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/index.html',
        {
            'title':'Home Page',
            'year':datetime.now().year,
        }
    )

def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/contact.html',
        {
            'title':'Autores de la web',
            'message':'Datos de los contactos',
            'year':datetime.now().year,
        }
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        {
            'title':'About',
            'message':'Your application description page.',
            'year':datetime.now().year,
        }
    )
def index(request):
    latest_question_list = Question.objects.order_by('question_topic').values_list('question_topic', flat=True).distinct()
    template = loader.get_template('polls/index.html')
    context = {
                'title':'Lista de temas de las encuestas',
                'latest_question_list': latest_question_list,
              }
    return render(request, 'polls/index.html', context)

def topic(request, topic):
    question_list = Question.objects.filter(question_topic = topic)
    template = loader.get_template('polls/topic.html')
    context = {
                'title':'Lista de preguntas del tema ' + topic,
                'question_list': question_list,
              }
    return render(request, 'polls/topic.html', context)

def detail(request, question_id):
     question = get_object_or_404(Question, pk=question_id)
     return render(request, 'polls/detail.html', {'title':'Respuestas asociadas a la pregunta:','question': question})

def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/results.html', {'title':'Resultados de la pregunta:','question': question})

def vote(request, question_id):
    p = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = p.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Vuelve a mostrar el form.
        return render(request, 'polls/detail.html', {
            'question': p,
            'error_message': "ERROR: No se ha seleccionado una opcion",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Siempre devolver un HttpResponseRedirect despues de procesar
        # exitosamente el POST de un form. Esto evita que los datos se
        # puedan postear dos veces si el usuario vuelve atras en su browser.
        return HttpResponseRedirect(reverse('results', args=(p.id,)))

def question_new(request):
    try:
        if request.method == "POST":
            form = QuestionForm(request.POST)
            if form.is_valid():
                question = form.save(commit=False)
                question.pub_date=datetime.now()
                question.save()
                #return redirect('detail', pk=question_id)
                #return render(request, 'polls/index.html', {'title':'Respuestas posibles','question': question})
                return render(request, 'polls/question_new.html', {
                    'form': form,
                    'sucess_message': "¡Pregunta insertada correctamente!",
                })
        else:
            form = QuestionForm()
        return render(request, 'polls/question_new.html', {'form': form,})
    except Exception as e: 
        #El control de que las opciones sean de 2 o 4 respuestas está realizado en la base de datos, esta parte se ejecutará cuando se detecte error operacional.
        # Vuelve a mostrar el form.
        return render(request, 'polls/question_new.html', {
            'form': form,
            'error_message': "ERROR: El número de respuestas debe ser 2 o 4 y la respuesta correcta no debe pasarse del rango del tipo máximo.",
        })

def choice_add(request, question_id):
        question = Question.objects.get(id = question_id)
        cresponse = question.correct_response
        try:
            numch = Choice.objects.filter(question_id = question_id).count()
        except Choice.DoesNotExist as e: #Por si no se ha creado respuesta anteriormente para la pregunta.
            info_question = "Esta pregunta admite " + str(question.choice_max) + " respuestas. Actualmente no hay ninguna respuesta escrita."

            if cresponse==1:
                info_message = "La respuesta que escriba a continuación será la respuesta correcta de la pregunta."
            else:
                info_message = "Esta respuesta será incorrecta. La respuesta correcta será la respuesta número " + str(cresponse) + "."

            if request.method =='POST':
                form = ChoiceForm(request.POST)
                if form.is_valid():
                    choice = form.save(commit = False)
                    choice.question = question
                    choice.vote = 0
                    choice.save()
                    #form.save()
                    return render(request, 'polls/choice_new.html', {'title':'Pregunta:'+ question.question_text,
                        'form': form,
                        'info_question': info_question,
                        'info_message': info_message,
                        'sucess_message': "¡Respuesta insertada correctamente a la pregunta " + str(question_id) + "!",
                    })
            else: 
                form = ChoiceForm()

            return render(request, 'polls/choice_new.html', {'title':'Pregunta:'+ question.question_text,
                'form': form,
                'info_question': info_question,
                'info_message': info_message,
            })

        if(numch+1>question.choice_max):
            info_question = "Esta pregunta no admite más respuestas. Su límite de respuestas es de " + str(question.choice_max) + " respuestas."
            info_message = ""
        else:
            if cresponse==numch+1:
                info_message = "La respuesta que escriba a continuación será la respuesta correcta de la pregunta."
            else:
                info_message = "Esta respuesta será incorrecta. La respuesta correcta será la respuesta número " + str(cresponse) + "."

            info_question = "Esta pregunta admite " + str(question.choice_max) + " respuestas. Actualmente hay escritas " + str(numch) + " respuesta/s." 

        if request.method =='POST':
            form = ChoiceForm(request.POST)
            if form.is_valid():
                if(numch+1<=question.choice_max):
                    choice = form.save(commit = False)
                    choice.question = question
                    choice.vote = 0
                    choice.save()
                    #form.save()
                    return render(request, 'polls/choice_new.html', {'title':'Pregunta:'+ question.question_text,
                        'form': form,
                        'info_question': info_question,
                        'info_message': info_message,
                        'sucess_message': "¡Respuesta insertada correctamente a la pregunta " + str(question_id) + "!",
                    })
                else:
                    return render(request, 'polls/choice_new.html', {
                        'form': form,
                        'info_question': info_question,
                        'info_message': info_message,
                        'error_message': "ERROR: El número de respuestas no debe pasarse de las opciones declaradas en la pregunta.",
                    })
        else: 
            form = ChoiceForm()

        #return render_to_response ('choice_new.html', {'form': form, 'poll_id': poll_id,}, context_instance = RequestContext(request),)

        return render(request, 'polls/choice_new.html', {'title':'Pregunta:'+ question.question_text,
            'form': form,
            'info_question': info_question,
            'info_message': info_message,
        })

def chart(request, question_id):
    q=Question.objects.get(id = question_id)
    qs = Choice.objects.filter(question=q)
    dates = [obj.choice_text for obj in qs]
    counts = [obj.votes for obj in qs]
    context = {
        'dates': json.dumps(dates),
        'counts': json.dumps(counts),
    }

    return render(request, 'polls/grafico.html', context)

def user_new(request):
        if request.method == "POST":
            form = UserForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                user.save()
                #return redirect('detail', pk=question_id)
                #return render(request, 'polls/index.html', {'title':'Respuestas posibles','question': question})
        else:
            form = UserForm()
        return render(request, 'polls/user_new.html', {'form': form})

def users_detail(request):
    latest_user_list = User.objects.order_by('email')
    template = loader.get_template('polls/users.html')
    context = {
                'title':'Lista de usuarios',
                'latest_user_list': latest_user_list,
              }
    return render(request, 'polls/users.html', context)