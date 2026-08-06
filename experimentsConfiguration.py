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
