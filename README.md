# ssurgoOnDemand
user driven SSURGO properties and interpretations

<b>*DISCLAIMER* <i>The information returned by the SSURO On-Demand tools are provided "as is".  Additionally, there is no expressed or implied accuracy of the data returned.  Use at your own risk.</i> </b>


The purpose of these tools are to give users the ability to get Soil Survey Geographic Database (SSURGO) properties and interpretations in an efficient manner.  They are very similiar to the United States Department of Agriculture  - Natural Resource Conservation Service's distributed Soil Data Viewer (SDV), although there are distinct differences.  The most important difference is the data collected with the SSURGO On-Demand (SOD) tools are collected in real-time via web requests to Soil Data Access (https://sdmdataaccess.nrcs.usda.gov/).  SOD tools do not require users to have the data found in a traditional SSURGO download from the NRCS's official repository, Web Soil Survey (https://websoilsurvey.sc.egov.usda.gov/App/HomePage.htm).  The main intent of both SOD and SDV are to hide the complex relationships of the SSURGO tables and allow the users to focus on asking the question they need to get the information they want.  This is accomplished in the user interface of the tools and the subsequent SQL is built and executed for the user. Currently, the tools packaged here are designed to run within the ESRI ArcGIS Desktop Application - ArcMap, version 10.1 or greater.  However, much of the Python code is recyclable and could run within a Python intepreter or other GIS applications such as Quantum GIS with some modification.

NOTE:  The queries in these tools only consider the major components of soil map units.

Within the SOD tools are 2 primary toolsets, descibed as follows:

<H1>1. Areasymbol</H1>
The Areasymbol tools collect SSURGO properties and interpretations based on a user supplied list of Soil Survey areasymbols (e.g. NC123).  After the areasymbols have been collected, an aggregation method (see below) is selected .  Tee aggregation method has no affect on interpretations other than how the SSURGO data aggregated.  For soil properties, the aggregation method drives what properties can be run.  For example, you can't run the weighted average aggregation method on Taxonomic Order. Similarly, for the same soil property, you wouldn't specify a depth range.  The point here is the aggregation method affects what parameters need to be supplied for the SQL generation.  It is important to note the user can specify any number of areasymbols and any number of interpretations.  This is another distinct advantage of these tools.  You could collect all of the SSURGO interpretations for every soil survey area (areasymbol) by executing the tool 1 time.  This also demonstrates the flexibility SOD has in defining the geographic extent over which information is collected. The only constraint is the extent of soil survey areas selected to run (and these can be discontinuous).  
 
As SOD Areasymbol tools execute, 2 lists are collected from the tool dialog, a list of interpretations/properties and a list of areasymbols.  As each interpretation/property is run, every areasymbol is run against the interpretation/property requested.  For instance, suppose you wanted to collect the weighted average of sand, silt and clay for 5 soil survey areas.  The sand property would run for all 5 soil survey areas and built into a table.  Next the silt would run for all 5 soil survey areas and built into a table, and so on.  In this example a total of 15 web request would have been sent and 3 tables are built.  Two VERY IMPORTANT things here... 
 
 A. All the areasymbol tools do is generate tables.  They are not collecting spatial data.
 
 B. They are collecting stored information.  They are not making calculations(with the exception of the weighted average aggregation method).

<H1>2. Express</H1>
The Express toolset is nearly identical to the Areasymbol toolset, with 2 exceptions.

A. The area to collect SSURGO information over is defined by the user.  The user digitizes coordinates into a 'feature set' after the tool is open. The points in the feature set are closed (first point is also the last) into a polygon.  The polygon is sent to Soil Data Access and the features set points (polygon) are used to clip SSURGO spatial data.  The geomotries of the clip operation are returned, along with the mapunit keys (unique identifier). It is best to keep the points in the feature set simple and beware of self intersections as they are fatal.

B. Instead of running on a list of areasymbols, the SQL queries on a list of mapunit keys.

The properties and interpretations options are identical to what was discussed for the Areasymbol toolset.

The Express tools present the user the option of creating layer files (.lyr) where the the resultant interpretation/property are joined to the geometry and saved to disk as a virtual join.  Additionally, for soil properties, an option exists to append all of the selected soil properties to a single table.  In this case, if the user ran sand, silt, and clay properties, instead of 3 output tables, there is only 1 table with a sand column, a silt column, and a clay column.

<H1>Supplemental Information</H1>
<H3>Aggregation Method</H3>
Aggregation is the process by which a set of component attribute values is reduced to a single value to represent the map unit as a whole.

A map unit is typically composed of one or more "components". A component is either some type of soil or some nonsoil entity, e.g., rock outcrop. The components in the map unit name represent the major soils within a map unit delineation. Minor components make up the balance of the map unit. Great differences in soil properties can occur between map unit components and within short distances. Minor components may be very different from the major components. Such differences could significantly affect use and management of the map unit. Minor components may or may not be documented in the database. The results of aggregation do not reflect the presence or absence of limitations of the components which are not listed in the database. An on-site investigation is required to identify the location of individual map unit components. For queries of soil properties, only major components are considered for Dominant Component (numeric) and Weighted Average aggregation methods (see below). Additionally, the aggregation method selected drives the available properties to be queried. For queries of soil interpretations, all components are condisered.

For each of a map unit's components, a corresponding percent composition is recorded. A percent composition of 60 indicates that the corresponding component typically makes up approximately 60% of the map unit. Percent composition is a critical factor in some, but not all, aggregation methods.

For the attribute being aggregated, the first step of the aggregation process is to derive one attribute value for each of a map unit's components. From this set of component attributes, the next step of the aggregation process derives a single value that represents the map unit as a whole. Once a single value for each map unit is derived, a thematic map for soil map units can be generated. Aggregation must be done because, on any soil map, map units are delineated but components are not.

The aggregation method "Dominant Component" returns the attribute value associated with the component with the highest percent composition in the map unit. If more than one component shares the highest percent composition, the value of the first named component is returned.

The aggregation method "Dominant Condition" first groups like attribute values for the components in a map unit. For each group, percent composition is set to the sum of the percent composition of all components participating in that group. These groups now represent "conditions" rather than components. The attribute value associated with the group with the highest cumulative percent composition is returned. If more than one group shares the highest cumulative percent composition, the value of the group having the first named component of the mapunit is returned.

The aggregation method "Weighted Average" computes a weighted average value for all components in the map unit. Percent composition is the weighting factor. The result returned by this aggregation method represents a weighted average value of the corresponding attribute throughout the map unit.

The aggregation method "Minimum or Maximum" returns either the lowest or highest attribute value among all components of the map unit, depending on the corresponding "tie-break" rule. In this case, the "tie-break" rule indicates whether the lowest or highest value among all components should be returned. For this aggregation method, percent composition ties cannot occur. The result may correspond to a map unit component of very minor extent. This aggregation method is appropriate for either numeric attributes or attributes with a ranked or logically ordered domain.


