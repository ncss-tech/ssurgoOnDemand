--dominant condition
DROP TABLE IF EXISTS sod_domcond_temp;

CREATE TABLE sod_domcond_temp AS
SELECT  cokey
    ,mrulekey 
    ,mrulename
  ,rulename
    ,ruledepth
    ,interphr 
    ,interphrc
  ,cointerpkey

FROM[cointerp] WHERE mrulename = 'ENG - Septic Tank Absorption Fields' ;


CREATE TABLE sod_dom_cond_ENG_Septic_Tank_Absorption_Fields AS SELECT areasymbol, musym, muname, mu.mukey/1  AS mukey, 
(SELECT ROUND (AVG(interphr) over(partition by interphrc),2)
FROM mapunit
INNER JOIN component ON component.mukey=mapunit.mukey
INNER JOIN sod_domcond_temp ON component.cokey = sod_domcond_temp.cokey AND mapunit.mukey = mu.mukey AND ruledepth = 0 AND mrulename LIKE 'ENG - Septic Tank Absorption Fields' GROUP BY interphrc, interphr
ORDER BY SUM (comppct_r) DESC LIMIT 1)as rating,
(SELECT interphrc
FROM mapunit
INNER JOIN component ON component.mukey=mapunit.mukey
INNER JOIN sod_domcond_temp ON component.cokey = sod_domcond_temp.cokey AND mapunit.mukey = mu.mukey AND ruledepth = 0 AND mrulename LIKE 'ENG - Septic Tank Absorption Fields'
GROUP BY interphrc, comppct_r ORDER BY SUM(comppct_r) over(partition by interphrc) DESC LIMIT 1) as class,

(SELECT GROUP_CONCAT( DISTINCT interphrc)
FROM mapunit
INNER JOIN component ON component.mukey=mapunit.mukey AND compkind != 'miscellaneous area' 
INNER JOIN sod_domcond_temp ON component.cokey = sod_domcond_temp.cokey AND mapunit.mukey = mu.mukey 
AND ruledepth != 0 AND interphrc NOT LIKE 'Not%' AND mrulename LIKE 'ENG - Septic Tank Absorption Fields' GROUP BY interphrc
ORDER BY interphr DESC, interphrc
)as reason

FROM legend  AS l
INNER JOIN  mapunit AS mu ON mu.lkey = l.lkey 
ORDER BY areasymbol, musym, muname, mu.mukey;

DROP TABLE IF EXISTS sod_domcond_temp;
