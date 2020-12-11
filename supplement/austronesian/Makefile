# Download commit 17a4b30922f9d1010667ae8974f814c624e3e9a4 (2020-07-10): “Regenerate CLDF, minor refactorings”
abvd.zip:
	curl https://codeload.github.com/lexibank/abvd/zip/17a4b30922f9d1010667ae8974f814c624e3e9a4 -o abvd.zip

check-zip: abvd.zip
	echo "1e47e29e1b417ac70dae9086f2e9f7e4500390205d7e4ea7c229e875  abvd.zip" | sha224sum -c
	touch check-zip

austronesian-template.xml: ../template.xml
	cp ../template.xml austronesian-template.xml

raw_cldf/forms.csv raw_cldf/cognates.csv raw_cldf/cldf-metadata.json: abvd.zip check-zip
	unzip -DD -o -j bantu.zip "abvd-master/cldf/*" -d raw_cldf/

high_coverage_languages: raw_cldf/cldf-metadata.json raw_cldf/forms.csv
	python -m lexedata.exporter.coverage -l --min-concepts 189 --dataset raw_cldf/cldf-metadata.json > high_coverage_languages

good_austronesian austronesian.xml stats.tex: raw_cldf/cldf-metadata.json high_coverage_languages add_calibrations.py austronesian-template.xml
	cp austronesian-template.xml austronesian.xml
	echo "Explicitly exclude Favorlang [831]."
	grep -v 831 high_coverage_languages | PYTHONPATH=../ python add_calibrations.py --subset - -f aust1307 -o austronesian.xml > good_austronesian
	python -m lexedata.exporter.phylogenetics --stats stats.tex --metadata raw_cldf/cldf-metadata.json --languages good_austronesian -b -o austronesian.xml

run/vocabulary.log: austronesian.xml
	mkdir -p run
	cd run && beast ../austronesian.xml
