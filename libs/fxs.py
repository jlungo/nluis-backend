import os
import traceback
from dateutil.relativedelta import *

from decouple import config

alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
            'V', 'W', 'X', 'Y', 'Z']

#alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U','V', 'W', 'X', 'Y', 'Z',
#            'A0', 'B0', 'C0', 'D0', 'E0', 'F0', 'G0', 'H0', 'I0', 'J0', 'K0', 'L0', 'M0', 'N0', 'O0', 'P0', 'Q0', 'R0', 'S0', 'T0', 'U0','V0',
#            'W0', 'X0', 'Y0', 'Z0','A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'H1', 'I1', 'J1', 'K1', 'L1', 'M1', 'N1', 'O1', 'P1', 'Q1', 'R1',
#            'S1', 'T1', 'U1','V1','W1', 'X1', 'Y1', 'Z1']

def get_ukubwa(msqr, unit='sqm'):
    try:
        meters_sq = float("{:.3f}".format(msqr))

        acres = round(meters_sq * 0.000247105, 3)
        hactor = round(meters_sq / 10000, 3)
        return str(meters_sq if unit == 'sqm' else acres if unit == 'ac' else hactor)
    except Exception as e:
        print(e)
        traceback.print_exc()
        return '0'


def get_image_url(url):
    try:
        SERVER = config('SERVER_LOCAL')
        # base64.b64encode(requests.get(f'http://{SERVER}:{PORT}/{url}').content)
        return f'{SERVER}{url}'
    except Exception as e:
        print(e)
        traceback.print_exc()
        return ''


# create history
def save_history(project_id, action, remarks, task_id, screen_code=''):
    from nluis_projects.models import ProjectHistory
    from nluis_projects.models import Project
    hist = ProjectHistory(project=Project.objects.get(id=project_id), task_id=task_id,
                          action=action, remarks=remarks, screen_code=screen_code)
    hist.save()


def get_dates_year_deff(date1, date2):
    return relativedelta(date1, date2).years


def val_answer(claim_no, form_field_id, is_monitoring=0):
    try:

        from nluis_collect.models import FormAnswer, FormAnswerQuestionnaire
        if is_monitoring == 1:
            answer = FormAnswerQuestionnaire.objects.get(claim_no=claim_no, form_field_id=form_field_id)
        else:
            answer = FormAnswer.objects.get(claim_no=claim_no, form_field_id=form_field_id)
        response = answer.response
        data_type = answer.form_field.data_type

        if data_type == 'polygon':
            if response is not None:
                return 'View on Map'
        if data_type == 'village' or data_type == 'hamlet' \
                or data_type == 'ward' or data_type == 'council'\
                or data_type == 'region':
            from nluis_localities.models import Locality
            return Locality.objects.get(id=int(response)).name
        if data_type == 'land_use':
            from nluis_setups.models import LandUse
            return LandUse.objects.get(id=int(response)).name
        if data_type == 'occupancy':
            from nluis_setups.models import OccupancyType
            return OccupancyType.objects.get(id=int(response)).name
        if data_type == 'file':
            return answer.file

        return response
    except Exception as e:
        print(e)
        return ''


def val_answer_list(form_field_id):
    try:

        from nluis_collect.models import FormAnswer
        return FormAnswer.objects.filter(form_field_id=form_field_id).values_list('response')
    except Exception as e:
        return ''


def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file),
                       os.path.relpath(os.path.join(root, file),
                                       os.path.join(path, '..')))


def register_parcel(parcel):
    try:
        print('Here.......................')
        village = parcel.locality
        hamlet = parcel.hamlet
        district = village.parent.parent

        from nluis_setups.models import LocalityDocumentCounter
        counter = LocalityDocumentCounter.objects.get(locality=village)

        from nluis_projects.models import Parcel
        count_ccro = Parcel.objects.filter(locality=village, uka_namba__isnull=False).count() + counter.count + 1

        print(f'count_ccro = {count_ccro}')

        count_district = LocalityDocumentCounter.objects.filter(locality=district).last().count + 1

        count_district_count = count_district + Parcel.objects.filter(locality__parent__parent=district,
                                                                      uka_namba__isnull=False).count()
        lead_count_ccro = "{:04}".format(count_ccro)
        print(f'count_ccro = {count_ccro} => {lead_count_ccro}')

        lead_count_district_count = "{:04}".format(count_district_count)

        code = str(village.registration_code)[0:3]
        vicode = village.registration_code.replace(code, '')
        uka = str(f'{district.registration_code}/{vicode}/{hamlet.registration_code}/{lead_count_ccro}')
        print(f'count_ccro = {count_ccro} => {lead_count_ccro}=>{uka}')
        reg_no = f'{district.registration_code}/{code}/{lead_count_district_count}'
        # reg_no = f'{village.registration_code}{lead_count_district_count}'

        if parcel.uka_namba is None:
            parcel.uka_namba = str(uka).upper()
        if parcel.registration_no is None:
            parcel.registration_no = str(reg_no).upper()

        parcel.stage = 'registered'
    except Exception as e:
        print(e)
        traceback.print_exc()

    return parcel


def val_none_str(no):
    if no is None:
        return ""
    return no


def str_to_list(word, number=True):
    lst = []
    word = str(word).replace('[', '').replace(']', '')
    if ',' in word:
        for w in word.split(','):
            if number:
                lst.append(int(w))
            else:
                lst.append(w)
    else:
        if number:
            try:
                lst.append(int(word))
            except Exception as e:
                pass
        else:
            lst.append(word)
    return lst


def check_image_url_exists_answers(answer_id, claim_no):
    from nluis_collect.models import FormAnswer
    obj = FormAnswer.objects.get(id=answer_id)  # Get an instance of your model containing the ImageField

    try:
        url = obj.picture.url

        file_path = f'/var/www/nluis{url}'  # Replace with the path to the file you want to check

        if os.path.isfile(file_path):
            print(f"{claim_no}...File exists!")
        else:
            # print("File does not exist or is not a regular file.")
            # print("Image URL does not exist.")

            claim_no = str(claim_no).replace("/", "__")

            directory = '/var/www/nluis/media/mobile'  # Replace with the directory path where you want to search
            prefix = f'{claim_no}_mmiliki'  # The prefix of the file name you are searching for

            # print(prefix)

            # List all files in the directory
            files = os.listdir(directory)

            # Iterate over the files and find the one with the desired prefix
            for file_name in files:
                # 75__1034__193_mmiliki
                if file_name.startswith(prefix):
                    # Full path to the file
                    file_path = os.path.join(directory, file_name)
                    print(f"Found file: {file_path}")

                    from django.core.files import File

                    with open(file_path, 'rb') as f:
                        django_file = File(f)

                        # Create an instance of your model and assign the ImageField

                        obj.image.save('image.jpg', django_file, save=True)
                        obj.save()

                    break  # If you want to stop searching after finding the first match
            # else:
            #     print("File not found.")

        # import requests
        # response = requests.head(url)  # Send a HEAD request to check the URL
        # if response.status_code == requests.codes.ok:
        #     print(f'IPO...{claim_no}')
        #     return True
    except Exception as e:
        pass


def check_image_url_exists(party_id, claim_no):
    from nluis_projects.models import Party
    obj = Party.objects.get(id=party_id)  # Get an instance of your model containing the ImageField

    try:
        url = obj.picture.url

        file_path = f'/var/www/nluis{url}'  # Replace with the path to the file you want to check

        if os.path.isfile(file_path):
            print(f"{claim_no}...File exists!")
        else:
            # print("File does not exist or is not a regular file.")
            # print("Image URL does not exist.")

            claim_no = str(claim_no).replace("/", "__")

            directory = '/var/www/nluis/media/mobile'  # Replace with the directory path where you want to search
            prefix = f'{claim_no}_mmiliki'  # The prefix of the file name you are searching for

            # print(prefix)

            # List all files in the directory
            files = os.listdir(directory)

            # Iterate over the files and find the one with the desired prefix
            for file_name in files:
                # 75__1034__193_mmiliki
                if file_name.startswith(prefix):
                    # Full path to the file
                    file_path = os.path.join(directory, file_name)
                    print(f"Found file: {file_path}")

                    from django.core.files import File

                    with open(file_path, 'rb') as f:
                        django_file = File(f)

                        # Create an instance of your model and assign the ImageField

                        obj.picture.save('image.jpg', django_file, save=True)
                        obj.save()

                    break  # If you want to stop searching after finding the first match
            # else:
            #     print("File not found.")

        # import requests
        # response = requests.head(url)  # Send a HEAD request to check the URL
        # if response.status_code == requests.codes.ok:
        #     print(f'IPO...{claim_no}')
        #     return True
    except Exception as e:
        pass
