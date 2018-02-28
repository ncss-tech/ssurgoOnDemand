~DeclareGeometry(@aoi)~
        select @aoi = geometry::STPolyFromText('POLYGON (( -89.7008309094 43.0934253545,-89.6785574043 43.0937667324,-89.6784799809 43.0823661006,-89.7002729347 43.0813705898,-89.7008309094 43.0934253545))', 4326)


        -- Extract all intersected polygons
        ~DeclareIdGeomTable(@intersectedPolygonGeometries)~
        ~GetClippedMapunits(@aoi,polygon,geo,@intersectedPolygonGeometries)~

        -- Return WKT for the polygonal geometries
        select * from @intersectedPolygonGeometries
        where geom.STGeometryType() = 'Polygon'

		
		SELECT areasymbol, musym, muname, mu.mukey  AS MUKEY,
                (SELECT interphr FROM component INNER JOIN cointerp ON component.cokey = cointerp.cokey AND component.cokey = c.cokey AND ruledepth = 0 AND mrulename LIKE 'AWM - Land Application of Municipal Sewage Sludge') as rating,
                (SELECT interphrc FROM component INNER JOIN cointerp ON component.cokey = cointerp.cokey AND component.cokey = c.cokey AND ruledepth = 0 AND mrulename LIKE 'AWM - Land Application of Municipal Sewage Sludge') as class,
                (SELECT DISTINCT SUBSTRING(  (  SELECT ( '; ' + interphrc)
                FROM mapunit
                INNER JOIN component ON component.mukey=mapunit.mukey AND compkind != 'miscellaneous area' AND component.cokey=c.cokey
                INNER JOIN cointerp ON component.cokey = cointerp.cokey AND mapunit.mukey = mu.mukey

                AND ruledepth != 0 AND interphrc NOT LIKE 'Not%' AND mrulename LIKE 'AWM - Land Application of Municipal Sewage Sludge' GROUP BY interphrc, interphr
                ORDER BY interphr DESC, interphrc
                FOR XML PATH('') ), 3, 1000) )as reason
                FROM legend  AS l
                INNER JOIN  mapunit AS mu ON mu.lkey = l.lkey AND  mu.mukey IN (753461,753550,753459,753505,2809845,753522,753594,753582,2809840,753583,753501,753462,753524,753460,2629035,2809839,2809842,753563,753549,753548,753586,753547,753588,753562,753458,2809846,753585,753502,753500,753597,753551,2809844)
                INNER JOIN  component AS c ON c.mukey = mu.mukey  AND c.cokey = (SELECT TOP 1 c1.cokey FROM component AS c1
                INNER JOIN mapunit ON c.mukey=mapunit.mukey AND c1.mukey=mu.mukey ORDER BY c1.comppct_r DESC, c1.cokey)