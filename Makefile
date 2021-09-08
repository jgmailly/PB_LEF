target=pb_LEF

all: ${target}.tex references.bib
	pdflatex ${target}.tex
	bibtex ${target}.aux
	pdflatex ${target}.tex
	pdflatex ${target}.tex

clean:
	rm -f *~ ${target}.aux ${target}.out ${target}.log ${target}.pdf ${target}.bbl ${target}.blg ${target}.synctex.gz
