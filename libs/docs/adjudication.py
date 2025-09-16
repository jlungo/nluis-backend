from celery import shared_task


@shared_task()
def generate_adjudication(parcel_id):
    import datetime
    import json
    import os
    import traceback

    from area import area
    from decouple import config
    from django.contrib.gis.geos import GEOSGeometry
    from libs.fxs import get_image_url, get_ukubwa, alphabet
    from nluis.settings import DOCS_OUTPUT
    from nluis_projects.models import ProjectSignatory, Party, Document
    try:
        from nluis_projects.models import Parcel
        parcel = Parcel.objects.get(id=parcel_id)

        kijiji = parcel.locality.name.strip()
        kitongoji = parcel.hamlet.name.strip()
        uuid = 'uuid'
        output = f'{DOCS_OUTPUT}uhakiki/{kijiji}/{kitongoji}/uhakiki_{parcel_id}_{uuid}.pdf'.replace("'", '_')
        out = f'{DOCS_OUTPUT}uhakiki/{kijiji}/{kitongoji}'
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
        mwez_mpaka = '07'
        mwaka_mpaka = mwaka_leo
        matumizi = 'Matumizi'

        uk = get_ukubwa(area(parcel.geom.geojson), 'ac')
        try:
            if float(uk) < 1.0:
                ukubwa = f"Mita za mraba {get_ukubwa(area(parcel.geom.geojson))}"
            else:
                ukubwa = f"Ekari {uk}"
        except Exception as e:
            ukubwa = f"Ekari {uk}"

        wilaya = "WILAYA"

        kas = str(parcel.north).title()
        kus = str(parcel.south).title()
        mash = str(parcel.east).title()
        magh = str(parcel.west).title()

        vc = ProjectSignatory.objects.first()  # .get(layer=layer, design='vc')
        ve = ProjectSignatory.objects.first()  # .get(layer=layer, design='ve')
        alo = ProjectSignatory.objects.first()  # .filter(project_id=layer.project.id, design='alo').last()

        mwenyekiti = vc.fullname()
        vc_sign_base_64 = str(get_image_url(vc.signature.url)).replace("b'", '')
        vc_sign_base_64 = str(vc_sign_base_64).replace("''", "'")

        mtendaji = ve.fullname()
        ve_sign_base_64 = str(get_image_url(ve.signature.url)).replace("b'", '')
        ve_sign_base_64 = str(ve_sign_base_64).replace("''", "'")

        slp = "S.L.P"
        alo_name = alo.fullname()
        alo_sign_base_64 = str(get_image_url(alo.signature.url)).replace("b'", '')
        alo_sign_base_64 = str(alo_sign_base_64).replace("''", "'")

        htmlTemplateFile = "/var/www/documents/doc/html/base_uhakiki.html"

        with open(htmlTemplateFile, 'r') as file:
            doc = file.read()

            doc = doc.replace("$ukaNamba", uka)
            doc = doc.replace("$aloSign", str(alo_sign_base_64))
            doc = doc.replace("$regno", regno)
            doc = doc.replace("$villageName", kijiji)
            doc = doc.replace("$matumizi", matumizi)
            doc = doc.replace("$ukubwa", ukubwa)
            doc = doc.replace("$wilaya", wilaya)
            doc = doc.replace("$hamletName", kitongoji)
            doc = doc.replace("$kas", kas)
            doc = doc.replace("$kus", kus)
            doc = doc.replace("$mash", mash)
            doc = doc.replace("$magh", magh)
            doc = doc.replace("$vcName", mwenyekiti)
            doc = doc.replace("$vcSign", str(vc_sign_base_64))
            doc = doc.replace("$mtendaji", mtendaji)
            doc = doc.replace("$jinaWilaya", wilaya)
            doc = doc.replace("$veSign", str(ve_sign_base_64))

            doc = doc.replace("$umiliki",
                              str(parcel.occupancy_type.swahili) if parcel.occupancy_type is not None else '')
            doc = doc.replace("$topology", str(parcel.topology))
            doc = doc.replace("$ekari", ukubwa)
            doc = doc.replace("$claimDate", str(parcel.claim_date))
            doc = doc.replace("$villageDate", f'{tar_leo}-{mwaka_leo}-{mwaka_leo}')
            doc = doc.replace("$currentUse", str(parcel.current_use.swahili) if parcel.current_use is not None else '')
            doc = doc.replace("$proposed", str(parcel.proposed_use.swahili) if parcel.proposed_use is not None else '')
            doc = doc.replace("$vac1", str(parcel.vac_1))
            doc = doc.replace("$vac2", str(parcel.vac_2))
            doc = doc.replace("$maslahi", '$maslahi')

            pic1 = ""
            pic2 = ""
            names = ""
            name1 = ""
            name2 = ""

            wamiliki = []

            claim = str(parcel.claim_no)

            own_names_f = Party.objects.last()

            i = 0
            for o in [own_names_f]:
                name = str(o.fullname()).upper()
                try:
                    picha = get_image_url(o.picture.url)
                except Exception as e:
                    print(e)
                    picha = ''

                wamiliki.append({
                    'name': name,
                    'pic': picha
                })
                i = i + 1

            if len(wamiliki) > 0:
                doc = doc.replace('$anuani1', '')
                doc = doc.replace('$fname1', '')
                doc = doc.replace('$mnm1', '')
                doc = doc.replace('$lnm1', '')
                doc = doc.replace('$mmiliki1', 'Ndiyo')
                doc = doc.replace('$msimamizi1', '')
                doc = doc.replace('$jinsia1', '')
                doc = doc.replace('$umri1', '')
                doc = doc.replace('$ndoa1', '')
                doc = doc.replace('$mkazi1', '')
                doc = doc.replace('$simu1', '')

            if len(wamiliki) > 1:
                doc = doc.replace('$anuani2', '')
                doc = doc.replace('$fname2', '')
                doc = doc.replace('$mnm2', '')
                doc = doc.replace('$lnm2', '')
                doc = doc.replace('$mmiliki2', 'Ndiyo')
                doc = doc.replace('$msimamizi2', '')
                doc = doc.replace('$jinsia2', '')
                doc = doc.replace('$umri2', '')
                doc = doc.replace('$ndoa2', '')
                doc = doc.replace('$mkazi2', '')
                doc = doc.replace('$simu2', '')

            server_ip = config('GEOSERVER')

            lst_markers = ''
            listCoordinates = ''

            lst_point = []
            coord = json.loads(parcel.geom.geojson)['coordinates'][0]
            pnt = GEOSGeometry(parcel.geom)
            print(pnt.srid)

            for i in range(len(coord) - 1):
                p = coord[i]
                alph = alphabet[i]
                lst_point.append([p[1], p[0]])

                marker = "L.marker([" + str(p[1]) + "," + str(p[0]) + "],{icon:L.divIcon({html:'" + alph + \
                         "',className:'bindTooltipBig2',iconSize:[100,40]})}).addTo(map);\n"
                lst_markers += marker

                pnt = GEOSGeometry('SRID=' + str(pnt.srid) + ';POINT(' + str(p[0]) + ' ' + str(p[1]) + ')')
                pnt.transform(32736)

                listCoordinates += "<tr><td style='text-align:left'>" + alph + "</td><td style='text-align:left'>" + str(
                    p[1]) + "</td><td>" + str(p[0]) + "</td></tr>"

            centroid = str(parcel.geom.centroid).split(';')[1]
            cent = centroid.split('(')[1]
            cent = cent.replace(')', '')
            cent_point = cent.split(' ')

            # pnt = GEOSGeometry(parcel.geom)
            # print(pnt)
            # pnt.transform(32736)
            # print(pnt)
            # print(pnt.extent)

            doc = doc.replace("$listCoordinates", listCoordinates)
            poly = """
            <script>
                var map = L.map('mapid_1', {drawControl: true, zoomControl:false,attributionControl: false});
                 var poly = L.polygon([""" + str(lst_point) + """]);
                 L.marker([""" + str(float(cent_point[1])) + """,""" + str(
                float(cent_point[0])) + """],{icon:L.divIcon({html:'""" + ukubwa + """',className:'bindTooltipBig3',iconSize:[100,40]})}).addTo(map);
                
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
                    'typeName=project_parcel&cql_filter=deleted not in (true)&DWITHIN(geom,""" + centroid + """,500,meters)&outputFormat=application%2Fjson',function(data){

                    var datalayer = L.geoJson(data ,{
                        onEachFeature: function(feature, featureLayer) {
                            if (feature.id==='project_parcel.""" + str(parcel_id) + """'){
                                var current = L.geoJson(feature,{
                                    color: '#484848',weight:4,zIndex:2
                                }).addTo(map);

                                map.fitBounds(current.getBounds(),{padding: [30,30]});
                            }else{
            var jirani = '';   
            L.marker(featureLayer.getBounds().getCenter(),{
                                            icon:L.divIcon({
                                                className:'bindTooltipBig4',
                                                 html:feature.properties.uka_namba,
                                                iconSize:[100,40]
                                            })
                                        }).addTo(map);}            },
                        color: '#888',weight:1,zIndex:1, fillOpacity: 0
                    })
                   datalayer.addTo(map);            setTimeout(function(){ window.status = 'ready_to_print';}, 3000);        


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
                                    setTimeout(function(){ window.status = 'ready_to_print';}, 2000);       
                                }catch (e){
                                    console.log(e)
                                }
                    })"""

            doc = doc.replace("$polygon", poly)

            newHtmlFileParent = "/var/www/documents/doc/html/deed/adj"

            if not os.path.isdir(newHtmlFileParent):
                try:
                    os.makedirs(newHtmlFileParent)
                except Exception as e:
                    print(e)
                    traceback.print_exc()
                    pass

            newHtmlFile = f"{newHtmlFileParent}/adj_{parcel_id}.html"

            with open(newHtmlFile, "w") as text_file:
                text_file.write(doc)
        os.system(
            "wkhtmltopdf  -B 14 -L 14 -R 14 -T 14  -O Landscape -s A4 --title UHAKIKI --copies 3 --window-status ready_to_print --enable-local-file-access --debug-javascript "
            "/var/www/documents/doc/html/uhakiki.html " + output)

        from nluis_setups.models import DocumentType

        with open(output, 'rb') as fi:
            from django.core.files import File
            _file = File(fi, name=os.path.basename(fi.name))

            adj = Document(project=parcel.project,
                           locality=parcel.locality,
                           document_type=DocumentType.objects.get(code='adjudication_form',
                                                                  project_type=parcel.project.project_type,
                                                                  is_input=False),
                           description=parcel.uka_namba, file=_file)
            adj.save()
            parcel.documents.add(adj)
        return {
            'status': 1,
            'message': 'success',
            'path': output.replace('/var/www/html', config('FILE_SERVER'))
        }
    except Exception as e:
        print(e)
        traceback.print_exc()
        return {
            'status': 0,
            'message': str(e),
            'path': ''
        }
