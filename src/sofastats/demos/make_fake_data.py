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
    change_usually_up = partial(change_float_usually_up, min_val=40, max_val=100)
    df['reading_score_after_help'] = df['reading_score_before_help'].apply(change_usually_up)
    df['reading_score_after_help'] = df['reading_score_after_help'].apply(round2)
    df['school_satisfaction_before_help'] = pd.Series([sample([1, 2, 3, 4, 5], counts=[1, 2, 4, 3, 1], k=1)[0] for _x in range(n_records)])
    df['school_satisfaction_after_help'] = df['school_satisfaction_before_help'].apply(change_usually_up)
    if debug: print(df)
    df.to_csv('education.csv', index=False)

def make_independent_difference(*, debug=False):
    n_records = 2_000
    data = [(fake.name(), ) for _i in range(n_records)]
    df = pd.DataFrame(data, columns = ['name'])
    df['sport'] = pd.Series([choice(['Archery', 'Badminton', 'Basketball']) for _i in range(n_records)])
    df['height'] = pd.Series([round(constrain(gauss(mu=1.75, sigma=0.2), min_val=1.5, max_val=2.3), 2) for _i in range(n_records)])
    df.loc[df['sport'] == 'Badminton', ['height']] = df.loc[df['sport'] == 'Badminton', ['height']] * 1.1
    df.loc[df['sport'] == 'Basketball', ['height']] = df.loc[df['sport'] == 'Basketball', ['height']] * 1.25
    constrain_height = partial(constrain, min_val=1.5, max_val=2.3)
    df['height'] = df['height'].apply(constrain_height)
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

def make_correlation(*, debug=False):
    n_records = 100_000
    data = [fake.address() for _i in range(n_records)]
    df = pd.DataFrame(data, columns = ['address'])
    df['address'] = df['address'].apply(lambda s: s.replace('\n', ', '))
    df['floor_space_square_metres'] = pd.Series([constrain(gauss(mu=100, sigma=50), min_val=10, max_val=1_500) for _i in range(n_records)])
    df['floor_space_square_metres'] = df['floor_space_square_metres'].apply(round2)
    df['price'] = df['floor_space_square_metres'].apply(area2price)
    df['area_group'] = df['floor_space_square_metres'].apply(area2area_group)
    df['price_group'] = df['price'].apply(price2price_group)
    if debug: print(df)
    df.to_csv('properties.csv', index=False)

def run(*, debug=False):
    pass
    # make_paired_difference(debug=debug)
    # make_independent_difference(debug=debug)
    # make_group_pattern(debug=debug)
    # make_correlation(debug=debug)

if __name__ == '__main__':
    run(debug=True)
