#!/bin/bash

### À placer dans le répertoire des résultats.
### Mon script pour lancer les expérimentations produit deux fichiers par instance :
### instance.time pour le runtime et instance.log pour l'affichage de la solution (ou un message indiquant qu'il n'y a pas d'allocation LEF)
### En plus de ça, mes noms de fichiers précisent la taille des instances.


cat inst_10*.time > results_10.time
cat inst_20*.time > results_20.time
cat inst_30*.time > results_30.time
cat inst_40*.time > results_40.time
cat inst_50*.time > results_50.time

cat inst_10*.log | grep LEF | wc -l > non_lef_10.log
cat inst_20*.log | grep LEF | wc -l > non_lef_20.log
cat inst_30*.log | grep LEF | wc -l > non_lef_30.log
cat inst_40*.log | grep LEF | wc -l > non_lef_40.log
cat inst_50*.log | grep LEF | wc -l > non_lef_50.log
