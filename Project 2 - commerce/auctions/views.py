from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import *


def index(request):
    listings=Listing.objects.filter(open=True)
    return render(request, "auctions/index.html", {"listings":listings})


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
            return render(request, "auctions/login.html", {
                "redMessage": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


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
            return render(request, "auctions/register.html", {
                "redMessage": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "redMessage": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required
def new(request):

    # grab a list of categories for the new listing form
    categories = Category.objects.all()

    if request.method == "GET":
        return render(request, "auctions/newListing.html", {"categories":categories})
    
    # if user submitted a new listing form:
    else:
        # make sure the user supplied the required fields (title, description, and starting bid)
        if(request.POST['title'] == ""):
            return render(request, "auctions/newListing.html", {"categories":categories, "redMessage":"'Listing Title' is a required field."})
        
        if(request.POST['description'] == ""):
            return render(request, "auctions/newListing.html", {"categories":categories, "redMessage":"'Description' is a required field."})
        
        if(request.POST['startingBid'] == ""):
            return render(request, "auctions/newListing.html", {"categories":categories, "redMessage":"'Starting Bid' is a required field."})

        # make sure the title doesn't already match another listing
        if(Listing.objects.filter(title=request.POST["title"])):
            return render(request, "auctions/newListing.html", {"categories":categories, "redMessage":"A listing by this name already exists."})

        # make sure the starting bid is a valid number
        try:
            startingBid = float(request.POST["startingBid"])
        except ValueError:
            return render(request, "auctions/newListing.html", {"categories":categories, "redMessage":"Starting bid is not a valid amount."})

        if startingBid < 0.01:
            return render(request, "auctions/newListing.html", {"categories":categories, "redMessage":"Starting bid is not a valid amount."})
        
        # truncate the starting bid down to just two digits after the decimal place
        startingBid = int(startingBid * 100)
        startingBid = float(startingBid / 100)

        # create the listing and redirect to the home page
        newListing = Listing(title=request.POST["title"], description=request.POST["description"], startingBid=startingBid, open=True, creator_id=request.user, image=request.POST["imgURL"], category_id=Category.objects.filter(category=request.POST['category']).first())
        newListing.save()
        return redirect(index)
    

def listing(request, listingName):
    # gets all the info about the listing from the db
    listing = Listing.objects.get(title = listingName)

    # get the listings current price. Will be either the starting bid or the most recent bid placed on the item
    currentBid = listing.price.last()

    # grab a list of comments that have been posted on the listing
    comments = Comment.objects.filter(listing_id=listing)


    # the user can get here via form submittal, either by placing a bid, adding an item to their watchlist, by closing the auction, or by leaving a comment
    if request.method == "POST":
        
        # if a 'bid' item exists in the POST data, validate the input and create the bid in the database
        if('bid' in request.POST):
            # first make sure the bid is a valid number
            try:
                bid = float(request.POST['bid'])
            except ValueError:
                # render the page with an error if it is not
                return render(request, "auctions/listing.html", {"listing":listing, "price":currentBid, "comments":comments, "redMessage":"Invalid bid entered"})

            # multiply bid by 100, cast it to an int, and then reverse the two operations. This should truncate the value down to two decimal places.
            # I want to truncate instead of rounding. I don't like the idea of Python automatically rounding a number up when we're hypotheically dealing with someone else's money, even if it's just a penny.
            bid = int(bid * 100)
            bid = float(bid / 100)

            # make sure the bid is at least == the starting bid, and is greater than any other bids placed
            if((not currentBid and bid < listing.startingBid) or (currentBid and bid <= currentBid.bid)):
                # render page with an error if the bid isn't high enough
                return render(request, "auctions/listing.html", {"listing":listing, "price":currentBid, "comments":comments, "redMessage":"Bid must be higher than the current price"})
            else:
                # if the bid is good, add it to the db, and render the page with the new bid, and a green success message
                newBid = Bid(listing_id=listing, user_id=request.user, bid=bid)
                newBid.save()
                return render(request, "auctions/listing.html", {"listing":listing, "price":newBid, "comments":comments, "greenMessage":"Bid placed!"})
        
        # if a 'watchlist' item exists in the POST data, create a watchlist entry in the database
        if('watchlist' in request.POST):
            # check that an item isn't already in the users watchlist
            if(WatchList.objects.filter(user_id=request.user).filter(listing_id=listing)):
                #if it is, render the page with an error message
                return render(request, "auctions/listing.html", {"listing":listing, "price":currentBid, "comments":comments, "redMessage":"Item is already in Watchlist"})
            else:
                # if it is not, add the Watchlist entry to the database and render the page with a success message
                watch = WatchList(user_id=request.user, listing_id=listing)
                watch.save()
                return render(request, "auctions/listing.html", {"listing":listing, "price":currentBid, "comments":comments, "greenMessage":"Item added to Watchlist!"})

        # if a 'close' item exists in the POST data, the user is trying to close the auction. Update the db entry with the winner, and refresh the page.
        if('close' in request.POST):
            messageAddendum = ""
    
            if(currentBid):
                listing.winner_id = currentBid.user_id
                messageAddendum = f"{currentBid.user_id} is the winner."

            listing.open = False
            listing.save()
            return render(request, "auctions/listing.html", {"listing":listing, "price":currentBid, "comments":comments, "greenMessage":"Auction successfully closed. " + messageAddendum})

        # if a 'comment' item exists in the POST data, the user is trying to leave a comment
        if('comment' in request.POST):
            newComment = Comment(user_id=request.user, listing_id=listing, comment=request.POST['comment'])
            newComment.save()
            # re-grab the list of comments before rendering the page to ensure the new one shows up
            comments = Comment.objects.filter(listing_id=listing)

    # if the listing is closed, check if the logged in user won the auction, and render a message accordingly
    if(listing.open == False):
        if(listing.winner_id == request.user):
            return render(request, "auctions/listing.html", {"listing":listing, "price":currentBid, "comments":comments, "greenMessage":"You've won this auction!"})
        else:
            return render(request, "auctions/listing.html", {"listing":listing, "price":currentBid, "comments":comments, "redMessage":"This auction has ended."})

    return render(request, "auctions/listing.html", {"listing":listing, "price":currentBid, "comments":comments})
    

@login_required
def watchlist(request):

    # generate the list of items being watched by the logged in user
    watchedItems = WatchList.objects.filter(user_id=request.user)

    # if the user submits one of the removal forms, remove the watchlist entry from the database before rendering the page
    if request.method == "POST":
        watchedItems.get(listing_id=Listing.objects.filter(title=request.POST["remove"]).first()).delete()


    return render(request, "auctions/watchlist.html", {"watchedItems":watchedItems})


def categories(request):
    cat=Category.objects.all()
    return render(request, "auctions/categories.html", {'categories':cat})


def browse(request, category):
    # grab a category object with a name that matches the input parameter
    cat = Category.objects.get(category=category)

    # grab a list of all the open listings that match the supplied category
    listings=Listing.objects.filter(category_id=cat).filter(open=True)

    # render a page very similar to the homepage, but with only listings that match the given category
    return render(request, "auctions/browse.html", {"category":category, "listings":listings})

