from django.urls import path

from . import views

urlpatterns = [path("", views.splash, name="splash"),
               path("home/", views.index, name="index"),
		   path('bidder/', views.BidderScreen, name='BidderScreen'),
		   path('bidderscreen/', views.BidderScreen, name='BidderScreen'),

	       path("TenderLogin.html", views.TenderLogin, name="TenderLogin"),
	       path("TenderLoginAction", views.TenderLoginAction, name="TenderLoginAction"),
	       path("logout/", views.Logout, name="Logout"),
	       path("Register.html", views.Register, name="Register"),
	       path("BidderLoginAction", views.BidderLoginAction, name="BidderLoginAction"),
	       path("BidderLogin.html", views.BidderLogin, name="BidderLogin"),
	       path("CreateTender.html", views.CreateTender, name="CreateTender"),
	       path("CreateTenderAction", views.CreateTenderAction, name="CreateTenderAction"),
	       path("BidTender", views.BidTender, name="BidTender"),
	       path("ViewTender", views.ViewTender, name="ViewTender"),
	       path("EvaluateTender", views.EvaluateTender, name="EvaluateTender"),
	       path("EvaluateTenderAction", views.EvaluateTenderAction, name="EvaluateTenderAction"),
	       path("WinnerSelection", views.WinnerSelection, name="WinnerSelection"),
	       path("TenderScreen", views.TenderScreen, name="TenderScreen"),
	       path("Signup", views.Signup, name="Signup"),
	       path("BidTenderActionPage", views.BidTenderActionPage, name="BidTenderActionPage"),
	       path("BidTenderAction", views.BidTenderAction, name="BidTenderAction"),
]