from django.shortcuts import render
from django.http import HttpResponse
from . import fusioncharts
from django.template.response import TemplateResponse
from webapp.models import Hhv2Pub
from webapp.models import Vehv2Pub
from webapp.models import Perv2Pub
from webapp.models import Dayv2Pub
import csv
from webapp.models import Hhpub, Perpub,Vehpub,Trippub
from django.db.models import Count
from django.db.models import Sum
from django.db.models import Avg
from django.db import connection
from django.http import StreamingHttpResponse
from .fusioncharts import FusionCharts
from django.db.models import Func

from django.template.defaulttags import register
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
ethnicityV = {-1:"Appropriate Skip",-7:"Refused",-8:"Don't Know",-9:"Not ascertained",1:"White",2:"African American, Black",3:"Asian Only",4:"American Indian, Alaskan Native",5:"Native Hawaiian, other Pacific" ,6:"Multiracial",7:"Hispanic/Mexican",97:"Other specify"}
urbanruralV={'-9':"Not Ascertained",'01':"Urban",'02':"Rural"}
urbanruralV17={-9:"Not Ascertained",1:"Urban",2:"Rural"}
incomeV={-7:"Refused",-8:"Don't Know",-9:"Not ascertained",1:"< $5,000",2:"$5,000 - $9,999",3:"$10,000 - $14,999",4:"$15,000 - $19,999",5:"$20,000 - $24,999",6:"$25,000 - $29,999",7:"$30,000 - $34,999",8:"$35,000 - $39,999",9:"$40,000 - $44,999",10:"$45,000 - $49,999",11:"$50,000 - $54,999",12:"$55,000 - $59,999",13:"$60,000 - $64,999",14:"$65,000 - $69,999",15:"$70,000 - $74,999",16:"$75,000 - $79,999",17:"$80,000 - $99,999",18:"> = $100,000"}

class Round(Func):
    function = 'ROUND'
    template='%(function)s(%(expressions)s, 2)'


def chart(request):
    if request.method == 'POST':
        selected = request.POST.get('stateChart', None)
        if selected=="bargraph":
            dataSource = {}
            dataSource['chart'] = { 
            "caption": "State Total Vehicles ",
            "subCaption": "Bar graph",
            "xAxisName": "State",
            "yAxisName": "Number of Vehicles",
            "numberPrefix": "",
            "theme": "zune",
            "exportEnabled": "1"
            }
   
             # The data for the chart should be in an array where each element of the array is a JSON object
             # having the `label` and `value` as key value pair.

            dataSource['data'] = []
                 # Iterate through the data in `Revenue` model and insert in to the `dataSource['data']` list.
            pp=Vehv2Pub.objects.values('hhstate').annotate(Count('hhstate')).order_by('hhstate')
            for key in pp:
                data = {}
                data['label'] = key['hhstate']
                data['value'] = key['hhstate__count']
                dataSource['data'].append(data)
            column2D = FusionCharts("column2D", "ex1" , "600", "350", "chart-1", "json", dataSource)
            return render(request, 'webapp/index.html', {'output': column2D.render()})	
	# Chart data is passed to the `dataSource` parameter, as dict, in the form of key-value pairs.
        elif selected=="linegraph":    
            dataSource = {}
            dataSource['chart'] = { 
            "caption": "State Total Vehicles ",
            "subCaption": "Line graph",
            "xAxisName": "State",
            "yAxisName": "Number of Vehicles",
            "numberPrefix": "",
            "theme": "zune",
            "exportEnabled": "1"
            }
   
             # The data for the chart should be in an array where each element of the array is a JSON object
             # having the `label` and `value` as key value pair.

            dataSource['data'] = []
                 # Iterate through the data in `Revenue` model and insert in to the `dataSource['data']` list.
            pp=Vehv2Pub.objects.values('hhstate').annotate(Count('hhstate')).order_by('hhstate')
            for key in pp:
                data = {}
                data['label'] = key['hhstate']
                data['value'] = key['hhstate__count']
                dataSource['data'].append(data)
            column2D = FusionCharts("line", "ex1" , "600", "350", "chart-1", "json", dataSource)
            return render(request, 'webapp/index.html', {'output': column2D.render()})	
        elif selected=="0":
            try:
                state1 = Vehv2Pub.objects.values('hhstate').annotate(Count('hhstate')).order_by('hhstate')
                result=[]
                for p in state1:
                    result.append(p)
                return render(request, 'webapp/statevehcount.html', {"result":result})
            except:
                return HttpResponse("No data available")
    else :
        return render(request, 'webapp/home.html')
			



def index(request) :
		return render(request, 'webapp/header.html')
		
def contact(request):
    return render(request, 'webapp/basic.html',{'content':['If you would like to contact me, please email me.','akash.rathore8@gmail.com']})
# Create your views here.
def nonquery(request):
    if request.method == 'POST':
        selected = request.POST.get('allFiles', None)
        if selected=="individual":
            try:
                user = Hhv2Pub.objects.values("houseid")
                result=[]
                for p in user:
                    result.append(p)
                #return HttpResponse("<H> Reached</H>")
                return render(request, 'webapp/individual.html', {"user": result})
            except:
                return HttpResponse("Query returns no result")  
        elif selected=="aggregated":
            return render(request, 'webapp/aggregated.html') 
        elif selected=="weightedA":
            return render(request, 'webapp/weightedA.html') 
    else :
        return render(request, 'webapp/home.html')

def avgtriprace(request):
    if request.method=='POST':
        selected = request.POST.get('ethnicity', None)
        if selected=="avgtrip":
            try:
                urbrur1 = Dayv2Pub.objects.values('hh_race').annotate(trpmiles__avg=Round(Avg('trpmiles'))).order_by('hh_race')
                result=[]
                for p in urbrur1:
                    result.append(p)
                urbrur117 = Trippub.objects.values('hh_race').annotate(trpmiles__avg=Round(Avg('trpmiles'))).order_by('hh_race')
                result17=[]
                for p in urbrur117:
                    result17.append(p)
                return render(request, 'webapp/avgtriprace.html', {"result":result,"result17":result17, "ethnicityV":ethnicityV})
            except:
                return HttpResponse("No data available")
        elif selected=="avgtripbystate":
            try:
                urbrur1 = Dayv2Pub.objects.values('hhstate','hh_race').annotate(trpmiles__avg=Round(Avg('trpmiles'))).order_by('hhstate','hh_race')
                result1=[]
                for p in urbrur1:
                    result1.append(p)
                urbrur117 = Trippub.objects.values('hhstate','hh_race').annotate(trpmiles__avg=Round(Avg('trpmiles'))).order_by('hhstate','hh_race')
                result17=[]
                for p in urbrur117:
                    result17.append(p)
                return render(request, 'webapp/avgtripracebystate.html', {"result1":result1,"result17":result17, "ethnicityV":ethnicityV})
            except:
                return HttpResponse("No data available")
        elif selected=="avgtripbyincome":
            try:
                urbrur1 = Dayv2Pub.objects.values('hhfaminc','hh_race').annotate(trpmiles__avg=Round(Avg('trpmiles'))).order_by('hhfaminc','hh_race')
                result1=[]
                for p in urbrur1:
                    result1.append(p)
                urbrur117 = Trippub.objects.values('hhfaminc','hh_race').annotate(trpmiles__avg=Round(Avg('trpmiles'))).order_by('hhfaminc','hh_race')
                result17=[]
                for p in urbrur117:
                    result17.append(p)
                return render(request, 'webapp/avgtripracebyincome.html', {"result1":result1, "result17":result17, "ethnicityV":ethnicityV,"incomeV":incomeV})
            except:
                return HttpResponse("No data available")
        elif selected=="avgtriptimebyincome":
            try:
                urbrur1 = Dayv2Pub.objects.values('hhfaminc','hh_race').annotate(trvlcmin__avg=Round(Avg('trvlcmin'))).order_by('hhfaminc','hh_race')
                result1=[]
                for p in urbrur1:
                    result1.append(p)
                urbrur117 = Trippub.objects.values('hhfaminc','hh_race').annotate(trvlcmin__avg=Round(Avg('trvlcmin'))).order_by('hhfaminc','hh_race')
                result17=[]
                for p in urbrur117:
                    result17.append(p)
                return render(request, 'webapp/avgtriptimeracebyincome.html', {"result1":result1, "result17":result17, "ethnicityV":ethnicityV, "incomeV":incomeV})
            except:
                return HttpResponse("No data available")
        elif selected=="avgtriptime":
            try:
                urbrur1 = Dayv2Pub.objects.values('hh_race').annotate(trvlcmin__avg=Round(Avg('trvlcmin')))
                result=[]
                for p in urbrur1:
                    result.append(p)
                urbrur117 = Trippub.objects.values('hh_race').annotate(trvlcmin__avg=Round(Avg('trvlcmin')))
                result17=[]
                for p in urbrur117:
                    result17.append(p)
                return render(request, 'webapp/avgtriptimerace.html', {"result":result, "result17":result17, "ethnicityV":ethnicityV})
            except:
                return HttpResponse("No data available")                                    
        elif selected=="avgtriptimebystate":
            try:
                urbrur1 = Dayv2Pub.objects.values('hhstate','hh_race').annotate(trvlcmin__avg=Round(Avg('trvlcmin'))).order_by('hhstate','hh_race')
                result1=[]
                for p in urbrur1:
                    result1.append(p)
                urbrur117 = Trippub.objects.values('hhstate','hh_race').annotate(trvlcmin__avg=Round(Avg('trvlcmin'))).order_by('hhstate','hh_race')
                result17=[]
                for p in urbrur117:
                    result17.append(p)
                return render(request, 'webapp/avgtriptimeracebystate.html', {"result1":result1, "result17":result17,  "ethnicityV":ethnicityV})
            except:
                return HttpResponse("No data available")
        else:
            return render(request, 'webapp/ethnicity.html')		
    else:
        return HttpResponse("Reached POST request Ethnicity")



def stateaction(request):
    if request.method=='POST':
        selected = request.POST.get('state', None)
        if selected=="totalvehcount":
            dataSourceLine = {}
            dataSourceLine['chart'] = { 
            "caption": "State Total Vehicles ",
            "subCaption": "",
            "xAxisName": "State",
            "yAxisName": "Number of Vehicles",
            "numberPrefix": "",
            "theme": "zune",
            "exportEnabled": "1"
            }
            dataSourceLine['data'] = []
                 # Iterate through the data in `Revenue` model and insert in to the `dataSource['data']` list.
            lineData=Vehv2Pub.objects.values('hhstate').annotate(Count('hhstate')).order_by('hhstate')
            for key in lineData:
                data = {}
                data['label'] = key['hhstate']
                data['value'] = key['hhstate__count']
                dataSourceLine['data'].append(data)
            line = FusionCharts("line", "ex1" , "600", "350", "chart-1", "json", dataSourceLine)
            column2D = FusionCharts("column2D", "ex2" , "600", "350", "chart-2", "json", dataSourceLine)
            #return render(request, 'webapp/index.html', {'output': column2D.render()})	
            try:
                state1 = Vehv2Pub.objects.values('hhstate').annotate(Count('hhstate')).order_by('hhstate')
                result=[]
                for p in state1:
                    result.append(p)
                state17 = Vehpub.objects.values('hhstate').annotate(Count('hhstate')).order_by('hhstate')
                result17=[]
                for p in state17:
                    result17.append(p)					
                return render(request, 'webapp/statevehcount.html', {"result":result, "result17":result17, 'bargraph':column2D.render(),'line':line.render()})
            except:
                return HttpResponse("No data available")
        elif selected=="avgtripmilesbystate":
            try:
                urbrur1 = Dayv2Pub.objects.values('hhstate').annotate(trpmiles__avg=Round(Avg('trpmiles'))).order_by('hhstate')
                result=[]
                for p in urbrur1:
                    result.append(p)
                state17 = Trippub.objects.values('hhstate').annotate(trpmiles__avg=Round(Avg('trpmiles'))).order_by('hhstate')
                result17=[]
                for p in state17:
                    result17.append(p)					
                return render(request, 'webapp/avgtripmilesbystate.html', {"result":result, "result17":result17})
            except:
                return HttpResponse("No data available")
        elif selected=="avgtriptimebystate":
            try:
                urbrur1 = Dayv2Pub.objects.values('hhstate').annotate(trvlcmin__avg=Round(Avg('trvlcmin'))).order_by('hhstate')
                result1=[]
                for p in urbrur1:
                    result1.append(p)
                state17 = Trippub.objects.values('hhstate').annotate(trvlcmin__avg=Round(Avg('trvlcmin'))).order_by('hhstate')
                result17=[]
                for p in state17:
                    result17.append(p)										
                return render(request, 'webapp/avgtriptimebystate.html', {"result1":result1, "result17":result17})
            except:
                return HttpResponse("No data available")
        else:
            return render(request, 'webapp/state.html')
                                    
                                        
    else:
        return HttpResponse("Reached POST request State")
		
def weightedavgtripUR(request):
    if request.method=='POST':
        selected = request.POST.get('weightedurbanrural', None)
        if selected=="avgtrip":
            try:
                urbrur1 = Dayv2Pub.objects.values('urbrur').annotate(trpmiles__avg=Round(Avg('trpmiles'))).order_by('urbrur')
                result=[]
                for p in urbrur1:
                    result.append(p)
                return render(request, 'webapp/avgtripur.html', {"result":result, "urbanruralV":urbanruralV})
            except:
                return HttpResponse("No data available")
        elif selected=="trippurposewhyto":
            try:
                urbrur1 = Dayv2Pub.objects.filter(urbrur__contains="1").values('urbrur','whyto').annotate(Count('whyto')).order_by('whyto','urbrur')
                urbrur2 = Dayv2Pub.objects.filter(urbrur__contains="2").values('urbrur','whyto').annotate(Count('whyto')).order_by('whyto','urbrur')
                result1=[]
                for p in urbrur1:
                    result1.append(p)
                result2=[]
                for p in urbrur2:
                    result2.append(p)
                #result=zip(result1,result2)
                return render(request, 'webapp/trippurposewhyto.html', {"result1":result1,"result2":result2})
            except:
                return HttpResponse("No data available")
        elif selected=="avgtripbystate":
            try:
                urbrur1 = Dayv2Pub.objects.filter(urbrur__contains="1").values('hhstate','urbrur').annotate(trpmiles__avg=Round(Avg('trpmiles'))).order_by('hhstate')
                urbrur2 = Dayv2Pub.objects.filter(urbrur__contains="2").values('hhstate','urbrur').annotate(trpmiles__avg=Round(Avg('trpmiles'))).order_by('hhstate')
                result1=[]
                for p in urbrur1:
                    result1.append(p)
                result2=[]
                for p in urbrur2:
                    result2.append(p)
                result=zip(result1,result2)
                return render(request, 'webapp/avgtripurbystate.html', {"result":result})
            except:
                return HttpResponse("No data available")
        elif selected=="avgtripbyrace":
            try:
                urbrur1 = Dayv2Pub.objects.filter(urbrur__contains="1").values('hh_race','urbrur').annotate(trpmiles__avg=Round(Avg('trpmiles'))).order_by('hh_race')
                urbrur2 = Dayv2Pub.objects.filter(urbrur__contains="2").values('hh_race','urbrur').annotate(trpmiles__avg=Round(Avg('trpmiles'))).order_by('hh_race')
                result1=[]
                for p in urbrur1:
                    result1.append(p)
                result2=[]
                for p in urbrur2:
                    result2.append(p)
                result=zip(result1,result2)
                return render(request, 'webapp/avgtripurbyrace.html', {"result":result, "ethnicityV":ethnicityV})
            except:
                return HttpResponse("No data available")
        elif selected=="avgtripbyincome":
            try:
                urbrur1 = Dayv2Pub.objects.filter(urbrur__contains="1").values('hhfaminc','urbrur').annotate(trpmiles__avg=Round(Avg('trpmiles'))).order_by('hhfaminc')
                urbrur2 = Dayv2Pub.objects.filter(urbrur__contains="2").values('hhfaminc','urbrur').annotate(trpmiles__avg=Round(Avg('trpmiles'))).order_by('hhfaminc')
                result1=[]
                for p in urbrur1:
                    result1.append(p)
                result2=[]
                for p in urbrur2:
                    result2.append(p)
                result=zip(result1,result2)							
                return render(request, 'webapp/avgtripurbyincome.html', {"result":result,"incomeV":incomeV})
            except:
                return HttpResponse("No data available")
        elif selected=="avgtriptimebystate":
            try:
                urbrur1 = Dayv2Pub.objects.filter(urbrur__contains="1").values('hhstate').annotate(trvlcmin__avg=Round(Avg('trvlcmin'))).order_by('hhstate')
                urbrur2 = Dayv2Pub.objects.filter(urbrur__contains="2").values('hhstate').annotate(trvlcmin__avg=Round(Avg('trvlcmin'))).order_by('hhstate')
                result1=[]
                for p in urbrur1:
                    result1.append(p)
                result2=[]
                for p in urbrur2:
                    result2.append(p)
                result=zip(result1,result2)									
                return render(request, 'webapp/avgtriptimeurbystate.html', {"result":result})
            except:
                return HttpResponse("No data available")
                                    
        elif selected=="avgtriptimebyrace":
            try:
                urbrur1 = Dayv2Pub.objects.filter(urbrur__contains="1").values('hh_race').annotate(trvlcmin__avg=Round(Avg('trvlcmin'))).order_by('hh_race')
                urbrur2 = Dayv2Pub.objects.filter(urbrur__contains="2").values('hh_race').annotate(trvlcmin__avg=Round(Avg('trvlcmin'))).order_by('hh_race')
                result1=[]
                for p in urbrur1:
                    result1.append(p)
                result2=[]
                for p in urbrur2:
                    result2.append(p)
                result=zip(result1,result2)				
                return render(request, 'webapp/avgtriptimeurbyrace.html', {"result":result, "ethnicityV":ethnicityV})
            except:
                return HttpResponse("No data available")            
        elif selected=="avgtriptimebyincome":
            try:
                urbrur1 = Dayv2Pub.objects.filter(urbrur__contains="1").values('hhfaminc').annotate(trvlcmin__avg=Round(Avg('trvlcmin'))).order_by('hhfaminc')
                urbrur2 = Dayv2Pub.objects.filter(urbrur__contains="2").values('hhfaminc').annotate(trvlcmin__avg=Round(Avg('trvlcmin'))).order_by('hhfaminc')
                result1=[]
                for p in urbrur1:
                    result1.append(p)
                result2=[]
                for p in urbrur2:
                    result2.append(p)
                result=zip(result1,result2)		
                return render(request, 'webapp/avgtriptimeurbyincome.html', {"result":result,"incomeV":incomeV})
            except:
                return HttpResponse("No data available") 
        else:
            return render(request, 'webapp/urbanrural.html')		
    else:
        return HttpResponse("Reached POST request Urban")		
		
def avgtripUR(request):
    if request.method=='POST':
        selected = request.POST.get('urbanrural', None)
        if selected=="avgtrip":
            try:
                urbrur1 = Dayv2Pub.objects.values('urbrur').annotate(trpmiles__avg=Round(Avg('trpmiles'))).order_by('urbrur')
                result=[]
                for p in urbrur1:
                    result.append(p)
                urbrur117 = Trippub.objects.values('urbrur').annotate(trpmiles__avg=Round(Avg('trpmiles'))).order_by('urbrur')
                result17=[]
                for p in urbrur117:
                    result17.append(p)
                return render(request, 'webapp/avgtripur.html', {"result":result,"result17": result17, "urbanruralV":urbanruralV,"urbanruralV17":urbanruralV17})
            except:
                return HttpResponse("No data available")
        elif selected=="trippurposewhyto":
            try:
                urbrur1 = Dayv2Pub.objects.filter(urbrur__contains="1").values('urbrur','whyto').annotate(Count('whyto')).order_by('whyto','urbrur')
                urbrur2 = Dayv2Pub.objects.filter(urbrur__contains="2").values('urbrur','whyto').annotate(Count('whyto')).order_by('whyto','urbrur')
                result1=[]
                for p in urbrur1:
                    result1.append(p)
                result2=[]
                for p in urbrur2:
                    result2.append(p)

                urbrur117 = Trippub.objects.filter(urbrur__contains="1").values('urbrur','whyto').annotate(Count('whyto')).order_by('whyto','urbrur')
                urbrur217 = Trippub.objects.filter(urbrur__contains="2").values('urbrur','whyto').annotate(Count('whyto')).order_by('whyto','urbrur')
                result117=[]
                for p in urbrur117:
                    result117.append(p)
                result217=[]
                for p in urbrur217:
                    result217.append(p)
                return render(request, 'webapp/trippurposewhyto.html', {"result1":result1,"result2":result2, "result117":result117, "result217":result217})
            except:
                return HttpResponse("No data available")
        elif selected=="avgtripbystate":
            try:
                urbrur1 = Dayv2Pub.objects.filter(urbrur__contains="1").values('hhstate','urbrur').annotate(trpmiles__avg=Round(Avg('trpmiles'))).order_by('hhstate')
                urbrur2 = Dayv2Pub.objects.filter(urbrur__contains="2").values('hhstate','urbrur').annotate(trpmiles__avg=Round(Avg('trpmiles'))).order_by('hhstate')
                result1=[]
                for p in urbrur1:
                    result1.append(p)
                result2=[]
                for p in urbrur2:
                    result2.append(p)
                result=zip(result1,result2)
                urbrur117 = Trippub.objects.filter(urbrur__contains="1").values('hhstate','urbrur').annotate(trpmiles__avg=Round(Avg('trpmiles'))).order_by('hhstate')
                urbrur217 = Trippub.objects.filter(urbrur__contains="2").values('hhstate','urbrur').annotate(trpmiles__avg=Round(Avg('trpmiles'))).order_by('hhstate')
                result117=[]
                for p in urbrur117:
                    result117.append(p)
                result217=[]
                for p in urbrur217:
                    result217.append(p)
                result317=zip(result117,result217)	     				
                return render(request, 'webapp/avgtripurbystate.html', {"result":result,"result317":result317})
            except:
                return HttpResponse("No data available")
        elif selected=="avgtripbyrace":
            try:
                urbrur1 = Dayv2Pub.objects.filter(urbrur__contains="1").values('hh_race','urbrur').annotate(trpmiles__avg=Round(Avg('trpmiles'))).order_by('hh_race')
                urbrur2 = Dayv2Pub.objects.filter(urbrur__contains="2").values('hh_race','urbrur').annotate(trpmiles__avg=Round(Avg('trpmiles'))).order_by('hh_race')
                result1=[]
                for p in urbrur1:
                    result1.append(p)
                result2=[]
                for p in urbrur2:
                    result2.append(p)
                result=zip(result1,result2)
                urbrur117 = Trippub.objects.filter(urbrur__contains="1").values('hh_race','urbrur').annotate(trpmiles__avg=Round(Avg('trpmiles'))).order_by('hh_race')
                urbrur217 = Trippub.objects.filter(urbrur__contains="2").values('hh_race','urbrur').annotate(trpmiles__avg=Round(Avg('trpmiles'))).order_by('hh_race')
                result117=[]
                for p in urbrur117:
                    result117.append(p)
                result217=[]
                for p in urbrur217:
                    result217.append(p)
                result17=zip(result117,result217)					
                return render(request, 'webapp/avgtripurbyrace.html', {"result":result, "ethnicityV":ethnicityV, "result17":result17})
            except:
                return HttpResponse("No data available")
        elif selected=="avgtripbyincome":
            try:
                urbrur1 = Dayv2Pub.objects.filter(urbrur__contains="1").values('hhfaminc','urbrur').annotate(trpmiles__avg=Round(Avg('trpmiles'))).order_by('hhfaminc')
                urbrur2 = Dayv2Pub.objects.filter(urbrur__contains="2").values('hhfaminc','urbrur').annotate(trpmiles__avg=Round(Avg('trpmiles'))).order_by('hhfaminc')
                result1=[]
                for p in urbrur1:
                    result1.append(p)
                result2=[]
                for p in urbrur2:
                    result2.append(p)
                result=zip(result1,result2)	
                urbrur117 = Trippub.objects.filter(urbrur__contains="1").values('hhfaminc','urbrur').annotate(trpmiles__avg=Round(Avg('trpmiles'))).order_by('hhfaminc')
                urbrur217 = Trippub.objects.filter(urbrur__contains="2").values('hhfaminc','urbrur').annotate(trpmiles__avg=Round(Avg('trpmiles'))).order_by('hhfaminc')
                result117=[]
                for p in urbrur117:
                    result117.append(p)
                result217=[]
                for p in urbrur217:
                    result217.append(p)
                result17=zip(result117,result217)								
                return render(request, 'webapp/avgtripurbyincome.html', {"result":result,"incomeV":incomeV, "result17":result17})
            except:
                return HttpResponse("No data available")
        elif selected=="avgtriptimebystate":
            try:
                urbrur1 = Dayv2Pub.objects.filter(urbrur__contains="1").values('hhstate').annotate(trvlcmin__avg=Round(Avg('trvlcmin'))).order_by('hhstate')
                urbrur2 = Dayv2Pub.objects.filter(urbrur__contains="2").values('hhstate').annotate(trvlcmin__avg=Round(Avg('trvlcmin'))).order_by('hhstate')
                result1=[]
                for p in urbrur1:
                    result1.append(p)
                result2=[]
                for p in urbrur2:
                    result2.append(p)
                result=zip(result1,result2)				
                urbrur117 = Trippub.objects.filter(urbrur__contains="1").values('hhstate').annotate(trvlcmin__avg=Round(Avg('trvlcmin'))).order_by('hhstate')
                urbrur217 = Trippub.objects.filter(urbrur__contains="2").values('hhstate').annotate(trvlcmin__avg=Round(Avg('trvlcmin'))).order_by('hhstate')
                result117=[]
                for p in urbrur117:
                    result117.append(p)
                result217=[]
                for p in urbrur217:
                    result217.append(p)
                result17=zip(result117,result217)								
                return render(request, 'webapp/avgtriptimeurbystate.html', {"result":result, "result17":result17})
            except:
                return HttpResponse("No data available")
                                    
        elif selected=="avgtriptimebyrace":
            try:
                urbrur1 = Dayv2Pub.objects.filter(urbrur__contains="1").values('hh_race').annotate(trvlcmin__avg=Round(Avg('trvlcmin'))).order_by('hh_race')
                urbrur2 = Dayv2Pub.objects.filter(urbrur__contains="2").values('hh_race').annotate(trvlcmin__avg=Round(Avg('trvlcmin'))).order_by('hh_race')
                result1=[]
                for p in urbrur1:
                    result1.append(p)
                result2=[]
                for p in urbrur2:
                    result2.append(p)
                result=zip(result1,result2)			
                urbrur117 = Trippub.objects.filter(urbrur__contains="1").values('hh_race').annotate(trvlcmin__avg=Round(Avg('trvlcmin'))).order_by('hh_race')
                urbrur217 = Trippub.objects.filter(urbrur__contains="2").values('hh_race').annotate(trvlcmin__avg=Round(Avg('trvlcmin'))).order_by('hh_race')
                result117=[]
                for p in urbrur117:
                    result117.append(p)
                result217=[]
                for p in urbrur217:
                    result217.append(p)
                result17=zip(result117,result217)						
                return render(request, 'webapp/avgtriptimeurbyrace.html', {"result":result,"result17":result17, "ethnicityV":ethnicityV})
            except:
                return HttpResponse("No data available")            
        elif selected=="avgtriptimebyincome":
            try:
                urbrur1 = Dayv2Pub.objects.filter(urbrur__contains="1").values('hhfaminc').annotate(trvlcmin__avg=Round(Avg('trvlcmin'))).order_by('hhfaminc')
                urbrur2 = Dayv2Pub.objects.filter(urbrur__contains="2").values('hhfaminc').annotate(trvlcmin__avg=Round(Avg('trvlcmin'))).order_by('hhfaminc')
                result1=[]
                for p in urbrur1:
                    result1.append(p)
                result2=[]
                for p in urbrur2:
                    result2.append(p)
                result=zip(result1,result2)		
                urbrur117 = Trippub.objects.filter(urbrur__contains="1").values('hhfaminc').annotate(trvlcmin__avg=Round(Avg('trvlcmin'))).order_by('hhfaminc')
                urbrur217 = Trippub.objects.filter(urbrur__contains="2").values('hhfaminc').annotate(trvlcmin__avg=Round(Avg('trvlcmin'))).order_by('hhfaminc')
                result117=[]
                for p in urbrur117:
                    result117.append(p)
                result217=[]
                for p in urbrur217:
                    result217.append(p)
                result17=zip(result117,result217)		
                return render(request, 'webapp/avgtriptimeurbyincome.html', {"result":result, "result17":result17, "incomeV":incomeV})
            except:
                return HttpResponse("No data available") 
        else:
            return render(request, 'webapp/urbanrural.html')		
    else:
        return HttpResponse("Reached POST request Urban")

def urbanrural(request):
    if request.method=='POST':
        selected = request.POST.get('allaggregate', None)
        if selected=="urbanrural":
            return render(request, 'webapp/urbanrural.html')
        elif selected=="ethnicity":
            return render(request, 'webapp/ethnicity.html')
        elif selected=="state":
            return render(request, 'webapp/state.html')
    else:
        return HttpResponse("reached post request urban")

def weightedurbanrural(request):
    if request.method=='POST':
        selected = request.POST.get('allaggregate', None)
        if selected=="urbanrural":
            return render(request, 'webapp/weightedurbanrural.html')
        elif selected=="ethnicity":
            return render(request, 'webapp/weightedethnicity.html')
        elif selected=="state":
            return render(request, 'webapp/weightedstate.html')
    else:
        return HttpResponse("reached post request urban")

		
def output(request):
    if request.method == 'POST':
        
        search_id = request.POST.get('queryBox', None)
        cursor = connection.cursor()        
        try:
            cursor.execute(search_id)
            user=cursor.fetchall()
            result=[]
            for p in user:
                result.append(p[0])
            #return HttpResponse("<H> Reached</H>")
            return render(request, 'webapp/output.html', {"user": result, "query":search_id})
        except Exception as e:
            print('%s (%s)' % (e.args, type(e))) 
            typeE= type(e)
            print(typeE)
            return render(request, 'webapp/errorinquery.html',{"e":e,"typeE":typeE})  
    else:
        return render(request, 'webapp/home.html')
    
def some_view(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'

    writer = csv.writer(response)
    writer.writerow(['First row', 'Foo', 'Bar', 'Baz'])
    writer.writerow(['Second row', 'A', 'B', 'C', '"Testing"', "Here's a quote"])

    return response