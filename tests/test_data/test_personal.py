# -*- coding: utf-8 -*-

import re

import pytest

import mimesis
from mimesis.data import (BLOOD_GROUPS, ENGLISH_LEVEL, GENDER_SYMBOLS,
                          MUSIC_GENRE, SEXUALITY_SYMBOLS)
from mimesis.enums import Gender, SocialNetwork, TitleType
from mimesis.exceptions import NonEnumerableError

from ._patterns import EMAIL_REGEX, STR_REGEX, USERNAME_REGEX


@pytest.fixture
def _personal():
    return mimesis.Personal()


def test_str(personal):
    assert re.match(STR_REGEX, str(personal))


@pytest.mark.parametrize(
    'minimum, maximum', [
        (16, 18),
        (18, 21),
        (22, 28),
    ],
)
def test_age(_personal, minimum, maximum):
    result = _personal.age(minimum, maximum)
    assert (result >= minimum) and (result <= maximum)


def test_age_store(_personal):
    result = _personal._store['age']
    assert result == 0


def test_age_update(_personal):
    result = _personal.age() - _personal._store['age']
    assert result == 0


def test_child_count(_personal):
    result = _personal.child_count(max_childs=10)
    assert result <= 10


def test_work_experience(_personal):
    result = _personal.work_experience(
        working_start_age=0) - _personal._store['age']
    assert result == 0


def test_work_experience_store(_personal):
    result = _personal.work_experience() - _personal.work_experience()
    assert result == 0


def test_work_experience_extreme(_personal):
    result = _personal.work_experience(working_start_age=100000)
    assert result == 0


def test_password(_personal):
    result = _personal.password(length=15)
    assert len(result) == 15

    result = _personal.password(hashed=True)
    assert len(result) == 32


@pytest.mark.parametrize(
    'template', [
        'U-d', 'U.d', 'UU-d',
        'UU.d', 'UU_d', 'U_d',
        'Ud', 'default', 'l-d',
        'l.d', 'l_d', 'ld',
        None,
    ],
)
def test_username(_personal, template):
    result = _personal.username(template=template)
    assert re.match(USERNAME_REGEX, result)


def test_username_unsupported_template(_personal):
    with pytest.raises(KeyError):
        _personal.username(template=':D')


def test_email(_personal):
    result = _personal.email()
    assert re.match(EMAIL_REGEX, result)

    domains = ['@example.com']
    result = _personal.email(domains=domains)
    assert re.match(EMAIL_REGEX, result)
    assert result.split('@')[1] == 'example.com'


def test_height(_personal):
    result = _personal.height(minimum=1.60, maximum=1.90)
    assert result.startswith('1')
    assert isinstance(result, str)


def test_weight(_personal):
    result = _personal.weight(minimum=40, maximum=60)
    assert result >= 40
    assert result <= 60


def test_blood_type(_personal):
    result = _personal.blood_type()
    assert result in BLOOD_GROUPS


def test_favorite_movie(personal):
    result = personal.favorite_movie()
    assert result in personal._data['favorite_movie']


def test_favorite_music_genre(_personal):
    result = _personal.favorite_music_genre()
    assert result in MUSIC_GENRE


@pytest.mark.parametrize(
    'site', [
        SocialNetwork.INSTAGRAM,
        SocialNetwork.FACEBOOK,
        SocialNetwork.TWITTER,
        SocialNetwork.VK,
        None,
    ],
)
def test_social_media_profile(_personal, site):
    result = _personal.social_media_profile(site=site)
    assert result is not None


def test_avatar(_personal):
    result = _personal.avatar(size=512)
    img, size, *__ = result.split('/')[::-1]
    assert int(size) == 512
    assert 32 == len(img.split('.')[0])


def test_identifier(_personal):
    result = _personal.identifier()
    mask = '##-##/##'
    assert len(mask) == len(result)

    result = _personal.identifier(mask='##-##/## @@')
    suffix = result.split(' ')[1]
    assert suffix.isalpha()


def test_level_of_english(_personal):
    result = _personal.level_of_english()
    assert result in ENGLISH_LEVEL


@pytest.mark.parametrize(
    'gender', [
        Gender.FEMALE,
        Gender.MALE,
    ],
)
def test_name(personal, gender):
    result = personal.name(gender=gender)
    assert result in personal._data['names'][gender.value]


def test_name_with_none(_personal):
    result = _personal.name(gender=None)
    names = _personal._data['names']

    females = names['female']
    males = names['male']
    assert result is not None
    assert (result in females) or (result in males)


def test_name_unexpected_gender(personal):
    with pytest.raises(NonEnumerableError):
        personal.name(gender='nil')


def test_telephone(personal):
    result = personal.telephone()
    assert result is not None

    mask = '+5 (###)-###-##-##'
    result = personal.telephone(mask=mask)
    head = result.split(' ')[0]
    assert head == '+5'


@pytest.mark.parametrize(
    'gender', [
        Gender.FEMALE,
        Gender.MALE,
    ],
)
def test_surname(personal, gender):
    surnames = personal._data['surnames']

    # Surnames separated by gender.
    if isinstance(surnames, dict):
        result = personal.surname(gender=gender)
        assert result in surnames[gender.value]
    else:
        result = personal.surname()
        assert result in surnames


@pytest.mark.parametrize(
    'gender', [
        Gender.FEMALE,
        Gender.MALE,
    ],
)
def test_full_name(personal, gender):
    result = personal.full_name(gender=gender)

    result = result.split(' ')
    assert result[0] is not None
    assert result[1] is not None

    result = personal.full_name(reverse=True)
    assert result is not None


def test_gender(personal):
    result = personal.gender()
    assert result in personal._data['gender']

    result = personal.gender(symbol=True)
    assert result in GENDER_SYMBOLS

    # The four codes specified in ISO/IEC 5218 are:
    # 0 = not known, 1 = male, 2 = female, 9 = not applicable.
    codes = [0, 1, 2, 9]
    iso5218 = personal.gender(iso5218=True)
    assert iso5218 in codes


def test_sexual_orientation(personal):
    result = personal.sexual_orientation()
    assert result in personal._data['sexuality']

    symbol = personal.sexual_orientation(symbol=True)
    assert symbol in SEXUALITY_SYMBOLS


def test_profession(personal):
    result = personal.occupation()
    assert result in personal._data['occupation']


def test_university(personal):
    result = personal.university()
    assert result in personal._data['university']


def test_academic_degree(personal):
    result = personal.academic_degree()
    assert result in personal._data['academic_degree']


def test_language(personal):
    result = personal.language()
    assert result in personal._data['language']


def test_worldview(personal):
    result = personal.worldview()
    assert result in personal._data['worldview']


def test_views_on(personal):
    result = personal.views_on()
    assert result in personal._data['views_on']


def test_political_views(personal):
    result = personal.political_views()
    assert result in personal._data['political_views']


@pytest.mark.parametrize(
    'title_type', [
        TitleType.ACADEMIC,
        TitleType.TYPICAL,
        None,
    ],
)
@pytest.mark.parametrize(
    'gender', [
        Gender.FEMALE,
        Gender.MALE,
        None,
    ],
)
def test_title(personal, gender, title_type):
    result = personal.title(gender=gender, title_type=title_type)
    assert result is not None

    with pytest.raises(NonEnumerableError):
        personal.title(title_type='nil')
        personal.title(gender='nil')


@pytest.mark.parametrize(
    'gender', [
        Gender.FEMALE,
        Gender.MALE,
    ],
)
def test_nationality(personal, gender):
    nationality = personal._data['nationality']
    if isinstance(nationality, dict):
        result = personal.nationality(gender=gender)
        assert result in personal._data['nationality'][gender.value]

    result = personal.nationality()
    assert result is not None
