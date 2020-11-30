# Download commit 17a4b30922f9d1010667ae8974f814c624e3e9a4 (2020-07-10): “Regenerate CLDF, minor refactorings”
abvd.zip:
	curl https://codeload.github.com/lexibank/abvd/zip/17a4b30922f9d1010667ae8974f814c624e3e9a4 -o abvd.zip

check-zip: abvd.zip
	echo "1e47e29e1b417ac70dae9086f2e9f7e4500390205d7e4ea7c229e875  abvd.zip" | sha224sum -c
	touch check-zip

raw_cldf/forms.csv raw_cldf/cognates.csv raw_cldf/cldf-metadata.json: abvd.zip check-zip
	unzip -f -j abvd.zip  "abvd-master/cldf/*" -d raw_cldf/
	touch raw_cldf/forms.csv raw_cldf/cognates.csv raw_cldf/cldf-metadata.json

high_coverage_languages: raw_cldf/cldf-metadata.json raw_cldf/forms.csv
	python -m lexedata.exporter.coverage -l --min-concepts 189 --dataset raw_cldf/cldf-metadata.json | python filter-austronesian.py > high_coverage_languages

austronesian.xml stats.tex: raw_cldf/cldf-metadata.json high_coverage_languages
	cp austronesian-template.xml austronesian.xml
	python -m lexedata.exporter.phylogenetics --stats stats.tex --metadata raw_cldf/cldf-metadata.json --languages high_coverage_languages -b -o austronesian.xml
