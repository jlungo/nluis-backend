from celery import shared_task, current_task


# @app.task(bind=True)
@shared_task
def download_shp(village_id, project_id):
    from nluis_localities.models import Locality
    from nluis_collect.models import Category
    from nluis_collect.models import FormField
    import shapefile
    from nluis_collect.models import FormAnswer
    from libs.fxs import val_answer
    import json
    import traceback
    import time

    subw = Locality.objects.get(id=village_id)

    date = subw.name  # uuid.uuid4().hex + '_'  # request.user.username
    from nluis.settings import UPLOADS_ROOT
    out = f'{UPLOADS_ROOT}{date}'

    try:
        import os
        os.makedirs(out)
    except OSError as e:
        pass

    from nluis_projects.models import Project
    proj = Project.objects.get(id=project_id)
    data = []

    for categories in Category.objects.filter(project_type=proj.project_type).filter(flag='dodoso'):
        categories_questions = []

        for qn in FormField.objects.filter(form__category=categories):
            categories_questions.append({
                'id': qn.id,
                'name': qn.form_field
            })

        data.append(categories_questions)

    w = shapefile.Writer(f'{out}/{date}', shapefile.POLYGON)

    w.field('PID', 'N', '40')
    w.field('CLAIM_NO', 'C', '40')
    w.field('DATE_', 'C', '40')
    w.field('PARAS', 'C', '100')
    w.field('VILLAGE', 'C', '100')
    w.field('HAMLET', 'C', '100')
    w.field('PARTIES', 'C', '100')

    for d in data[0]:
        title = str(d['name']).replace('(', '')
        title = title.replace(')', '')
        title = title.replace('\'', '')
        w.field(title, 'C', '100')

    # answers = []

    from nluis_projects.models import Parcel
    lst_claims = Parcel.objects.filter(locality=village_id).values_list('claim_no')
    qs_answer = FormAnswer.objects.exclude(claim_no__in=lst_claims).filter(form_field__form__category__flag='dodoso',
                                                                           response__istartswith='polygon',
                                                                           locality__parent=subw).order_by(
        'claim_no').distinct('claim_no')
    count_process = 0
    total = qs_answer.count()

    for d in qs_answer:

        ans = []

        try:

            for qn in data[0]:
                try:
                    jibu = FormAnswer.objects.get(claim_no=d.claim_no, form_field_id=qn['id'])
                    resp = jibu.response
                    if resp.lower().startswith('polygon'):
                        resp = 'Spatial Unit'

                        wamiliki = ''
                        try:
                            for mm in FormAnswer.objects.filter(form_field__flag='person_name',
                                                                claim_no__startswith=f'{d.claim_no}_'):
                                wamiliki += mm.response + ", "
                        except Exception as e:
                            pass

                        w.poly(json.loads(jibu.geom.geojson)['coordinates'])

                        if len(data[0]) == 14:
                            q = data[0]
                            try:
                                hm = Locality.objects.get(id=int(str(d.claim_no).split('/')[1]))

                                w.record(
                                    jibu.id,
                                    d.claim_no,
                                    d.local_answer_date,
                                    d.para_surveyor.user.username,
                                    hm.parent.name,
                                    hm.name,
                                    wamiliki,
                                    val_answer(d.claim_no, form_field_id=q[0]['id']),
                                    val_answer(d.claim_no, form_field_id=q[1]['id']),
                                    val_answer(d.claim_no, form_field_id=q[2]['id']),
                                    val_answer(d.claim_no, form_field_id=q[3]['id']),
                                    val_answer(d.claim_no, form_field_id=q[4]['id']),
                                    val_answer(d.claim_no, form_field_id=q[5]['id']),
                                    val_answer(d.claim_no, form_field_id=q[6]['id']),
                                    val_answer(d.claim_no, form_field_id=q[7]['id']),
                                    val_answer(d.claim_no, form_field_id=q[8]['id']),
                                    val_answer(d.claim_no, form_field_id=q[9]['id']),
                                    val_answer(d.claim_no, form_field_id=q[10]['id']),
                                    val_answer(d.claim_no, form_field_id=q[11]['id']),
                                    val_answer(d.claim_no, form_field_id=q[12]['id']),
                                    val_answer(d.claim_no, form_field_id=q[13]['id'])
                                )
                            except Exception as e:
                                pass
                        if len(data[0]) == 15:
                            q = data[0]

                            try:
                                hm = Locality.objects.get(id=int(str(d.claim_no).split('/')[1]))
                                w.record(
                                    jibu.id,
                                    d.claim_no,
                                    d.local_answer_date,
                                    d.para_surveyor.user.username,
                                    hm.parent.name,
                                    hm.name,
                                    wamiliki,
                                    val_answer(d.claim_no, form_field_id=q[0]['id']),
                                    val_answer(d.claim_no, form_field_id=q[1]['id']),
                                    val_answer(d.claim_no, form_field_id=q[2]['id']),
                                    val_answer(d.claim_no, form_field_id=q[3]['id']),
                                    val_answer(d.claim_no, form_field_id=q[4]['id']),
                                    val_answer(d.claim_no, form_field_id=q[5]['id']),
                                    val_answer(d.claim_no, form_field_id=q[6]['id']),
                                    val_answer(d.claim_no, form_field_id=q[7]['id']),
                                    val_answer(d.claim_no, form_field_id=q[8]['id']),
                                    val_answer(d.claim_no, form_field_id=q[9]['id']),
                                    val_answer(d.claim_no, form_field_id=q[10]['id']),
                                    val_answer(d.claim_no, form_field_id=q[11]['id']),
                                    val_answer(d.claim_no, form_field_id=q[12]['id']),
                                    val_answer(d.claim_no, form_field_id=q[13]['id']),
                                    val_answer(d.claim_no, form_field_id=q[14]['id'])
                                )
                            except Exception as e:
                                pass
                        if len(data[0]) == 16:
                            q = data[0]
                            try:
                                hm = Locality.objects.get(id=int(str(d.claim_no).split('/')[1]))
                                w.record(
                                    jibu.id,
                                    d.claim_no,
                                    d.local_answer_date,
                                    d.para_surveyor.user.username,
                                    hm.parent.name,
                                    hm.name,
                                    wamiliki,
                                    val_answer(d.claim_no, form_field_id=q[0]['id']),
                                    val_answer(d.claim_no, form_field_id=q[1]['id']),
                                    val_answer(d.claim_no, form_field_id=q[2]['id']),
                                    val_answer(d.claim_no, form_field_id=q[3]['id']),
                                    val_answer(d.claim_no, form_field_id=q[4]['id']),
                                    val_answer(d.claim_no, form_field_id=q[5]['id']),
                                    val_answer(d.claim_no, form_field_id=q[6]['id']),
                                    val_answer(d.claim_no, form_field_id=q[7]['id']),
                                    val_answer(d.claim_no, form_field_id=q[8]['id']),
                                    val_answer(d.claim_no, form_field_id=q[9]['id']),
                                    val_answer(d.claim_no, form_field_id=q[10]['id']),
                                    val_answer(d.claim_no, form_field_id=q[11]['id']),
                                    val_answer(d.claim_no, form_field_id=q[12]['id']),
                                    val_answer(d.claim_no, form_field_id=q[13]['id']),
                                    val_answer(d.claim_no, form_field_id=q[14]['id']),
                                    val_answer(d.claim_no, form_field_id=q[15]['id'])
                                )
                            except Exception as e:
                                print(e)
                                pass
                        if len(data[0]) == 17:
                            q = data[0]
                            try:
                                hm = Locality.objects.get(id=int(str(d.claim_no).split('/')[1]))
                                w.record(
                                    jibu.id,
                                    d.claim_no,
                                    d.local_answer_date,
                                    d.para_surveyor.user.username,
                                    hm.parent.name,
                                    hm.name,
                                    wamiliki,
                                    val_answer(d.claim_no, form_field_id=q[0]['id']),
                                    val_answer(d.claim_no, form_field_id=q[1]['id']),
                                    val_answer(d.claim_no, form_field_id=q[2]['id']),
                                    val_answer(d.claim_no, form_field_id=q[3]['id']),
                                    val_answer(d.claim_no, form_field_id=q[4]['id']),
                                    val_answer(d.claim_no, form_field_id=q[5]['id']),
                                    val_answer(d.claim_no, form_field_id=q[6]['id']),
                                    val_answer(d.claim_no, form_field_id=q[7]['id']),
                                    val_answer(d.claim_no, form_field_id=q[8]['id']),
                                    val_answer(d.claim_no, form_field_id=q[9]['id']),
                                    val_answer(d.claim_no, form_field_id=q[10]['id']),
                                    val_answer(d.claim_no, form_field_id=q[11]['id']),
                                    val_answer(d.claim_no, form_field_id=q[12]['id']),
                                    val_answer(d.claim_no, form_field_id=q[13]['id']),
                                    val_answer(d.claim_no, form_field_id=q[14]['id']),
                                    val_answer(d.claim_no, form_field_id=q[15]['id']),
                                    val_answer(d.claim_no, form_field_id=q[16]['id'])
                                )
                            except Exception as e:
                                print(e)
                                pass
                        if len(data[0]) == 18:
                            q = data[0]
                            try:
                                hm = Locality.objects.get(id=int(str(d.claim_no).split('/')[1]))
                                w.record(
                                    jibu.id,
                                    d.claim_no,
                                    d.local_answer_date,
                                    d.para_surveyor.user.username,
                                    hm.parent.name,
                                    hm.name,
                                    wamiliki,
                                    val_answer(d.claim_no, form_field_id=q[0]['id']),
                                    val_answer(d.claim_no, form_field_id=q[1]['id']),
                                    val_answer(d.claim_no, form_field_id=q[2]['id']),
                                    val_answer(d.claim_no, form_field_id=q[3]['id']),
                                    val_answer(d.claim_no, form_field_id=q[4]['id']),
                                    val_answer(d.claim_no, form_field_id=q[5]['id']),
                                    val_answer(d.claim_no, form_field_id=q[6]['id']),
                                    val_answer(d.claim_no, form_field_id=q[7]['id']),
                                    val_answer(d.claim_no, form_field_id=q[8]['id']),
                                    val_answer(d.claim_no, form_field_id=q[9]['id']),
                                    val_answer(d.claim_no, form_field_id=q[10]['id']),
                                    val_answer(d.claim_no, form_field_id=q[11]['id']),
                                    val_answer(d.claim_no, form_field_id=q[12]['id']),
                                    val_answer(d.claim_no, form_field_id=q[13]['id']),
                                    val_answer(d.claim_no, form_field_id=q[14]['id']),
                                    val_answer(d.claim_no, form_field_id=q[15]['id']),
                                    val_answer(d.claim_no, form_field_id=q[16]['id']),
                                    val_answer(d.claim_no, form_field_id=q[17]['id'])
                                )
                            except Exception as e:
                                print(e)
                                pass
                        if len(data[0]) == 19:
                            q = data[0]
                            try:
                                hm = Locality.objects.get(id=int(str(d.claim_no).split('/')[1]))
                                w.record(
                                    jibu.id,
                                    d.claim_no,
                                    d.local_answer_date,
                                    d.para_surveyor.user.username,
                                    hm.parent.name,
                                    hm.name,
                                    wamiliki,
                                    val_answer(d.claim_no, form_field_id=q[0]['id']),
                                    val_answer(d.claim_no, form_field_id=q[1]['id']),
                                    val_answer(d.claim_no, form_field_id=q[2]['id']),
                                    val_answer(d.claim_no, form_field_id=q[3]['id']),
                                    val_answer(d.claim_no, form_field_id=q[4]['id']),
                                    val_answer(d.claim_no, form_field_id=q[5]['id']),
                                    val_answer(d.claim_no, form_field_id=q[6]['id']),
                                    val_answer(d.claim_no, form_field_id=q[7]['id']),
                                    val_answer(d.claim_no, form_field_id=q[8]['id']),
                                    val_answer(d.claim_no, form_field_id=q[9]['id']),
                                    val_answer(d.claim_no, form_field_id=q[10]['id']),
                                    val_answer(d.claim_no, form_field_id=q[11]['id']),
                                    val_answer(d.claim_no, form_field_id=q[12]['id']),
                                    val_answer(d.claim_no, form_field_id=q[13]['id']),
                                    val_answer(d.claim_no, form_field_id=q[14]['id']),
                                    val_answer(d.claim_no, form_field_id=q[15]['id']),
                                    val_answer(d.claim_no, form_field_id=q[16]['id']),
                                    val_answer(d.claim_no, form_field_id=q[17]['id']),
                                    val_answer(d.claim_no, form_field_id=q[18]['id'])
                                )
                            except Exception as e:
                                print(e)
                                pass

                    ans.append({
                        'id': jibu.id,
                        'jibu': resp
                    })
                except Exception as e:
                    ans.append({
                        'id': 0,
                        'jibu': ''
                    })
            # answers.append(ans)
        except Exception as e:
            print(e)

            traceback.print_exc()

        current_task.update_state(state='PROGRESS',
                                  meta={'current': count_process, 'total': total})

        count_process = count_process + 1

    try:
        prj = open(f'{out}/{date}.prj', 'w')
        proyeccion = "'GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]]," \
                     "PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]' "
        prj.write(proyeccion)

        for i in range(0, 5):
            time.sleep(1)

        # shutil.make_archive(out, 'zip', out)

        # with zipfile.ZipFile('file1.zip', 'w') as ff:
        #     for (dirpath, dirnames, filenames) in os.walk(out):
        #         # zip.write(filenames, basename(filenames))
        #         for f in filenames:
        #             file = f'{dirpath}/{f}'
        #             print(file)
        #             ff.write(file)
        #
        # zip.write(out, out)
        # zip.close()
        # shutil.make_archive(out, "zip", out)

        # zip_file = open(f'{out}.zip', 'rb')

        # response = HttpResponse(zip_file, content_type='application/zip')
        # response['Content-Disposition'] = 'attachment; filename=name.zip'

        # try:
        #     shutil.rmtree(out)
        #     os.remove(f'{out}.zip')
        # except Exception as e:
        #     print(e)

        # print(date)
        # return response

        # Create zip
        # buffer = io.BytesIO()
        # zipfile = open(f'{out}.zip', 'rb')
        # zip_file = zipfile.ZipFile(buffer, 'w')
        # zip_file.writestr(filename, response.content)
        # zip_file.close()
        # Return zip
        # response = HttpResponse(zipfile.read())
        # response = HttpResponse(FileWrapper(open(f'{out}.zip', 'rb')), content_type='application/zip')
        # response['Content-Type'] = 'application/force-download'
        # response['Content-Disposition'] = 'attachment; filename=' + f'{date}.zip'

        # return response

        # zip_file = open(f'{out}.zip', 'rb')
        # response = Response(File(zip_file), content_type='application/zip')
        # response['Content-Disposition'] = 'attachment; filename="%s"' % f'{date}.zip'
        # return response
        # return Response({
        #     'status': status,
        #     'data': f'{date}.zip'
        # })

    except Exception as e:
        print(e)
        traceback.print_exc()

    # return Response({
    #     'status': status,
    #     'message': message
    # })




@shared_task()
def qn_download_shp(village_id, project_id):
    from nluis_localities.models import Locality
    from nluis_collect.models import Category
    from nluis_collect.models import FormField
    import shapefile
    from nluis_collect.models import FormAnswer
    from libs.fxs import val_answer
    import json
    import traceback
    import time

    subw = Locality.objects.get(id=village_id)

    date = subw.name  # uuid.uuid4().hex + '_'  # request.user.username
    from nluis.settings import UPLOADS_ROOT
    out = f'{UPLOADS_ROOT}{date}'

    try:
        import os
        os.makedirs(out)
    except OSError as e:
        pass

    from nluis_projects.models import Project
    proj = Project.objects.get(id=project_id)
    data = []

    for categories in Category.objects.filter(project_type=proj.project_type).filter(flag='dodoso'):
        categories_questions = []

        for qn in FormField.objects.filter(form__category=categories):
            categories_questions.append({
                'id': qn.id,
                'name': qn.form_field
            })

        data.append(categories_questions)

    w = shapefile.Writer(f'{out}/{date}', shapefile.POLYGON)

    w.field('PID', 'N', '40')
    w.field('CLAIM_NO', 'C', '40')
    w.field('DATE_', 'C', '40')
    w.field('PARAS', 'C', '100')
    w.field('VILLAGE', 'C', '100')
    w.field('COORDINATE_TYPE', 'C', '100')
    w.field('LAND USE', 'C', '100')

    for d in data[0]:
        title = str(d['name']).replace('(', '')
        title = title.replace(')', '')
        title = title.replace('\'', '')
        w.field(title, 'C', '100')

    # answers = []

    from nluis_projects.models import Parcel
    qs_answer = FormAnswer.objects.filter(form_field__form__category__flag='dodoso',
                                        response__istartswith='polygon', locality__parent=subw).order_by(
                                        'claim_no').distinct('claim_no')
    count_process = 0
    total = qs_answer.count()

    for d in qs_answer:

        ans = []

        try:

            for qn in data[0]:
                try:
                    jibu = FormAnswer.objects.get(claim_no=d.claim_no, form_field_id=qn['id'])
                    resp = jibu.response
                    if resp.lower().startswith('polygon'):
                        resp = 'Spatial Unit'

                        w.poly(json.loads(jibu.geom.geojson)['coordinates'])

                        if len(data[0]) == 4:
                            q = data[0]
                            try:
                                hm = Locality.objects.get(id=int(str(d.claim_no).split('/')[1]))

                                w.record(
                                    jibu.id,
                                    d.claim_no,
                                    d.local_answer_date,
                                    d.para_surveyor.user.username,
                                    hm.name,
                                    val_answer(d.claim_no, form_field_id=q[0]['id']),
                                    val_answer(d.claim_no, form_field_id=q[1]['id']),
                                    val_answer(d.claim_no, form_field_id=q[2]['id']),
                                    val_answer(d.claim_no, form_field_id=q[3]['id']),
                                )
                            except Exception as e:
                                pass

                    ans.append({
                        'id': jibu.id,
                        'jibu': resp
                    })
                except Exception as e:
                    ans.append({
                        'id': 0,
                        'jibu': ''
                    })
            # answers.append(ans)
        except Exception as e:
            print(e)

            traceback.print_exc()

        current_task.update_state(state='PROGRESS',
                                  meta={'current': count_process, 'total': total})

        count_process = count_process + 1

    try:
        prj = open(f'{out}/{date}.prj', 'w')
        proyeccion = "'GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]]," \
                     "PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]' "
        prj.write(proyeccion)

        for i in range(0, 5):
            time.sleep(1)

    except Exception as e:
        print(e)
        traceback.print_exc()
