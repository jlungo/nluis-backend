from account.models import User
from django.db import models
from nluis.settings import BILL_DATE_INPUT_FORMATS
from django.db.models import Sum

# Create your models here.
from django_currentuser.db.models import CurrentUserField
from nluis_projects.models import ProjectType, Project
from nluis_setups.models import Currency, ExchangeRate


class Fee(models.Model):
    class Meta:
        db_table = 'billing_fees'

    payment_options = (
        ('1', 'Full Payment'),
        ('2', 'Partial Payment'),
        ('3', 'Exact Payment')
    )
    name = models.CharField(max_length=50)
    gfs_code = models.CharField(max_length=50)
    project_type = models.ForeignKey(
        ProjectType, blank=True, null=True, on_delete=models.CASCADE)
    currency = models.ForeignKey(
        Currency, on_delete=models.CASCADE)
    payment_option = models.CharField(max_length=50, choices=payment_options,
                                      blank=True, null=True)

    price = models.DecimalField(decimal_places=2, max_digits=16)
    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    created_by = CurrentUserField(related_name='billing_fee_created')
    updated_by = CurrentUserField(related_name='billing_fee_updated')
    last_update_date = models.DateField(auto_now=True)
    last_update_time = models.DateField(auto_now=True)

    def __str__(self):
        return self.name

    def project_type_name(self):
        return self.project_type.name

    def currency_info(self):
        return self.currency

    def currency_name(self):
        return self.currency.name


class Bill(models.Model):
    class Meta:
        db_table = 'billing_bills'
        # verbose_name_plural = ''

    status = (
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Expired', 'Expired'),
        ('Cancelled', 'Cancelled')
    )
    holder_name = models.CharField(max_length=50)
    holder_phone = models.CharField(max_length=15)
    holder_address = models.CharField(max_length=100)
    gepg_post_status = models.CharField(max_length=10, blank=True, null=True)
    gepg_control_number_status = models.CharField(
        max_length=10, blank=True, null=True)
    control_number = models.CharField(max_length=50, blank=True, null=True)
    exchange_rate = models.ForeignKey(
        ExchangeRate, blank=True, null=True, on_delete=models.CASCADE)
    currency = models.ForeignKey(
        Currency, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=status, default='Pending',
                              blank=True, null=True)
    amount = models.DecimalField(
        decimal_places=2, max_digits=16, blank=True, null=True)
    issued_date = models.DateTimeField()
    expiry_date = models.DateTimeField()
    cancelled_by = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.CASCADE)
    remarks = models.TextField(blank=True, null=True)
    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    created_by = CurrentUserField(related_name='billing_bill_created')
    updated_by = CurrentUserField(related_name='billing_bill_updated')
    last_update_date = models.DateField(auto_now=True)
    last_update_time = models.DateField(auto_now=True)

    def items(self):
        return BillItem.objects.filter(bill=self)

    def paymentOption(self):
        return BillItem.objects.filter(bill=self).first().fee.payment_option

    def totalAmount(self):
        total = BillItem.objects.filter(bill=self).aggregate(Sum('amount'))
        return total['amount__sum']

    def totalEqvAmount(self):
        total = 0
        items = BillItem.objects.filter(bill=self)
        for item in items:
            total = total + item.eqvAmount()
        return total


class BillItem(models.Model):
    class Meta:
        db_table = 'billing_items'

    bill = models.ForeignKey(
        Bill, on_delete=models.CASCADE)
    fee = models.ForeignKey(
        Fee, on_delete=models.CASCADE)
    project = models.ForeignKey(
        Project, blank=True, null=True, on_delete=models.CASCADE)
    quantity = models.DecimalField(
        decimal_places=2, max_digits=10)
    unit_price = models.DecimalField(
        decimal_places=2, max_digits=16)
    amount = models.DecimalField(
        decimal_places=2, max_digits=16)
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = CurrentUserField()
    update_date = models.DateTimeField(auto_now=True)

    def eqvAmount(self):
        fee = self.fee
        eqAmount = 0
        exchange_rate = ExchangeRate.objects.filter(
            is_active=True, currency=fee.currency).last()

        if exchange_rate != None:
            eqAmount = fee.price * exchange_rate.amount

        return eqAmount


class Subscriber(models.Model):
    class Meta:
        db_table = 'project_subscribers'

    bill = models.ForeignKey(
        Bill, on_delete=models.CASCADE)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = CurrentUserField(related_name="project_subscriber")
    update_date = models.DateTimeField(auto_now=True)


class Payment(models.Model):
    class Meta:
        db_table = 'billing_payments'

    bill_id = models.ForeignKey(
        Bill, blank=True, null=True, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=100, unique=True)
    currency = models.CharField(max_length=50)
    sp_code = models.CharField(max_length=50)
    payment_ref = models.CharField(max_length=100)
    payer_name = models.CharField(max_length=50, blank=True, null=True)
    payer_email = models.CharField(max_length=100, blank=True, null=True)
    payer_mobile_number = models.CharField(
        max_length=100, blank=True, null=True)
    control_number = models.CharField(max_length=50)
    payment_channel = models.CharField(max_length=50)
    paid_amount = models.DecimalField(
        decimal_places=2, max_digits=16, blank=True, null=True)
    receipt_number = models.CharField(max_length=100)
    psp_name = models.CharField(max_length=100)
    date_paid = models.DateField()

    remarks = models.TextField(blank=True, null=True)
    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    created_by = CurrentUserField(related_name='billing_payment_created')
    deleted_by = CurrentUserField(related_name='billing_payment_deleted')
    last_update_date = models.DateField(auto_now=True)
    last_update_time = models.DateField(auto_now=True)
