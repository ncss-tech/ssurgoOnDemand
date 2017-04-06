# ssurgoOnDemand
user driven SSURGO properties and interpretations


THe purpose of these tools are to give users the ability to get Soil Survey Geographic Database (SSURGO) properties and interpretations in an efficient manner.  It is very similiar to the United States Department of Agriculture  - Natural Resource Conservation Service's distributed Soil Data Viewer (SDV), although there are distinct differences.  The most importatn difference is the data collected with the SSURGO On-Demand (SOD) tools are collecting the information in real-time via web requests to Soil Data Access (https://sdmdataaccess.nrcs.usda.gov/).  SOD tools do not require users to have the data found in a traditional SSURGO download from the NRCS's official repository, Web Soil Survey (https://websoilsurvey.sc.egov.usda.gov/App/HomePage.htm).  The main intent of both SOD and SDV are to hide the complex relationships of the National Soil Information System (NASIS) databse tables and allow the users to focus on asking the question they need to get the information they want.  This is acconplished in the user interface of the tools and the subsequent SQL is built and executed for the user. Currently, the tools packaged here are designed to run within the ESRI ArcGIS Desktop Application - ArcMap, version 10.1 or greater.  However, much of the Python code is recyclable and could run within a Python intepreter or other GIS applicaations such as Quantum GIS with some modification.

Within the SOD tools are 2 primary toolsets, descibed as follows:

<H1>Areasymbol</H1>
 The Areasymbol tools collect SSURGO properties and interpretations based on a user supplied list of Soil Survey areasymbols (e.g. NC123).  It is important to 
