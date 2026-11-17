import json
from dataclasses import fields
from datetime import date
from pathlib import Path
from unittest.mock import patch

import pytest

from SurveyLogic.PromptBuilders.Profiles.ProfileData import ProfileData
from SurveyLogic.PromptBuilders.Profiles.ProfileDataLoader import ProfileDataLoader
from SurveyLogic.PromptBuilders.Profiles.StandardProfilesProvider import StandardProfilesProvider


@pytest.mark.parametrize('reverseOrder', [False, True])
@pytest.mark.parametrize(
    'surveyDate,expectedYear',
    [
        (date.min, 2012),
        (date(2011, 12, 31), 2012),
        (date(2012, 1, 1), 2012),
        (date(2017, 12, 31), 2012),
        (date(2018, 6, 15), 2018),
        (date(2019, 1, 1), 2018),
        (date(2023, 12, 31), 2018),
        (date(2024, 12, 31), 2024),
        (date(2025, 1, 1), 2024),
        (date(2026, 7, 9), 2024),
        (date.max, 2024),
    ],
)
def test_getProfilesSelectsWaveRegardlessOfDirectoryOrder(
    tmp_path: Path, surveyDate: date, expectedYear: int, reverseOrder: bool
) -> None:
    folders = []
    for year in (2012, 2018, 2024):
        folder = tmp_path / str(year)
        folder.mkdir()
        profile = {field.name: field.type() for field in fields(ProfileData)}
        profile['respondentId'] = str(year)
        (folder / 'profile.json').write_text(json.dumps(profile), encoding='utf-8')
        folders.append(folder)
    if reverseOrder:
        folders.reverse()
    provider = StandardProfilesProvider(tmp_path, ProfileDataLoader())

    with patch.object(Path, 'iterdir', return_value=iter(folders)):
        profiles = provider.getProfiles(surveyDate)

    assert [profile.respondentId for profile in profiles] == [str(expectedYear)]
