from django.shortcuts import render

# Create your views here.
from libs.docs.adjudication import generate_adjudication
from libs.docs.ccro import generate_ccro
from libs.docs.trans_sheet import generate_transaction
from libs.shp.ushp import read_shp, verify_land_use_shp
from nluis_localities.models import Locality
from nluis_setups.models import LandUse
from nluis_spatial.models import SpatialUnit


def test_logic():
    # generate_ccro.delay(2)

    lst_name = []
    for d in read_shp('/home/ugali/Videos/Wards.zip'):
        col = str(d.get('Ward_Name')).strip()
        if col not in lst_name:
            try:
                lst_name.append(col)
                # print(col)
                nm = str(d.get('District_C')).replace('-', ' ').strip()
                # region = Locality.objects.get(name=nm, level_id=7, registration_code=d.get(d.get('Region_Cod')))

                # region.geom = d.geom.geojson
                # region.save(update_fields=['geom'])
                # print(region)

                # parent = Locality.objects.get(level_id=3, name=nm)
                pnm = d.get('Region_Nam')
                parent = Locality.objects.get(level_id=2, registration_code=int(nm), parent__name__iexact=pnm)
                code = int(d.get('Ward_Code'))
                print(f'{parent} - {code}')

                # locality = Locality(name=col, level_id=6, geom=d.geom.geojson, parent=parent,registration_code=code)
                # locality.save()
                # print(parent)

            except Exception as e:
                print(e)

    # print(verify_land_use_shp('/home/ugali/Videos/mpango.zip', 1))

    # for d in read_shp('/home/ugali/Videos/BARABARA1.zip'):
    #     landuse = LandUse.objects.get(code__iexact=d.get('code'))
    #     if 'SQM' in str(landuse.geometry_type.si_unit):
    #         try:
    #             spatial_unit = SpatialUnit(geometry_type=landuse.geometry_type, land_use=landuse,
    #                                        locality=Locality.objects.get(id=234), width=0, length=0,
    #                                        description=d.get('Name'), sqm=d.get('sqm'), geom=d.geom.geojson)
    #             spatial_unit.save()
    #         except Exception as e:
    #             pass
    #     else:
    #         try:
    #             spatial_unit = SpatialUnit(geometry_type=landuse.geometry_type, land_use=landuse,
    #                                        locality=Locality.objects.get(id=234), width=d.get('width'),
    #                                        length=d.get('length'),
    #                                        description=d.get('Name'), sqm=0, geom=d.geom.geojson)
    #             spatial_unit.save()
    #         except Exception as e:
    #             print(e)
    #             pass
    # generate_adjudication.delay(2)
    pass
