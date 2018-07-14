#Script copies input feature class
#Creates output feature class with
#additional fields for ag land use per county/year
#and poverty pct per county/year

#Import the required ArcPy and custom modules
import time
import arcpy
from arcpy import env
from arcpy.da import *
import commonArcPyValidate
import commonArcPyProcessing

start_time = time.time()

#Override environment variables
#allow output to be overwritten
#for the sake of this assignment
arcpy.env.overwriteOutput = True
arcpy.env.cellSize = 30
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(3081)


#Specify input parameters
targetWorkspace = r"C:\PSUGIS\GEOG586\TermProject\generatedData"

inputFeatureClass = r"C:\PSUGIS\GEOG586\TermProject\reprojectedFiles\Tx_countyBndry_detail_tiger500K_reprojected.shp"

#test
#povertyYears = ["2008", "2009"]
#landUseYears= ["2008", "2009"]

povertyYears = ["1990", "2000", "", "2008", "2009", "2010", "2011", "2012", "2013", "2014", "2015", "", ""]
landUseYears= ["1992", "2001", "2006", "2008", "2009", "2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017"]

#Specifify additional variables needed within the script

spatialRef = arcpy.SpatialReference(3081)
boolLicenseAvail = False
newFields = ["povpct1990", "cnt1992","aguse1992", "povpct2000", "cnt2001", "aguse2001",  "cnt2006","aguse2006",  "cnt2008", "povpct2008", "aguse2008","cnt2009", "povpct2009", "aguse2009","cnt2010", "povpct2010", "aguse2010","cnt2011", "povpct2011", "aguse2011","cnt2012", "povpct2012", "aguse2012","cnt2013", "povpct2013", "aguse2013","cnt2014", "povpct2014", "aguse2014","cnt2015", "povpct2015", "aguse2015","cnt2016", "povpct2016", "aguse2016","cnt2017", "povpct2017", "aguse2017","top3_2008", "bot3_2008","top3_2009", "bot3_2009","top3_2010", "bot3_2010","top3_2011", "bot3_2011","top3_2012", "bot3_2012","top3_2013", "bot3_2013","top3_2014", "bot3_2014","top3_2015", "bot3_2015","top3_2016", "bot3_2016","top3_2017", "bot3_2017","sc2008","cntsc2008","sc2009","cntsc2009","sc2010","cntsc2010","sc2011","cntsc2011","sc2012","cntsc2012","sc2013","cntsc2013","sc2014","cntsc2014","sc2015","cntsc2015","sc2016","cntsc2016","sc2017","cntsc2017","cntdiff", "povpctdiff", "cntscdiff","topdiff","botdiff", "scdiff","cropct1992","cropct2001","cropct2006","cropct2008","cropct2009","cropct2010","cropct2011","cropct2012","cropct2013","cropct2014","cropct2015","cropct2016","cropct2017","pctsc2008","pctsc2009","pctsc2010","pctsc2011","pctsc2012","pctsc2013","pctsc2014","pctsc2015","pctsc2016","pctsc2017","cropctdiff","pctscdiff"]
changeNewFields = ["crop0809","crop0910","crop1011", "crop1112","crop1213","crop1314","crop1415","crop1516","crop1617","pov0809","pov0910","pov1011","pov1112","pov1213","pov1314","pov1415","sc0809","sc0910","sc1011","sc1112","sc1213","sc1314","sc1415","sc1516","sc1617"]
outputFeatureClassName  = "counties_output"
countyLayersList= [] 

#Need to check out spatial extension license
print commonArcPyValidate.checkSpatialExtension()
if(commonArcPyValidate.checkSpatialExtension()):
    try:
        arcpy.CheckOutExtension("spatial")
        boolLicenseAvail = True     
        print "Spatial license checked out"
    except:
        print "Exception caught checking out license"
        
#fields = arcpy.ListFields(inputACSAttribute2009)
#for field in fields:
    #print("{0} is a type of {1} with a length of {2}".format(field.name, field.type, field.length))
      
if(boolLicenseAvail):
    #Perform some basic validation to verify input file and field existence before proceeding
    if(commonArcPyValidate.workspaceExists(targetWorkspace)):
        #Once workspace existence is verified, set the environment workspace
        arcpy.env.workspace = targetWorkspace
        arcpy.env.extent = inputFeatureClass
        if(commonArcPyValidate.featureClassExists(inputFeatureClass)):
            #Make sure there are actually records in the input feature class
            countResult =  int(arcpy.GetCount_management(inputFeatureClass).getOutput(0))
            if (countResult > 0):
                print "Input Feature Class contains {0} records".format(str(countResult))
                #arcpy.AddMessage("Input Feature Class contains {0} records.".format(str(countResult)))

                print "Validation complete, proceeding with output feature class creation and address standardization"
                #arcpy.AddMessage("Validation complete, proceeding with output feature class creation and address standardization")

                #Determine output feature class name, data type
                #Get the Describe object of the Input Feature Class
                #Properties from describe object needed for later use
                descInputFeature = arcpy.Describe(inputFeatureClass)
                outputDataType =  descInputFeature.dataType
                print "Output Feature Class Data Type {0}".format(outputDataType)
                #arcpy.AddMessage("Output Feature Class Data Type {0}".format(outputDataType))

                #Copy the input feature class
                try:

                    #Copy input feature class to new output feature class
                    arcpy.CopyFeatures_management(inputFeatureClass, outputFeatureClassName)

                    print "Input Feature Class successfully copied to {0}".format(outputFeatureClassName)
             
                    #AddField needs to know full path with extension
                    #So, set full feature class name based on data type
                    if("ShapeFile" == outputDataType):
                        outputFeatureClassName  +=".shp"
                    try:
                        #Add new fields to output feature class
                        for newFieldName in newFields:
                            #field = newFields[newFieldName]
                            fieldType="DOUBLE"
                            fieldLen=50
                            fieldPrecision=9
                            fieldScale=2
                            if ((newFieldName.find("aguse") > -1) or ((newFieldName.find("sc") > -1) and (newFieldName != "cntscdiff") and (newFieldName.find("cntsc") < 0) and (newFieldName.find("pctsc") < 0)) or (newFieldName.find("top") > -1) or (newFieldName.find("bot") > -1)):
                                fieldType="TEXT"
                                fieldLen=1000
                            print "New field {0}, type {1}, length {2}".format(newFieldName, fieldType, fieldLen)
                            arcpy.AddField_management(outputFeatureClassName, newFieldName, fieldType,field_length=fieldLen, field_precision=fieldPrecision, field_scale=fieldScale, field_is_nullable="NON_NULLABLE")

                    except Exception as e:
                        print "Exception caught adding fields to output feature class {0}".format(e.args[0])

                    try:
                        #Add new fields to output feature class
                        for newFieldName in changeNewFields:
                            #field = newFields[newFieldName]
                            fieldType="DOUBLE"
                            fieldLen=50
                            fieldPrecision=9
                            fieldScale=2
                            print "New field {0}, type {1}, length {2}".format(newFieldName, fieldType, fieldLen)
                            arcpy.AddField_management(outputFeatureClassName, newFieldName, fieldType,field_length=fieldLen, field_precision=fieldPrecision, field_scale=fieldScale, field_is_nullable="NON_NULLABLE")

                    except Exception as e:
                        print "Exception caught adding change new fields to output feature class {0}".format(e.args[0])

                    #obtain list of countries and create temporary layers for each
                    countiesList = []
                    try:
                        with arcpy.da.SearchCursor(outputFeatureClassName, ("NAME", )) as cursor:
                            for row in cursor:
                                distinctCounty = row[0]
                                if (distinctCounty not in countiesList):
                                    print distinctCounty
                                    countiesList.append(distinctCounty)
                                    
                    except Exception as e:
                        print "Exception caught in SearchCursor obtaining countiees list {0}".format(e.args[0])

                    try:
                        #create temporary county layers       
                        for targetCounty in countiesList:
                                countiesLayerWhereClause =  'NAME = '+"'"+str(targetCounty) + "'"
                                countyLayerName = str(targetCounty).replace(" County", "") + "Layer"
                                try:
                                    arcpy.MakeFeatureLayer_management(outputFeatureClassName, countyLayerName, countiesLayerWhereClause)
                                    countyLayersList.append(countyLayerName)
                                    print "County Feature Layer created {0}".format(countyLayerName)
                                except Exception as e:
                                    print "General Exception caught making target county feature layer {0}".format(e.args[0])

                    except Exception as e:
                        print "Exception caught creating temporay county layers {0}".format(e.args[0])

                    
                    #iterate the county polygons list, clip each crop layer raster to get values per year                   
                    for txCounty in countyLayersList:
                        #Clip each crop raster by county polygon
                        #sum the counts where value <> 0
                        #create the list of ag uses
                        #find poverty percentage from acs data
                        #update the output feature class for each year
                        txCountyName =  str(txCounty).replace("Layer", "")
                        txCountyName = txCountyName + " County"
                        print "County Name: {0}".format(txCountyName)

                        yearsIndex = 0; 
                        for year in landUseYears:
                            povertyYear = povertyYears[yearsIndex]
                            commonArcPyProcessing.processAnnualData(year, povertyYear, txCounty, txCountyName, outputFeatureClassName)
                            yearsIndex += 1                            
                           
                    try:
                        for countyLayerName in countyLayersList:
                            print "deleting temporary county layer {0}".format(countyLayerName)
                            arcpy.Delete_management(countyLayerName)
                    except Exception as e:
                        print "Exception caught deleting temporary county layers {0}".format(e.args[0])

                    #now iterate output feature class to get difference counts and data
                    try:                 
                        cursorFields = ["cnt2008", "povpct2008","cnt2017", "povpct2015","cntdiff", "povpctdiff", "top3_2008", "bot3_2008", "top3_2017", "bot3_2017","topdiff","botdiff", "sc2008","cntsc2008","sc2017","cntsc2017","cntscdiff","scdiff","cropct2008","cropct2017","cropctdiff","pctsc2008","pctsc2017","pctscdiff"]
                        with arcpy.da.UpdateCursor(outputFeatureClassName, cursorFields) as cursor:
                            for row in cursor:
                                c2008 = float(row[0])
                                c2017  = float(row[2])
                                cntdiff = (c2017 - c2008)
                                row[4] = cntdiff
                                print "cntdiff: {0}".format(str(cntdiff))
                                p2008 = float(row[1])
                                p2017 = float(row[3])
                                povdiff = p2017 - p2008                    
                                row[5] = povdiff
                                print "povdiff: {0}".format(povdiff)

                                #also need to see differences in actual top and bottom crops between 2008 & 2017
                                t08 = str(row[6])
                                t17 = str(row[8])
                                b08=str(row[7])
                                b17 = str(row[9])
                                
                                if (t08 != t17):
                                    temptdiff = "2008: " + t08 + ", 2017: " + t17
                                    print ("temptdiff: " + temptdiff)
                                    row[10] = temptdiff

                                if (b08 != b17):
                                    tempbdiff = "2008: " + b08 + ", 2017: " + b17
                                    print ("tempbdiff: " + tempbdiff)
                                    row[11] = tempbdiff
                                #"sc2008","cntsc2008","sc2017","cntsc2017","cntscdiff","scdiff"

                                sc2008 = str(row[12])
                                sc2017 = str(row[14])
                                cntsc2008 = float(row[13])
                                cntsc2017 = float(row[15])
                                cntscdiff = (cntsc2017 - cntsc2008)
                                row[16] = cntscdiff
                                if (sc2008 != sc2017):
                                    tempscdiff = "2008: {0}, 2017: {1}".format(sc2008, sc2017)
                                    row[17] = tempscdiff
                                #"cropct2008","cropct2017","cropctdiff","pctsc2008","pctsc2017","pctscdiff"
                                cropct2008 = float(row[18])
                                cropct2017 = float(row[19])
                                cropctdiff = (cropct2017 - cropct2008)
                                row[20] = cropctdiff
                                pctsc2008 = float(row[21])
                                pctsc2017 = float(row[22])
                                pctscdiff = (pctsc2017 - pctsc2008)
                                row[23] = pctscdiff
                                
                                #Update output feature class
                                cursor.updateRow(row)
                    except Exception as e:
                        print "Exception caught in final UpdateCursor {0}".format(e.args[0])

                    changeFields = ["cropct2008","pctsc2008","povpct2008","cropct2009","pctsc2009","povpct2009","crop0809","pov0809","sc0809","cropct2010","pctsc2010","povpct2010","crop0910","pov0910","sc0910","cropct2011","pctsc2011","povpct2011","crop1011","pov1011","sc1011","cropct2012","pctsc2012","povpct2012","crop1112","pov1112","sc1112","cropct2013","pctsc2013","povpct2013","crop1213","pov1213","sc1213","cropct2014","pctsc2014","povpct2014","crop1314","pov1314","sc1314","cropct2015","pctsc2015","povpct2015","crop1415","pov1415","sc1415","cropct2016","pctsc2016","crop1516","sc1516","cropct2017","pctsc2017","crop1617","sc1617"]                     
                    fieldsValid = False
                    try:
                        allFields = [f.name for f in arcpy.ListFields(outputFeatureClassName)]
                        for changeField in changeFields:
                            if (changeField in allFields):
                                fieldsValid = True
                            else:
                                print "changeField {0} not valid: ".format(changeField)
                                fieldsValid = False                                
                    except Exception as e:
                        print "Exception caught in fiedl check {0}".format(e.args[0])
                    if (fieldsValid):    
                        try:                 
                            with arcpy.da.UpdateCursor(outputFeatureClassName, changeFields) as cursor:
                                for row in cursor:
                                    #0809
                                    row[6]  = (float(row[3]) - float(row[0]))
                                    row[7]  = (float(row[5]) - float(row[2]))
                                    row[8]  = (float(row[4]) - float(row[1]))
                                    #0910
                                    row[12]  = (float(row[9]) - float(row[3]))
                                    row[13]  = (float(row[11]) - float(row[5]))
                                    row[14]  = (float(row[10]) - float(row[4]))
                                    #1011
                                    row[18]  = (float(row[15]) - float(row[9]))
                                    row[19]  = (float(row[17]) - float(row[11]))
                                    row[20]  = (float(row[16]) - float(row[10]))
                                    #1112
                                    row[24]  = (float(row[21]) - float(row[15]))
                                    row[25]  = (float(row[23]) - float(row[17]))
                                    row[26]  = (float(row[22]) - float(row[16]))
                                    #1213
                                    row[30]  = (float(row[27]) - float(row[21]))
                                    row[31]  = (float(row[29]) - float(row[23]))
                                    row[32]  = (float(row[28]) - float(row[22]))
                                    #1314
                                    row[36]  = (float(row[33]) - float(row[27]))
                                    row[37]  = (float(row[35]) - float(row[29]))
                                    row[38]  = (float(row[34]) - float(row[28]))
                                     #1415
                                    row[42]  = (float(row[39]) - float(row[33]))
                                    row[43]  = (float(row[41]) - float(row[35]))
                                    row[44]  = (float(row[40]) - float(row[34]))
                                    #1516
                                    row[47]  = (float(row[45]) - float(row[39]))
                                    row[48]  = (float(row[46]) - float(row[41]))
                                    #1617
                                    row[51]  = (float(row[49]) - float(row[45]))
                                    row[52]  = (float(row[50]) - float(row[46]))
                                    #Update output feature class
                                    cursor.updateRow(row)
                        except Exception as e:
                            print "Exception caught in changeFields UpdateCursor {0}".format(e.args[0])
                    
                    else:
                        print "cursor Fields not valid"
                    
                    
                except Exception as e:
                    print "Exception caught in feature copy {0}".format(e.args[0])
                
            else:
                print "The input feature class does not contain any records. Exiting script."

        try:
            arcpy.CheckInExtension("spatial")
            print "Spatial license checked back in"
        except:
            print "Exception caught checking in license"

    else:
        print "Input feature class and input address fields did not pass validation.  Please correct input parameters and try again."

else:
    print "Spatial License not available"


print("--- %s seconds ---" % (time.time() - start_time))
