LOAD CSV WITH HEADERS FROM 'file:///buses.csv' AS bus_row 
WITH bus_row WHERE bus_row.name IS NOT NULL 
MERGE (bus:Bus {name: bus_row.name, longitude: toFloat(bus_row.longitude), 
latitude: toFloat(bus_row.latitude)});

LOAD CSV WITH HEADERS FROM 'file:///loads.csv' AS load_row 
WITH load_row WHERE load_row.name IS NOT NULL 
MERGE (load:Load {name: load_row.name, kw: toFloat(load_row.kw), 
kvar: toFloat(load_row.kvar), source: load_row.source, 
critical_load_factor: toFloat(load_row.critical_load_factor)})
MERGE (load_bus:Bus {name: load_row.source})
MERGE (load)-[:CONSUMES_POWER_FROM]->(load_bus);

LOAD CSV WITH HEADERS FROM 'file:///line_sections.csv' AS line_row 
WITH line_row WHERE line_row.name IS NOT NULL 
MERGE (from_bus:Bus {name: line_row.source})
MERGE (to_bus:Bus {name: line_row.target})
MERGE (from_bus)-[:CONNECTS_TO {name: line_row.name, source: line_row.source, 
target: line_row.target,ampacity: toFloat(line_row.ampacity),
height_m: toFloat(line_row.height_m), geom_type: line_row.geom_type}]->(to_bus);

LOAD CSV WITH HEADERS FROM 'file:///transformers.csv' AS xfmr_row
WITH xfmr_row WHERE xfmr_row.name IS NOT NULL 
MERGE (from_bus:Bus {name: xfmr_row.source})
MERGE (to_bus:Bus {name: xfmr_row.target})
MERGE (from_bus)-[:CONNECTS_TO {name: xfmr_row.name, source: xfmr_row.source, 
target: xfmr_row.target, kva: xfmr_row.kva, 
height_m: toFloat(xfmr_row.height_m)}]->(to_bus);


LOAD CSV WITH HEADERS FROM 'file:///pv_systems.csv' AS pv_row
WITH pv_row WHERE pv_row.name IS NOT NULL 
MERGE (sa:Solar {capacity: toFloat(pv_row.capacity), 
    name: pv_row.name, owner: pv_row.owner})
MERGE (ba:Bus {name: pv_row.bus})
MERGE (lo:Load {name: pv_row.owner})
MERGE (sa)-[:INJECTS_ACTIVE_POWER_TO]->(ba)
MERGE (lo)-[:OWNS]->(sa);

LOAD CSV WITH HEADERS FROM 'file:///energy_storage.csv' AS es_row
WITH es_row WHERE es_row.name IS NOT NULL 
MERGE (ea:EnergyStorage {kw: toFloat(es_row.kw), name: es_row.name, 
     owner:es_row.owner})
MERGE (ba:Bus {name: es_row.bus})
MERGE (lo:Load {name: es_row.owner})
MERGE (ea)-[:INJECTS_POWER]->(ba)
MERGE (ba)-[:CONSUMES_POWER]->(ea)
MERGE (lo)-[:OWNS]->(ea);

LOAD CSV WITH HEADERS FROM 'file:///substation.csv' AS sub_row
WITH sub_row WHERE sub_row.name IS NOT NULL 
MERGE (b:Bus {name: sub_row.name}) 
SET b:Substation;

MATCH (b:Bus)-[CONSUMES_POWER]-(c:Load)
SET c.longitude = b.longitude
SET c.latitude = b.latitude;

MATCH (c:Load)
WHERE c.latitude IS NULL
DETACH DELETE c;

LOAD CSV WITH HEADERS FROM 'file:///pharmacies.csv' AS p_row
WITH p_row WHERE p_row.name IS NOT NULL 
MERGE (p:Pharmacy {name: (p_row.name + p_row.gid), source:p_row.source, 
kw:toFloat(p_row.kw), kvar:toFloat(p_row.kvar), 
backup_capacity_kw:toFloat(p_row.backup_capacity_kw),
backup: toInteger(p_row.backup), 
longitude: toFloat(p_row.longitude), latitude: toFloat(p_row.latitude)})
WITH p
     MATCH (lo:Load)
     MERGE (lo)-[:VISITS_FOR_MEDICINE {distance: point.distance(
        point({longitude: p.longitude, latitude:p.latitude}),
        point({longitude: lo.longitude, latitude:lo.latitude})
     )}]->(p);

MATCH (p:Pharmacy)
WITH p 
    MATCH (b:Bus {name: p.source})
    MERGE (b)<-[:GETS_POWER_FROM]-(p);

LOAD CSV WITH HEADERS FROM 'file:///groceries.csv' AS g_row
WITH g_row WHERE g_row.name IS NOT NULL 
MERGE (g:Grocery {name: (g_row.name + g_row.gid), source:g_row.source, 
kw:toFloat(g_row.kw), kvar:toFloat(g_row.kvar), 
backup_capacity_kw:toFloat(g_row.backup_capacity_kw),
backup: toInteger(g_row.backup),
longitude: toFloat(g_row.longitude), latitude: toFloat(g_row.latitude)})
WITH g
    MATCH (lo:Load)
    MERGE (lo)-[:VISITS_FOR_GROCERIES {distance: point.distance(
       point({longitude: g.longitude, latitude:g.latitude}),
       point({longitude: lo.longitude, latitude:lo.latitude})
        )}]->(g);

MATCH (g:Grocery)
WITH g 
    MATCH (b:Bus {name: g.source})
    MERGE (b)<-[:GETS_POWER_FROM]-(g);

LOAD CSV WITH HEADERS FROM 'file:///medical_centers.csv' AS m_row
WITH m_row WHERE m_row.name IS NOT NULL 
MERGE (m:Hospital {name: (m_row.name + m_row.gid),
source:m_row.source, kw:toFloat(m_row.kw), kvar:toFloat(m_row.kvar), 
backup_capacity_kw:toFloat(m_row.backup_capacity_kw),
longitude: toFloat(m_row.longitude), 
latitude: toFloat(m_row.latitude), backup: toInteger(m_row.backup)})
WITH m
    MATCH (lo:Load)
    MERGE (lo)-[:VISITS_DURING_HEALTH_EMERGENCY {distance: point.distance(
       point({longitude: m.longitude, latitude:m.latitude}),
       point({longitude: lo.longitude, latitude:lo.latitude})
        )}]->(m);

MATCH (h:Hospital)
WITH h 
    MATCH (b:Bus {name: h.source})
    MERGE (b)<-[:GETS_POWER_FROM]-(h);

LOAD CSV WITH HEADERS FROM 'file:///banking.csv' AS b_row
WITH b_row WHERE b_row.name IS NOT NULL 
MERGE (b:Banking {name: (b_row.name + b_row.gid),
source: b_row.source,kw:toFloat(b_row.kw), kvar:toFloat(b_row.kvar), 
backup_capacity_kw:toFloat(b_row.backup_capacity_kw),
backup: toInteger(b_row.backup),
longitude: toFloat(b_row.longitude), latitude: toFloat(b_row.latitude)})
WITH b
    MATCH (lo:Load)
    MERGE (lo)-[:VISITS_TO_WITHDRAW_OR_DEPOSIT_CURRENCY {distance: point.distance(
       point({longitude: b.longitude, latitude:b.latitude}),
       point({longitude: lo.longitude, latitude:lo.latitude})
        )}]->(b);

MATCH (b1:Banking)
WITH b1
    MATCH (b:Bus {name: b1.source})
    MERGE (b)<-[:GETS_POWER_FROM]-(b1);

LOAD CSV WITH HEADERS FROM 'file:///convenience.csv' AS c_row
WITH c_row WHERE c_row.name IS NOT NULL 
MERGE (c:Convenience {name: (c_row.name + c_row.gid), 
source:c_row.source, kw:toFloat(c_row.kw), kvar:toFloat(c_row.kvar), 
backup_capacity_kw:toFloat(c_row.backup_capacity_kw),
backup: toInteger(c_row.backup),
longitude: toFloat(c_row.longitude), latitude: toFloat(c_row.latitude)})
WITH c
    MATCH (lo:Load)
    MERGE (lo)-[:VISITS_FOR_SERVICE {distance: point.distance(
       point({longitude: c.longitude, latitude:c.latitude}),
       point({longitude: lo.longitude, latitude:lo.latitude})
        )}]->(c);

MATCH (c:Convenience)
WITH c
    MATCH (b:Bus {name: c.source})
    MERGE (b)<-[:GETS_POWER_FROM]-(c);

LOAD CSV WITH HEADERS FROM 'file:///shelters.csv' AS s_row
WITH s_row WHERE s_row.use_type IS NOT NULL 
MERGE (s:Shelter {name: (s_row.use_type + s_row.gid), 
backup: toInteger(s_row.backup), source: s_row.source, kw:toFloat(s_row.kw), 
kvar:toFloat(s_row.kvar), 
backup_capacity_kw:toFloat(s_row.backup_capacity_kw),
longitude: toFloat(s_row.longitude), latitude: toFloat(s_row.latitude)})
WITH s
    MATCH (lo:Load)
    MERGE (lo)-[:VISITS_FOR_SERVICE {distance: point.distance(
       point({longitude: s.longitude, latitude:s.latitude}),
       point({longitude: lo.longitude, latitude:lo.latitude})
    )}]->(s);

MATCH (s:Shelter)
WITH s
    MATCH (b:Bus {name: s.source})
    MERGE (b)<-[:GETS_POWER_FROM]-(s);

MATCH (b1:Bus)-[r:CONNECTS_TO]-(b2:Bus)
SET r.longitude = (b1.longitude + b2.longitude)/2
SET r.latitude = (b1.latitude + b2.latitude)/2;

MATCH p=(sourceNode:Bus)-[r:CONNECTS_TO]-(targetNode:Bus)
WHERE r.ampacity IS NOT NULL
WITH r,sourceNode, CASE r.num_phase
WHEN 3 THEN 1.732
ELSE 1
END AS multiplier
SET r.kva = multiplier*r.ampacity*sourceNode.kv;

MATCH p=(sourceNode:Bus)-[r:CONSUMES_POWER_FROM]-(targetNode:Load)
SET targetNode.kw = toFloat(targetNode.kw)
SET targetNode.kvar = toFloat(targetNode.kvar)
SET r.kva = sqrt(targetNode.kw*targetNode.kw+targetNode.kvar*targetNode.kvar);

MATCH p=(sourceNode:Bus)-[r:INJECTS_ACTIVE_POWER_TO]-(targetNode:Solar)
SET targetNode.capacity = toFloat(targetNode.capacity)
SET r.kva = targetNode.capacity;


MATCH p=(sourceNode:Bus)-[r:INJECTS_POWER]-(targetNode:EnergyStorage)
SET targetNode.kw = toFloat(targetNode.kw)
SET r.kva = targetNode.kw;

MATCH (sourceNode:Bus)-[r:CONNECTS_TO]-(targetNode:Bus)
SET r.kva = toFloat(r.kva);

MATCH p=()-[r:GETS_POWER_FROM]->()
WHERE r.kva is null
SET r.kva = 300;

MATCH p=()-[r:CONNECTS_TO]->() 
WHERE r.kva IS null
SET r.kva = 300;