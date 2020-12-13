indoeuropean.nex:
	curl https://raw.githubusercontent.com/PhyloStar/ie-phylo-exps/a63c0b52f7772adc2341572932a74b23d92570df/medium1.nex -o indoeuropean.nex

indoeuropean.zip:
	curl https://muse.jhu.edu/article/576999/file/supp02.zip -o indoeuropean.zip

check-zip: indoeuropean.zip indoeuropean.nex
	echo "2c04d51bc1b800715fbd8342771faae8e08b7c7d07cc554819989e74  indoeuropean.zip" | sha224sum -c
	echo "59451dbfcdb949ba8d8a42c74d9f70f629b35027a08323393bf3b415  indoeuropean.nex" | sha224sum -c
	touch check-zip

data/ielex-130421-ag-cc.txt: indoeuropean.zip check-zip
	unzip -DD -o -j indoeuropean.zip "sup/ielex-130421-ag-cc.txt" -d data/

data/ielex-130421-ag-cc-with-concept.tsv: data/ielex-130421-ag-cc.txt
	 python add_singleton_cognate_sets.py data/ielex-130421-ag-cc.txt | grep -v 22842 > data/ielex-130421-ag-cc-with-concept.tsv

indoeuropean-template.xml: ../template.xml
	cp ../template.xml indoeuropean-template.xml

indoeuropean.xml: indoeuropean-template.xml add_calibrations.py data/ielex-130421-ag-cc-with-concept.tsv data/force-metadata.json
	cp indoeuropean-template.xml indoeuropean.xml
	PYTHONPATH=../ python add_calibrations.py -o indoeuropean.xml
	python -m lexedata.exporter.phylogenetics --stats stats.tex --metadata data/force-metadata.json --use-ids -b -o indoeuropean.xml


run/vocabulary.log: indoeuropean.xml
	mkdir -p run
	cd run && beast ../indoeuropean.xml
