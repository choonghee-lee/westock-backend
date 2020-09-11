from django.urls import path

from .views      import SignUp, SignIn, KakaoSignin, ProductFollow, GoogleSignInView, BuyingList

urlpatterns = [
    path('/sign-up', SignUp.as_view()),
    path('/sign-in', SignIn.as_view()),
    path('/sign-in/kakao', KakaoSignin.as_view()),
    path('/sign-in/google', GoogleSignInView.as_view()),
    path('/follow', ProductFollow.as_view()),
    path('/buying-list', BuyingList.as_view()),
]