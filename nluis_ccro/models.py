from django.db import models
# Create your models here.
from django_currentuser.db.models import CurrentUserField
from django.contrib.gis.db.models import PointField, GeometryField

# Create your models here.
class DeedPlan(models.Model):
    class Meta:
        db_table = 'project_deed_plans'

    name = models.CharField(max_length=50, unique=True)
    srid = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    created_by = CurrentUserField()
    updated_by = CurrentUserField(
        on_update=True, related_name='deed_plan_info_updated_by')
    project = models.ForeignKey(
        'nluis_projects.Project', on_delete=models.CASCADE, blank=True, null=True)
    locality = models.ForeignKey(
        'nluis_localities.Locality', on_delete=models.CASCADE)

    def muda(self):
        return str(f'{self.created_date} {self.created_time}')[:16]

    def __str__(self):
        return self.name


class Parcel(models.Model):
    class Meta:
        db_table = 'project_parcel'
        unique_together = ['claim_no', 'project']
        ordering = ['-id']

    ch_status = (
        ('vacant', 'Vacant'),
        ('occupied', 'Occupied')
    )
    p_stages = (
        ('draft', 'Draft'),
        ('rejected', 'Rejected'),
        ('gis_approval', 'GIS Approval'),
        ('registered', 'Registered'),
        ('printed', 'Printed'),
    )

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    created_by = CurrentUserField()
    updated_by = CurrentUserField(
        on_update=True, related_name='deed_plan_updated_by')
    deleted = models.BooleanField(default=False)
    deed_plan = models.ForeignKey(
        DeedPlan, on_delete=models.CASCADE, null=True, blank=True)
    project = models.ForeignKey(
        'nluis_projects.Project', on_delete=models.CASCADE, blank=True, null=True)
    claim_no = models.CharField(max_length=50)
    claim_date = models.DateTimeField(blank=True, null=True)
    current_use = models.ForeignKey(
        'nluis_setups.LandUse', on_delete=models.SET_NULL, null=True, blank=True)
    proposed_use = models.ForeignKey('nluis_setups.LandUse', on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='proposed')
    occupancy_type = models.ForeignKey(
        'nluis_setups.OccupancyType', on_delete=models.SET_NULL, null=True, blank=True)
    vac_1 = models.CharField(max_length=50, null=True, blank=True)
    vac_2 = models.CharField(max_length=50, null=True, blank=True)

    locality = models.ForeignKey(
        'nluis_localities.Locality', on_delete=models.CASCADE, blank=True, null=True)
    hamlet = models.ForeignKey('nluis_localities.Locality', on_delete=models.CASCADE, blank=True, null=True,
                               related_name='hamlets')

    topology = models.CharField(max_length=50, blank=True, null=True)
    north = models.CharField(max_length=250, blank=True, null=True)
    south = models.CharField(max_length=250, blank=True, null=True)
    east = models.CharField(max_length=250, blank=True, null=True)
    west = models.CharField(max_length=250, blank=True, null=True)
    status = models.CharField(
        max_length=50, default='vacant', choices=ch_status)
    stage = models.CharField(max_length=50, default='draft', choices=p_stages)

    uka_namba = models.CharField(
        max_length=50, unique=True, null=True, blank=True)
    registration_no = models.CharField(
        max_length=50, unique=True, null=True, blank=True)

    geom = GeometryField(blank=True, null=True)
    data_source = models.CharField(max_length=50, default='nluis')
    reference_id = models.IntegerField(default=0)
    documents = models.ManyToManyField(
        'nluis_projects.Document', blank=True)
    remarks = models.ManyToManyField('nluis_projects.Remark', blank=True)
    paras_comment = models.CharField(
        max_length=250, null=True, blank=True)

    def __str__(self):
        return self.claim_no

    def datetime(self):
        return str(f'{self.created_date} {self.created_time}')[:16]

    def project_info(self):
        return {
            'id': self.project.id,
            'name': self.project.name
        }

    def created_user(self):
        return self.created_by.username if self.created_by is not None else ''

    def last_remark(self):
        return self.remarks.values('description', 'action')

    def locality_info(self):
        try:
            return {
                'village': self.locality.name,
                'hamlet': self.hamlet.name
            }
        except Exception as e:
            print(e)
            return {
                'village': '',
                'hamlet': ''
            }

    def use(self):
        return self.proposed_use.name if self.proposed_use is not None else \
            self.current_use.name if self.current_use is not None else 'Not Approved'

    def occupancy(self):
        return self.occupancy_type.name if self.occupancy_type is not None else ''

    def parties(self):
        names = []
        for n in Allocation.objects.filter(parcel=self):
            names.append(n.party.fullname().replace("--", "'"))

        if len(names) == 0:
            try:
                answ = FormAnswer.objects.get(claim_no__istartswith=f'{self.claim_no}_mmi',
                                              form_field__flag='person_name')
            except Exception as e:
                pass
        return names

    def phones(self):
        names = []
        for n in Allocation.objects.filter(parcel=self):
            if n.party.phone is None:
                names.append('')
            else:
                names.append(n.party.phone.replace("--", "'"))
        return names

    def jinsi(self):
        names = []
        for n in Allocation.objects.filter(parcel=self):
            if n.party.gender is None:
                names.append('')
            else:
                names.append(n.party.gender)
        return names

    def kuzaliwa(self):
        names = []
        for n in Allocation.objects.filter(parcel=self):
            if n.party.dob is None:
                names.append('')
            else:
                names.append(n.party.dob)
        return names

    def ulemavu(self):
        names = []
        for n in Allocation.objects.filter(parcel=self):
            if n.party.disability is None:
                names.append('')
            else:
                names.append(n.party.disability)
        return names


    def idnamba(self):
        names = []
        for n in Allocation.objects.filter(parcel=self):
            if n.party.id_no is None:
                names.append('')
            else:
                names.append(n.party.id_no.replace('--', " "))
        return names


    def ndoa(self):
        names = []
        for n in Allocation.objects.filter(parcel=self):
            if n.party.marital is None:
                names.append('')
            else:
                names.append(n.party.marital.replace('--', " "))
        return names




    def get_parties_with_pictures(self):
        wamiliki = []
        for o in Allocation.objects.filter(parcel=self):
            name = str(o.party.fullname()).upper()
            try:
                picha = get_image_url(o.party.picture.url)
            except Exception as e:
                print(e)
                picha = ''

            wamiliki.append({
                'name': name,
                'pic': picha
            })
        return wamiliki

    def datetime(self):
        return str(f'{self.created_date} {self.created_time}')[:16]

    def area(self):
        try:
            from area import area
            return get_ukubwa(area(self.geom.geojson))
        except Exception as e:
            return '0'

    def district(self):
        return str(self.locality.parent.parent.name).split(' ')[0]


class Party(models.Model):
    class Meta:
        db_table = 'project_party'

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    created_by = CurrentUserField()
    updated_by = CurrentUserField(
        on_update=True, related_name='party_updated_by')
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(
        max_length=20, choices=(('M', 'Male'), ('F', 'Female')))
    dob = models.DateField(null=True, blank=True)
    picture = models.ImageField(upload_to='dp', blank=True, null=True)
    citizen = models.CharField(max_length=50, blank=True, null=True)
    id_type = models.CharField(max_length=50, blank=True, null=True)
    id_no = models.CharField(max_length=50, blank=True, null=True)
    id_pic = models.ImageField(upload_to='id_pic', blank=True, null=True)
    role = models.ForeignKey('nluis_setups.PartyRole',
                             null=True, blank=True, on_delete=models.SET_NULL)
    acquire = models.CharField(max_length=50, blank=True, null=True)
    marital = models.CharField(max_length=50, blank=True, null=True)
    disability = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(max_length=50, blank=True, null=True)
    address = models.CharField(max_length=50, blank=True, null=True)
    occupation = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.fullname()

    def fullname(self):
        return f'{self.first_name} {self.middle_name} {self.last_name}'.replace('--', "'")


    # def muda(self):
    #     return str(f'{self.created_date} {self.created_time}')[:16]
    #
    # def plots(self):
    #     try:
    #         return Allocation.objects.filter(party=self).values_list('deed_plan__claim_no')
    #     except Exception as e:
    #         return ''
    #
    # def value(self):
    #     return self.id

    # def label(self):
    #     return f'{self.fullname} - {self.phone} - {self.role}'
    #


class Allocation(models.Model):
    class Meta:
        db_table = 'project_parcel_allocation'
        unique_together = ['parcel', 'party']

    parcel = models.ForeignKey(
        Parcel, on_delete=models.DO_NOTHING, blank=True, null=True)
    party = models.ForeignKey(Party, on_delete=models.CASCADE)

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    created_by = CurrentUserField()
    updated_by = CurrentUserField(
        on_update=True, related_name='allocation_updated_by')

    def claim_no(self):
        return self.parcel.claim_no

    def uka(self):
        return self.parcel.uka_namba

    def regno(self):
        return self.parcel.registration_no

    def owner(self):
        return self.party.fullname()


class ProjectLayer(models.Model):
    class Meta:
        db_table = 'project_layers_spatial'

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    created_by = CurrentUserField()
    deleted = models.BooleanField(default=False)
    updated_by = CurrentUserField(
        on_update=True, related_name='layers_spatial_updated_by')

    locality = models.ForeignKey(
        'nluis_localities.Locality', on_delete=models.DO_NOTHING, blank=True, null=True)
    project = models.ForeignKey(
        'nluis_projects.Project', on_delete=models.DO_NOTHING, blank=True, null=True)
    map_type = models.ForeignKey(
        'nluis_setups.MapType', on_delete=models.DO_NOTHING, blank=True, null=True)
    label = models.CharField(max_length=50)
    description = models.CharField(max_length=50)
    srid = models.IntegerField()
    geom = GeometryField(blank=True, null=True)

    def map_type_name(self):
        return self.map_type.name

    def locality_name(self):
        return self.locality.name

    def project_name(self):
        return self.project.name


class Screen(models.Model):
    class Meta:
        db_table = 'screen'

    code = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=50, blank=True, null=True)
    order_number = models.IntegerField()

    def __str__(self):
        return self.name
