import base64

from celery import shared_task


@shared_task()
def generate_ccro(parcel_id):
    import datetime
    import json
    import os
    import traceback
    import string

    from area import area
    from decouple import config
    from django.core.files import File

    from django.contrib.gis.geos import GEOSGeometry

    from libs.fxs import get_ukubwa, get_image_url, alphabet
    from nluis.settings import DOCS_OUTPUT, HTML_TEMPLATE_DIR
    from nluis_projects.models import ProjectSignatory, Party, Document
    from nluis_collect.models import FormAnswer

    try:
        from nluis_projects.models import Parcel
        parcel = Parcel.objects.get(id=parcel_id)

        kijiji = parcel.locality.name.strip().replace("'", '_')
        kijiji = kijiji.replace(' ', '_')
        kijiji = kijiji.replace('"', '_')

        kitongoji = parcel.hamlet.name.strip().replace("'", '_')
        kitongoji = kitongoji.replace(' ', '_')
        kitongoji = kitongoji.replace('"', '_')

        uuid = 'uuid'

        out = f'{DOCS_OUTPUT}ccro/{kijiji}/{kitongoji}'.replace("'", '_').replace(' ', '_').replace('"', '_')
        output = f'{out}/ccro_{parcel_id}_{uuid}.pdf'

        try:
            if not os.path.exists(out):
                os.makedirs(out)
                print('Creating DIRECTORY...............................')
        except Exception as e:
            traceback.print_exc()
            print(e)
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

        kas = str(parcel.north).title()
        kus = str(parcel.south).title()
        mash = str(parcel.east).title()
        magh = str(parcel.west).title()

        vc = ProjectSignatory.objects.get(project_id=parcel.project.id, locality=parcel.locality,
                                          designation__name='VC')  # .get(layer=layer, design='vc' pro)
        ve = ProjectSignatory.objects.get(project_id=parcel.project.id, locality=parcel.locality,
                                          designation__name='VEO')
        alo = ProjectSignatory.objects.get(project_id=parcel.project.id, locality=parcel.locality,
                                           designation__name='ALO')

        mwenyekiti = vc.fullname()
        vc_sign_base_64 = str(get_image_url(vc.signature.url)).replace("b'",
                                                                       '')  # str(base64.b64encode(vc.signature.read())).replace("b'", 'data:image/png;base64,')
        vc_sign_base_64 = str(vc_sign_base_64).replace("''", "'")

        mtendaji = ve.fullname()
        ve_sign_base_64 = str(get_image_url(ve.signature.url)).replace("b'",
                                                                       '')  # str(base64.b64encode(ve.signature.read())).replace("b'", 'data:image/png;base64,')
        ve_sign_base_64 = str(ve_sign_base_64).replace("''", "'")

        address = string.capwords(str(parcel.locality.address))
        slp = f"S.L.P {address}".replace('-', ' ')
        alo_name = alo.fullname()
        alo_sign_base_64 = str(get_image_url(alo.signature.url)).replace("b'",
                                                                         '')  # str(base64.b64encode(alo.signature.read())).replace("b'", 'data:image/png;base64,')
        alo_sign_base_64 = str(alo_sign_base_64).replace("''", "'")

        htmlTemplateFile = f'{HTML_TEMPLATE_DIR}base_ccro.html'

        with open(htmlTemplateFile, 'r') as file:
            doc = file.read()

            doc = doc.replace("$uka", uka)
            doc = doc.replace("$aloSign", str(alo_sign_base_64))
            doc = doc.replace("$regno", regno)
            doc = doc.replace("$leoTarehe",
                              "<b>" + tar_leo + "</b> mwezi <b>" + mwez_leo + "</b> mwaka <b>" + mwaka_leo + "</b>")
            doc = doc.replace("$kijiji", kijiji)
            doc = doc.replace("$tanguTarehe",
                              "<b>" + tar_mpaka + "</b> mwezi <b>" + mwez_mpaka + "</b> mwaka <b>" + mwaka_mpaka + "</b>")
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

                pic1 = str(wamiliki[0]['pic']).replace("b'", '')

                doc = doc.replace("$mmilikiWaKwanza", name1)
                if parcel.occupancy_type.swahili != 'Taasisi':
                    doc = doc.replace("$waKwanza", str(pic1))

            if len(wamiliki) > 1:
                name2 = "<b>" + str(wamiliki[1]['name']).upper() + "</b>"
                names += " na " + name2

                pic2 = str(wamiliki[1]['pic']).replace("b'", '')
                pic2 = str(pic2).replace("''", "'")
                doc = doc.replace("$mmilikiWaPili", name2)
                if parcel.occupancy_type.swahili != 'Taasisi':
                    doc = doc.replace("$waPiliPicha", str(pic2))

            cheo = 'Mmiliki (Mkazi)'
            pichaLakiri = 'PICHA'

            if parcel.occupancy_type.swahili == 'Taasisi':
                cheo = 'Wawakilishi'
                doc = doc.replace("$waKwanza", '')
                doc = doc.replace("$mmilikiWaPili", '')
                pichaLakiri = 'LAKIRI/MUHURI'
                doc = doc.replace("$waKwanza", '')
                doc = doc.replace("$waPiliPicha", '')

                try:
                    names = str(FormAnswer.objects.get(claim_no=parcel.claim_no,form_field__flag='taasisi').response).upper()
                    names = f'<b>{names}</b>'
                except Exception as e:
                    names = f'Hakuna jina la Taasisi {str(e)}'


            doc = doc.replace("$aloJina", alo_name)
            doc = doc.replace("$wamiliki", names)
            doc = doc.replace("$cheoChake", cheo)
            doc = doc.replace("$pichaLakiri",pichaLakiri)

            server_ip = config('GEOSERVER')

            lst_markers = ''
            listCoordinates = ''

            lst_point = []

            parcel.geom.transform(4326)
            parcel.save()

            coord = json.loads(parcel.geom.geojson)['coordinates'][0]
            pnt = GEOSGeometry(parcel.geom)

            centroid = str(parcel.geom.centroid).split(';')[1]
            cent = centroid.split('(')[1]
            cent = cent.replace(')', '')
            cent_point = cent.split(' ')

            for i in range(len(coord) - 1):
                p = coord[i]
                alph = alphabet[i]
                lst_point.append([p[1], p[0]])

                marker = "L.marker([" + str(p[1]) + "," + str(p[0]) + "],{icon:L.divIcon({html:'" + alph + \
                         "',className:'bindTooltipBig2',iconSize:[100,40]})}).addTo(map);\n"
                lst_markers += marker

            utm_zone = 36  # Example: UTM Zone 17 (change according to your desired zone)
            parcel.geom.transform(f'EPSG:327{utm_zone}')
            parcel.save()

            coord = json.loads(parcel.geom.geojson)['coordinates'][0]
            pnt = GEOSGeometry(parcel.geom)

            for i in range(len(coord) - 1):
                # pnt = GEOSGeometry('SRID=' + str(pnt.srid) + ';POINT(' + str(p[0]) + ' ' + str(p[1]) + ')')
                # pnt.transform(32736)

                p = coord[i]
                alph = alphabet[i]

                x = f'{p[1]:,.3f}'
                y = f'{p[0]:,.3f}'
                listCoordinates += "<tr><td style='text-align:center'>" + alph + "</td><td style='text-align:center'>" + str(
                    x.replace(',', '')) + "</td><td>" + str(y.replace(',', '')) + "</td></tr>"

            parcel.geom.transform(4326)
            parcel.save()

            # pnt = GEOSGeometry(parcel.geom)
            # print(pnt)
            # pnt.transform(32736)
            # print(pnt)
            # print(pnt.extent)

            doc = doc.replace("$listCoordinates", listCoordinates)

            poly = """<script>
            var map = L.map('mapid_1', {drawControl: true, zoomControl:false,attributionControl: false});
            
            """ + lst_markers + """

var poly = L.polygon([""" + str(lst_point) + """],{
        fillColor:'transparent',        color:'#888',
        weight:4
    }).addTo(map);
   L.marker([""" + str(float(cent_point[1])) + """,""" + str(
                float(cent_point[0])) + """],{icon:L.divIcon({html:'""" + ukubwa + """',className:'bindTooltipBig3',iconSize:[100,40]})}).addTo(map);    map.fitBounds(poly.getBounds());
window.status = 'ready_to_print';
</script><script>
    var map = L.map('mapid', {drawControl: true, zoomControl:false,attributionControl: false});
function getZoom(d) {
    return d > 40000 ? 2:
           d > 30000 ? 4:
           d > 20000 ? 5:
           d > 15000 ? 8:
           d > 10000 ? 9:
           d > 9000 ? 12:
           d > 7000 ? 16:
           d > 4000 ? 18:
           d > 2000 ? 18:
           d > 1000 ? 18:
           d > 500  ? 19:
           d < 500  ? 20 :
                      20;
}


    $.getJSON('""" + server_ip + """/ows?&service=WFS&version=1.0.0&request=GetFeature&' +
        'typeName=vw_majirani&cql_filter=DWITHIN(geom,""" + centroid + """,500,meters)&outputFormat=application%2Fjson',function(data){

        var datalayer = L.geoJson(data ,{
            onEachFeature: function(feature, featureLayer) {
                if (feature.properties.parcel_id===""" + str(parcel_id) + """){
                    var current = L.geoJson(feature,{
                        color: '#484848',weight:4,zIndex:2
                    }).addTo(map);

                    map.fitBounds(current.getBounds(),{padding: [30,30]});
                }else{
var jirani = '';   
L.marker(featureLayer.getBounds().getCenter(),{
                                icon:L.divIcon({
                                    className:'bindTooltipBig4',
                                     html:feature.properties.fullname,
                                    iconSize:[100,40]
                                })
                            }).addTo(map);}            },
            color: '#888',weight:1,zIndex:1, fillOpacity: 0
        })
       datalayer.addTo(map);            setTimeout(function(){ window.status = 'ready_to_print';}, 1000);        


    });
</script>"""

            poly32 = """
         "    $.getJSON('""" + server_ip + """/ows?cql_filter='+filter+'&service=WFS&version=1.0.0&request=GetFeature&typeName=project_parcel&outputFormat=application%2Fjson').then(r=>{

            try {
                        //console.log(r.data)
                        r.data.features.forEach(p=>{

                            let myLayer = LF.geoJSON(p,{
                                onEachFeature:(f,l)=>{
                                    LF.marker(l.getBounds().getCenter(),{
                                        icon:LF.divIcon({
                                            className:'bindTooltipBig',
                                            html:f.properties.claim_no,
                                            iconSize:[100,40]
                                        })
                                    }).addTo(ly_labels)
                                    l.setStyle({
                                        color:f.properties.status==='occupied'?'#000':'#f80',
                                        fillColor:f.properties.status==='occupied'?'#000':'#f80',
                                         fillOpacity: f.properties.status==='occupied'?0.4:0,
                                    })
                                },
                                coordsToLatLng: function (coords) {
                                    return LF.utm({x: coords[0], y: coords[1], zone: 36, band: 'M'}).latLng();
                                },
                                weight:3,zIndex:2,

                            }).on('dblclick',e=>{


                            }).on('click', function (e) {

                                if (e.layer.feature.properties.status==="occupied"){
                                    alert('Occupied')
                                    return
                                }
                                //if (selected) {e.target.resetStyle(selected)}
                                selected = e.layer


                                let arr = self.state.selected_plots
                                let new_arr = self.state.selected_plots
                                let description = self.state.description
                                let new_desr = self.state.description

                                let id = parseInt(e.layer.feature.id.split('.')[1])
                                let claim = e.layer.feature.properties.claim_no

                                if (arr.includes(id)){
                                    new_arr = []
                                    new_desr = []
                                    arr.forEach(it=>{
                                        if (it!==id){
                                            new_arr.push(it)
                                        }
                                    })
                                    description.forEach(it=>{
                                        if (it!==claim){
                                            new_desr.push(claim)
                                        }
                                    })
                                    selected.setStyle({color: '#f80', weight:4})
                                }else{
                                    selected.setStyle({color: '#00f', weight:4})
                                    map.fitBounds(selected.getBounds())
                                    new_arr.push(id)
                                    new_desr.push(claim)
                                }

                                self.setState({
                                    selected_plots:new_arr,
                                    description:new_desr
                                })

                                selected.bringToFront()

                            })
                            myLayer.addTo(ly_plots)
                        })
                        let myLayer = LF.geoJSON(r.data,{coordsToLatLng: function (coords) {return LF.utm({x: coords[0], y: coords[1], zone: 36, band: 'M'}).latLng();}})
                        try{ map.fitBounds(myLayer.getBounds())}catch (e) { }
                        setTimeout(function(){ window.status = 'ready_to_print';}, 5000);       
                    }catch (e){
                        console.log(e)
                    }
        })"""

            doc = doc.replace("$polygon", poly)

            newHtmlFileParent = f'{HTML_TEMPLATE_DIR}deed/ccro'

            if not os.path.isdir(newHtmlFileParent):
                try:
                    os.makedirs(newHtmlFileParent)
                except Exception as e:
                    traceback.print_exc()
                    print(e)

            newHtmlFile = f"{newHtmlFileParent}/ccro_{parcel_id}.html"

            with open(newHtmlFile, "w") as text_file:
                text_file.write(doc)

            with open(newHtmlFile, "w") as text_file:
                text_file.write(doc)

        try:
            cmd = f"wkhtmltopdf  -B 14 -L 14 -R 14 -T 0   -O Portrait -s A4 --title CCRO --copies 1 " \
                  f"--window-status ready_to_print --enable-local-file-access --debug-javascript " \
                  f"{newHtmlFile} {output}"
            os.system(cmd)
            print(cmd)
            print(output)
            print("Ndio NIMEPITAA....................")
        except Exception as e:
            print("HAPANA NIMEPITAA....................")
            traceback.print_exc()
            print(e)

        # out = OutgoingDocument.objects.get(deedplan=deed)
        # out.output = output
        # out.save(update_fields=['output'])

        # deed.docs = output
        # deed.save(update_fields=['docs'])
        # print(output)

        # base_64 = ''
        # with open(output, "rb") as image_file:
        #     base_64 = str(base64.b64encode(image_file.read())).replace('b\'', '')
        #     base_64 = ve_sign_base_64.replace('\'', '')

        from nluis_setups.models import DocumentType

        with open(output, 'rb') as fi:
            _file = File(fi, name=os.path.basename(fi.name))

            ccro = Document(project=parcel.project,
                            locality=parcel.locality,
                            document_type=DocumentType.objects.get(code='ccro',
                                                                   project_type=parcel.project.project_type,
                                                                   is_input=False),
                            description=parcel.uka_namba, file=_file)
            ccro.save()
            parcel.documents.add(ccro)
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
