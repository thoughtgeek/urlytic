from django.shortcuts import render
from home.models import Document

def filedetail(request):
    filename = request.GET.get('filename')
    documents = Document.objects.filter(upload=filename)
    return render(request, 'filedetail/filedetail.html', {
            'documents':documents,
            'filename':filename,
        })