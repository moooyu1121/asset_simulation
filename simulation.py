import numpy as np
import matplotlib.pyplot as plt

# パラメータ設定
monthly_investment = 100000  # 毎月の積立額（円）
years = 30
months = years * 12
mean_return_annual = 0.0678
volatility_annual = 0.2081
simulations = 10000

initial_age = 25
end_age = 90
monthly_withdrawal = 200000
target_final_asset = 10_000_000
confidence_level = 0.95


# 月次に変換
mean_return_monthly = (1 + mean_return_annual) ** (1/12) - 1
volatility_monthly = volatility_annual / np.sqrt(12)

# 年数変数
max_work_years = end_age - initial_age

# モンテカルロシミュレーション関数定義
def simulate_retirement(work_years, simulations=10000):
    total_months = (end_age - initial_age) * 12
    work_months = work_years * 12
    withdraw_months = total_months - work_months

    results = np.zeros(simulations)
    for i in range(simulations):
        value = 5_000_000  # initial asset
        for m in range(work_months):
            monthly_return = np.random.normal(mean_return_monthly, volatility_monthly)
            value = value * (1 + monthly_return) + monthly_investment
        for m in range(withdraw_months):
            monthly_return = np.random.normal(mean_return_monthly, volatility_monthly)
            value = value * (1 + monthly_return) - monthly_withdrawal
            if value <= 0:
                value = 0
                break
        results[i] = value
    prob_above_target = np.mean(results >= target_final_asset)
    return prob_above_target

# 最小の労働年数を探す
required_work_years = None
for work_years in range(1, max_work_years + 1):
    print(f"シミュレーション中: {work_years} 年")
    prob = simulate_retirement(work_years, simulations)
    if prob >= confidence_level:
        required_work_years = work_years
        break

required_work_years, initial_age + required_work_years

print(f"必要な労働年数: {required_work_years} 年")
print(f"退職年齢: {initial_age + required_work_years} 歳") 
