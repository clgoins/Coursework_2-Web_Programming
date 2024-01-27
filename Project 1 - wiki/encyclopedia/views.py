from django.shortcuts import render
from django.http import HttpResponse
from markdown2 import Markdown
from django.shortcuts import redirect
import random

from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

# when a user wants to view a specific article
def entry(request, entryName):
    
    # 'entry' will grab the body of the article
    entry = util.get_entry(entryName)

    # object to convert from Markdown to HTML
    mdConverter = Markdown()

    # if the article exists, take the user to the articles page
    if entry != None:
        return render(request, "encyclopedia/entry.html", {"entry": mdConverter.convert(entry), "title": entryName})
    # if it does not exist, send them to an error page
    else:
        return render(request, "encyclopedia/error.html")
    
# when a user wants to search for articles
def search(request):
    # contains the search query
    query = request.GET
    # grabs a list of the names of all articles on the site
    entries = util.list_entries()
    # markdown-to-html converter
    mdConverter = Markdown()
    # an empty list of search results
    results = []

    # if no query is provided (for example if the user visits by simply typing "/search" in their address bar) just treat it like an empty results list was passed in
    if not query:
        return render(request, "encyclopedia/search.html", {"query" : []})
    
    # if the query exactly matches an article name (case insensitive), send them straight to that article
    if str.upper(query['q']) in map(str.upper, entries):
        return render(request, "encyclopedia/entry.html", {"entry": mdConverter.convert(util.get_entry(query['q']))})
    
    # if the query doesn't exactly match any existing article, populate results[] with any article that contains the query as a substring in the title, and pass that list along to search.html
    for entry in entries:
        if str.upper(query['q']) in str.upper(entry):
            results.append(entry)
        
    return render(request, "encyclopedia/search.html", {"results" : results})

# when a user wants to create a new article
def newEntry(request):

    # if they visit this page by clicking the link or typing it in their address bar, send them to the "create new entry" page
    if request.method == 'GET':
        return render(request, "encyclopedia/newEntry.html")
    
    # if they got here by POST, i.e. by submitting the form; check the title and make sure there isn't another article by the same name
    articleTitle = request.POST['title']

    # if there is, send them to an error page
    if articleTitle in util.list_entries():
        return render(request, "encyclopedia/pageExists.html")
    # if there isn't, save the article and redirect them to the newly created entry page
    else:
        util.save_entry(request.POST['title'], request.POST['body'])
        return redirect("entry", entryName=request.POST['title'])
    
# when a user wants to edit an existing entry
def editEntry(request, entryName):

    # if they've accessed this page via the link; bring them to the editing form
    if request.method == 'GET':
        return render(request, "encyclopedia/editEntry.html", {'title': entryName, 'bodyText': util.get_entry(entryName)})
    
    # if they've accessed this page by submitting the form, save the entry and redirect them to the newly updated article
    util.save_entry(entryName, request.POST['body'])
    return redirect("entry", entryName=entryName)

# when a user wants a random article
def randomEntry(request):
    # pick a random article title from the list of all articles, and pass it to the 'entry' view
    return redirect("entry", entryName=random.choice(util.list_entries()))