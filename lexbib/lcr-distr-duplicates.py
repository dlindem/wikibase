


query = """
select distinct ?lcr ?distnode1 ?distdate1 ?distplace1 ?distnode2 ?distdate2 ?distplace2 #(count(?distnode) as ?count)
where { ?lcr ldp:P5 lwb:Q4; lp:P55 ?distnode1.
       ?distnode1 lpq:P15 ?distdate1 .
       optional { ?distnode1 lpq:P164 ?distplace1 . }
       ?lcr lp:P55 ?distnode2. filter(?distnode1 != ?distnode2)
       ?distnode2 lpq:P15 ?distdate2 . filter(?distdate2 = ?distdate1)
       optional { ?distnode2 lpq:P164 ?distplace2 .  }
    } group by ?lcr ?distnode1 ?distdate1 ?distplace1 ?distnode2 ?distdate2 ?distplace2
# HAVING (count(?distnode) > 1)
"""
