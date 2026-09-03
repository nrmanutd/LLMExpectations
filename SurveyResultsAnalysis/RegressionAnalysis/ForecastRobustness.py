import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm


class ForecastRobustness:
    """
    Robustness-анализ OOS forecast errors двух вложенных моделей.

    Parameters
    ----------
    e_llm : pd.Series
        OOS ошибки модели с LLM:
        actual - predicted_llm

    e_base : pd.Series
        OOS ошибки baseline:
        actual - predicted_base
    """

    def __init__(self, e_llm: pd.Series, e_base: pd.Series):

        errors = pd.concat(
            [
                e_llm.rename("llm"),
                e_base.rename("base")
            ],
            axis=1
        ).dropna()

        if len(errors) < 10:
            raise ValueError(
                "Слишком мало совместных наблюдений."
            )

        self.errors = errors
        self.e_llm = errors["llm"]
        self.e_base = errors["base"]

    def print_robustness_report(
            self,
            block_size=4,
            n_boot=10_000,
            confidence_level=0.95,
            hac_lags=3
    ):
        """
        Запускает все три robustness-теста
        и выводит компактный отчет.
        """

        loo_results, loo = self.leave_one_out_gain()

        _, boot = self.block_bootstrap_gain(
            block_size=block_size,
            n_boot=n_boot,
            confidence_level=confidence_level
        )

        cw = self.clark_west_test(
            hac_lags=hac_lags
        )

        # Наиболее влиятельное наблюдение:
        # после его исключения gain минимален
        influential_date = loo_results["gain"].idxmin()
        influential_gain = loo_results.loc[
            influential_date, "gain_percent"
        ]

        # Насколько полный gain уменьшается
        # после исключения наиболее влиятельной точки
        impact_share = (
                               loo["full_gain"] - loo["loo_min"]
                       ) / loo["full_gain"]

        print("=" * 65)
        print("OOS FORECAST ROBUSTNESS REPORT")
        print("=" * 65)

        print("\n1. FULL-SAMPLE FORECAST GAIN")
        print("-" * 65)
        print(
            f"LLM reduction in SSE: "
            f"{loo['full_gain_percent']:.2f}%"
        )

        print("\n2. LEAVE-ONE-OUT SENSITIVITY")
        print("-" * 65)
        print(
            f"Mean LOO gain:          "
            f"{loo['loo_mean'] * 100:.2f}%"
        )
        print(
            f"Median LOO gain:        "
            f"{loo['loo_median'] * 100:.2f}%"
        )
        print(
            f"Minimum LOO gain:       "
            f"{loo['loo_min_percent']:.2f}%"
        )
        print(
            f"Maximum LOO gain:       "
            f"{loo['loo_max_percent']:.2f}%"
        )
        print(
            f"Positive in all LOO:    "
            f"{loo['share_positive']:.2%}"
        )

        print(
            f"\nMost influential date:  "
            f"{influential_date}"
        )
        print(
            f"Gain without this date: "
            f"{influential_gain:.2f}%"
        )
        print(
            f"Share of full gain associated "
            f"with this observation: "
            f"{impact_share:.2%}"
        )

        print("\n3. MOVING-BLOCK BOOTSTRAP")
        print("-" * 65)
        print(
            f"Block size:             "
            f"{boot['block_size']}"
        )
        print(
            f"Bootstrap replications: "
            f"{boot['n_boot']:,}"
        )
        print(
            f"Bootstrap mean gain:    "
            f"{boot['bootstrap_mean'] * 100:.2f}%"
        )
        print(
            f"Bootstrap median gain:  "
            f"{boot['bootstrap_median'] * 100:.2f}%"
        )
        print(
            f"95% CI:                 "
            f"[{boot['ci_lower_percent']:.2f}%, "
            f"{boot['ci_upper_percent']:.2f}%]"
        )
        print(
            f"P(gain <= 0):           "
            f"{boot['prob_gain_le_zero']:.3f}"
        )

        print("\n4. CLARK-WEST TEST")
        print("-" * 65)
        print(
            f"CW statistic:           "
            f"{cw['cw_statistic']:.3f}"
        )
        print(
            f"One-sided p-value:      "
            f"{cw['p_value_one_sided']:.4f}"
        )

        if cw["p_value_one_sided"] < 0.01:
            significance = "significant at 1%"
        elif cw["p_value_one_sided"] < 0.05:
            significance = "significant at 5%"
        elif cw["p_value_one_sided"] < 0.10:
            significance = "significant at 10%"
        else:
            significance = "not statistically significant"

        print(
            f"Result:                 "
            f"{significance}"
        )

        print("\n" + "=" * 65)

        return {
            "loo_results": loo_results,
            "loo_summary": loo,
            "bootstrap_summary": boot,
            "clark_west": cw
        }

    # ---------------------------------------------------------
    # 1. Leave-one-out sensitivity
    # ---------------------------------------------------------

    def leave_one_out_gain(self):
        """
        По очереди исключает каждое наблюдение и пересчитывает:

            gain = 1 - SSE_LLM / SSE_base

        gain > 0:
            LLM лучше baseline.

        Returns
        -------
        results : pd.DataFrame
            gain при исключении каждого наблюдения.

        summary : dict
            Основные статистики устойчивости.
        """

        full_gain = (
            1
            - np.sum(self.e_llm ** 2)
            / np.sum(self.e_base ** 2)
        )

        results = []

        for idx in self.errors.index:

            reduced = self.errors.drop(index=idx)

            sse_llm = np.sum(reduced["llm"] ** 2)
            sse_base = np.sum(reduced["base"] ** 2)

            gain = 1 - sse_llm / sse_base

            results.append({
                "excluded": idx,
                "gain": gain,
                "gain_percent": gain * 100
            })

        results = pd.DataFrame(results).set_index("excluded")

        summary = {
            "full_gain": full_gain,
            "full_gain_percent": full_gain * 100,

            "loo_mean": results["gain"].mean(),
            "loo_median": results["gain"].median(),

            "loo_min": results["gain"].min(),
            "loo_max": results["gain"].max(),

            "loo_min_percent":
                results["gain_percent"].min(),

            "loo_max_percent":
                results["gain_percent"].max(),

            "share_positive":
                (results["gain"] > 0).mean()
        }

        print(summary)

        # Какие наблюдения сильнее всего влияют
        print(results.sort_values("gain").head(10))

        return results, summary

    # ---------------------------------------------------------
    # 2. Moving-block bootstrap
    # ---------------------------------------------------------

    def block_bootstrap_gain(
        self,
        block_size=4,
        n_boot=10_000,
        confidence_level=0.95,
        random_state=42
    ):
        """
        Moving-block bootstrap для:

            gain = 1 - SSE_LLM / SSE_base

        Ошибки LLM и baseline бутстрэпятся ПАРНО,
        сохраняя временную структуру внутри блоков.

        Parameters
        ----------
        block_size : int
            Длина временного блока.
            Для месячных данных разумно попробовать 3-6.

        n_boot : int
            Количество bootstrap-итераций.

        confidence_level : float
            Например 0.95.

        random_state : int

        Returns
        -------
        bootstrap_gains : np.ndarray

        summary : dict
        """

        rng = np.random.default_rng(random_state)

        data = self.errors[["llm", "base"]].to_numpy()

        n = len(data)

        if block_size >= n:
            raise ValueError(
                "block_size должен быть меньше длины ряда."
            )

        # исходный эффект
        original_gain = (
            1
            - np.sum(data[:, 0] ** 2)
            / np.sum(data[:, 1] ** 2)
        )

        # все возможные overlapping blocks
        blocks = [
            data[i:i + block_size]
            for i in range(n - block_size + 1)
        ]

        n_blocks_needed = int(
            np.ceil(n / block_size)
        )

        bootstrap_gains = np.empty(n_boot)

        for b in range(n_boot):

            selected = rng.integers(
                0,
                len(blocks),
                size=n_blocks_needed
            )

            sample = np.vstack(
                [blocks[i] for i in selected]
            )

            # обрезаем до исходной длины
            sample = sample[:n]

            e_llm_boot = sample[:, 0]
            e_base_boot = sample[:, 1]

            sse_llm = np.sum(e_llm_boot ** 2)
            sse_base = np.sum(e_base_boot ** 2)

            bootstrap_gains[b] = (
                1 - sse_llm / sse_base
            )

        alpha = 1 - confidence_level

        lower = np.quantile(
            bootstrap_gains,
            alpha / 2
        )

        upper = np.quantile(
            bootstrap_gains,
            1 - alpha / 2
        )

        # bootstrap probability того,
        # что LLM не лучше baseline
        prob_nonpositive = np.mean(
            bootstrap_gains <= 0
        )

        summary = {
            "original_gain": original_gain,
            "original_gain_percent":
                original_gain * 100,

            "bootstrap_mean":
                bootstrap_gains.mean(),

            "bootstrap_median":
                np.median(bootstrap_gains),

            "ci_lower": lower,
            "ci_upper": upper,

            "ci_lower_percent": lower * 100,
            "ci_upper_percent": upper * 100,

            "prob_gain_le_zero":
                prob_nonpositive,

            "block_size": block_size,
            "n_boot": n_boot
        }

        print(summary)

        return bootstrap_gains, summary

    # ---------------------------------------------------------
    # 3. Clark-West test
    # ---------------------------------------------------------

    def clark_west_test(
        self,
        hac_lags=3
    ):
        """
        Clark-West test для сравнения nested OOS forecasts.

        H0:
            модель с LLM не улучшает прогноз.

        H1:
            модель с LLM улучшает прогноз.

        Тест ОДНОСТОРОННИЙ.

        Используется HAC / Newey-West standard error.

        Важно:
        forecast difference можно восстановить только из ошибок:

            yhat_base - yhat_llm
                = e_llm - e_base

        Clark-West adjusted differential:

            f_t =
                e_base^2
                - e_llm^2
                + (yhat_base - yhat_llm)^2

        Returns
        -------
        dict
        """

        e_base = self.e_base.to_numpy()
        e_llm = self.e_llm.to_numpy()

        # yhat_base - yhat_llm
        forecast_diff = e_llm - e_base

        # Clark-West adjusted loss differential
        cw_diff = (
            e_base ** 2
            - e_llm ** 2
            + forecast_diff ** 2
        )

        # regression cw_diff on constant
        X = np.ones((len(cw_diff), 1))

        model = sm.OLS(
            cw_diff,
            X
        ).fit(
            cov_type="HAC",
            cov_kwds={
                "maxlags": hac_lags
            }
        )

        mean_diff = model.params[0]
        se = model.bse[0]

        statistic = mean_diff / se

        # Clark-West — one-sided test:
        # H1: mean adjusted differential > 0
        p_value = 1 - stats.norm.cdf(
            statistic
        )

        result = {
            "cw_mean_adjusted_gain":
                mean_diff,

            "cw_statistic":
                statistic,

            "p_value_one_sided":
                p_value,

            "hac_lags":
                hac_lags,

            "n_obs":
                len(cw_diff),

            "significant_10pct":
                p_value < 0.10,

            "significant_5pct":
                p_value < 0.05,

            "significant_1pct":
                p_value < 0.01
        }

        print(result)

        return result