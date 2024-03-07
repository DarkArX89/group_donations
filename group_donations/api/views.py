from rest_framework import viewsets, mixins
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from payment.models import Collect
from .serializers import PaymentSerializer, CollectSerializer
from .permissions import AuthorOrReadOnly


class CreateListRetriveViewSet(mixins.CreateModelMixin,
                               mixins.ListModelMixin,
                               mixins.RetrieveModelMixin,
                               viewsets.GenericViewSet):
    pass


class PaymentViewSet(CreateListRetriveViewSet):
    serializer_class = PaymentSerializer

    @method_decorator(cache_page(60))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        collect = get_object_or_404(Collect, id=self.kwargs.get('collect_id'))
        return collect.payments.all()

    def perform_create(self, serializer):
        collect_id = self.kwargs.get('collect_id')
        collect = get_object_or_404(Collect, id=collect_id)
        serializer.save(user=self.request.user, collect=collect)
        send_mail(
            'Создан новый платёж',
            f'Платёж для {collect.title} успешно создан!',
            get_current_site(self.request).domain,
            [self.request.user.email,],
            fail_silently=False
        )


class CollectViewSet(viewsets.ModelViewSet):
    queryset = Collect.objects.all()
    serializer_class = CollectSerializer
    permission_classes = (AuthorOrReadOnly,)

    @method_decorator(cache_page(60))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        title = self.request.data.get('title')
        send_mail(
            'Создан новый денежный сбор',
            f'Новый денежный сбор {title} создан!',
            get_current_site(self.request).domain,
            [self.request.user.email,],
            fail_silently=False
        )
