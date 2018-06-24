import arcpy

def processAnnualData(landuseYear, povertyYear, txCountyLayer, txCountyName, outputFeatureClassName):
    print "processAnnualData (landuseYear {0}, povertyYear {1}, txCountyName {2})".format(str(landuseYear), str(povertyYear), str(txCountyName))

    dictInputRasters = {}
    
    dictInputRasters["inputRaster1992"]=r"C:\PSUGIS\GEOG586\TermProject\reprojectedFiles\ncld_tx_1992_rp_rc_71.tif"
    dictInputRasters["inputRaster2001"]=r"C:\PSUGIS\GEOG586\TermProject\reprojectedFiles\ncld_2001_tx_rp_rc_71.img"
    dictInputRasters["inputRaster2006"]=r"C:\PSUGIS\GEOG586\TermProject\reprojectedFiles\ncld_2006_tx_rp_rc_71.img"
    dictInputRasters["inputRaster2008"]=r"C:\PSUGIS\GEOG586\TermProject\reprojectedFiles\CDL_2008_48_rp_rc.tif"
    dictInputRasters["inputRaster2009"]=r"C:\PSUGIS\GEOG586\TermProject\reprojectedFiles\CDL_2009_48_rp_rc.tif"
    dictInputRasters["inputRaster2010"]=r"C:\PSUGIS\GEOG586\TermProject\reprojectedFiles\CDL_2010_48_rp_rc.tif"
    dictInputRasters["inputRaster2011"]=r"C:\PSUGIS\GEOG586\TermProject\reprojectedFiles\CDL_2011_48_rp_rc.tif"
    dictInputRasters["inputRaster2012"]=r"C:\PSUGIS\GEOG586\TermProject\reprojectedFiles\CDL_2012_48_rp_rc.tif"
    dictInputRasters["inputRaster2013"]=r"C:\PSUGIS\GEOG586\TermProject\reprojectedFiles\CDL_2013_48_rp_rc.tif"
    dictInputRasters["inputRaster2014"]=r"C:\PSUGIS\GEOG586\TermProject\reprojectedFiles\CDL_2014_48_rp_rc.tif"
    dictInputRasters["inputRaster2015"]=r"C:\PSUGIS\GEOG586\TermProject\reprojectedFiles\CDL_2015_48_rp_rc.tif"
    dictInputRasters["inputRaster2016"]=r"C:\PSUGIS\GEOG586\TermProject\reprojectedFiles\CDL_2016_48_rp_rc.tif"
    dictInputRasters["inputRaster2017"]=r"C:\PSUGIS\GEOG586\TermProject\reprojectedFiles\CDL_2017_48_rp_rc.tif"

    dictPovertyRasters = {}
    
    dictPovertyRasters["inputPoverty1990"]=r"C:\PSUGIS\GEOG586\TermProject\acs_files\1990_Texas.csv"
    dictPovertyRasters["inputPoverty2000"]=r"C:\PSUGIS\GEOG586\TermProject\acs_files\2000_Texas.csv"
    dictPovertyRasters["inputPoverty2008"]=r"C:\PSUGIS\GEOG586\TermProject\acs_files\ACS_09_5YR_GCT1701.ST05_with_ann.csv"
    dictPovertyRasters["inputPoverty2009"]=r"C:\PSUGIS\GEOG586\TermProject\acs_files\ACS_10_5YR_GCT1701.ST05_with_ann.csv"
    dictPovertyRasters["inputPoverty2010"]=r"C:\PSUGIS\GEOG586\TermProject\acs_files\ACS_11_5YR_GCT1701.ST05_with_ann.csv"
    dictPovertyRasters["inputPoverty2011"]=r"C:\PSUGIS\GEOG586\TermProject\acs_files\ACS_12_5YR_GCT1701.ST05_with_ann.csv"
    dictPovertyRasters["inputPoverty2012"]=r"C:\PSUGIS\GEOG586\TermProject\acs_files\ACS_13_5YR_GCT1701.ST05_with_ann.csv"
    dictPovertyRasters["inputPoverty2013"]=r"C:\PSUGIS\GEOG586\TermProject\acs_files\ACS_14_5YR_GCT1701.ST05_with_ann.csv"
    dictPovertyRasters["inputPoverty2014"]=r"C:\PSUGIS\GEOG586\TermProject\acs_files\ACS_15_5YR_GCT1701.ST05_with_ann.csv"
    dictPovertyRasters["inputPoverty2015"]=r"C:\PSUGIS\GEOG586\TermProject\acs_files\ACS_16_5YR_GCT1701.ST05_with_ann.csv"



    txCountyCountSum = 0
    txCountyAgUseList= []
    txCountyAgUseString = ""
    top3String = ""
    bottom3String = ""
    txCountyPovPct = 0
    specialCropCountSum = 0
    specialCropList = []
    specialCropString = ""
    outputName = landuseYear + "_temp_" + str(txCountyName) + ".tif"
    print "outputName: {0}".format(outputName)
    landUseRaster = "inputRaster"+landuseYear
    povertyRaster = ""
    if(povertyYear != ""):
        povertyRaster = "inputPoverty"+povertyYear

    print "land use raster: {0}, povertyRaster: {1}".format(str(landUseRaster), str(povertyRaster))
    try:
        arcpy.Clip_management(dictInputRasters[landUseRaster], "#", outputName, txCountyLayer, "0", "ClippingGeometry")
    except Exception as e:
        print "General Exception caught clipping raster {0}".format(e.args[0])

    #sum up counts for the county where value <> 0
    try:
        with arcpy.da.SearchCursor(outputName, ("VALUE","COUNT", "CLASS_NAME", ),sql_clause=(None, 'ORDER BY COUNT DESC')) as cursor:
            for row in cursor:
                val = row[0]
                if (val != 0):
                    txCountyCountSum += row[1]
                    crop = row[2]
                    if(crop != ""):
                        txCountyAgUseList.append(crop)

                        #specialtyCrop
                        if (isSpecialtyCrop(crop)):
                            specialCropCountSum += row[1]
                            specialCropList.append(crop)
                        
            print "txCountyCountSum {0}".format(txCountyCountSum)
            
            if (len(txCountyAgUseList) >=6 ):
                #print "ag use list >=6"
                top3List = txCountyAgUseList[0:3]
                #print top3List
                top3String = ",".join(top3List)
                bottom3List = txCountyAgUseList[-3:]
                #print bottom3List
                bottom3String = ",".join(bottom3List)
            elif (len(txCountyAgUseList) ==5):
                #print "ag use list  = 5"
                top3List = txCountyAgUseList[0:3]
                top3String = ",".join(top3List)
                bottom3List = txCountyAgUseList[-2:]
                bottom3String = ",".join(bottom3List)
            elif (len(txCountyAgUseList) ==4):
                #print "ag use list  = 4"
                top3List = txCountyAgUseList[0:2]
                top3String = ",".join(top3List)
                bottom3List = txCountyAgUseList[-2:]
                bottom3String = ",".join(bottom3List)
            elif (len(txCountyAgUseList) ==3):
                #print "ag use list  = 3"
                top3List = txCountyAgUseList[0:2]
                top3String = ",".join(top3List)
                bottom3List = txCountyAgUseList[-1]
                bottom3String = ",".join(bottom3List)
            elif (len(txCountyAgUseList) ==2):
                print "ag use list  = 2"
                top3String = txCountyAgUseList[0]
                bottom3String = txCountyAgUseList[-1]
            elif (len(txCountyAgUseList) ==1):
                print "ag use list  = 1"
                top3String = txCountyAgUseList[0]

            txCountyAgUseList.sort()
            txCountyAgUseString = ",".join(txCountyAgUseList)
            print "Texas County {0}  info: Count sum: {1}, Ag Uses: {2}".format(txCountyName, str(txCountyCountSum),txCountyAgUseString )
            specialCropList.sort()
            specialCropString = ",".join(specialCropList)
    except Exception as e:
        print "Exception caught in SearchCursor on the clipped output raster: {0}".format(e.args[0]) 

    #get poverty info here
    #use succeeding year because that data is for previous 12 months
    #PERCENT OF PEOPLE BELOW POVERTY LEVEL IN THE PAST 12 MONTHS (FOR WHOM POVERTY STATUS IS DETERMINED)
    if(povertyYear <> ""):
        try:
            acsSearchWhereClause =  'county_name = '+"'"+str(txCountyName) + "'"
            with arcpy.da.SearchCursor(dictPovertyRasters[povertyRaster], ("HC01", ),where_clause=acsSearchWhereClause) as cursor:
                for row in cursor:
                    txCountyPovPct = row[0]
                print "Texas County {0}  info: Poverty Percent {1}".format(txCountyName, txCountyPovPct)
        except Exception as e:
            print "Exception caught in SearchCursor on acs file {0}".format(e.args[0]) 


    #update output feature class with  values
    try:
        cursorCount = 0
        updateSearchWhereClause =  'NAME = '+"'"+str(txCountyName) + "'"
        print "updateSearchWhereClause: {0}".format(updateSearchWhereClause)
        if (landuseYear == "1992"):
            cursorFields = ["cnt1992",  "aguse1992", "povpct1990"]
        elif (landuseYear == "2001"):
            cursorFields = ["cnt2001",  "aguse2001", "povpct2000"]
        elif (landuseYear == "2006"):
            cursorFields = ["cnt2006",  "aguse2006"]
        elif (int(landuseYear) > 2006 and int(landuseYear) < 2016 ):
            cursorFields = ["cnt"+landuseYear,  "aguse"+landuseYear, "povpct"+landuseYear, "top3_"+landuseYear, "bot3_"+landuseYear,"sc"+landuseYear,"cntsc"+landuseYear]
            print "cursorFields: {0}".format(",".join(cursorFields))
        else:
            cursorFields = ["cnt"+landuseYear,  "aguse"+landuseYear, "top3_"+landuseYear, "bot3_"+landuseYear,"sc"+landuseYear,"cntsc"+landuseYear]
        with arcpy.da.UpdateCursor(outputFeatureClassName, cursorFields,  where_clause=updateSearchWhereClause) as cursor:
            for row in cursor:
                cursorCount +=1
                row[0] = txCountyCountSum
                row[1] = txCountyAgUseString
                if (povertyYear != ""):
                    row[2] = float(txCountyPovPct)
                if (int(landuseYear) > 2006 and int(landuseYear) < 2016 ):
                    row[3] = top3String
                    row[4] = bottom3String
                    row[5] = specialCropString
                    row[6] = specialCropCountSum
                elif (int(landuseYear) == 2016 or int(landuseYear) == 2017):
                    row[2] = top3String
                    row[3] = bottom3String
                    row[4] = specialCropString
                    row[5] = specialCropCountSum
                #Update output feature class
                cursor.updateRow(row)
    except Exception as e:
        print "Exception caught in UpdateCursor: {0}".format(e.args[0])

    #delete the temporary clipped feature
    try:
        arcpy.Delete_management(outputName)
    except Exception as e:
        print "Exception caught deleting temporary clipped output feature {0}".format(e.args[0])

def isSpecialtyCrop(cropName):
    print "cropName: {0}".format(cropName)
    slicedCropName = ""
    specialtyCropIdentified = False

    #Go ahead and return True for some of the harder ones to identify based on cropscape legend
    if cropName.lower() == "dry beans":
        return True

    if (cropName.lower().find("lettuce") > -1):
        return True

    if (cropName.lower().find("melon") > -1):
        return True

    if (cropName.lower().find("cantaloupe") > -1):
        return True

    ineligibleCrops = ["Alfalfa","Peanuts","Amylomaize","Pod corn","Barley (including malting barley)","Primrose","Buckwheat","Quinoa","Camelina","Rapeseed oil","Canola","Range grasses","Canola Oil","Rice","Clover","Rye","Cotton","Safflower meal","Cottonseed oil","Safflower oil","Dairy products","Shellfish (marine or freshwater)","Dent corn","Sorghum","Eggs","Soybean oil","Field corn","Soybeans","Fish (marine or freshwater)","Striped Maize","Flax","Sugar beets","Flaxseed","Sugarcane","Flint corn","Sunflower oil","Flower corn","Tobacco","Hay","Tofu","Hemp","Triticale","Livestock products","Waxy corn","Millet","Wheat","Mustard seed oil","White corn","Oats","Wild Rice","Peanut oil"]

    cropNameList = cropName.split(" ")
    for token in cropNameList:
        for nonSpecialCrop in ineligibleCrops:
            if token.lower() in nonSpecialCrop.lower():
                return False

    specialCrops = ["Herbs","Greens","Dry Beans","Dry Peas","Aborvitae","African Violet","Ajwain","Allspice","Almond","Angelica","Anise","Annatto","Anthurium","Apple","Apricot","Aronia Berry","Artemisia","Artichoke","Arum","Asafetida","Ash","Asparagus","Asparagus Fern","Astilbe","Astragalus","Avocado","Azalea","Azalea","Balsam Fir","Banana","Barberry","Basil","Bay","Snap Bean","Green Bean","Lima Bean","Bean","Beet","Begonia","Blackberry","Bladder wrack","Blue Spruce","Blueberry","Boldo","Bolivian coriander","Borage","Boxwood","Breadfruit","Broccoli","Broccoli Raab","Bromeliad","Brussels sprouts","Bubbleia","Cabbage","Chinese Cabbage","Cacao","Cacti","Calendula","Cananga","Candle nut","Caper","Caraway","Cardamom","Carnation","Carrot","Cashew","Cassia","Catnip","Cauliflower","Celeriac","Celery","Chamaecyparis","Chamomile","Cherimoya","Cherry","Chervil","Chestnut","Chickpeas","Chicory","Chive","Chrysanthemum","Cicely","Cilantro","Cinnamon","Citrus","Clary","Cloves","Coconut","Coffee","Coleus","Collards","Kale","Columbine","Comfrey","Comfrey","Common rue","Coneflower","Coniferous Evergreens","Coreopsis","Coriander","Cotoneaster","Crabapple","Cranberry","Crepe Myrtle","Cress","Cucumber","Cumin","Currant","Curry","Dahlia","Date","Daylily","Delphinium","Delphinium","Dianthus","Dieffenbachia","Dill","Dogwood","Douglas Fir","Dracaena","Edamame","Eggplant","Elm","Endive","Eucalyptus","Euonymus","Feijoa","Fennel","Fenugreek","Fenugreek","Fern","Feverfew","Ficus","Fig","Filbert","File","Fingerroot","Fir","Florist Chrysanthemum","Flowering Bulbs","Flowering Cherry","Flowering Pear","Flowering Plum","Foxglove","Fraser Fir","French sorrel","Galangal","Garden Chrysanthemum","Garlic","Geranium","Ginger","Ginkgo biloba","Ginseng","Gladiolus","Goat's rue","Goldenseal","Gooseberry","Grape","Guava","Gypsywort","Hawthorn","Hazelnut","Hemlock","Heuchera","Hibiscus","Holly","Holly","Honey","Honey Locust","Hops","Hops","Horehound","Horehound","Horseradish","Horsetail","Hosta","Hydrangea","Hydrangea","Hyssop","Impatiens","Iris","Ivy","Juniper","Kiwi","Kohlrabi","Lavender","Leatherleaf Fern","Leek","Lemon balm","Lemon thyme","Lentils","Lettuce","Lily","Linden","Liquorice","Litchi","Living Christmas Tree","Lovage","Macadamia","Mace","Magnolia","Mahlab","Malabathrum","Mango","Maple","Maple Syrup","Marigold","Marjoram","Marshmallow","Melon","Mint","Mullein","Mushroom","Mustard and other greens","Nectarine","Noble Fir","Nutmeg","Oak","Okra","Olive","Onion","Opuntia","Orchid","Orchid","Oregano","Ornamental Grasses","Orris root","Palm","Pansy","Papaya","Paprika","Parsley","Parsley","Parsnip","Passion flower","Passion Fruit","Patchouli","Garden Pea","English Pea","Pea","Peach","Pear","Pecan","Pennyroyal","Peony","Pepper","Persimmion","Petunia","Philodendron","Phlox","Pieris","Pine","Pineapple","Pistachio","Pittosporum","Plum","Prune","Poinsettia","Pokeweed","Pomegranate","Poplar","Potato","Pumpkin","Quince","Radish","Raisin","Raspberry","Redbud","Rhododendron","Rhubarb","Rocket","Arugula","Rose","Rose","Rose","Rosemary","Rudbeckia","Rue","Rutabaga","Saffron","Sage","Salsify","Salvia","Savory","Scots Pine","Senna","Service Berry","Skullcap","Snapdragon","Snapdragon","Sonchus","Sorrel","Spathipyllum","Spinach","Spirea","Spruce","Squash","St. John's wort","Stevia","Strawberry","Suriname cherry","Sweet corn","Sweet potato","Sweetgum","Swiss chard","Sycamore","Tansy","Taro","Tarragon","Tea Leaves","Thyme","Tomato","Tomatillo","Tulip","Turfgrass","Turmeric","Turnip","Urtica","Vanilla","Vegetable Transplants","Viburnum","Viburnum","Vinca","Walnut","Wasabi","Water cress","Watermelon","Weigela","White Pine","Witch hazel","Wood betony","Wormwood","Yarrow","Yerba buena","Yew"]
    if cropName.find(" ") > 0:
        whitespaceIndex = cropName.find(" ")
        slicedCropName = cropName[0:whitespaceIndex]
    else:
        slicedCropName = cropName

    slicedCropNameLen = len(slicedCropName)
    if slicedCropNameLen > 3:
        slicedCropName = slicedCropName[0:(slicedCropNameLen - 2)]

    print "slicedCropName  = {0}".format(slicedCropName)

    #now see if this is a specialty crop
    for spCrop in specialCrops:
        if slicedCropName.lower() in spCrop.lower():
            print "slicedCropName {0} found in spCrop {1}".format(slicedCropName.lower(), spCrop.lower()) 
            specialtyCropIdentified = True
            break
        

    return specialtyCropIdentified



class SpecialtyCrop:
    
    def __init__(self, cropName, cropCount):
        self.cropName = cropName
        self.cropCount = cropCount

    def setFields(self, cropName, cropCount):
        self.cropName = cropName
        self.cropCount = cropCount
