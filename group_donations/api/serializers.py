import base64

from rest_framework import serializers
from django.core.files.base import ContentFile

from payment.models import Payment, Collect, Reason


class PaymentSerializer(serializers.ModelSerializer):
    fio = serializers.SerializerMethodField()
    collect = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Payment
        fields = ('fio', 'pay_sum', 'pay_date', 'collect')

    def get_fio(self, obj):
        fio = [obj.user.first_name, obj.user.last_name]
        return ' '.join(fio)

    def validate(self, attrs):
        pay_sum = attrs.get('pay_sum')
        if int(pay_sum) <= 0:
            raise serializers.ValidationError(
                'Платёж не может быть нулевымили отрицательным!')
        return attrs


class ReasonNameField(serializers.Field):
    def to_representation(self, value):
        return value.name

    def to_internal_value(self, data):
        reason = Reason.objects.get(id=data)
        return reason


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class CollectSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    collect_sum = serializers.SerializerMethodField()
    amount_donaters = serializers.SerializerMethodField()
    reason = ReasonNameField()
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Collect
        fields = (
            'id', 'author', 'title', 'description', 'reason', 'max_sum',
            'collect_sum', 'amount_donaters', 'end_date', 'payments', 'image'
        )

    def validate(self, attrs):
        author = self.context.get('request').user
        title = attrs.get('title')
        max_sum = self.initial_data.get('max_sum')
        reason = self.initial_data.get('reason')
        if Collect.objects.filter(author=author, title=title).exists():
            raise serializers.ValidationError(
                'Сбор с таким именем у вас уже существует!')
        if max_sum is not None and int(max_sum) <= 0:
            raise serializers.ValidationError(
                'Максимальная сумма не может быть нулевой или отрицательной!')
        if not str(reason).isdigit():
            raise serializers.ValidationError(
                'Для поля "reason" должен быть указан id в числовом виде!')
        if not Reason.objects.filter(id=int(reason)).exists():
            raise serializers.ValidationError(
                'Повода (reason) с таким id не существует!')
        return attrs

    def get_collect_sum(self, obj):
        payments = Payment.objects.filter(collect=obj)
        collect_sum = 0
        for payment in payments:
            collect_sum += payment.pay_sum
        return collect_sum

    def get_amount_donaters(self, obj):
        payments = Payment.objects.filter(collect=obj)
        donaters = set()
        for payment in payments:
            donaters.add(payment.user)
        return len(donaters)
