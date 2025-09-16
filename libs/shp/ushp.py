import os
import traceback
import uuid
import zipfile

from django.contrib.gis.gdal import DataSource
from django.contrib.gis.gdal.layer import Layer

from nluis.settings import UPLOADS_ROOT
from nluis_setups.models import LandUse


def read_shp(file_path):
    directory_to_extract_to = f'{UPLOADS_ROOT}shapefiles/{uuid.uuid4().hex}'
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        zip_ref.extractall(directory_to_extract_to)

    shp = ''
    layer = None
    for f in os.listdir(directory_to_extract_to):
        if os.path.isdir(f'{directory_to_extract_to}/{f}'):
            print('Dir')
        elif os.path.isfile(f'{directory_to_extract_to}/{f}'):
            # print('File')
            if f.lower().endswith('.shp'):
                shp = f'{directory_to_extract_to}/{f}'

    for ly in DataSource(shp):
        print(ly.fields)
        for col in ly:
            # col.get('NAME')
            # print(col.geom)
            pass
        layer = ly

    return layer


def verify_land_use_shp(file_path, file_id):
    try:
        has_code = []
        has_si = []
        has_name = False
        message = set()
        count = 0
        preview_list = []

        for ly in read_shp(file_path):
            if count == 0:
                if 'name' in ly.fields or 'NAME' in ly.fields or 'Name' in ly.fields:
                    has_name = True
            count = count + 1

            if 'code' in ly.fields or 'CODE' in ly.fields or 'Code' in ly.fields:
                try:
                    code = LandUse.objects.get(code__iexact=ly.get('Code'))
                    has_code.append(code is not None)
                    for si in code.geometry_type.si_unit['si_unit']:
                        try:
                            ly.get(si)
                        except Exception as e:
                            has_si.append(False)
                            message.add(si)
                except Exception as e:
                    message.add(ly.get('Code'))
                    has_code.append(False)

            preview_list.append(ly.geom.geojson)

        return {
            'has_code': False not in has_code,
            'has_name': has_name,
            'has_si_unit': False not in has_si,
            'preview_list': preview_list,
            'message': message
        }
    except Exception as e:
        print(e)
        traceback.print_exc()
        return {
            'has_code': False,
            'has_name': False,
            'has_si_unit': False,
            'preview_list': [],
            'message': [str(e)]
        }


def verify_plot(file_path, file_id):
    try:
        has_code = []
        has_si = []
        has_name = False
        message = set()
        count = 0
        preview_list = []

        for ly in read_shp(file_path):
            if count == 0:
                if 'plotnumber' in ly.fields or 'PLOTNUMBER' in ly.fields or 'Plotnumber' in ly.fields:
                    has_name = True
            count = count + 1

            preview_list.append(ly.geom.geojson)

        return {
            'has_code': False not in has_code,
            'has_name': has_name,
            'has_si_unit': False not in has_si,
            'preview_list': preview_list,
            'message': message
        }
    except Exception as e:
        print(e)
        traceback.print_exc()
        return {
            'has_code': False,
            'has_name': False,
            'has_si_unit': False,
            'preview_list': [],
            'message': [str(e)]
        }
