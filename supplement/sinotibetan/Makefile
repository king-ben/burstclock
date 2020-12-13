sinotibetan.zip:
	curl https://zenodo.org/record/2581321/files/lexibank/sagartst-v1.1.0.zip?download=1 -o sinotibetan.zip

check-zip: sinotibetan.zip
	echo "95f84332e1c5d1ec353899544cf563281dab95de0b6eee8cfb64241c  sinotibetan.zip" | sha224sum -c
	touch check-zip

sinotibetan-template.xml: ../template.xml
	cp ../template.xml sinotibetan-template.xml

raw_cldf/forms.csv raw_cldf/cognates.csv raw_cldf/cldf-metadata.json: sinotibetan.zip check-zip
	unzip -DD -o -j sinotibetan.zip  "lexibank-sagartst-24c5829/cldf/*" -d raw_cldf/

sinotibetan.xml stats.tex: raw_cldf/cldf-metadata.json add_calibrations.py sinotibetan-template.xml
	cp sinotibetan-template.xml sinotibetan.xml
	PYTHONPATH=../ python add_calibrations.py -o sinotibetan.xml
	python -m lexedata.exporter.phylogenetics --stats stats.tex --metadata raw_cldf/cldf-metadata.json --use-ids -b -o sinotibetan.xml

run/vocabulary.log: sinotibetan.xml
	mkdir -p run
	cd run && beast ../sinotibetan.xml
