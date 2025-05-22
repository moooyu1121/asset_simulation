import numpy as np

# 基本設定
monthly_investment = 150000  # 毎月の積立額（円）
initial_asset = 10000000  # 初期資産（円）
mean_return_annual = 0.0678
volatility_annual = 0.2081
simulations = 10000

initial_age = 25
end_age = 90
monthly_withdrawal = 200000
monthly_pension_from_70 = 200000
target_final_asset = 20000000
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
                    withdrawal -= monthly_pension_from_70
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
        prob = simulate_retirement_with_pension(mid, simulations)
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
    cash_switch_ages = []  # ← 追加：現金モードに切り替えた年齢

    for i in range(simulations):
        value = initial_asset
        cash_mode = False
        path = []
        switch_age = None

        for m in range(total_months):
            monthly_return = np.random.normal(mean_return_monthly, volatility_monthly)
            value *= (1 + monthly_return)

            if m < work_months:
                value += monthly_investment
            else:
                withdrawal = monthly_withdrawal
                if m >= pension_start_month:
                    withdrawal -= monthly_pension_from_70
                withdrawal = max(withdrawal, 0)

                if not cash_mode and value >= (withdrawal * (total_months - m)):
                    cash_mode = True
                    switch_age = initial_age + m // 12  # ← 年齢として記録

                value -= withdrawal if value > 0 else 0
                value = max(value, 0)

            path.append(value)

        results[i] = path
        cash_switch_ages.append(switch_age if switch_age is not None else np.nan)

    return results, cash_switch_ages

# 実行
path_results, cash_switch_ages = simulate_retirement_path_with_pension(min_work_years_with_pension, simulations=simulations)

# パーセンタイル計算と年齢軸
median = np.percentile(path_results, 50, axis=0)
p_low_num = int((1-confidence_level)*100)
p_low = np.percentile(path_results, p_low_num, axis=0)
p95 = np.percentile(path_results, 95, axis=0)

months = np.arange(path_results.shape[1])
ages = initial_age + months // 12
xticks_idx = np.arange(0, len(ages), 12 * 5)

# グラフ描画
plt.figure(figsize=(12, 6))
plt.plot(median, label='Median', color='black')
plt.plot(p_low, label=str(p_low_num)+'th Percentile', linestyle='--', color='red')
plt.plot(p95, label='95th Percentile', linestyle='--', color='green')
plt.yscale('log')
plt.xticks(ticks=xticks_idx, labels=ages[xticks_idx])
plt.title(f'Retirement Portfolio Projection (Retire at Age {retirement_age_with_pension})')
plt.xlabel('Age')
plt.ylabel('Portfolio Value (JPY, log scale)')
plt.legend()
plt.grid(True, which='both', linestyle='--', linewidth=0.5)
plt.tight_layout()
plt.savefig('retirement_projection_logscale_age.png')
print("📊 グラフ 'retirement_projection_logscale_age.png' を保存しました。")

# 現金モードへの切替年齢の統計情報
cash_switch_ages = np.array(cash_switch_ages)
valid_switch_ages = cash_switch_ages[~np.isnan(cash_switch_ages)]

print("\n💬 現金モードに切り替えた年齢の統計:")
print(f"  平均年齢: {np.mean(valid_switch_ages):.2f} 歳")
print(f"  中央年齢: {np.median(valid_switch_ages):.2f} 歳")
print(f"  最小年齢: {np.min(valid_switch_ages):.0f} 歳")
print(f"  最大年齢: {np.max(valid_switch_ages):.0f} 歳")
