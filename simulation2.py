import numpy as np

# 基本設定
monthly_investment = 150000  # 毎月の積立額（円）
initial_asset = 5000000  # 初期資産（円）
mean_return_annual = 0.0678
volatility_annual = 0.2081
simulations = 10000

initial_age = 25
end_age = 90
monthly_withdrawal = 300000
target_final_asset = 10000000
confidence_level = 0.95

# 月次リターンに変換
mean_return_monthly = (1 + mean_return_annual) ** (1/12) - 1
volatility_monthly = volatility_annual / np.sqrt(12)

# 最大労働年数
max_work_years = end_age - initial_age

# シナリオ：年金支給と現金モード付き
def simulate_retirement_with_pension(work_years, simulations):
    total_months = (end_age - initial_age) * 12
    work_months = work_years * 12
    pension_start_month = (70 - initial_age) * 12

    results = np.zeros(simulations)
    for i in range(simulations):
        value = initial_asset
        cash_mode = False

        for m in range(total_months):
            monthly_return = np.random.normal(mean_return_monthly, volatility_monthly)
            value = value * (1 + monthly_return)

            if m < work_months:
                value += monthly_investment
            else:
                withdrawal = monthly_withdrawal
                if m >= pension_start_month:
                    withdrawal -= 200000 
                withdrawal = max(withdrawal, 0)

                if not cash_mode and value >= (withdrawal * (total_months - m)):
                    cash_mode = True  # 現金で最後まで持つと判断

                if not cash_mode:
                    value -= withdrawal
                else:
                    value -= withdrawal  # 現金からの単純減少

                if value <= 0:
                    value = 0
                    break

        results[i] = value

    prob_above_target = np.mean(results >= target_final_asset)
    return prob_above_target

# バイナリサーチで必要年数を探索
def find_min_work_years_with_pension(min_years, max_years):
    while min_years < max_years:
        mid = (min_years + max_years) // 2
        prob = simulate_retirement_with_pension(mid)
        if prob >= confidence_level:
            max_years = mid
        else:
            min_years = mid + 1
    return min_years, initial_age + min_years

# 実行
min_work_years_with_pension, retirement_age_with_pension = find_min_work_years_with_pension(1, max_work_years)
print(f"必要な労働年数（年金支給あり）: {min_work_years_with_pension} 年")
print(f"リタイア: {retirement_age_with_pension} 歳")


import matplotlib
matplotlib.use('Agg')  # GUIを使わずファイル保存用
import matplotlib.pyplot as plt

def simulate_retirement_path_with_pension(work_years, simulations=1000):
    total_months = (end_age - initial_age) * 12
    work_months = work_years * 12
    pension_start_month = (70 - initial_age) * 12

    results = np.zeros((simulations, total_months))

    for i in range(simulations):
        value = 5_000_000
        cash_mode = False
        path = []

        for m in range(total_months):
            monthly_return = np.random.normal(mean_return_monthly, volatility_monthly)
            value *= (1 + monthly_return)

            if m < work_months:
                value += monthly_investment
            else:
                withdrawal = monthly_withdrawal
                if m >= pension_start_month:
                    withdrawal -= 200000
                withdrawal = max(withdrawal, 0)

                if not cash_mode and value >= (withdrawal * (total_months - m)):
                    cash_mode = True

                value -= withdrawal if value > 0 else 0
                value = max(value, 0)

            path.append(value)

        results[i] = path

    return results

# グラフ用のシミュレーション（1000回程度）
path_results = simulate_retirement_path_with_pension(min_work_years_with_pension, simulations=1000)

# パーセンタイル計算
median = np.percentile(path_results, 50, axis=0)
p5 = np.percentile(path_results, 5, axis=0)
p95 = np.percentile(path_results, 95, axis=0)

# 年齢ベースのx軸ラベル作成
months = np.arange(path_results.shape[1])
ages = initial_age + months // 12
xticks_idx = np.arange(0, len(ages), 12 * 5)  # 5年ごとに表示

# グラフ描画
plt.figure(figsize=(12, 6))
plt.plot(median, label='Median', color='black')
plt.plot(p5, label='5th Percentile', linestyle='--', color='red')
plt.plot(p95, label='95th Percentile', linestyle='--', color='green')
plt.yscale('log')  # 対数スケールで成長を可視化
plt.xticks(ticks=xticks_idx, labels=ages[xticks_idx])  # 年齢をX軸に
plt.title(f'Retirement Portfolio Projection (Retire at Age {retirement_age_with_pension})')
plt.xlabel('Age')
plt.ylabel('Portfolio Value (JPY, log scale)')
plt.legend()
plt.grid(True, which='both', linestyle='--', linewidth=0.5)
plt.tight_layout()
plt.savefig('retirement_projection_logscale_age.png')
print("📊 グラフ 'retirement_projection_logscale_age.png' を保存しました（対数スケール＆年齢軸）。")