from calibrations import main, normal, until  # noqa: 401

r = main(
    [
        {"languages": {"Hittite"}, "d": normal(3400, 100)},
        # {"languages": {"Vedic_Sanskrit"}, "d": normal(3250, 250)},
        # {"languages": {"Avestan"}, "d": normal(2500, 50)},
        # {"languages": {"Ancient_Greek"}, "d": normal(2450, 50)},
        {"languages": {"Latin"}, "d": normal(2150, 50)},
        {"languages": {"Gothic"}, "d": normal(1650, 25)},
        # {"languages": {"Old_High_German"}, "d": normal(1150, 50)},
        # {"languages": {"Old_English"}, "d": normal(1000, 50)},
        {"languages": {"Old_Norse"}, "d": normal(800, 50)},
        # {"languages": {"Classical_Armenian"}, "d": normal(1550, 50)},
        {"languages": {"Tocharian_B"}, "d": normal(1350, 150)},
        # {"languages": {"Old_Irish"}, "d": normal(1200, 100)},
        {"languages": {"Cornish"}, "d": normal(300, 100)},
        {"languages": {"Old_Church_Slavonic"}, "d": normal(1000, 50)},
        {
            "languages": {
                "Gothic",
                "Old_Norse",
                # "Icelandic_ST",
                # "Faroese",
                "Norwegian",
                # "Swedish",
                # "Danish",
                # "Old_English",
                "English",
                "Frisian",
                # "Old_High_German",
                "German",
                # "Luxembourgish",
                "Schwyzerdutsch",
                # "Dutch_List",
                "Flemish",
                "Afrikaans",
            },
            "name": "Germanic",
            "monophyletic": True,
            "d": {"tag": "Uniform", "name": "distr", "lower": "2250", "upper": "20000"},
        },
        {
            "languages": {
                "Latin",
                "Sardinian_N",
                "Sardinian_C",
                "Rumanian_List",
                # "Catalan",
                # "Portuguese_ST",
                "Spanish",
                "French",
                # "Provencal",
                # "Walloon",
                # "Ladin",
                "Romansh",
                # "Friulian",
                # "Italian",
            },
            "name": "Romance",
            "d": {"tag": "Uniform", "name": "distr", "lower": "1750", "upper": "20000"},
        },
        # {
        #     # Old Norse and Norwegian are both West Scandinavian languages, so
        #     # two branches of Scandinavian are missing – and Old Norse does have
        #     "languages": {
        #         "Old_Norse",
        #         # "Icelandic_ST",
        #         # "Faroese",
        #         "Norwegian",
        #         # "Swedish",
        #         # "Danish",
        #     },
        #     "name": "Scandinavian",
        #     "monophyletic": True,
        #     "d": {"tag": "Uniform", "name": "distr", "lower": "1500", "upper": "20000"},
        # },
        # {
        #     # No West Slavic language. Presumably, the split between West and
        #     # South Slavic is secondary, after the split of East Slavic from
        #     # the rest, so this would be fine; but we don't want to rely on it,
        #     # and we do have OCS as calibration tip.
        #     "languages": {
        #         # "Czech",
        #         # "Slovak",
        #         # "Polish",
        #         # "Upper_Sorbian",
        #         # "Ukrainian",
        #         # "Byelorussian",
        #         "Russian",
        #         # "Slovenian",
        #         # "Macedonian",
        #         "Bulgarian",
        #         "Serbian",
        #         "Old_Church_Slavonic",
        #     },
        #     "name": "Slavic",
        #     "d": {"tag": "Uniform", "name": "distr", "lower": "1500", "upper": "20000"},
        # },
        # {
        #     "languages": {
        #         "Lithuanian_ST",
        #         "Latvian",
        #     },
        #     "name": "East_Baltic",
        #     "d": {"tag": "Uniform", "name": "distr", "lower": "1300", "upper": "20000"},
        # },
        {
            "languages": {
                "Welsh_N",
                "Breton_ST",
                "Cornish",
            },
            "name": "British_Celtic",
            "d": {"tag": "Uniform", "name": "distr", "lower": "1250", "upper": "20000"},
        },
        {
            "languages": {
                "Irish_B",
                "Scots_Gaelic",
            },
            "name": "Modern_Irish-Scots_Gaelic",
            "d": {"tag": "Uniform", "name": "distr", "lower": "1050", "upper": "20000"},
        },
        {
            "languages": {
                "Welsh_N",
                "Breton_ST",
                "Cornish",
                # "Old_Irish",
                "Irish_B",
                "Scots_Gaelic",
            },
            "name": "Celtic",
            "monophyletic": True,
            "d": {"tag": "Uniform", "name": "distr", "lower": "1050", "upper": "20000"},
        },
        # {
        #     "languages": {"Classical_Armenian", "Armenian_Mod", "Armenian_List"},
        #     "name": "Armenian_Clade",
        #     "monophyletic": True,
        #     "d": {"tag": "Uniform", "name": "distr", "lower": "0", "upper": "20000"},
        # },
        # {
        #     "languages": {
        #         "Tadzik",
        #         "Persian",
        #     },
        #     "name": "Persian-Tajik",
        #     "d": {"tag": "Uniform", "name": "distr", "lower": "750", "upper": "20000"},
        # },
    ]
)
