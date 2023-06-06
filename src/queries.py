# -*- coding: UTF-8 -*-

get_mineral_log = """
    SELECT ml.id, ml.mindat_id, ml.formula, ml.ns_class, ml.ns_subclass, ml.ns_family FROM mineral_log ml;
"""

get_carbonates_mr = """
    SELECT ml.id, ml.name FROM mineral_log ml 
    INNER JOIN ns_subclass ns ON ml.ns_subclass = ns.id 
    WHERE ns.ns_class = 5 AND ns.ns_subclass != '5.N';
"""

get_carbonates_mindat = """
    SELECT ml.id, ml.name, ml.description, ml.formula, ml.ima_status FROM minerals ml 
    WHERE ml.strunz10ed1 = 5 AND ml.strunz10ed2 != 'N';
"""

get_ns_for_carbonates = """
    SELECT ns.id AS id, ns.ns_subclass as subclass, 
    ns.description AS subclass_description 
    FROM ns_subclass ns 
    LEFT JOIN ns_class nc ON nc.id = ns.ns_class 
    WHERE nc.id = 5 AND ns.ns_subclass != '5.N';
"""
