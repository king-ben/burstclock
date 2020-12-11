from calibrations import main, normal, until

main(
    [
        # ‘(i) Proto-Oceanic (mean of 3,300 y, SD = 100 y)’
        # Development of Proto-Oceanic 3,200 – 3,600 [Lynch et al. (2002)]
        # Oceanic: https://glottolog.org/resource/languoid/id/ocea1241
        {"glottolog_clade": "ocea1241", "d": normal(mean=3300, std=100)},
        # ‘(ii) Proto-Central Pacific (mean of 3,000 y, SD = 100)’
        # Central Pacific linkage: https://glottolog.org/resource/languoid/id/cent2060
        {"glottolog_clade": "cent2060", "d": normal(mean=3000, std=100)},
        # ‘(iii) Proto-Malayo-Polynesian (mean of 4,000 y, SD = 250)’
        # Austronesian Entry into the Philippines (Proto-Malayo-Polynesian) 3,600 – 4,500 [Pawley (2002)]
        # Malayo-Polynesian: https://glottolog.org/resource/languoid/id/mala1545
        {"glottolog_clade": "mala1545", "d": normal(mean=4000, std=250)},
        # ‘(iv) Proto-Micronesian (mean of 2,000 y, SD = 100)’
        # Micronesian: https://glottolog.org/resource/languoid/id/micr1243
        # Settlement of Micronesia 1,900 – 2,200 Pawley (2002)
        {"glottolog_clade": "micr1243", "d": normal(mean=2000, std=100)},
        # ‘(v) Proto-Austronesian (mean of 5,200 y, SD = 300)’
        # Austronesian: https://glottolog.org/resource/languoid/id/aust1307
        {"glottolog_clade": "aust1307", "d": normal(mean=5200, std=300)},
        # Old Javanese 700 – 1,200 [Zoetmulder (1982)]
        # https://abvd.shh.mpg.de/austronesian/language.php?id=290
        {"languages": {"290"}, "d": until(700, 1200)},
        # Settlement of Madagascar 1,100 – 1,300 [Vérin & Wright (1999)]
        # Malagasic: https://glottolog.org/resource/languoid/id/mala1537
        {"glottolog_clade": "mala1537", "d": until(1100, 1300)},
        # Proto-Javanese 1,100 – 1,300 [Zoetmulder (1982), Anderson & Sinoto (2002)]
        # Modern Javanese: https://glottolog.org/resource/languoid/id/mode1251
        {"glottolog_clade": "java1253", "d": until(1100, 1300)},
        # Initial Settlement of Eastern Polynesia 1,150 – 1,800 [Green (2003), Kirch & Green (2001), Pawley (2002)]
        # East Polynesian: https://glottolog.org/resource/languoid/id/east2449
        {"glottolog_clade": "east2449", "d": until(1150, 1800)},
        # Habitation of Tuvalu/Tokelau becomes possible 1,000 – 2,000 Dickinson (2003)
        # Ellicean [clade with Tuvalu and Samoan-Tokelauan]: https://glottolog.org/resource/languoid/id/elli1239
        {"glottolog_clade": "elli1239", "d": until(1000, 2000)},
        # Historical Attestation of Chamic Subgroup 1,800 – 2,500 Thurgood (1999)
        # Chamic: https://glottolog.org/resource/languoid/id/cham1330
        {"glottolog_clade": "cham1330", "d": until(1800, 2500)},
        # Existence of Malayo-Chamic Subgroup 2,000 – 3,000 Thurgood (1999)
        # North and East Malayo-Sumbawan [clade with Malayic and Chamic]: https://glottolog.org/resource/languoid/id/nort3170
        {"glottolog_clade": "nort3170", "d": until(2000, 3000)},
    ]
)

# Favorlang 346 – 384 [Age of Source Data]
# https://abvd.shh.mpg.de/austronesian/language.php?id=831
# “In Ogawa & Li (2003), Some data may have also been derived from Dutch sources (missionary tracts, etc.) dating from the mid-1600's.”
# Manually excluded.
{"languages": {"831"}, "d": until(346, 384)},

# Human settlement of the Reefs and Santa Cruz 3,000 – 3,150 Green et al. (2008)
# Reefs-Santa Cruz: https://glottolog.org/resource/languoid/id/reef1242
# Only one tip, excluded
{"glottolog_clade": "reef1242", "d": until(3000, 3150)},
