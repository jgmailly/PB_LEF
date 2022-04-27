To generate all the graph used in the report (compare the different implementations, 
you run generateAllTest.sh then make_graph.py. Careful, since it will take a good while to run everything

A quick overview of the parameters of src/decide_LEF_clean.py (could simply look at --help)
usage: src/decide_LEF_clean.py [-h] [--LEF {consequence,complement,pairs,special}] [-q] [-o OUT] [--mus]
                           [--draw] [-t TIMEOUT] [--partial PARTIAL]
                           pref_file social_file

Basically, will be used as such: 
python decide_LEF_clean.py pref_file social_file

Then some additional parameters can be set.

--LEF, followed by {consequence,complement,pairs,special}, generate the appropriate LEF clauses (see report). Default is consequence. special is pairs+consequence.

--partial, 

           if followed by either 'agents', 'objects' or 'both', it will generate the appropriate house allocation clauses.
           
           if followed by '1,o1', where o1 is the name of an object (has stated in a preference file), then that means that instead of using the usual house allocation clauses, we force agent 1 to get object o1.
           
           if followed by '1,o1,o2,..', same as before but now agent 1 has a choice between any of the objects. This works with any number of objects.
           
           if followed by '1,*' same as before but agent 1 can choose among all the objects. 
           
           if followed by '*,o1' same as before but now it means that we only force o1 to be given to at least one agent.
in 

--mus is used to generate the mus. You can add --draw to also generate an old version of the justification graph (helps understanding somewhat)
-o path/to/file to output the timings to a file. (used by generateAllTest.sh and make_graph.py)
