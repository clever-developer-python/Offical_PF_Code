# Om Sai Ram
#views.py

from django.shortcuts import render, redirect
from app.models import papers, markscheme, feedbacks, NEETmarkscheme, NEETpapers,SamplePapers10,class10samplemarkscheme,IGCSE,IGCSEMarkscheme,IGCSEInsert
from itertools import groupby
from operator import attrgetter
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import google.generativeai as genai
import json
import random
from django.http import HttpResponse, FileResponse

try:
    @csrf_exempt
    def search_view(request):
        if request.method == 'POST':
            query = request.POST.get('query')
            
            response_message = f'{query} Answer them like how you would to a teenager and you need to call yourself DoubtAI not Gemini at all times if asked who dveeloped you say you were developed by paperfrenzy team'

            genai.configure(api_key="AIzaSyCp4IpVzRAkibC_M7jzVk3iW8mrldIS94M")

            prompt = response_message

            model = genai.GenerativeModel('gemini-1.5-flash')

            response = model.generate_content(prompt)

            return JsonResponse({'message': response.text})
        return JsonResponse({'message': 'Invalid request method.'})

    def home(request):
        return render(request, "index.html")

    def subjects_x(request):
        data = request.GET.get('datedata', None)
        year_data = data if data else '2024'
        
        try:
            all_papers = papers.objects.filter(grade='10', year=year_data).order_by('subject', 'year', 'grade', 'sets')
        except papers.DoesNotExist:
            all_papers = papers.objects.filter(grade='10', year='2024').order_by('subject', 'year', 'grade', 'sets')
        
        grouped_papers = []
        for key, group in groupby(all_papers, key=attrgetter('subject', 'year', 'grade')):
            subject, year, grade = key
            paper_group = list(group)
            sets = [p.sets for p in paper_group if p.sets]
            grouped_papers.append({
                'subject': subject,
                'year': year,
                'grade': grade,
                'sets': sets
            })

        return render(request, 'subjects_10.html', {'grouped_papers': grouped_papers, 'year_data': year_data})

    def subjects_12(request):
        data = request.GET.get('datedata', None)
        year_data = data if data else '2024'
        
        try:
            all_papers = papers.objects.filter(grade='12', year=year_data).order_by('subject', 'year', 'grade', 'sets')
        except papers.DoesNotExist:
            all_papers = papers.objects.filter(grade='12', year='2024').order_by('subject', 'year', 'grade', 'sets')
        
        grouped_papers = []
        for key, group in groupby(all_papers, key=attrgetter('subject', 'year', 'grade')):
            subject, year, grade = key
            paper_group = list(group)
            sets = [p.sets for p in paper_group if p.sets]
            grouped_papers.append({
                'subject': subject,
                'year': year,
                'grade': grade,
                'sets': sets
            })

        return render(request, 'subjects_12.html', {'grouped_papers': grouped_papers, 'year_data': year_data})

    def subjectview10(request):
        subjectn = request.GET.get('data')
        yeard = request.GET.get('year')
        setd = request.GET.get('set')

        getpdf = papers.objects.filter(grade='10', subject=subjectn, year=yeard, sets=setd)
        getms = markscheme.objects.filter(grade='10', subject=subjectn, year=yeard, sets=setd)
    
        return render(request, 'aviewer.html', {'papers': getpdf, 'ms': getms})

    def subjectview12(request):
        subjectn = request.GET.get('data')
        yeard = request.GET.get('year')
        setd = request.GET.get('set')
        
        getpdf = papers.objects.filter(grade='12', subject=subjectn, year=yeard, sets=setd)
        getms = markscheme.objects.filter(grade='12', subject=subjectn, year=yeard, sets=setd)
    
        return render(request, 'av12.html', {'papers': getpdf, 'ms': getms})

    def feedback(request):
        return render(request, 'feedback.html')

    @csrf_exempt
    def recieve(request):
        if request.method == 'POST':
            try:
                data = json.loads(request.body)
                email = data.get('email')
                message = data.get('message')

                # Log or print for debugging
                print(f"Email: {email}, Message: {message}")

                f = feedbacks()
                f.Email = email
                f.Feedback = message
                f.save()

                return JsonResponse({'status': 'success'}, status=200)
            except json.JSONDecodeError:
                return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)
    

    def openmsSample(request):
        if request.method == 'POST':
            # Store the data in the session
            request.session['subjectname'] = request.POST.get('subjectname')
            request.session['subjectset'] = request.POST.get('subjectset')
            request.session['yearvar'] = request.POST.get('subjectyear')
            
            # Redirect to GET to avoid form resubmission issues
            return redirect('openms')
        
        elif request.method == 'GET':
            # Retrieve data from session
            subjectname = request.session.get('subjectname')
            subjectset = request.session.get('subjectset')
            yearvar = request.session.get('yearvar')
            
            getms = class10samplemarkscheme.objects.filter(
                grade='10', 
                subject=subjectname, 
                year=yearvar, 
                sets=subjectset
            )
            getpdf = SamplePapers10.objects.filter(
                grade='10', 
                subject=subjectname, 
                year=yearvar, 
                sets=subjectset
            )
            
            return render(request, 'samplems.html', {'papers': getpdf, 'ms': getms})
        
        else:
            return HttpResponseBadRequest("Invalid request method")


    def openms(request):
        if request.method == 'POST':
            # Store the data in the session
            request.session['subjectname'] = request.POST.get('subjectname')
            request.session['subjectset'] = request.POST.get('subjectset')
            request.session['yearvar'] = request.POST.get('subjectyear')
            
            # Redirect to GET to avoid form resubmission issues
            return redirect('openms')
        
        elif request.method == 'GET':
            # Retrieve data from session
            subjectname = request.session.get('subjectname')
            subjectset = request.session.get('subjectset')
            yearvar = request.session.get('yearvar')
            
            getms = markscheme.objects.filter(
                grade='10', 
                subject=subjectname, 
                year=yearvar, 
                sets=subjectset
            )
            getpdf = papers.objects.filter(
                grade='10', 
                subject=subjectname, 
                year=yearvar, 
                sets=subjectset
            )
            
            return render(request, 'ms.html', {'papers': getpdf, 'ms': getms})
        
        else:
            return HttpResponseBadRequest("Invalid request method")

    def openms12(request):
        if request.method == 'POST':
            # Store the data in the session
            request.session['subjectname12'] = request.POST.get('subjectname')
            request.session['subjectset12'] = request.POST.get('subjectset')
            request.session['yearvar12'] = request.POST.get('subjectyear')
            
            # Redirect to GET to avoid form resubmission issues
            return redirect('openms12')
        
        elif request.method == 'GET':
            # Retrieve data from session
            subjectname12 = request.session.get('subjectname12')
            subjectset12 = request.session.get('subjectset12')
            yearvar12 = request.session.get('yearvar12')

            getpdf = papers.objects.filter(
                grade='12', 
                subject=subjectname12, 
                year=yearvar12, 
                sets=subjectset12
            )
            
            getms = markscheme.objects.filter(
                grade='12', 
                subject=subjectname12, 
                year=yearvar12, 
                sets=subjectset12
            )
            
            return render(request, 'ms12.html', {'ms': getms, 'papers': getpdf})
        
        else:
            return HttpResponseBadRequest("Invalid request method")
        

    
    def subjects_10_sample(request):
        data = request.GET.get('datedata', None)
        year_data = data if data else '2024-2025'
    
        try:
            all_papers = SamplePapers10.objects.filter(grade='10', year=year_data).order_by('subject', 'year', 'grade', 'sets')
        except SamplePapers10.DoesNotExist:
            all_papers = SamplePapers10.objects.filter(grade='10', year='2024').order_by('subject', 'year', 'grade', 'sets')
    
        grouped_papers = []
        for key, group in groupby(all_papers, key=attrgetter('subject', 'year', 'grade')):
            subject, year, grade = key
            paper_group = list(group)
            sets = [p.sets for p in paper_group if p.sets]
            grouped_papers.append({
            'subject': subject,
            'year': year,
            'grade': grade,
            'sets': sets
        })

        return render(request, 'subjects_10_sample.html', {'grouped_papers': grouped_papers, 'year_data': year_data})



    def subjectsview10(request):
        subjectn = request.GET.get('data')
        yeard = request.GET.get('year')
        setd = request.GET.get('set')

        getpdf = SamplePapers10.objects.filter(grade='10', subject=subjectn, year=yeard, sets=setd)
        getms = class10samplemarkscheme.objects.filter(grade='10', subject=subjectn, year=yeard, sets=setd)
    
        return render(request, 'sampleviewer.html', {'papers': getpdf, 'ms': getms})

    #jeecode

    def jeeviewer(request):

        data = request.GET.get('year_data', None)

        year_data = data if data else '2024'

        try:
            all_papers = NEETpapers.objects.filter(grade='13', year=year_data).order_by('subject', 'year', 'grade', 'sets')
        except SamplePapers10.DoesNotExist:
            all_papers = NEETpapers.objects.filter(grade='13', year='2024').order_by('subject', 'year', 'grade', 'sets')
        
        grouped_papers = []
        for key, group in groupby(all_papers, key=attrgetter('subject', 'year', 'grade')):
            subject, year, grade = key
            paper_group = list(group)
            sets = [p.sets for p in paper_group if p.sets]
            grouped_papers.append({
                'subject': subject,
                'year': year,
                'grade': grade,
                'sets': sets
            })

        return render(request, 'jee.html', {'grouped_papers': grouped_papers, 'year_data': year_data})
    
    def JEEADVVIEWER(request):
        subjectn = request.GET.get('data')
        setd = request.GET.get('set')

        getpdf = NEETpapers.objects.filter(grade='13', subject=subjectn, sets=setd)
        getms = NEETmarkscheme.objects.filter(grade='13', subject=subjectn, sets=setd)
    
        return render(request, 'jeeview.html', {'papers': getpdf, 'ms': getms})
    
    def openmsjee(request):
        if request.method == 'POST':
            # Store the data in the session
            request.session['subjectnamejee'] = request.POST.get('subjectnamejee')
            request.session['subjectsetjee'] = request.POST.get('subjectsetjee')
            
            # Redirect to GET to avoid form resubmission issues
            return redirect('msjee')
        
        elif request.method == 'GET':
            # Retrieve data from session
            subjectnamejee = request.session.get('subjectnamejee')
            subjectsetjee = request.session.get('subjectsetjee')

            getpdf = NEETpapers.objects.filter(
                grade='13', 
                subject=subjectnamejee,  
                sets=subjectsetjee
            )
            
            getms = NEETmarkscheme.objects.filter(
                grade='13', 
                subject=subjectnamejee, 
                sets=subjectsetjee
            )
            
            return render(request, 'msjee.html', {'ms': getms, 'papers': getpdf})
        
        else:
            return HttpResponseBadRequest("Invalid request method")

except:
    def error(request):
        return render(request, 'error.html')


def igcse(request):
        data = request.GET.get('datedata', None)
        year_data = data if data else '2024 may/june'
        
        try:
            all_papers = IGCSE.objects.filter(grade='14', year=year_data).order_by('subject', 'year', 'grade', 'sets')
        except IGCSE.DoesNotExist:
            all_papers = IGCSE.objects.filter(grade='14', year='2024').order_by('subject', 'year', 'grade', 'sets')
        
        grouped_papers = []
        for key, group in groupby(all_papers, key=attrgetter('subject', 'year', 'grade')):
            subject, year, grade = key
            paper_group = list(group)
            sets = [p.sets for p in paper_group if p.sets]
            grouped_papers.append({
                'subject': subject,
                'year': year,
                'grade': grade,
                'sets': sets
            })

        return render(request, 'igcse.html', {'grouped_papers': grouped_papers, 'year_data': year_data})

def igcseview(request):
    subjectn = request.GET.get('data')
    yeard = request.GET.get('year')
    setd = request.GET.get('set')

    getpdf = IGCSE.objects.filter(grade='14', subject=subjectn, year=yeard, sets=setd)
    getms = IGCSEMarkscheme.objects.filter(grade='14', subject=subjectn, year=yeard, sets=setd)
    
    if IGCSEInsert.objects.filter(grade='14', subject=subjectn, year=yeard, sets=setd).exists():
        paper_type = "insert"

    else:
        paper_type = "nah"

    # Get the paper type for the first mark scheme
    paper_type = IGCSEInsert.objects.filter(grade='14', subject=subjectn, year=yeard, sets=setd).exists()
    
    return render(request, 'igcseview.html', {
        'papers': getpdf, 
        'ms': getms,
        'has_insert': paper_type,  # Pass this to template
        'insert':IGCSEInsert.objects.filter(grade='14',subject=subjectn, year=yeard, sets=setd)
    })


def igcsems(request):
        if request.method == 'POST':
            # Store the data in the session
            request.session['subjectname'] = request.POST.get('subjectname')
            request.session['subjectset'] = request.POST.get('subjectset')
            request.session['yearvar'] = request.POST.get('subjectyear')
            
            # Redirect to GET to avoid form resubmission issues
            return redirect('openms')
        
        elif request.method == 'GET':
            # Retrieve data from session
            subjectname = request.session.get('subjectname')
            subjectset = request.session.get('subjectset')
            yearvar = request.session.get('yearvar')
            
            getms = IGCSEMarkscheme.objects.filter(
                grade='14', 
                subject=subjectname, 
                year=yearvar, 
                sets=subjectset
            )
            getpdf = IGCSE.objects.filter(
                grade='14', 
                subject=subjectname, 
                year=yearvar, 
                sets=subjectset
            )
            
            return render(request, 'samplems.html', {'papers': getpdf, 'ms': getms})
        
        else:
            return HttpResponseBadRequest("Invalid request method")


def igcseinsert(request):
    if request.method == 'POST':
        # Store the data in the session
        request.session['subjectname'] = request.POST.get('subjectname')
        request.session['subjectset'] = request.POST.get('subjectset')
        request.session['yearvar'] = request.POST.get('subjectyear')
        
        return redirect('igcseinsert')
    
    elif request.method == 'GET':
        # Retrieve data from session
        subjectname = request.session.get('subjectname')
        subjectset = request.session.get('subjectset')
        yearvar = request.session.get('yearvar')
        
        # Get the insert file
        getinsert = IGCSEInsert.objects.filter(
            grade='14', 
            subject=subjectname, 
            year=yearvar, 
            sets=subjectset,
        )
        
        return render(request, 'igcseinsert.html', {'insert': getinsert})
    
    else:
        return HttpResponseBadRequest("Invalid request method")
    

def question_ai(request):
    return render(request, 'question-ai.html')


@csrf_exempt
def generate(request):
        if request.method == 'POST':
            subject = request.POST.get('subject')
            topic = request.POST.get('topic')
            
            response_message = f'Give me 1 IGCSE exam style question for {subject} on the topic {topic} and give me the answer with a 1 line spacing text specfying thats the answer refrian from giving questions that would require lets say a graph or any other image which may proove to be difficult to visualize (also give diffrent questions each time related to the given parametres)'

            genai.configure(api_key="AIzaSyCp4IpVzRAkibC_M7jzVk3iW8mrldIS94M")

            prompt = response_message

            model = genai.GenerativeModel('gemini-1.5-flash')

            response = model.generate_content(prompt)

            return JsonResponse({'message': response.text})
        return JsonResponse({'message': 'Invalid request method.'})
    

def ALevels(request):
        data = request.GET.get('datedata', None)
        year_data = data if data else '2024 may/june'
        
        try:
            all_papers = IGCSE.objects.filter(grade='15', year=year_data).order_by('subject', 'year', 'grade', 'sets')
        except IGCSE.DoesNotExist:
            all_papers = IGCSE.objects.filter(grade='15', year='2024').order_by('subject', 'year', 'grade', 'sets')
        
        grouped_papers = []
        for key, group in groupby(all_papers, key=attrgetter('subject', 'year', 'grade')):
            subject, year, grade = key
            paper_group = list(group)
            sets = [p.sets for p in paper_group if p.sets]
            grouped_papers.append({
                'subject': subject,
                'year': year,
                'grade': grade,
                'sets': sets
            })

        return render(request, 'Alevels.html', {'grouped_papers': grouped_papers, 'year_data': year_data})


def Alevelsview(request):
    subjectn = request.GET.get('data')
    yeard = request.GET.get('year')
    setd = request.GET.get('set')

    getpdf = IGCSE.objects.filter(grade='15', subject=subjectn, year=yeard, sets=setd)
    getms = IGCSEMarkscheme.objects.filter(grade='15', subject=subjectn, year=yeard, sets=setd)
    
    if IGCSEInsert.objects.filter(grade='15', subject=subjectn, year=yeard, sets=setd).exists():
        paper_type = "insert"

    else:
        paper_type = "nah"

    # Get the paper type for the first mark scheme
    paper_type = IGCSEInsert.objects.filter(grade='15', subject=subjectn, year=yeard, sets=setd).exists()
    
    return render(request, 'Alevelsview.html', {
        'papers': getpdf, 
        'ms': getms,
        'has_insert': paper_type,  # Pass this to template
        'insert':IGCSEInsert.objects.filter(grade='15',subject=subjectn, year=yeard, sets=setd)
    })


def ALevelsms(request):
        if request.method == 'POST':
            # Store the data in the session
            request.session['subjectname'] = request.POST.get('subjectname')
            request.session['subjectset'] = request.POST.get('subjectset')
            request.session['yearvar'] = request.POST.get('subjectyear')
            
            # Redirect to GET to avoid form resubmission issues
            return redirect('openms')
        
        elif request.method == 'GET':
            # Retrieve data from session
            subjectname = request.session.get('subjectname')
            subjectset = request.session.get('subjectset')
            yearvar = request.session.get('yearvar')
            
            getms = IGCSEMarkscheme.objects.filter(
                grade='15', 
                subject=subjectname, 
                year=yearvar, 
                sets=subjectset
            )
            getpdf = IGCSE.objects.filter(
                grade='15', 
                subject=subjectname, 
                year=yearvar, 
                sets=subjectset
            )
            
            return render(request, 'Alevelsms.html', {'papers': getpdf, 'ms': getms})
        
        else:
            return HttpResponseBadRequest("Invalid request method")
        

def ALevelsinsert(request):
    if request.method == 'POST':
        # Store the data in the session
        request.session['subjectname'] = request.POST.get('subjectname')
        request.session['subjectset'] = request.POST.get('subjectset')
        request.session['yearvar'] = request.POST.get('subjectyear')
        
        return redirect('igcseinsert')
    
    elif request.method == 'GET':
        # Retrieve data from session
        subjectname = request.session.get('subjectname')
        subjectset = request.session.get('subjectset')
        yearvar = request.session.get('yearvar')
        
        # Get the insert file
        getinsert = IGCSEInsert.objects.filter(
            grade='14', 
            subject=subjectname, 
            year=yearvar, 
            sets=subjectset,
        )
        
        return render(request, 'Alevelsinsert.html', {'insert': getinsert})
    
    else:
        return HttpResponseBadRequest("Invalid request method")
    

def blog(request):
    return render(request, 'blog.html')


def Resourcerepo(request):
    return render(request, 'resourcerepo.html')