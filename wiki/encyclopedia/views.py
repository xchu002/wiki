import imp
from re import I
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from markdown import markdown2
from django import forms
from django.shortcuts import redirect
from . import util
from random import randint

class searchForm(forms.Form):
    searchedItem = forms.CharField(label="Search")    


def search(request):
    if request.method == "POST":
        form = searchForm(request.POST)
        if form.is_valid():
            item = form.cleaned_data["searchedItem"]
            if util.get_entry(item):
                return redirect(f'/{item}/')
            else:
                existingEntries = util.list_entries()
                newlist = []
                errormsg = ""
                for entry in existingEntries:
                    if item.upper() in entry.upper():
                        newlist.append(entry)
                if len(newlist) == 0:
                    errormsg = "We couldn't find your search."
            
                return render(request, "encyclopedia/search.html",{
                    "form": searchForm(),
                    "newlist": newlist,
                    "item": item,
                    "errormsg": errormsg
                })
                

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "form": searchForm()
    })

def entry(request, title):
    mdfile = util.get_entry(title)
    if mdfile:
        mdfile = markdown2.markdown(mdfile)
        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "mdfile": mdfile,
            "form": searchForm()
        })
         
    else:
        return render(request, "encyclopedia/entry.html", {
            "title": title + " was not found. Did you type in correctly?",
            "form": searchForm()
        })


class newTitleForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={"placeholder":"Title", 'style':'width:300px', 'class':'form-control'}))
class newContentForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea(attrs={"placeholder":"Content", 'style':'width:600px', 'class':'form-control'}))

def newpage(request):
    title = ""
    content = ""
    if request.method == "POST":
        filledTitleForm = newTitleForm(request.POST)
        filledContentForm = newContentForm(request.POST)
        if filledTitleForm.is_valid():
            title = filledTitleForm.cleaned_data["title"]
        if filledContentForm.is_valid():
            content = filledContentForm.cleaned_data["content"] 
            util.save_entry(title, content)
            return HttpResponseRedirect(reverse('encyclopedia:index'))
                                                                    

    return render(request, "encyclopedia/newpage.html", {
        "form": searchForm(),
        "titleForm": newTitleForm(),
        "contentForm": newContentForm(),
    })

class editForm(forms.Form):
    Content = forms.CharField(widget=forms.Textarea(attrs={"placeholder":"Content", 'style':'width:600px', 'class':'form-control'}))

def edit(request, title):    
    mdcontent = util.get_entry(title)
    if request.method == "POST":
        form = editForm(request.POST)
        if form.is_valid():
            editedContent = form.cleaned_data["Content"]
            util.save_entry(title, editedContent)
            return HttpResponseRedirect(reverse("encyclopedia:index"))
    return render(request, "encyclopedia/edit.html", {
        "title": title,
        "form": searchForm(),
        "editForm": editForm(initial={"Content": mdcontent})
    }) 

def random(request):
    all_entries = util.list_entries()
    number = randint(0, len(all_entries) - 1)
    chosen_entry = all_entries[number]
    return redirect(f'/{chosen_entry}/')
    