from calibrations import main, normal, until

r = main(
    [
        {"languages": {"Sinitic_Old_Chinese"}, "d": until(2300, 2800)},
        {"languages": {"Burmish_Old_Burmese"}, "d": normal(800, 25)},
        {"languages": {"Tibetan_Old_Tibetan"}, "d": normal(1200, 25)},
        {"languages": {"Tangut"}, "d": normal(900, 25)},
    ]
)
