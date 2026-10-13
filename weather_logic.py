"""Pure weather recommendation logic for RunWeather Bot."""


def make_recommendation(weather):
    """Return an approximate running verdict and clothing recommendation."""
    temp = weather["temperature"]
    wind = weather["wind"]
    gusts = weather["gusts"]
    precipitation = weather["precipitation"]
    code = weather["code"]

    if (
        precipitation >= 2
        or weather["snowfall"] > 0
        or wind >= 40
        or gusts >= 60
        or code in {95, 96, 99}
    ):
        verdict = "Краще перенести пробіжку або обрати тренування в приміщенні."
    elif wind >= 25 or gusts >= 40 or precipitation > 0 or temp <= -10 or temp >= 30:
        verdict = "Бігати можна з обережністю; за можливості скоротіть дистанцію."
    elif -5 <= temp <= 20 and wind < 20 and precipitation == 0:
        verdict = "Умови загалом комфортні для пробіжки на вулиці."
    else:
        verdict = "Оцініть власне самопочуття та підберіть одяг за відчутною температурою."

    if temp <= -5:
        clothing = "Термобілизна, утеплений верхній шар, рукавички та шапка або баф."
    elif temp < 5:
        clothing = "Лонгслів або базовий шар, легка вітрозахисна куртка та рукавички."
    elif temp < 15:
        clothing = "Лонгслів або футболка з легким верхнім шаром; за вітру — вітровка."
    elif temp < 23:
        clothing = "Футболка та шорти або легінси; за потреби візьміть тонкий верхній шар."
    else:
        clothing = "Легка дихаюча футболка та шорти, кепка; не забувайте про воду."

    if precipitation > 0 or weather["rain"] > 0 or weather["showers"] > 0:
        clothing += " Додайте легку водонепроникну куртку та взуття з добрим зчепленням."
    if wind >= 20 or gusts >= 30:
        clothing += " Бажаний вітрозахисний верхній шар."
    return verdict, clothing
