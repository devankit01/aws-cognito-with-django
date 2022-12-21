import boto3
from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from django.contrib.auth.models import User
from authy_microservice.credentials import REGION_NAME, COGNITO_USER_CLIENT # USE .ENV FILE TO STORE CREDENTIALS
from rest_framework_api_key.models import APIKey

# Global Declaration
client = boto3.client('cognito-idp', region_name=REGION_NAME)



class SignupViewAPI(APIView):

    def post(self, request):
        email = request.POST.get('email', None)
        password = request.POST.get('password', None)
        response = {}
        try:
            client_response = client.sign_up(ClientId=COGNITO_USER_CLIENT, Username=email,
                                             Password=password)
            user = User.objects.get_or_create(email=email, password=password, username=email)
            response['message'] = 'User account created succesfully'
            response['status'] = 201
            response['data'] : client_response

        except client.exceptions.UsernameExistsException as e:
            response['error'] = 'email already exists'
            response['status'] = 400

        return Response(response)


class ResendConfirmationAPI(APIView):

    def post(self, request):
        email = request.POST.get('email', None)

        # Check if email exists the resend_confirmation_code
        response = client.resend_confirmation_code(ClientId=COGNITO_USER_CLIENT,
                                                   Username=email)
        api_key, key = APIKey.objects.create_key(name="Dev")
        print(api_key, key)
        return Response(response)


class ConfirmAccountAPI(APIView):

    def post(self, request):
        email = request.POST.get('email', None)
        confirm_code = request.POST.get('code', None)
        response = {}
        try:
            client_response = client.confirm_sign_up(ClientId=COGNITO_USER_CLIENT,
                                                     Username=email, ConfirmationCode=confirm_code)
            response['message'] = 'User account confirmed succesfully'
            response['status'] = 200

        except client.exceptions.ExpiredCodeException:
            response['error'] = 'Expired confirmation_code'
            response['status'] = 401

        except client.exceptions.NotAuthorizedException:
            response['message'] = 'user already verified'
            response['status'] = 401

        except client.exceptions.CodeMismatchException:
            response['message'] = 'Invalid confirmation_code'
            response['status'] = 401

        return Response(response)


class SignInViewAPI(APIView):

    def post(self, request):
        email = request.POST.get('email', None)
        password = request.POST.get('password', None)
        response = {}

        try:
            client_response = client.initiate_auth(ClientId=COGNITO_USER_CLIENT, AuthFlow="USER_PASSWORD_AUTH", AuthParameters={
                'USERNAME': email,
                'PASSWORD': password
            }
            )
            response['AccessToken'] = client_response['AuthenticationResult']['AccessToken']
            response['RefreshToken'] = client_response['AuthenticationResult']['RefreshToken']
            response['RefreshTTokenTypeoken'] = client_response['AuthenticationResult']['TokenType']
            response['ExpiresIn'] = client_response['AuthenticationResult']['ExpiresIn']
            response['data'] = client_response

        except client.exceptions.NotAuthorizedException:
            response['error'] = 'Invalid Credentials'
            response['status'] = 401
        return Response(response)

class RefreshTokenViewAPI(APIView):

    def post(self, request):
        refresh_token = request.POST.get('refresh_token', None)
        response = {}

        try:
            client_response = client.initiate_auth(ClientId=COGNITO_USER_CLIENT, AuthFlow="REFRESH_TOKEN_AUTH", AuthParameters={
                'REFRESH_TOKEN': refresh_token

            }
            )
            response['AccessToken'] = client_response['AuthenticationResult']['AccessToken']
            response['RefreshTTokenTypeoken'] = client_response['AuthenticationResult']['TokenType']
            response['ExpiresIn'] = client_response['AuthenticationResult']['ExpiresIn']
            # response['data'] = client_response

        except client.exceptions.NotAuthorizedException:
            response['error'] = 'Invalid access_token'
            response['status'] = 401
        return Response(response)

class GetUserViewAPI(APIView):

    def post(self, request):
        access_token = request.POST.get('access_token', None)
        response = {}

        try:
            client_response = client.get_user(AccessToken=access_token)
            if 'UserAttributes' in client_response.keys():
                for key in client_response['UserAttributes']:
                    if key['Name'] == 'email':
                        response[key['Name']] = key['Value']
                        break
            response['status'] = 200

        except client.exceptions.NotAuthorizedException as e:
            response['error'] = "access token expired"
            response['status'] = 401

        return Response(response)


class ForgetPasswordAPIView(APIView):

    def post(self, request):
        email = request.POST.get('email', None)

        # Check if email exists the resend_confirmation_code
        response = client.forgot_password(
            ClientId=COGNITO_USER_CLIENT, Username=email)

        return Response(response)


class SetPasswordAPIView(APIView):

    def post(self, request):
        email = request.POST.get('email', None)
        set_password = request.POST.get('password', None)
        confirm_code = request.POST.get('confirm_code', None)

        response = {}
        try:
            client_response = client.confirm_forgot_password(
                ClientId=COGNITO_USER_CLIENT, Username=email, Password=set_password, ConfirmationCode=confirm_code)
            response['error'] = 'Password created successfulyy'
            response['status'] = 200

        except client.exceptions.CodeMismatchException:
            response['message'] = 'Invalid confirmation_code'
            response['status'] = 401

        return Response(response)


class ChangePasswordAPIView(APIView):

    def post(self, request):
        last_password = request.POST.get('last_password', None)
        change_password = request.POST.get('new_password', None)
        access_token = request.POST.get('access_token', None)

        response = {}

        try:
            client_response = client.change_password(
                PreviousPassword=last_password, ProposedPassword=change_password, AccessToken=access_token)
            response['message'] = "Password updated succesfully"
            response['status'] = 200

        except client.exceptions.NotAuthorizedException:
            response['error'] = "Invalid credentials"
            response['status'] = 401

        return Response(response)


class LogoutAPIView(APIView):

    def post(self, request):
        refresh_token = request.POST.get('refresh_token', None)

        response = {}
        try:
            client_response = client.revoke_token(ClientId=COGNITO_USER_CLIENT,
                                                  Token=refresh_token)

            response['message'] = "Revoked token successfully"
            response['status'] = 200

        except client.exceptions.NotAuthorizedException:
            response['error'] = "Invalid credentials"
            response['status'] = 401

        return Response(response)


class DeleteUserAPIView(APIView):

    def post(self, request):
        access_token = request.POST.get('access_token', None)

        response = {}
        try:
            client_response = client.delete_user(AccessToken=access_token)

            response['message'] = "User deleted successfully"
            response['status'] = 200

        except client.exceptions.NotAuthorizedException:
            response['error'] = "Invalid request"
            response['status'] = 401

        return Response(response)
