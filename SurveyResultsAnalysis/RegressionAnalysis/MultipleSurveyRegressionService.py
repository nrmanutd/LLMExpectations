import numpy as np
import pandas as pd

from SurveyResultsAnalysis.RegressionAnalysis.BaseSurveyRegressionService import BaseSurveyRegressionService


class MultipleSurveyRegressionService(BaseSurveyRegressionService):
    def __init__(self, service: BaseSurveyRegressionService):
        self.service = service

    def fitBaseVariablesWithConfig(self, survey, v, isOOS: bool, isExpandingOOS: bool, nMonth: int = 1,
                                   cutoff_date: np.datetime64 | None = None, train_share: float = 0.8):
        return self.service.fitBaseVariablesWithConfig(survey[0], v, isOOS, isExpandingOOS, cutoff_date=cutoff_date, nMonth=nMonth, train_share=train_share)

    def fitWithConfig(
            self, survey, v, isOOS, isExpandingOOS,
            nMonth=1, cutoff_date=None, train_share=0.8
    ):
        print(len(survey))
        assert len(survey) == 3

        predictions = []
        resultY = None
        resultTM = None

        for i, curSurvey in enumerate(survey):

            ty, tr, tm, tdates = self.service.fitWithConfig(
                curSurvey, v, isOOS, isExpandingOOS,
                cutoff_date=cutoff_date,
                nMonth=nMonth,
                train_share=train_share
            )

            assert ty.index.equals(tr.index), (
                f"Survey {i}: actual/prediction dates differ"
            )

            assert ty.index.is_unique, (
                f"Survey {i}: duplicate dates"
            )

            assert not ty.isna().any()
            assert not tr.isna().any()

            if i == 0:
                resultY = ty.copy()
                resultTM = tm
            else:
                assert resultY.index.equals(ty.index), (
                    f"Survey {i}: OOS dates differ"
                )

                np.testing.assert_allclose(
                    resultY.to_numpy(),
                    ty.to_numpy(),
                    rtol=0,
                    atol=1e-12,
                    err_msg=f"Survey {i}: actual targets differ"
                )

            predictions.append(tr.copy())

        matrix = np.column_stack([
            p.to_numpy() for p in predictions
        ])

        ensemble = pd.Series(
            matrix.mean(axis=1),
            index=resultY.index,
            name="prediction"
        )

        # RMSE отдельных моделей на точно тех же датах
        errors = resultY.to_numpy()[:, None] - matrix

        individual_rmse = np.sqrt(
            np.mean(errors ** 2, axis=0)
        )

        ensemble_rmse = np.sqrt(
            np.mean((resultY.to_numpy() -
                     ensemble.to_numpy()) ** 2)
        )

        upper_bound = np.sqrt(
            np.mean(individual_rmse ** 2)
        )

        assert ensemble_rmse <= upper_bound + 1e-12, (
            f"Ensemble inequality violated: "
            f"{ensemble_rmse} > {upper_bound}"
        )

        print("Individual RMSE:", individual_rmse)
        print("Ensemble RMSE:", ensemble_rmse)

        return resultY, ensemble, resultTM, list(resultY.index)