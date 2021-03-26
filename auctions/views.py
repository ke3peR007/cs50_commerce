from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django import forms
from django.contrib import messages
from django.db.models import Max

from .models import User, Product, Bid, Comment



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

def index(request):
    listings = Product.objects.all().filter(status_of_listing=True)
    return render(request, "auctions/index.html", {
        "listings": listings
    })

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
        return render(request, "auctions/add_product.html", {
            "form" : ListingForm()
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
            


        # try:
        #     title = request.POST["title"]
        #     description = request.POST["description"]
        #     category = request.POST["category"]
        #     image_url = request.POST["image_url"]
        #     starting_bid = float(request.POST["starting_bid"])
        #     status_of_listing = request.POST.get("status_of_listing", False)
        #     user = request.user
        #     print(status_of_listing)
        # except:
        #     return render(request, "auctions/add_product.html", {
        #         "message" : "Please enter valid details."
        #     })
        # product = Product(title=title, description=description, category=category, image_url=image_url, starting_bid=starting_bid, highest_bid=0, user=user,status_of_listing=status_of_listing)
        # product.save()
        # return HttpResponseRedirect(reverse("index"))


@login_required()
def user_listing(request):
    if request.method == "GET":
        listing = Product.objects.all().filter(user=request.user)
        return render(request, "auctions/user_listing.html", {
            "listing" : listing
        })



@login_required()
def listing(request, listing_id):
    if request.method == "GET":
        try:
            listing = Product.objects.get(pk=listing_id)
            highest_bids = Bid.objects.all().filter(product=listing).aggregate(Max('bid_price'))
            bids_count = Bid.objects.all().filter(product=listing).count()
            comments = Comment.objects.all().filter(product=listing)
        except:
            return HttpResponseRedirect(reverse("index"))
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
    product = Product.objects.get(pk=listing_id)
    product.status_of_listing = False
    product.save()
    # highest_bid = Bid.objects.all().filter(product=product).aggregate(Max('bid_price'))
    # winner = Bid.objects.get(bid_price=highest_bid["bid_price__max"])
    # print(winner)
    return HttpResponseRedirect(reverse("user_listing"))


@login_required()
def add_comment(request):
    
    form = CommentForm(request.POST)

    if form.is_valid():
        
            user_comment = form.cleaned_data["comment"]
            
            commented_on = int(request.POST["commented_on"])
            listing_id = request.POST["listing_id"]
            product = Product.objects.get(pk=listing_id)
            user = request.user
            print(type(commented_on))
            comment = Comment(product=product, comment=user_comment,commented_on=commented_on,user=user)
            comment.save()
            return HttpResponseRedirect(reverse("listing", args={listing_id}))
        

            # return HttpResponseRedirect(reverse("index")) 