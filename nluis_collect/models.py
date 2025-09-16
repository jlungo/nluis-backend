from account.models import User
from django.contrib.gis.db.models import GeometryField
from django.db import models

# Create your models here.
from django_currentuser.db.models import CurrentUserField


class Category(models.Model):
    class Meta:
        db_table = 'collect_categories'
        ordering = ['order_no']
        unique_together = ['flag', 'name']
        # verbose_name=''
        verbose_name_plural = 'Categories'

    ch_flags = (
        ('party_info', 'party_info'),
        ('preliminary_info', 'preliminary_info'),
        ('house_hold', 'house_hold'),
        ('focused_group', 'focused_group'),
        ('key_informants', 'key_informants'),
        ('multimedia', 'multimedia'),
        ('verification', 'verification'),
        ('dodoso', 'dodoso'),
        ('auditing', 'auditing'),
        ('zonal_monitoring', 'zonal_monitoring'),
    )
    name = models.CharField(max_length=1000)
    project_type = models.ForeignKey(
        'nluis_projects.ProjectType', blank=True, null=True, on_delete=models.CASCADE)
    flag = models.CharField(max_length=50, choices=ch_flags,
                            blank=True, null=True)

    order_no = models.IntegerField(null=True, blank=True)
    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    created_by = CurrentUserField(related_name='collect_categories_created')
    updated_by = CurrentUserField(related_name='collect_categories_updated')
    last_update_date = models.DateField(auto_now=True)
    last_update_time = models.DateField(auto_now=True)
    parent = models.ForeignKey(
        'nluis_collect.Category', blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name

    # def page(self):
    #     try:
    #         return Page.objects.filter(chapter=self).values('id', 'name')
    #     except Exception as e:
    #         return []


class Form(models.Model):
    class Meta:
        db_table = 'collect_forms'
        unique_together = ['category', 'name']

    category = models.ForeignKey(
        'nluis_collect.Category', on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=1000)
    order_no = models.IntegerField(null=True, blank=True)
    flag = models.CharField(max_length=50, choices=(
        ('person_name', 'Person Name'),
        ('occupancy_category', 'Occupancy Category'),
        ('table_data', 'Table Data')), blank=True, null=True)

    is_default = models.BooleanField(default=True)
    is_enabled = models.BooleanField(default=False)
    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    created_by = CurrentUserField(related_name='collect_forms_created')
    updated_by = CurrentUserField(related_name='collect_forms_updated')
    last_update_date = models.DateField(auto_now=True)
    last_update_time = models.DateField(auto_now=True)

    def __str__(self):
        return f'{self.name} - {self.category.name}'

    def questions(self):
        try:
            return FormField.objects.filter(form=self).order_by('order_no')
        except Exception as e:
            print(e)
            return []


class FormField(models.Model):
    class Meta:
        db_table = 'collect_form_fields'
        unique_together = ['form', 'form_field']

    form = models.ForeignKey('nluis_collect.Form',
                             on_delete=models.CASCADE, null=True, blank=True)
    form_field = models.CharField(max_length=1000)
    placeholder = models.CharField(max_length=50, null=True, blank=True)
    data_type = models.CharField(max_length=20, choices=(
        ('number', 'Number'),
        ('text', 'Text'),
        ('radio', 'Radio Button'),
        ('check', 'Check Box'),
        ('select', 'DropDown'),
        ('date', 'Date'),
        ('email', 'Email'),
        ('phone', 'Phone Number'),
        ('image', 'Image'),
        ('file', 'File'),
        ('point', 'Point'),
        ('line', 'Line'),
        ('polygon', 'Polygon'),
        ('country', 'country'),
        ('region', 'region'),
        ('council', 'council'),
        ('ward', 'ward'),
        ('village', 'village'),
        ('hamlet', 'hamlet'),
        ('land_use', 'land_use'),
        ('occupancy', 'occupancy')
    ))

    # , choices=(
    #     ('person_name', 'Person Name'),
    #     ('occupancy_category', 'Occupancy Category'),
    #     ('person_picture', 'Person Picture'),
    #     ('land_use', 'Land Use'),
    #     ('north', 'north'),
    #     ('south', 'south'),
    #     ('east', 'east'),
    #     ('west', 'west'),
    #     ('institute', 'Taasisi/Kikundi')
    # )
    
    options = models.TextField(blank=True, null=True)
    order_no = models.IntegerField(blank=True, null=True)
    required = models.BooleanField(default=False)
    error_message = models.TextField(blank=True, null=True)
    hint = models.TextField(blank=True, null=True)
    flag = models.CharField(max_length=50, blank=True, null=True)
    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    created_by = CurrentUserField(related_name='question_created')
    updated_by = CurrentUserField(related_name='question_updated')
    last_update_date = models.DateField(auto_now=True)
    last_update_time = models.DateField(auto_now=True)
    parent = models.ForeignKey("nluis_collect.FormField", related_name='parent_formfield', null=True, blank=True,
                               on_delete=models.SET_NULL)
    parent_value = models.CharField(max_length=50, blank=True, null=True)
    chapter = models.ForeignKey('nluis_projects.Chapter',
                                on_delete=models.CASCADE, null=True, blank=True)
    param_code = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.form_field


class FormAnswer(models.Model):
    class Meta:
        db_table = 'collect_form_answer'
        unique_together = ['form_field', 'claim_no']

    local_answer_id = models.IntegerField(blank=True, null=True)
    local_answer_date = models.CharField(max_length=50, null=True, blank=True)
    claim_no = models.CharField(max_length=50, null=True, blank=True)
    project = models.ForeignKey(
        'nluis_projects.Project', on_delete=models.SET_NULL, null=True, blank=True)
    para_surveyor = models.ForeignKey(
        'nluis_projects.TeamMember', on_delete=models.SET_NULL, null=True, blank=True)
    form_field = models.ForeignKey(
        'nluis_collect.FormField', null=True, blank=True, on_delete=models.SET_NULL)
    locality = models.ForeignKey(
        'nluis_localities.Locality', on_delete=models.SET_NULL, null=True, blank=True)

    response = models.TextField(null=True, blank=True)

    image = models.ImageField(upload_to='answers', null=True, blank=True)
    file = models.FileField(upload_to='answers', null=True, blank=True)
    geom = GeometryField(blank=True, null=True)

    freeze = models.BooleanField(default=False)
    stage = models.CharField(max_length=50, default='draft')

    deleted_at = models.TimeField(null=True, default=None, blank=True)
    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    created_by = CurrentUserField(related_name='collect_form_answers_created')
    updated_by = CurrentUserField(related_name='collect_form_answers_updated')
    deleted_by = CurrentUserField(related_name='collect_form_answers_deleted')
    last_update_date = models.DateField(auto_now=True)
    last_update_time = models.DateField(auto_now=True)

    def __str__(self):
        return self.claim_no

    @property
    def image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        else:
            return ''

    @property
    def file_url(self):
        if self.file and hasattr(self.file, 'url'):
            return self.file.url
        else:
            return ''

    def village(self):
        try:
            return self.locality.parent.name if self.locality is not None else ''
        except Exception as e:
            return str(e)


class TemporaryFile(models.Model):
    class Meta:
        db_table = 'collect_temporary_files'

    updated_by = CurrentUserField(
        on_update=True, related_name='collect_temporary_files_updated_by')
    file = models.FileField(upload_to='files')
    description = models.TextField(blank=True, null=True)
    device_id = models.CharField(max_length=50)

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    created_by = CurrentUserField()


class Monitoring(models.Model):
    class Meta:
        db_table = 'collect_monitoring'

    ch_flags = (
        ('verification', 'verification'),
        ('auditing', 'auditing')
    )
    flag = models.CharField(max_length=50, choices=ch_flags)
    action = models.ForeignKey(
        'nluis_collect.FormField', on_delete=models.SET_NULL, null=True, blank=True)
    means_of_verification = models.CharField(max_length=1000)
    form_fields = models.ManyToManyField(
        'nluis_collect.FormField', blank=True, related_name='form_fields')
    assessment_performance = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    created_by = CurrentUserField()


class FormAnswerQuestionnaire(models.Model):
    class Meta:
        db_table = 'collect_form_answer_questionnaire'
        unique_together = ['form_field', 'claim_no']

    local_answer_id = models.IntegerField(blank=True, null=True)
    local_answer_date = models.CharField(max_length=50, null=True, blank=True)
    claim_no = models.CharField(max_length=50, null=True, blank=True)
    project = models.ForeignKey(
        'nluis_projects.Project', on_delete=models.SET_NULL, null=True, blank=True)
    para_surveyor = models.ForeignKey(
        'nluis_projects.TeamMember', on_delete=models.SET_NULL, null=True, blank=True)
    form_field = models.ForeignKey(
        'nluis_collect.FormField', null=True, blank=True, on_delete=models.SET_NULL)
    locality = models.ForeignKey(
        'nluis_localities.Locality', on_delete=models.SET_NULL, null=True, blank=True)

    response = models.TextField(null=True, blank=True)

    image = models.ImageField(upload_to='answers', null=True, blank=True)
    file = models.FileField(upload_to='answers', null=True, blank=True)
    geom = GeometryField(blank=True, null=True)

    freeze = models.BooleanField(default=False)
    stage = models.CharField(max_length=50, default='draft')

    deleted_at = models.TimeField(null=True, default=None, blank=True)
    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    created_by = CurrentUserField(
        related_name='collect_form_answers_questionnaire_created')
    updated_by = CurrentUserField(
        related_name='collect_form_answers_questionnaire_updated')
    deleted_by = CurrentUserField(
        related_name='collect_form_answers_questionnaire_deleted')
    last_update_date = models.DateField(auto_now=True)
    last_update_time = models.DateField(auto_now=True)

    def __str__(self):
        return self.claim_no

    @property
    def image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        else:
            return ''

    @property
    def file_url(self):
        if self.file and hasattr(self.file, 'url'):
            return self.file.url
        else:
            return ''

    def village(self):
        try:
            return self.locality.parent.name if self.locality is not None else ''
        except Exception as e:
            return str(e)
