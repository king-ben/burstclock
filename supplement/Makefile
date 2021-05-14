arawak-template.xml: templates/template.xml
	python strip-markdown.py > arawak-template.xml

arawak.xml stats.tex: ../languages.csv ../forms.csv ../cognates.csv ../Wordlist-metadata.json add_calibrations.py arawak-template.xml
	sed -e 's/vocabulary/arawak/g' arawak-template.xml > arawak.xml
	python -m lexedata.exporter.phylogenetics --stats stats.tex --metadata ../Wordlist-metadata.json -b -o arawak.xml

arawak-dated.xml: ../languages.csv ../Wordlist-metadata.json add_calibrations.py arawak.xml
	sed -e 's/vocabulary/arawak/g' arawak.xml > arawak-dated.xml
	python add_calibrations.py -s -o arawak-dated.xml -m ../Wordlist-metadata.json

run/vocabulary.log: arawak-dated.xml
	mkdir -p run
	cd run && beast ../arawak-dated.xml
