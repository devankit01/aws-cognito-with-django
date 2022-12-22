
from rest_framework.views import APIView
from rest_framework.response import Response
from authy_microservice.models import BookModel
from authy_microservice.serializers import BookSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_api_key.permissions import HasAPIKey

class BookViewAPI(APIView):

    # Request should have JWTToken and Authorization Key respectively
    permission_classes = [ IsAuthenticated & HasAPIKey ]

    def get(self, request, format=None):
        
        # Get info about request user
        print(request.user)

        # Get all data in request oject
        # print(vars(request))

        snippets = BookModel.objects.all()
        serializer = BookSerializer(snippets, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):

        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
            
        return Response(serializer.errors, status=400)
        
