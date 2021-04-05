from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django import forms
from django.contrib import messages
from django.db.models import Max
from django.utils import timezone
import pytz
import datetime
from django.http import JsonResponse
from .models import User, Product, Bid, Comment, UserWatchlist



class ListingForm(forms.Form):
    title = forms.CharField(label="Title", required=True, max_length=64)
    description = forms.CharField(label="Description", required=True, widget=forms.Textarea(attrs={"rows": 3, "cols": 20}))
    starting_bid = forms.FloatField(label="Starting Bid", min_value=0.0, required=True)
    image_url = forms.CharField(label="Image URL", required=False,widget=forms.Textarea(attrs={"rows": 1}))
    category = forms.CharField(label="Category",required=False, max_length=64)
    status_of_listing = forms.BooleanField(label="Status", widget=forms.CheckboxInput)

    def __init__(self, *args, **kwargs):
        super(ListingForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            
            if visible.name == "status_of_listing":
                visible.field.widget.attrs['class'] = 'form-check-input'
                continue
            visible.field.widget.attrs['class'] = 'form-control'



class BidForm(forms.Form):
    bid = forms.FloatField(label="Starting Bid", min_value=0.0, required=True)
    def __init__(self, *args, **kwargs):
        super(BidForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

class CommentForm(forms.Form):
    comment = forms.CharField(label="comment", required=True, widget=forms.Textarea(attrs={"rows": 3, "cols": 58}))
    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'



def index(request):
    listings = Product.objects.all().filter(status_of_listing=True)
    try:
        watchlist_count = UserWatchlist.objects.filter(user=request.user).count
        return render(request, "auctions/index.html", {
            "listings": listings,
            "watchlist_count": watchlist_count,
        })
    except:
        return render(request, "auctions/index.html", {
            "listings": listings,
            "watchlist_count": None,
        })

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
                "message": "Invalid username and/or password."
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
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required()
def create_listing(request):
    if request.method == "GET":
        watchlist_count = UserWatchlist.objects.filter(user=request.user).count
        return render(request, "auctions/add_product.html", {
            "form" : ListingForm(),
            "watchlist_count" : watchlist_count,
        })
    if request.method == "POST":
        form = ListingForm(request.POST)

        if form.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            category = form.cleaned_data["category"]
            image_url = form.cleaned_data["image_url"]
            starting_bid = form.cleaned_data["starting_bid"]
            status_of_listing = form.cleaned_data["status_of_listing"]
            user = request.user
            product = Product(title=title, description=description, category=category, image_url=image_url, starting_bid=starting_bid, highest_bid=0, user=user,status_of_listing=status_of_listing)
            product.save()
            messages.success(request, "Listing added successfully." )
            return render(request, "auctions/add_product.html", {
                "form" : ListingForm(),
                "isListingAdded": True,

            })
            


@login_required()
def user_listing(request):
    if request.method == "GET":
        listing = Product.objects.all().filter(user=request.user)
        watchlist_count = UserWatchlist.objects.filter(user=request.user).count
        return render(request, "auctions/user_listing.html", {
            "listing" : listing,
            "watchlist_count": watchlist_count,
        })



@login_required()
def listing(request, listing_id):
    if request.method == "GET":
        try:
            dlisting = Product.objects.filter(pk=listing_id)
            print(dlisting)
            listing = Product.objects.get(pk=listing_id)
            highest_bids = Bid.objects.all().filter(product=listing).aggregate(Max('bid_price'))
            bids_count = Bid.objects.all().filter(product=listing).count()
            comments = Comment.objects.all().filter(product=listing)
            watchlist = listing.product_watchlist.filter(user=request.user)
            watchlist_count = UserWatchlist.objects.filter(user=request.user).count
            # print(watchlist)
            if listing.status_of_listing == False:
                winner = Bid.objects.get(bid_price=highest_bids["bid_price__max"])
            else:
                winner = None
        except:
            pass
            # return HttpResponseRedirect(reverse("index"))
        if listing.status_of_listing == False:
            winner = Bid.objects.get(bid_price=highest_bids["bid_price__max"])
        else:
            winner = None
        return render(request, "auctions/listing.html", {
            "listing" : listing,
            "form" : BidForm(),
            "highest_bids" : highest_bids["bid_price__max"],
            "bids_count" : bids_count,
            "winner" : winner,
            "commentForm" : CommentForm(),
            "comments" : comments,
            "watchlist" : watchlist,
            "watchlist_count": watchlist_count,
        })

    if request.method == "POST":
        form = BidForm(request.POST)
        
        if form.is_valid():
            bid = form.cleaned_data["bid"]
            product = Product.objects.get(pk=listing_id)
            if bid > product.highest_bid and bid > product.starting_bid:
                user = request.user
                
                bid_insert = Bid(product=product, user=user, bid_price=bid)
                product.highest_bid = bid
                bid_insert.save()
                product.save()
                return HttpResponseRedirect(reverse("listing", args={listing_id}))
            else:
                messages.success(request, "Bid must be greater than starting bid and higher bid. Please enter correct Bid." )
                return HttpResponseRedirect(reverse("listing", args={listing_id}))

@login_required()
def remove_listing(request, listing_id):
    product = Product.objects.get(pk=listing_id, user=request.user)
    product.status_of_listing = False
    product.save()
    return HttpResponseRedirect(reverse("user_listing"))


@login_required()
def add_comment(request):
    
    form = CommentForm(request.POST)

    if form.is_valid():
            user_comment = form.cleaned_data["comment"]
            listing_id = request.POST["listing_id"]
            product = Product.objects.get(pk=listing_id)
            user = request.user
            
            comment = Comment(product=product, comment=user_comment,user=user)
            comment.save()
            return HttpResponseRedirect(reverse("listing", args={listing_id}))
    else:
        return HttpResponseRedirect(reverse("index"))


@login_required()
def add_remove_to_watchlist(request, listing_id):
    print(request)
    product = Product.objects.get(pk=listing_id)
    user = request.user
    user_watchlist_item = UserWatchlist.objects.filter(product=product , user=user)
    print(user_watchlist_item)
    if not user_watchlist_item:
        watchlist = UserWatchlist(product=product, user=user)
        watchlist.save()
        messages.success(request, "Added to wishlist.")
        return HttpResponseRedirect(reverse("listing", args={listing_id}))
    else:
        user_watchlist_item.delete()
        messages.success(request, "Removed from wishlist.")
        return HttpResponseRedirect(reverse("listing", args={listing_id}))

@login_required()
def add_remove_to_watchlist_index(request, listing_id):
    print(request)
    product = Product.objects.get(pk=listing_id)
    user = request.user
    user_watchlist_item = UserWatchlist.objects.filter(product=product , user=user)
    print(user_watchlist_item)
    if not user_watchlist_item:
        watchlist = UserWatchlist(product=product, user=user)
        watchlist.save()
        messages.success(request, "Added to wishlist.")
        return HttpResponseRedirect(reverse("index"))
    else:
        user_watchlist_item.delete()
        messages.success(request, "Removed from wishlist.")
        return HttpResponseRedirect(reverse("index"))


@login_required()
def view_watchlist(request):
    users_watchlist = UserWatchlist.objects.filter(user=request.user)
    product = users_watchlist
    for ul in users_watchlist:
        print(ul.product.id)
    watchlist_count = UserWatchlist.objects.filter(user=request.user).count
    return render(request,"auctions/watchlist.html", {
        "users_watchlist": product,
        "watchlist_count": watchlist_count,
    })

def view_categories(request):
    product = Product.objects.filter(status_of_listing=True)
    try:
        watchlist_count = UserWatchlist.objects.filter(user=request.user).count
    except:
        watchlist_count = 0
    categories = []
    for item in product:
        if item.category not in categories:
            categories.append(item.category)
    print(categories)
    return render(request, "auctions/categories.html", {
        "categories": categories,
        "watchlist_count": watchlist_count
    })

def category(request, category_name):
    print(category_name)
    if category_name == "None":
        listings = Product.objects.filter(category="", status_of_listing=True)
    else:
        listings = Product.objects.filter(category=category_name, status_of_listing=True)
    try:
        watchlist_count = UserWatchlist.objects.filter(user=request.user).count
    except:
        watchlist_count = 0
    return render(request, "auctions/category.html", {
        "listings": listings,
        "watchlist_count": watchlist_count
    })


def autocomplete(request):
    if 'term' in request.GET:
        qs = Product.objects.filter(title__icontains=request.GET.get('term'), status_of_listing=True)
        titles = list()
        for product in qs:
            if product.title not in titles:
                titles.append(product.title)
        return JsonResponse(titles, safe=False)
    if request.method == "POST":
        text = request.POST["txtSearch"]
        listings = Product.objects.all().filter(status_of_listing=True, title=text)
        try:
            watchlist_count = UserWatchlist.objects.filter(user=request.user).count
            return render(request, "auctions/index.html", {
                "listings": listings,
                "watchlist_count": watchlist_count,
            })
        except:
            return render(request, "auctions/index.html", {
                "listings": listings,
                "watchlist_count": None,
            })