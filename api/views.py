from rest_framework import generics, permissions, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django.db.models import Q
from capsules.models import Capsule
from .serializers import CapsuleSerializer, UserSerializer
from accounts.models import CustomUser


class PublicCapsuleListView(generics.ListAPIView):
    serializer_class = CapsuleSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'open_date', 'views_count']

    def get_queryset(self):
        return Capsule.objects.filter(privacy='public', status='sealed')


class CapsuleDetailView(generics.RetrieveAPIView):
    queryset = Capsule.objects.all()
    serializer_class = CapsuleSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance.can_user_view(request.user):
            return Response({'error': 'You do not have permission to view this capsule'}, status=403)
        return super().retrieve(request, *args, **kwargs)


class MyCapsulesView(generics.ListAPIView):
    serializer_class = CapsuleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Capsule.objects.filter(creator=self.request.user)


class UserProfileView(generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'username'


class UserStatsView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, username):
        user = CustomUser.objects.get(username=username)
        capsules = Capsule.objects.filter(creator=user)

        stats = {
            'total_capsules': capsules.count(),
            'public_capsules': capsules.filter(privacy='public').count(),
            'total_views': sum(c.views_count for c in capsules),
            'joined_date': user.date_joined,
        }
        return Response(stats)
