from celery import shared_task


@shared_task()
def generate_transaction(parcel_id):
    import datetime
    import os
    import traceback
    import string

    from area import area
    from decouple import config

    from libs.fxs import get_ukubwa, get_image_url
    from nluis.settings import DOCS_OUTPUT, HTML_TEMPLATE_DIR
    from nluis_projects.models import ProjectSignatory, Party, Document
    try:
        from nluis_projects.models import Parcel
        parcel = Parcel.objects.get(id=parcel_id)
        # kijiji = parcel.locality.name.strip()
        # kitongoji = parcel.hamlet.name.strip()

        kijiji = parcel.locality.name.strip().replace("'", '_')
        kijiji = kijiji.replace(' ', '_')
        kijiji = kijiji.replace('"', '_')

        kitongoji = parcel.hamlet.name.strip().replace("'", '_')
        kitongoji = kitongoji.replace(' ', '_')
        kitongoji = kitongoji.replace('"', '_')

        uuid = 'uuid'

        out = f'{DOCS_OUTPUT}trans/{kijiji}/{kitongoji}'.replace("'", '_').replace(' ', '_').replace('"', '_')
        output = f'{out}/trans_{parcel_id}_{uuid}.pdf'


        try:
            if not os.path.exists(out):
                os.makedirs(out)
        except Exception as e:
            pass

        uka = str(parcel.uka_namba)
        regno = str(parcel.registration_no)

        leo = str(datetime.date.today()).split('-')  # Meeting Date

        tar_leo = leo[2]
        mwez_leo = leo[1]
        mwaka_leo = leo[0]

        tar_mpaka = '01'
        mwez_mpaka = '04' if int(mwez_leo) < 7 else "07"

        mwaka_mpaka = mwaka_leo
        matumizi = parcel.current_use.name

        uk = get_ukubwa(area(parcel.geom.geojson), 'ac')
        try:
            if float(uk) < 1.0:
                ukubwa = f"Mita za mraba {get_ukubwa(area(parcel.geom.geojson))}"
            else:
                ukubwa = f"Ekari {uk}"
        except Exception as e:
            ukubwa = f"Ekari {uk}"

        wilaya = parcel.district()

        kas = str(parcel.north).title().replace('--', "'")
        kus = str(parcel.south).title().replace('--', "'")
        mash = str(parcel.east).title().replace('--', "'")
        magh = str(parcel.west).title().replace('--', "'")

        vc = ProjectSignatory.objects.get(project_id=parcel.project.id, locality=parcel.locality,
                                          designation__name='VC')  # .get(layer=layer, design='vc' pro)
        ve = ProjectSignatory.objects.get(project_id=parcel.project.id, locality=parcel.locality,
                                          designation__name='VEO')
        alo = ProjectSignatory.objects.get(project_id=parcel.project.id, locality=parcel.locality,
                                           designation__name='ALO')

        mwenyekiti = vc.fullname()
        vc_sign_base_64 = str(get_image_url(vc.signature.url)).replace("b'", '')
        vc_sign_base_64 = str(vc_sign_base_64).replace("''", "'")

        mtendaji = ve.fullname()
        ve_sign_base_64 = str(get_image_url(ve.signature.url)).replace("b'", '')
        ve_sign_base_64 = str(ve_sign_base_64).replace("''", "'")

        address = string.capwords(str(parcel.locality.address))
        slp = f"S.L.P {address}".replace('-', ' ')

        alo_name = alo.fullname()
        alo_sign_base_64 = str(get_image_url(alo.signature.url)).replace("b'", '')
        alo_sign_base_64 = str(alo_sign_base_64).replace("''", "'")

        htmlTemplateFile = f'{HTML_TEMPLATE_DIR}base_trans.html'

        with open(htmlTemplateFile, 'r') as file:
            doc = file.read()

            doc = doc.replace("$uka", uka)
            doc = doc.replace("$aloSign", str(alo_sign_base_64))
            doc = doc.replace("$regno", regno)
            doc = doc.replace("$leoTarehe",
                              "<b>" + tar_leo + "-" + mwez_leo + "-" + mwaka_leo + "</b>")
            doc = doc.replace("$kijiji", kijiji)
            doc = doc.replace("$tanguTarehe",
                              "<b>" + tar_mpaka + "-" + mwez_mpaka + "-" + mwaka_mpaka + "</b>")
            doc = doc.replace("$matumizi", matumizi)
            doc = doc.replace("$ukubwa", ukubwa)
            doc = doc.replace("$wilaya", wilaya)
            doc = doc.replace("$kitongoji", kitongoji)
            doc = doc.replace("$kaskazini", kas)
            doc = doc.replace("$kusini", kus)
            doc = doc.replace("$mashariki", mash)
            doc = doc.replace("$magharibi", magh)
            doc = doc.replace("$mwenyekiti", mwenyekiti)
            doc = doc.replace("$vcSign", str(vc_sign_base_64))
            doc = doc.replace("$mtendaji", mtendaji)
            doc = doc.replace("$jinaWilaya", wilaya)
            doc = doc.replace("$veSign", str(ve_sign_base_64))
            doc = doc.replace("$slp", slp)

            wamiliki = parcel.get_parties_with_pictures()
            doc = doc.replace("$wa_pili", "table-row" if len(wamiliki) > 1 else "none")

            if len(wamiliki) > 0:
                names = "<b>" + str(wamiliki[0]['name']).upper() + "</b>"
                name1 = names
                # pic1 = wamiliki[0]['pic']
                doc = doc.replace("$mmiliki1", name1)
                # doc = doc.replace("$waKwanza", pic1)
            else:
                doc = doc.replace("$mmiliki1", '')

            doc = doc.replace("$mmiliki2", '')

            if len(wamiliki) > 1:
                name2 = "<b>" + str(wamiliki[1]['name']).upper() + "</b>"
                doc = doc.replace("$mmiliki2", name2)

            doc = doc.replace("$aloJina", alo_name)
            doc = doc.replace("$wa_pili", "table-row" if len(wamiliki) > 1 else "none")
            # doc = doc.replace("$wamiliki", names)

            newHtmlFileParent = f'{HTML_TEMPLATE_DIR}deed/trans'

            if not os.path.isdir(newHtmlFileParent):
                try:
                    os.makedirs(newHtmlFileParent)
                except Exception as e:
                    traceback.print_exc()
                    pass

            newHtmlFile = f"{newHtmlFileParent}/trans_{str(parcel_id)}.html"

            with open(newHtmlFile, "w") as text_file:
                text_file.write(doc)

        try:
            os.system(
                "wkhtmltopdf  -B 14 -L 14 -R 14 -T 14   -O Landscape -s A3 --title TRANSACTION --copies 3 --enable-local-file-access --debug-javascript "
                f"{newHtmlFile} " + output)
        except Exception as e:
            pass

        # parcel.trans = output
        # deed.save(update_fields=['trans'])

        print(output)

        from nluis_setups.models import DocumentType

        with open(output, 'rb') as fi:
            from django.core.files import File
            _file = File(fi, name=os.path.basename(fi.name))

            if parcel.uka_namba is None:
                uka = ""
            else:
                uka = parcel.uka_namba

            trans = Document(project=parcel.project,
                             locality=parcel.locality,
                             document_type=DocumentType.objects.get(code='transaction_sheet',
                                                                    project_type=parcel.project.project_type,
                                                                    is_input=False),
                             description=uka, file=_file)
            trans.save()
            parcel.documents.add(trans)
        return {
            'status': 1,
            'message': 'success',
            'path': output.replace('/data/nluis', config('FILE_SERVER'))
        }
    except Exception as e:
        print(e)
        traceback.print_exc()
        return {
            'status': 0,
            'message': str(e),
            'path': ''
        }
