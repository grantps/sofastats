from enum import StrEnum
from functools import partial
from random import choice, gauss, lognormvariate, randint, sample

from faker import Faker
import pandas as pd

fake = Faker()

pd.set_option('display.max_rows', 200)
pd.set_option('display.min_rows', 30)
pd.set_option('display.max_columns', 50)
pd.set_option('display.width', 1_000)

class BookType(StrEnum):
    ADULT = 'Adult'
    LARGE_PRINT = 'Large Print'
    YOUTH = 'Youth'

class Genre(StrEnum):
    HISTORY = 'History'
    ROMANCE = 'Romance'
    SCI_FI = 'Science Fiction'

round2 = partial(round, ndigits=2)

def constrain(orig: float, *, max_val, min_val) -> float | int:
    return max(min(orig, max_val), min_val)

def change_float_usually_up(orig: float, *, min_val: float, max_val: float) -> float:
    """
    Between 0.8x to 1.5x
    mu = 1.35
    sigma = 0.2
    """
    scalar = gauss(mu=1.2, sigma=0.12)
    return constrain(orig * scalar, min_val=min_val, max_val=max_val)

def change_int_usually_up(orig: int) -> int:
    change = sample([-2, -1, 0, 1, 2], counts=[1, 3, 10, 9, 2], k=1)[0]
    raw_val = orig + change
    val = constrain(raw_val, min_val=1, max_val=5)
    return val

def make_paired_difference(*, debug=False):
    """
    Reading scores and educational_satisfaction before and after intervention
    """
    n_records = 5_000
    data = [(fake.name(), ) for _i in range(n_records)]
    df = pd.DataFrame(data, columns = ['name'])
    df['reading_score_before_help'] = pd.Series([
        round(constrain(gauss(mu=60, sigma=20), max_val=100, min_val=40), 2)
        for _i in range(n_records)])
    change_usually_up = partial(change_float_usually_up, min_val=1, max_val=5)
    df['reading_score_after_help'] = df['reading_score_before_help'].apply(change_usually_up)
    df['reading_score_after_help'] = df['reading_score_after_help'].apply(round2)
    df['school_satisfaction_before_help'] = pd.Series([sample([1, 2, 3, 4, 5], counts=[1, 2, 4, 3, 1], k=1)[0] for _x in range(n_records)])
    df['school_satisfaction_after_help'] = df['school_satisfaction_before_help'].apply(change_usually_up)
    if debug: print(df)
    df.to_csv('education.csv', index=False)

def make_sport_independent_difference(*, debug=False):
    n_records = 2_000
    data = [(fake.name(), ) for _i in range(n_records)]
    df = pd.DataFrame(data, columns = ['name'])
    df['country'] = df.apply(get_country, axis=1)
    df['sport'] = pd.Series([choice([
        1,  ## Archery
        2,  ## Badminton
        3,  ## Basketball,
    ]) for _i in range(n_records)])
    df['height'] = pd.Series([round(constrain(gauss(mu=1.8, sigma=0.115), min_val=1.5, max_val=2.3), 2) for _i in range(n_records)])
    df.loc[df['sport'] == 1, ['height']] = df.loc[df['sport'] == 1, ['height']] * 0.95
    df.loc[df['sport'] == 2, ['height']] = df.loc[df['sport'] == 2, ['height']] * 1.05
    df.loc[df['sport'] == 3, ['height']] = df.loc[df['sport'] == 3, ['height']] * 1.125
    df['height'] = df['height'].apply(constrain, min_val=1.5, max_val=2.3)
    df['height'] = df['height'].apply(round2)
    if debug: print(df)
    df.to_csv('sports.csv', index=False)

def get_book_type(age: int) -> str:
    if age < 20:
        book_type = BookType.YOUTH
    elif age < 75:
        book_type = BookType.ADULT
    else:
        book_type = BookType.LARGE_PRINT
    return book_type

def get_genre(*, history_rate: int = 100, romance_weight: int = 100, sci_fi_weight: int=100) -> Genre:
    genre = sample([Genre.HISTORY, Genre.ROMANCE, Genre.SCI_FI],
        counts=[history_rate, romance_weight, sci_fi_weight], k=1)[0]
    return genre

def book_type_to_genre(book_type: BookType) -> Genre:
    if book_type == BookType.YOUTH:
        genre = get_genre(history_rate=100, romance_weight=100, sci_fi_weight=300)
    elif book_type == BookType.ADULT:
        genre = get_genre(history_rate=80, romance_weight=100, sci_fi_weight=100)
    elif book_type == BookType.LARGE_PRINT:
        genre = get_genre(history_rate=300, romance_weight=100, sci_fi_weight=50)
    else:
        raise ValueError(f"Unexpected book_type '{book_type}'")
    return genre

def make_group_pattern(*, debug=False):
    n_records = 2_000
    data = [(fake.name(), ) for _i in range(n_records)]
    df = pd.DataFrame(data, columns = ['name'])
    df['age'] = pd.Series([randint(8, 100) for _i in range(n_records)])
    df['book_type'] = df['age'].apply(get_book_type)
    df['genre'] = df['book_type'].apply(book_type_to_genre)
    if debug: print(df)
    df.to_csv('books.csv', index=False)

def area2price(area: float) -> int:
    raw_price = 10_000 * area
    scalar = lognormvariate(mu=1, sigma=0.5)
    price = int(round(raw_price * scalar, -3))
    return price

def area2area_group(area: float) -> int:
    if area < 40:
        area_group = 1
    elif area < 50:
        area_group = 2
    elif area < 75:
        area_group = 3
    elif area < 100:
        area_group = 4
    elif area < 120:
        area_group = 5
    elif area < 150:
        area_group = 6
    elif area < 175:
        area_group = 7
    elif area < 200:
        area_group = 8
    elif area < 250:
        area_group = 9
    elif area < 300:
        area_group = 10
    else:
        area_group = 11
    return area_group

def price2price_group(price: int) -> int:
    if price < 200_000:
        price_group = 1
    elif price < 350_000:
        price_group = 2
    elif price < 500_000:
        price_group = 3
    elif price < 750_000:
        price_group = 4
    elif price < 1_000_000:
        price_group = 5
    elif price < 1_500_000:
        price_group = 6
    elif price < 2_000_000:
        price_group = 7
    elif price < 5_000_000:
        price_group = 8
    elif price < 10_000_000:
        price_group = 9
    else:
        price_group = 10
    return price_group

def get_agency(column: pd.Series) -> str:
    agency = sample(['Edge Real Estate', 'Supreme Investments', 'Castle Ridge Equity'],
        counts=[3, 2, 5], k=1)[0]
    return agency

def get_valuer(column: pd.Series) -> str:
    valuer = sample(['TopValue', 'Price It Right Inc', ],
        counts=[3, 25], k=1)[0]
    return valuer

def make_correlation(*, debug=False):
    n_records = 20_000
    data = [fake.address() for _i in range(n_records)]
    df = pd.DataFrame(data, columns = ['address'])
    df['address'] = df['address'].apply(lambda s: s.replace('\n', ', '))
    df['floor_area'] = pd.Series([constrain(gauss(mu=100, sigma=50), min_val=10, max_val=1_500) for _i in range(n_records)])
    df['floor_area'] = df['floor_area'].apply(round2)
    df['price'] = df['floor_area'].apply(area2price)
    df['floor_area_group'] = df['floor_area'].apply(area2area_group)
    df['price_group'] = df['price'].apply(price2price_group)
    df['agency'] = df['address'].apply(get_agency)
    df['valuer'] = df['address'].apply(get_valuer)
    if debug: print(df)
    df.to_csv('properties.csv', index=False)

def age2group(age: int) -> int:
    if age < 20:
        age_group = 1
    elif age < 30:
        age_group = 2
    elif age < 40:
        age_group = 3
    elif age < 50:
        age_group = 4
    elif age < 60:
        age_group = 5
    elif age < 70:
        age_group = 6
    elif age < 80:
        age_group = 7
    else:
        age_group = 8
    return age_group

def age2qual(age: int) -> int:
    if age < 20:
        qual = 1
    elif age < 22:
        qual = sample([1, 2], counts=[3, 1], k=1)[0]
    else:
        qual = sample([1, 2, 3], counts=[12, 3, 1], k=1)[0]
    return qual

def country2location(country: int) -> int:
    if country == 1:
        location = sample([1, 2, 3], counts=[5, 3, 2], k=1)[0]
    elif country == 2:
        location = sample([1, 2, 3], counts=[8, 3, 2], k=1)[0]
    elif country == 3:
        location = sample([1, 2, 3], counts=[4, 3, 4], k=1)[0]
    elif country == 4:
        location = sample([1, 2, 3], counts=[4, 3, 3], k=1)[0]
    else:
        raise ValueError(f"Unexpected country '{country}'")
    return location

population = range(8, 100)
counts = ([3, ] * 50) + ([2, ] * 30) + ([1, ] * 12)

def get_age(_row) -> int:
    return sample(population, counts=counts, k=1)[0]

def get_country(_row) -> int:
    country = sample([1, 2, 3, 4], counts=[5, 2, 1, 1], k=1)[0]
    return country

def age2sleep(age: int) -> float:
    if age < 20:
        mu = 8
    elif age < 55:
        mu = 7.5
    else:
        mu = 7
    raw_hours = gauss(mu=mu, sigma=1.5)
    return round(2 * raw_hours) / 2

def sleep2group(sleep: float) -> int:
    if sleep < 7:
        sleep_group = 1
    elif sleep < 9:
        sleep_group = 2
    else:
        sleep_group = 3
    return sleep_group

def make_varied_nestable_data(*, debug=False):
    n_records = 5_000
    data = [(fake.name(), ) for _i in range(n_records)]
    df = pd.DataFrame(data, columns = ['name', ])
    df['age'] = df.apply(get_age, axis=1)
    df['age_group'] = df['age'].apply(age2group)
    df['country'] = pd.Series([sample([1, 2, 3, 4], counts=[200, 100, 80, 70], k=1)[0] for _i in range(n_records)])
    df['handedness'] = pd.Series([sample([1, 2, 3], counts=[9, 2, 1], k=1)[0] for _i in range(n_records)])
    df['home_location_type'] = df['country'].apply(country2location)
    df['sleep'] = df['age'].apply(age2sleep)
    df['sleep_group'] = df['sleep'].apply(sleep2group)
    df['tertiary_qualifications'] = df['age'].apply(age2qual)

    if debug: print(df)
    df.to_csv('people.csv', index=False)

def run(*, debug=False):
    pass
    # make_paired_difference(debug=debug)
    # make_sport_independent_difference(debug=debug)
    # make_group_pattern(debug=debug)
    # make_correlation(debug=debug)
    # make_varied_nestable_data(debug=debug)

if __name__ == '__main__':
    run(debug=True)
