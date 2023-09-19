
from rest_framework.response import Response
from django.http.response import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import AccessToken,RefreshToken
from rest_framework.exceptions import AuthenticationFailed
from .serializers import UserSerializer, ResponseUserSerializer
from rest_framework.views import APIView, View
from rest_framework import status
from django.shortcuts import redirect
import stripe
import jwt


from .models import User

stripe.api_key='sk_test_51NpMKLFobSqgGAG31Vf7UDMarMp5Gg0a8umlS4xMZcKiTbGgmRXPhzQlKs5R5xHDA5FtalNIXs3fS4oWUKGRQBap00bWsM3LBr'


def get_user(request):
    token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
    # print(token)
    try:
    #   valid_data = jwt.decode(token, 'abc', algorithms=["HS256"])
      valid_data = AccessToken(token)
      user_id = valid_data['user_id']
      user=User.objects.filter(id=user_id).first()
    except ValidationError as v:
      print("validation error", v)
    return user

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['user_id'] = user.id
        token['username'] = user.username
        # ...

        return token


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class PaidView(APIView):
    def get(self, request):
        # print(request.COOKIES['access'])
        # token=request.COOKIES['access']
        # print(token)
        # user=get_user(request)
        # try:
        #     valid_data = AccessToken(token)
        #     user_id = valid_data['user_id']
        #     user=User.objects.filter(id=user_id).first()
        #     user.paid=True
        #     user.save()
        # except ValidationError as v:
        #     print("validation error", v)
        
        # return redirect('http://127.0.0.1:3000', code=200)
        return Response({'user':'user'})
class  LogoutView(APIView):
    def post(self, request):
        token = request.data.get('refresh')
        if token:
            try:
                # Hủy Refresh Token
                refresh_token = RefreshToken(token)
                refresh_token.blacklist()
                reponse = Response()
                reponse.data={'message': 'Có lỗi xảy ra khi đăng xuất.'}
                reponse.delete_cookie('access')
                reponse.delete_cookie('refresh')
                reponse.status_code=status.HTTP_200_OK
                # Trả về trạng thái thành công
                return reponse
            except Exception as e:
                return Response({'message': 'Có lỗi xảy ra khi đăng xuất.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': 'Không tìm thấy Access Token.'}, status=status.HTTP_400_BAD_REQUEST)


class TestGet(APIView):
    permission_classes=[AllowAny]
    def get(self, request):
        # user = get_user(request)
        # serialize=ResponseUserSerializer(user)
        return Response({'user':'user'})


class UserView(APIView):
    # permission_classes=[AllowAny]
    # permission_classes = [IsAuthenticated]
    def get(self, request):
        user = get_user(request)
        serialize=ResponseUserSerializer(user)
        return Response(serialize.data)

# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def getUser(request):
#     user = get_user(request)
#     serialize=ResponseUserSerializer(user)
#     return Response(serialize.data)

class create_checkout(APIView):
    def get(self, request):
        token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
        token1 = request.COOKIES['access']
        # valid_data = AccessToken(token1)

        print(token1)
        YOUR_DOMAIN='http://localhost:8000/'
        try:
            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                        # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                        'price': 'price_1NpNTTFobSqgGAG3K8E66wyO',
                        'quantity': 1,
                    },
                ],
                mode='payment',
                success_url=YOUR_DOMAIN + 'api/payment_successful?session_id='+token1,

                # success_url=YOUR_DOMAIN + 'api/payment_successful?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=YOUR_DOMAIN + '/cancel.html',
            )
        except Exception as e:
            raise AuthenticationFailed('Errr')

        return redirect(checkout_session.url, code=303)


# def calculate_order_amount(items):
#     # Replace this constant with a calculation of the order's amount
#     # Calculate the order total on the server to prevent
#     # people from directly manipulating the amount on the client
#     return 1400
# class create_payment(APIView):
#     def post(selt, request):
#         try:
#             data = request.data
#             # Create a PaymentIntent with the order amount and currency
#             intent = stripe.PaymentIntent.create(
#                 amount=calculate_order_amount(data['items']),
#                 currency='usd',
#                 # In the latest version of the API, specifying the `automatic_payment_methods` parameter is optional because Stripe enables its functionality by default.
#                 automatic_payment_methods={
#                     'enabled': True,
#                 },
#             )
#             return Response({
#                 'clientSecret': intent['client_secret']
#             })
#         except Exception as e:
#             return Response({'error':str(e)},status=status.HTTP_403_FORBIDDEN)
        

class payment_successful(APIView):
    def get(self, request):
        checkout_session_id = request.GET.get('session_id', None)
        valid_data = AccessToken(checkout_session_id)
        user = User.objects.get(id=valid_data['user_id'])
        user.paid=True
        user.save()
        print(user.paid)
        return redirect('http://localhost:3000/', code=200)
            # session = stripe.checkout.Session.retrieve(checkout_session_id)
            # customer = stripe.Customer.retrieve(session.customer)
            # user_id = request.user.user_id
            # user_payment = User.objects.get(id=user_id)
            # user_payment.stripe_checkout_id = checkout_session_id
            # user_payment.save()
	    