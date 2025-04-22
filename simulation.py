import numpy as np
import matplotlib
matplotlib.use('Agg')  # ← Tk を使わないバックエンド
import matplotlib.pyplot as plt
from tqdm import tqdm

# パラメータ設定
monthly_investment = 150000  # 毎月の積立額（円）
years = 30
months = years * 12
mean_return_annual = 0.0678
volatility_annual = 0.2081
simulations = 1000

initial_age = 25
end_age = 90
monthly_withdrawal = 200000
target_final_asset = 10000000
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
for work_years in tqdm(range(1, max_work_years + 1), desc="Finding Required Work Years"):
    prob = simulate_retirement(work_years, simulations)
    if prob >= confidence_level:
        required_work_years = work_years
        break

# グラフ描画用：全期間の推移を記録
def simulate_retirement_path(work_years, simulations=1000):  # 描画用なので少し減らす
    total_months = (end_age - initial_age) * 12
    work_months = work_years * 12
    withdraw_months = total_months - work_months

    results = np.zeros((simulations, total_months))
    for i in tqdm(range(simulations), desc="Simulating Paths"):
        value = 5_000_000
        path = []
        for m in range(work_months):
            monthly_return = np.random.normal(mean_return_monthly, volatility_monthly)
            value = value * (1 + monthly_return) + monthly_investment
            path.append(value)
        for m in range(withdraw_months):
            monthly_return = np.random.normal(mean_return_monthly, volatility_monthly)
            value = value * (1 + monthly_return) - monthly_withdrawal
            value = max(value, 0)
            path.append(value)
        results[i] = path
    return results

# 推移をシミュレーション
paths = simulate_retirement_path(required_work_years, simulations)

# パーセンタイル計算
median = np.percentile(paths, 50, axis=0)
p_low = np.percentile(paths, (1-confidence_level)*100, axis=0)
p95 = np.percentile(paths, 95, axis=0)

# グラフ描画
plt.figure(figsize=(12, 6))
plt.plot(median, label='Median', color='black')
plt.yscale('log')
plt.plot(p_low, label=str(int((1-confidence_level)*100))+'th Percentile', linestyle='--', color='red')
plt.plot(p95, label='95th Percentile', linestyle='--', color='green')
plt.title('Retirement Portfolio Simulation')
plt.xlabel('Months from Age 25')
plt.ylabel('Portfolio Value (JPY)')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("retirement_simulation.png")
# plt.show()

# 結果出力
print(f"必要な労働年数: {required_work_years} 年")
print(f"退職年齢: {initial_age + required_work_years} 歳")