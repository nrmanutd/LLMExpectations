from dataclasses import dataclass

@dataclass
class ExperimentsConfiguration:
    useEconomy: bool = False
    usePolitics: bool = False
    useStateInflation: bool = False
    useRegionalInflation: bool = False
    useFamilyInformation: bool = False
    useFamilyExpenses: bool = False
    useStateExpenses: bool = False

    def get_active_features(self) -> list:
        """Возвращает список активных фич"""
        features = []
        if self.useEconomy:
            features.append('economy')
        if self.usePolitics:
            features.append('politics')
        if self.useStateInflation:
            features.append('state_inf')
        if self.useRegionalInflation:
            features.append('regional_inf')
        if self.useFamilyInformation:
            features.append('family_info')
        if self.useFamilyExpenses:
            features.append('family_exp')
        if self.useStateExpenses:
            features.append('state_exp')
        return features

    def get_feature_names_en(self) -> list[str]:
        """Возвращает английские названия активных фич"""
        names_map = {
            'economy': 'Economy',
            'politics': 'Politics',
            'state_inf': 'State Inflation',
            'regional_inf': 'Regional Inflation',
            'family_info': 'Family Information',
            'family_exp': 'Family Expenses',
            'state_exp': 'State Expenses'
        }
        active = self.get_active_features()
        return [names_map[f] for f in active]

    def get_feature_abbr(self) -> str:
        """Возвращает краткое сокращение для активных фич"""
        abbr_map = {
            'economy': 'Econ',
            'politics': 'Pol',
            'state_inf': 'StInf',
            'regional_inf': 'RegInf',
            'family_info': 'FamInf',
            'family_exp': 'FamExp',
            'state_exp': 'StExp'
        }
        active = self.get_active_features()
        if not active:
            return 'Base'
        return '_'.join(abbr_map[f] for f in active)
