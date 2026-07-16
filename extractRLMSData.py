from RLMSLogic.SimpleRLMSProfileConverter import SimpleRLMSProfileConverter
from RLMSLogic.RLMSProfileExtractor import RLMSProfileExtractor

#dta_file = 'data\\r33iall_84_DTA\\r33iall_84.dta'
dta_file = 'data\\r33i_os_84_DTA\\r33i_os_84.dta'
out_folder = 'data\\rlms2024_os_profiles'
profiles_out_folder = 'data\\target_rlms2024_os_based_profiles'

converter = SimpleRLMSProfileConverter()
extractor = RLMSProfileExtractor(converter)

extractor.extractAndSaveRLMSProfiles(dta_file, out_folder)
extractor.generateAndSaveProfilesFromRLMS(out_folder, profiles_out_folder, 0.01 / 12)