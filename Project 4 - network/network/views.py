import json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core import serializers

from .models import *
from django.shortcuts import redirect
from datetime import datetime


def index(request):

    if(request.method == "POST"):
        newPost = Post(user_id=request.user, post=request.POST['body'], timestamp=datetime.now(), fmtTime=datetime.now().strftime("%b %d %Y, %I:%M%p"))
        newPost.save()

    # Get list of all posts
    posts = Post.objects.all().order_by('-timestamp')

    # Set up pagination
    paginator = Paginator(posts, 10)
    page = request.GET.get('page')
    pagedPosts = paginator.get_page(page)

    return render(request, "network/index.html", {'posts':pagedPosts})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


def profile(request, userProfile):
    # Grab a list of every post made by the user whose profile you're visiting
    posts = Post.objects.filter(user_id=User.objects.get(username=userProfile)).order_by('-timestamp')

    # Paginate posts
    p = Paginator(posts, 10)
    page = request.GET.get('page')
    pagedPosts = p.get_page(page)

    # Grab the number of followers this user has, and the number of people they're following
    followers = Follow.objects.filter(following_id=User.objects.get(username=userProfile)).count()
    following = Follow.objects.filter(follower_id=User.objects.get(username=userProfile)).count()

    # Checks if the logged in user is following this user
    if(request.user.is_authenticated):
        currentlyFollowingUser = Follow.objects.filter(follower_id = request.user, following_id = User.objects.get(username=userProfile)).exists()
    else:
        currentlyFollowingUser = False

    return render(request, "network/profile.html", {'userProfile':userProfile, 'posts':pagedPosts, 'followers':followers, 'following':following, 'currentlyFollowingUser':currentlyFollowingUser})


@login_required
def following(request):
    
    # Generate the list Follow relationships where the signed in user is following someone else
    follows = Follow.objects.filter(follower_id=request.user)
    
    # Empty list of posts to display
    posts = []

    # For each relationship, look at the user who is being followed and get the list of every post they've made
    for follow in follows:
        userPosts = Post.objects.filter(user_id = follow.following_id)

        # Add each Post to this list, then move on to the next User
        for userPost in userPosts:
            posts.append(userPost)

    # Sort the list by timestamp
    posts.sort(reverse=True, key=Post.sortCriteria)

    # Set up pagination
    p = Paginator(posts, 10)
    page = request.GET.get('page')
    pagedPosts = p.get_page(page)

    return render(request, "network/following.html", {'posts':pagedPosts})




# Functions used for API requests

# Creates a new 'follow' entry in the db
def follow(request):

    # Request MUST be via POST
    if(request.method == "POST"):

        # Grab the json data out of the POST request
        data = json.loads(request.body)

        # Check if the Follow entry already exists. Send a failure message and do nothing if so. Otherwise; create and save a Follow entry, and send a success message.
        if(Follow.objects.filter(follower_id = request.user, following_id = User.objects.get(username=data.get('userToFollow'))).exists()):
           return JsonResponse({'message' : 'entry already exists'}, status=400)
        else:
            newFollowRequest = Follow(follower_id=request.user, following_id=User.objects.get(username=data.get('userToFollow')))
            newFollowRequest.save()

        return JsonResponse({'message':'success'})
    
    else:
        return JsonResponse({'message' : 'invalid request method'}, status=405)


# Removes a 'follow' entry from the db
def unfollow(request):

    # Request MUST be via POST
    if(request.method == 'POST'):
        
        # Grab the json data out of the POST request
        data = json.loads(request.body)

        # Check that the Follow entry exists. If so, delete the entry and return a success message. Otherwise, send a failure message and do nothing.
        if(Follow.objects.filter(follower_id = request.user, following_id = User.objects.get(username=data.get('userToFollow'))).exists()):
            Follow.objects.get(follower_id = request.user, following_id = User.objects.get(username=data.get('userToFollow'))).delete()
            return JsonResponse({'message' : 'success'})
        else:
            return JsonResponse({'message' : 'entry does not exist'}, status=400)
        
    else:
        return JsonResponse({'message' : 'invalid request method'}, status=405)


# Creates or removes a 'Like' entry from the db
def like(request):

    # Request MUST be via POST
    if(request.method == 'POST'):
        
        #grab the json data
        data = json.loads(request.body)

        # if a 'like' entry between this post and the logged in user exists, delete it, otherwise create one
        if(Like.objects.filter(user_id=request.user, post_id=Post.objects.get(id=data.get('id'))).exists()):
            Like.objects.get(user_id=request.user, post_id=Post.objects.get(id=data.get('id'))).delete()
            return JsonResponse({'message' : 'success'})
        else:
            newLike = Like(user_id=request.user, post_id=Post.objects.get(id=data.get('id')))
            newLike.save()
            return JsonResponse({'message' : 'success'})

    else:
        return JsonResponse({'message' : 'invalid request method'}, status=405)


# Grabs a single post by ID. GET to read a post, POST to create/modify
def post(request):
    if request.method == "GET":
        post = Post.objects.get(id=request.GET.get('id'))

        # grabs a serialized version of a Post object to add a little data to and return as a JSON object
        postDict = post.serialize()
        postDict['likeCount'] = Like.objects.filter(post_id = post).count()

        # Adds a boolean thats = True if the signed in user has liked the post, and false otherwise
        if(Like.objects.filter(post_id = post, user_id = request.user).exists()):
            postDict['liked'] = True
        else:
            postDict['liked'] = False

        return JsonResponse(postDict)
    

    elif request.method == "POST":
        data = json.loads(request.body)

        # Check to make sure the post exists, and grab it from the DB if so
        if(Post.objects.filter(id=data['id']).exists()):
            postToEdit = Post.objects.get(id=data['id'])

            # VERY IMPORTANT; MAKE SURE the logged in user is the author of the post before making ANY changes to it
            if(postToEdit.user_id == request.user):
                postToEdit.post = data['body']
                postToEdit.save()
                return JsonResponse({'message' : 'success'})
            else:
                return JsonResponse({'message' : 'failed to edit post'}, status=401)

            
        else:
            return JsonResponse({'message' : 'invalid post id'})

        


    else:
        return JsonResponse({'message' : 'invalid request method'}, status=405)
 

# Takes a list of PostID's, counts the number of likes on each post, and returns a list of counts to the page
def getLikeCount(request):
    if request.method == "POST":
        data = json.loads(request.body)
        postIDs = data.get('postIDs')
        
        # will contain a list of dictionary objects, each holding a post id, a tally of the number of likes on the post, and a boolean to represent whether the signed in user has "liked" the post
        likeList = []

        for id in postIDs:
            dict = {}
            dict['id'] = id
            dict['likeCount'] = Like.objects.filter(post_id = Post.objects.get(id=id)).count()
            dict['liked'] = Like.objects.filter(user_id = request.user, post_id = Post.objects.get(id=id)).exists()
            likeList.append(dict)

        return JsonResponse(likeList, safe=False)


    else:
        return JsonResponse({'message' : 'invalid request method'}, status=405)


