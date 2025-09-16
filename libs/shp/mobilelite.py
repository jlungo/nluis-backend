import os
import sqlite3
import uuid
import zipfile
from time import sleep
from celery import shared_task
from nluis.settings import UPLOADS_ROOT, MEDIA_ROOT
from nluis_localities.models import Locality
from nluis_projects.models import TeamMember, Project


@shared_task
def zakaria(l):
    for i in range(l):
        print(i)
        sleep(2)
        # update_state(state='PROGRESS',
        #                   meta={'current': i, 'total': l})

    print('Task completed')
    return {'current': l, 'total': l, }


@shared_task()
def populate_mobile_data(user_id, file_path):
    try:
        uid = uuid.uuid4().hex[0:4]
        directory_to_extract_to = f'{MEDIA_ROOT}mobile/{uid}'
        # directory_to_extract_to = f'{MEDIA_ROOT}mobile'
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(directory_to_extract_to)

        db = ''
        save_hist = False
        for f in os.listdir(directory_to_extract_to):

            if str(f.lower()).endswith('_.sqlite3'):  # and str(f.lower()).startswith(str(user_id)):

                try:
                    db = f'{directory_to_extract_to}/{f}'
                    conn = sqlite3.connect(db)

                    cursor = conn.execute("SELECT * from tb_answer")

                    for row in cursor:
                        try:
                            # print(row)
                            id = row[0]
                            date = row[1]
                            claim = row[2]
                            qn_id = int(row[3])
                            answ = row[4]

                            para_surveyor = TeamMember.objects.get(id=int(str(claim).split('/')[0]))
                            hamlet = Locality.objects.get(id=int(str(claim).split('/')[1]))

                            from nluis_collect.models import FormField
                            qn = FormField.objects.get(id=qn_id)
                            image = None
                            file = None
                            polygon = None

                            if qn.data_type == 'image':
                                try:
                                    pic = answ.split('/zaka/')[1]
                                    image = f"{directory_to_extract_to.split('media/')[1]}/{pic}"
                                    print(image)
                                except Exception as e:
                                    print(e)

                            if qn.data_type == 'polygon':
                                polygon = answ

                            from nluis_collect.models import FormAnswer, FormAnswerQuestionnaire
                            if para_surveyor.project.project_type.code == 'CCRO':

                                answer = FormAnswer(
                                    project=para_surveyor.project,
                                    para_surveyor=para_surveyor,
                                    locality=hamlet,
                                    local_answer_id=id,
                                    local_answer_date=date,
                                    claim_no=claim,
                                    form_field=qn,
                                    response=answ,
                                    image=image,
                                    file=file,
                                    geom=polygon
                                )
                                answer.save()
                            else:
                                answer = FormAnswerQuestionnaire(
                                    project=para_surveyor.project,
                                    para_surveyor=para_surveyor,
                                    locality=hamlet,
                                    local_answer_id=id,
                                    local_answer_date=date,
                                    claim_no=claim,
                                    form_field=qn,
                                    response=answ,
                                    image=image,
                                    file=file,
                                    geom=polygon
                                )
                                answer.save()

                            if not save_hist:
                                from libs.fxs import save_history
                                save_history(para_surveyor.project_id, 'Create',
                                             f'{answer.id} was created', 9, 'ccro_draft_data')
                                save_hist = True

                        except Exception as e:
                            print(e)
                            pass
                    cursor.close()

                    conn.close()
                except Exception as e:
                    print(e)
                    pass

        # print(db)

        # shutil.rmtree(directory_to_extract_to)

        return {
            'status': 1,
            'message': ''
        }
    except Exception as e:
        return {
            'status': 0,
            'message': str(e)
        }


@shared_task()
def populate_mobile_data2(user_id, file_path, project_id):
    try:
        uid = uuid.uuid4().hex[0:4]
        # directory_to_extract_to = f'{MEDIA_ROOT}mobile/{uid}'
        directory_to_extract_to = f'{MEDIA_ROOT}mobile'
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(directory_to_extract_to)

        db = ''
        save_hist = False
        project = Project.objects.get(id=project_id)
        for f in os.listdir(directory_to_extract_to):

            if str(f.lower()).endswith('_.sqlite3') and str(f.lower()).startswith(str(user_id)):

                try:
                    db = f'{directory_to_extract_to}/{f}'
                    conn = sqlite3.connect(db)

                    cursor = conn.execute("SELECT * from tb_answer")

                    for row in cursor:
                        try:
                            # print(row)
                            id = row[0]
                            date = row[1]
                            claim = row[2]
                            qn_id = int(row[3])
                            answ = row[4]

                            para_surveyor = TeamMember.objects.get(id=int(str(claim).split('/')[0]))
                            hamlet = Locality.objects.get(id=int(str(claim).split('/')[1]))

                            from nluis_collect.models import FormField
                            qn = FormField.objects.get(id=qn_id)
                            image = None
                            file = None
                            polygon = None

                            if qn.data_type == 'image':
                                try:
                                    pic = answ.split('/zaka/')[1]
                                    image = f"{directory_to_extract_to.split('media/')[1]}/{pic}"
                                    print(image)
                                except Exception as e:
                                    print(e)

                            if qn.data_type == 'polygon':
                                polygon = answ

                            from nluis_collect.models import FormAnswer
                            answer = FormAnswer(
                                project=project,
                                para_surveyor=para_surveyor,
                                locality=hamlet,
                                local_answer_id=id,
                                local_answer_date=date,
                                claim_no=claim,
                                form_field=qn,
                                response=answ,
                                image=image,
                                file=file,
                                geom=polygon
                            )
                            answer.save()

                            if not save_hist:
                                from libs.fxs import save_history
                                save_history(para_surveyor.project_id, 'Create',
                                             f'{answer.id} was created', 9, 'ccro_draft_data')
                                save_hist = True

                        except Exception as e:
                            print(e)
                            pass
                    cursor.close()

                    conn.close()
                except Exception as e:
                    print(e)
                    pass

        # print(db)

        # shutil.rmtree(directory_to_extract_to)

        return {
            'status': 1,
            'message': ''
        }
    except Exception as e:
        return {
            'status': 0,
            'message': str(e)
        }
