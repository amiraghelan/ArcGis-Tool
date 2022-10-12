import os
import arcpy
import arcpy.mapping as mapping


# Feel free to edit this part but leave the rest as it is
servicesEng = [
"Health",
"Educational",
"Caltural",
"Recreational",
"Sport",
"Equipment",
"Religious",
"Park"]

servicesValue = [
"1","2","3","4","5","6","7","8"
]


# servicesValue = [
# "1",
# "2"
# ]

# servicesEng = [
# "Health",
# "Educational"
# ]

allServicesQuery = u"faaliat = '%s' OR faaliat = '%s' OR faaliat = '%s' OR faaliat = '%s' OR faaliat = '%s' OR faaliat = '%s' OR faaliat = '%s' OR faaliat = '%s'" % ("1","2","3","4","5","6","7","8")

#---------------------------------------------------------


class Service:
    def __init__(self, nameEng, nameValue, dataSet):
        self.namePer = nameValue
        self.nameEng = nameEng
        self.dataSet = dataSet
        self.query = "faaliat = '%s'" %  nameValue
    def getAllFacilitiesPath(self):
        featureClassName = "%s_All" % self.nameEng
        return os.path.join(str(self.dataSet),featureClassName)

try :
    rootFolder = arcpy.GetParameterAsText(0)
    inputParcels = arcpy.GetParameterAsText(1)
    networkDataSet = arcpy.GetParameterAsText(2)
    toolbaxFolderPath = arcpy.env.workspace.split("Default.gdb")[0] + "ServiceDistribution"
    if len(arcpy.GetParameterAsText(3))!=0:
        symbologyReferenceLayerPath = arcpy.GetParameterAsText(3)
    else:
        symbologyReferenceLayerPath = os.path.join(toolbaxFolderPath,"Symbology_ref.lyr")

    if len(arcpy.GetParameterAsText(4))!=0:
        GroupLayerPath = arcpy.GetParameterAsText(4)
    else:
        GroupLayerPath = os.path.join(toolbaxFolderPath,"Service_Distribution_All_temp.lyr")  
    
    os.mkdir(os.path.join(rootFolder,"Layers"))
except :
    print (arcpy.GetMessage())

mxd = mapping.MapDocument("CURRENT")
dataframe = mapping.ListDataFrames(mxd)[0]



services = []

#creating the database
database = arcpy.CreatePersonalGDB_management(rootFolder , "Service_Distribution")


#creating feature classes
for i in range(len(servicesEng)):
    t = arcpy.CreateFeatureDataset_management(database,servicesEng[i],inputParcels)
    services.append(Service(servicesEng[i],servicesValue[i],t,))


#selecting all services and creating polygon and point class 
allServicesPolygon = arcpy.Select_analysis(inputParcels,os.path.join(str(database),"AllservicesPolygon"),allServicesQuery)
allServicesPoint = arcpy.FeatureToPoint_management(allServicesPolygon,os.path.join(str(database),"AllservicesPoint"))



symbologyReferenceLayer = mapping.Layer(symbologyReferenceLayerPath)
layers = []
for i in range(len(services)):
    service = services[i]
    service.allFacilities = arcpy.Select_analysis(allServicesPoint,service.getAllFacilitiesPath(),service.query)
    layerName = "%s_All_SA" % service.nameEng
    featureClass = os.path.join(str(service.dataSet),layerName)
    arcpy.GenerateServiceAreas_na(service.allFacilities,"700","Meters",networkDataSet,featureClass)
    layer = mapping.Layer(str(arcpy.MakeFeatureLayer_management(featureClass,layerName)))
    symbologyReferenceLayer = mapping.Layer(symbologyReferenceLayerPath)
    arcpy.ApplySymbologyFromLayer_management(layer,symbologyReferenceLayer)
    layers.append(layer)

groupLayer = mapping.Layer(GroupLayerPath)   
mapping.AddLayer(dataframe, groupLayer)
groupLayer = mapping.Layer("Service_Distribution_All")
for layer in layers:
    mapping.AddLayerToGroup(dataframe,groupLayer,layer)
    mapping.RemoveLayer(dataframe,layer)

savedGroupLayerPath = os.path.join(rootFolder,"Layers","Service_Distribution_All.lyr")
groupLayer.saveACopy(savedGroupLayerPath)
mapping.RemoveLayer(dataframe,groupLayer)
mapping.AddLayer(dataframe,mapping.Layer(savedGroupLayerPath))    
