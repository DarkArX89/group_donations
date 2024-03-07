from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Reason(models.Model):
    name = models.CharField(
        verbose_name='Повод',
        max_length=200,
        unique=True
    )

    def __str__(self):
        return self.name


class Collect(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='author'
    )
    title = models.CharField(
        verbose_name='Название',
        max_length=200
    )
    reason = models.ForeignKey(
        Reason,
        on_delete=models.CASCADE
    )
    description = models.TextField(
        verbose_name='Описание'
    )
    max_sum = models.PositiveIntegerField(
        verbose_name='Запланированная сумма',
        null=True,
        blank=True
    )
    collect_sum = models.PositiveIntegerField(
        verbose_name='Собранная сумма',
        default=0
    )
    amount_donaters = models.PositiveIntegerField(
        verbose_name='Число людей, сделавших пожертвования',
        default=0
    )
    image = models.ImageField(
        upload_to='payment/images/',
        verbose_name='Обложка',
        null=True,
        blank=True
    )
    end_date = models.DateTimeField(
        verbose_name='Завершение сбора'
    )

    def __str__(self) -> str:
        return self.title


class Payment(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Донатер',
        related_name='donater'
    )
    pay_sum = models.PositiveIntegerField(
        verbose_name='Сумма'
    )
    pay_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        db_index=True
    )
    collect = models.ForeignKey(
        Collect,
        on_delete=models.CASCADE,
        verbose_name='Денежный сбор',
        related_name='payments'
    )

    class Meta:
        ordering = ['-pay_date']
