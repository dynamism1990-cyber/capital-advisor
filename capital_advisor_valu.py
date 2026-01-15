"""
企業資本市場選択肢分析AI - 日本市場版 with シミュレーター
"""

import streamlit as st
import anthropic
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime

# ページ設定
st.set_page_config(
    page_title="企業資本市場選択肢分析 with シミュレーター",
    page_icon="💼",
    layout="wide"
)

# タイトル
st.title("💼 企業資本市場選択肢分析ツール（日本版）")
st.markdown("""
> **新機能追加！** 📈 各選択肢の3年後をシミュレーションできます
""")

# サイドバー：企業情報入力
with st.sidebar:
    st.header("📊 企業基本情報")
    
    st.subheader("財務状況")
    revenue = st.number_input("年間売上高（百万円）", min_value=0, value=500, step=10)
    profit = st.number_input("経常利益（百万円）", min_value=-100, value=50, step=5)
    growth_rate = st.slider("前年比売上成長率（%）", -50, 200, 15)
    
    st.subheader("企業背景")
    years = st.number_input("設立年数", min_value=1, max_value=100, value=8)
    employees = st.number_input("従業員数", min_value=1, value=30, step=5)
    
    industry = st.selectbox(
        "業種",
        ["製造業", "IT・ソフトウェア", "医療・ヘルスケア", "環境・エネルギー", 
         "小売・サービス", "建設・不動産", "その他"]
    )
    
    location = st.selectbox(
        "本社所在地",
        ["東京都", "大阪府", "愛知県", "福岡県", "神奈川県", 
         "その他関東", "その他関西", "その他地方"]
    )
    
    st.subheader("事業特性")
    rd_ratio = st.slider("研究開発費比率（%）", 0, 50, 5)
    has_patent = st.checkbox("特許または独自技術を保有")
    is_hightech = st.checkbox("高度技術認定企業")
    has_export = st.checkbox("輸出実績あり")
    
    st.subheader("ご希望")
    need_money = st.radio(
        "資金調達の必要性",
        ["必要（急ぎ）", "必要（急がない）", "必要ない（選択肢を知りたい）", "未定"]
    )
    
    funding_amount = st.number_input("資金調達希望額（百万円）", min_value=0, value=100, step=10)
    
    accept_dilution = st.radio(
        "株式希薄化への考え方",
        ["受け入れ可能", "少量なら可（20%未満）", "できれば避けたい", "絶対に経営権は譲れない"]
    )
    
    timeline = st.selectbox(
        "希望期間",
        ["3ヶ月以内", "半年以内", "1年以内", "2〜3年", "急がない"]
    )
    
    priority = st.multiselect(
        "最重視する点（複数選択可）",
        ["資金調達", "経営権維持", "ブランド価値向上", "事業提携先獲得", 
         "経営体制強化", "将来的な上場準備", "事業承継"]
    )

# メイン画面：タブで機能を分割
tab1, tab2, tab3, tab4 = st.tabs(["💰 企業価値算定", "📋 選択肢分析", "📈 シミュレーター", "📊 比較表"])

# ========================================
# タブ1: 企業価値算定（新機能！）
# ========================================
with tab1:
    st.header("💰 あなたの会社は今いくら？")
    st.markdown("""
    複数の算定方法で、御社の企業価値を簡易的に評価します。
    M&Aや資金調達の前に、まず自社の価値を知ることが重要です。
    """)
    
    # 算定に必要な追加情報
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 財務情報（詳細）")
        
        # 基本情報はサイドバーから取得
        st.info(f"""
        **入力済みデータ：**
        - 年間売上：{revenue}百万円
        - 経常利益：{profit}百万円
        - 業種：{industry}
        """)
        
        # 追加情報
        total_assets = st.number_input("総資産（百万円）", min_value=0, value=int(revenue * 1.2), step=10)
        total_liabilities = st.number_input("総負債（百万円）", min_value=0, value=int(revenue * 0.5), step=10)
        depreciation = st.number_input("減価償却費（百万円/年）", min_value=0, value=int(revenue * 0.05), step=1)
        
        # 純資産の計算
        net_assets = total_assets - total_liabilities
        st.metric("純資産", f"{net_assets}百万円")
        
        # EBITDA計算
        ebitda = profit + depreciation
        st.metric("EBITDA", f"{ebitda}百万円", help="利益 + 減価償却費")
    
    with col2:
        st.subheader("⚙️ 算定パラメータ")
        
        # 業種別の標準倍率
        industry_multiples = {
            "製造業": {"per": 15, "pbr": 1.2, "ebitda": 5, "year_buy": 3},
            "IT・ソフトウェア": {"per": 25, "pbr": 3.0, "ebitda": 8, "year_buy": 5},
            "医療・ヘルスケア": {"per": 20, "pbr": 2.0, "ebitda": 7, "year_buy": 4},
            "環境・エネルギー": {"per": 18, "pbr": 1.5, "ebitda": 6, "year_buy": 4},
            "小売・サービス": {"per": 12, "pbr": 1.0, "ebitda": 4, "year_buy": 3},
            "建設・不動産": {"per": 10, "pbr": 0.8, "ebitda": 5, "year_buy": 3},
            "その他": {"per": 15, "pbr": 1.2, "ebitda": 5, "year_buy": 3}
        }
        
        default_multiples = industry_multiples.get(industry, industry_multiples["その他"])
        
        st.markdown(f"**{industry}の標準倍率**")
        
        per_multiple = st.slider(
            "PER（株価収益率）",
            min_value=5, max_value=50, 
            value=default_multiples["per"],
            help="利益の何倍で評価するか"
        )
        
        pbr_multiple = st.slider(
            "PBR（株価純資産倍率）",
            min_value=0.5, max_value=5.0, 
            value=default_multiples["pbr"],
            step=0.1,
            help="純資産の何倍で評価するか"
        )
        
        ebitda_multiple = st.slider(
            "EBITDA倍率",
            min_value=3, max_value=15,
            value=default_multiples["ebitda"],
            help="M&Aでよく使われる"
        )
        
        year_buy_multiple = st.slider(
            "年買法（営業利益の年数）",
            min_value=2, max_value=7,
            value=default_multiples["year_buy"],
            help="中小企業M&Aの実務で一般的"
        )
        
        discount_rate = st.slider(
            "割引率（%）",
            min_value=3, max_value=15,
            value=8,
            help="DCF法で使用"
        )
    
    # 算定実行ボタン
    if st.button("🧮 企業価値を算定する", type="primary", use_container_width=True):
        
        st.markdown("---")
        st.success("✅ 算定完了！")
        
        # 各手法で算定
        valuations = {}
        
        # 1. PER法（株価収益率法）
        if profit > 0:
            valuations['PER法'] = {
                'value': profit * per_multiple,
                'formula': f'{profit}百万円 × {per_multiple}倍',
                'description': '利益ベースの評価。成長企業向け。',
                'suitable': '✅' if profit > 0 and growth_rate > 10 else '△'
            }
        
        # 2. PBR法（株価純資産倍率法）
        if net_assets > 0:
            valuations['PBR法'] = {
                'value': net_assets * pbr_multiple,
                'formula': f'{net_assets}百万円 × {pbr_multiple}倍',
                'description': '純資産ベースの評価。安定企業向け。',
                'suitable': '✅' if net_assets > 0 else '△'
            }
        
        # 3. EBITDA倍率法
        if ebitda > 0:
            valuations['EBITDA倍率法'] = {
                'value': ebitda * ebitda_multiple,
                'formula': f'{ebitda}百万円 × {ebitda_multiple}倍',
                'description': 'M&Aで最も一般的。キャッシュフロー重視。',
                'suitable': '✅'
            }
        
        # 4. 年買法（中小企業M&Aの実務）
        time_net_assets = net_assets  # 時価純資産（簡易的には帳簿価額）
        valuations['年買法'] = {
            'value': time_net_assets + (profit * year_buy_multiple),
            'formula': f'{time_net_assets}百万円 + ({profit}百万円 × {year_buy_multiple}年)',
            'description': '日本の中小企業M&Aで実際に使われる方法。',
            'suitable': '✅'
        }
        
        # 5. DCF法（詳細版）
        # ===== WACC（加重平均資本コスト）の計算 =====
        
        # 株主資本コスト（CAPM簡易版）
        risk_free_rate = 0.5  # 日本国債利回り
        market_risk_premium = 6.0  # 株式リスクプレミアム
        
        # ベータ（業種別）
        industry_beta = {
            "製造業": 1.0,
            "IT・ソフトウェア": 1.3,
            "医療・ヘルスケア": 0.9,
            "環境・エネルギー": 1.1,
            "小売・サービス": 0.8,
            "建設・不動産": 1.2,
            "その他": 1.0
        }
        
        beta = industry_beta.get(industry, 1.0)
        cost_of_equity = risk_free_rate + beta * market_risk_premium  # CAPM
        
        # 負債コスト
        cost_of_debt = 2.0  # 簡易的に2%
        tax_rate = 30  # 法人税率30%
        
        # 資本構成（簡易的に負債比率を計算）
        if total_assets > 0:
            debt_ratio = total_liabilities / total_assets
            equity_ratio = 1 - debt_ratio
        else:
            debt_ratio = 0.3
            equity_ratio = 0.7
        
        # WACC計算
        wacc = (cost_of_equity * equity_ratio) + (cost_of_debt * (1 - tax_rate/100) * debt_ratio)
        
        # ===== フリーキャッシュフロー（FCF）の詳細計算 =====
        
        # 初年度のFCF
        ebit = profit  # 簡易的に営業利益≒経常利益
        nopat = ebit * (1 - tax_rate/100)  # 税引後営業利益
        
        # 運転資本の増減（簡易的に売上の2%）
        delta_working_capital = revenue * 0.02
        
        # 設備投資（簡易的に減価償却費の1.2倍）
        capex = depreciation * 1.2
        
        # 初年度FCF
        base_fcf = nopat + depreciation - delta_working_capital - capex
        
        # ===== 5年間の詳細予測 =====
        fcf_projections = []
        pv_fcf_total = 0
        
        for year in range(1, 6):
            # 成長率の逓減（毎年10%ずつ低下）
            year_growth = growth_rate * (0.9 ** (year - 1))
            
            # その年の予測売上
            projected_revenue = revenue * ((1 + year_growth/100) ** year)
            
            # その年の予測利益（利益率は徐々に改善）
            profit_margin = (profit / revenue) if revenue > 0 else 0.1
            improved_margin = profit_margin + (0.01 * year)  # 年1%ポイント改善
            projected_profit = projected_revenue * improved_margin
            
            # その年のFCF
            year_ebit = projected_profit
            year_nopat = year_ebit * (1 - tax_rate/100)
            year_depreciation = depreciation * ((1 + year_growth/100) ** year)
            year_wc_change = projected_revenue * 0.02 * (year_growth/100)
            year_capex = year_depreciation * 1.2
            
            year_fcf = year_nopat + year_depreciation - year_wc_change - year_capex
            
            # 現在価値に割引
            discount_factor = (1 + wacc/100) ** year
            pv_fcf = year_fcf / discount_factor
            
            pv_fcf_total += pv_fcf
            
            fcf_projections.append({
                'year': year,
                'revenue': projected_revenue,
                'fcf': year_fcf,
                'pv_fcf': pv_fcf
            })
        
        # ===== ターミナルバリュー（継続価値）の計算 =====
        
        # 永続成長率（通常2-3%）
        perpetual_growth_rate = min(2.5, growth_rate * 0.3)  # 成長率の30%、最大2.5%
        
        # 最終年のFCF
        final_year_fcf = fcf_projections[-1]['fcf']
        
        # ゴードン成長モデル
        if wacc > perpetual_growth_rate:
            terminal_value = (final_year_fcf * (1 + perpetual_growth_rate/100)) / ((wacc - perpetual_growth_rate) / 100)
            
            # ターミナルバリューの現在価値
            pv_terminal_value = terminal_value / ((1 + wacc/100) ** 5)
        else:
            # WACCが永続成長率以下の場合はExit倍率法
            pv_terminal_value = final_year_fcf * ebitda_multiple / ((1 + wacc/100) ** 5)
        
        # ===== 企業価値 =====
        dcf_enterprise_value = pv_fcf_total + pv_terminal_value
        
        # 株式価値 = 企業価値 - 純有利子負債
        # 簡易的に純有利子負債 = 総負債 × 50%
        net_debt = total_liabilities * 0.5
        dcf_equity_value = dcf_enterprise_value - net_debt
        
        if dcf_equity_value > 0:
            valuations['DCF法（詳細版）'] = {
                'value': dcf_equity_value,
                'formula': f'PV(5年間FCF) + PV(継続価値) - 純負債',
                'description': f'WACC {wacc:.1f}%で割引。理論的に最も正確。',
                'suitable': '✅' if growth_rate > 0 else '△',
                'details': {
                    'wacc': wacc,
                    'fcf_pv': pv_fcf_total,
                    'terminal_pv': pv_terminal_value,
                    'enterprise_value': dcf_enterprise_value,
                    'net_debt': net_debt,
                    'perpetual_growth': perpetual_growth_rate,
                    'projections': fcf_projections
                }
            }
        
        # 6. 純資産法（最低価格）
        valuations['純資産法'] = {
            'value': net_assets,
            'formula': f'{total_assets}百万円 - {total_liabilities}百万円',
            'description': '最低価格の目安。清算価値に近い。',
            'suitable': '参考値'
        }
        
        # 結果表示
        st.subheader("📊 算定結果サマリー")
        
        # メトリクス表示
        valuations_list = sorted(valuations.items(), key=lambda x: x[1]['value'], reverse=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            median_value = sorted([v['value'] for v in valuations.values()])[len(valuations)//2]
            st.metric("中央値", f"{median_value:.0f}百万円", help="最も信頼できる目安")
        
        with col2:
            max_value = max([v['value'] for v in valuations.values()])
            st.metric("最高値", f"{max_value:.0f}百万円", help="最も楽観的な評価")
        
        with col3:
            min_value = min([v['value'] for v in valuations.values()])
            st.metric("最低値", f"{min_value:.0f}百万円", help="最も保守的な評価")
        
        with col4:
            avg_value = sum([v['value'] for v in valuations.values()]) / len(valuations)
            st.metric("平均値", f"{avg_value:.0f}百万円", help="参考値")
        
        # 詳細な比較表
        st.subheader("📋 手法別詳細")
        
        comparison_data = []
        for method, data in valuations_list:
            comparison_data.append({
                '算定方法': method,
                '企業価値': f"{data['value']:.0f}百万円",
                '計算式': data['formula'],
                '説明': data['description'],
                '適用性': data['suitable']
            })
        
        comparison_df = pd.DataFrame(comparison_data)
        st.dataframe(comparison_df, use_container_width=True, hide_index=True)
        
        # グラフで可視化
        st.subheader("📊 手法別比較（棒グラフ）")
        
        fig = go.Figure()
        
        methods = [item[0] for item in valuations_list]
        values = [item[1]['value'] for item in valuations_list]
        colors = ['#2E86AB' if v == median_value else '#A23B72' if v == max_value else '#F18F01' if v == min_value else '#C6CACC' 
                  for v in values]
        
        fig.add_trace(go.Bar(
            x=methods,
            y=values,
            marker_color=colors,
            text=[f"{v:.0f}百万円" for v in values],
            textposition='outside'
        ))
        
        fig.update_layout(
            xaxis_title="算定方法",
            yaxis_title="企業価値（百万円）",
            height=400,
            showlegend=False
        )
        
        # 中央値のラインを追加
        fig.add_hline(y=median_value, line_dash="dash", line_color="red", 
                      annotation_text=f"中央値: {median_value:.0f}百万円")
        
        st.plotly_chart(fig, use_container_width=True)
        
        # DCF法の詳細内訳（エキスパンダー内）
        if 'DCF法（詳細版）' in valuations:
            st.subheader("🔬 DCF法の詳細内訳")
            
            with st.expander("📊 DCF計算の詳細を表示", expanded=False):
                dcf_details = valuations['DCF法（詳細版）']['details']
                
                # パラメータ表示
                st.markdown("### 📋 主要パラメータ")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("WACC", f"{dcf_details['wacc']:.2f}%", help="加重平均資本コスト")
                
                with col2:
                    st.metric("永続成長率", f"{dcf_details['perpetual_growth']:.2f}%", help="6年目以降の成長率")
                
                with col3:
                    beta_value = industry_beta.get(industry, 1.0)
                    st.metric("ベータ", f"{beta_value:.2f}", help="市場リスクとの相関")
                
                with col4:
                    st.metric("負債比率", f"{debt_ratio*100:.1f}%", help="総資産に占める負債")
                
                # 5年間のFCF予測テーブル
                st.markdown("### 📅 5年間のキャッシュフロー予測")
                
                fcf_df = pd.DataFrame(dcf_details['projections'])
                fcf_df['revenue'] = fcf_df['revenue'].apply(lambda x: f"{x:.0f}百万円")
                fcf_df['fcf'] = fcf_df['fcf'].apply(lambda x: f"{x:.0f}百万円")
                fcf_df['pv_fcf'] = fcf_df['pv_fcf'].apply(lambda x: f"{x:.0f}百万円")
                fcf_df.columns = ['年', '予測売上', 'FCF', 'FCF現在価値']
                
                st.dataframe(fcf_df, use_container_width=True, hide_index=True)
                
                # FCF推移グラフ
                fig_fcf = go.Figure()
                
                fcf_years = [f"{p['year']}年目" for p in dcf_details['projections']]
                fcf_values = [p['fcf'] for p in dcf_details['projections']]
                pv_fcf_values = [p['pv_fcf'] for p in dcf_details['projections']]
                
                fig_fcf.add_trace(go.Bar(
                    name='FCF（額面）',
                    x=fcf_years,
                    y=fcf_values,
                    marker_color='lightblue'
                ))
                
                fig_fcf.add_trace(go.Bar(
                    name='FCF（現在価値）',
                    x=fcf_years,
                    y=pv_fcf_values,
                    marker_color='darkblue'
                ))
                
                fig_fcf.update_layout(
                    title="フリーキャッシュフロー（FCF）の推移",
                    xaxis_title="",
                    yaxis_title="金額（百万円）",
                    barmode='group',
                    height=400
                )
                
                st.plotly_chart(fig_fcf, use_container_width=True)
                
                # 価値の内訳（ウォーターフォール）
                st.markdown("### 💧 企業価値の内訳（ウォーターフォール）")
                
                fig_waterfall = go.Figure(go.Waterfall(
                    name="企業価値",
                    orientation="v",
                    measure=["relative", "relative", "total", "relative", "total"],
                    x=["5年間FCF<br>現在価値", "継続価値<br>現在価値", "企業価値", "純有利子負債<br>（控除）", "株式価値"],
                    y=[dcf_details['fcf_pv'], dcf_details['terminal_pv'], 0, -dcf_details['net_debt'], 0],
                    text=[f"{dcf_details['fcf_pv']:.0f}", 
                          f"{dcf_details['terminal_pv']:.0f}", 
                          f"{dcf_details['enterprise_value']:.0f}",
                          f"-{dcf_details['net_debt']:.0f}",
                          f"{dcf_equity_value:.0f}"],
                    textposition="outside",
                    connector={"line": {"color": "rgb(63, 63, 63)"}},
                ))
                
                fig_waterfall.update_layout(
                    title="DCF法による企業価値の算定プロセス",
                    showlegend=False,
                    height=400
                )
                
                st.plotly_chart(fig_waterfall, use_container_width=True)
                
                # 計算式の説明
                st.markdown("### 📐 計算式の詳細")
                
                st.markdown(f"""
                **1. WACC（加重平均資本コスト）の計算**
                ```
                株主資本コスト = リスクフリーレート + ベータ × マーケットリスクプレミアム
                                = 0.5% + {beta_value:.2f} × 6.0%
                                = {cost_of_equity:.2f}%
                
                負債コスト（税引後） = 2.0% × (1 - 30%)
                                      = {cost_of_debt * 0.7:.2f}%
                
                WACC = {cost_of_equity:.2f}% × {equity_ratio:.1%} + {cost_of_debt * 0.7:.2f}% × {debt_ratio:.1%}
                     = {dcf_details['wacc']:.2f}%
                ```
                
                **2. フリーキャッシュフロー（FCF）の計算**
                ```
                各年のFCF = 税引後営業利益（NOPAT）
                          + 減価償却費
                          - 運転資本増加
                          - 設備投資（CAPEX）
                ```
                
                **3. ターミナルバリュー（継続価値）**
                ```
                継続価値 = 最終年FCF × (1 + 永続成長率) / (WACC - 永続成長率)
                         = {final_year_fcf:.0f}百万円 × 1.{int(dcf_details['perpetual_growth']*10):02d} / ({dcf_details['wacc']:.1f}% - {dcf_details['perpetual_growth']:.1f}%)
                         = {dcf_details['terminal_pv'] * ((1 + dcf_details['wacc']/100) ** 5):.0f}百万円
                
                現在価値 = {dcf_details['terminal_pv'] * ((1 + dcf_details['wacc']/100) ** 5):.0f}百万円 / (1 + {dcf_details['wacc']:.1f}%)^5
                         = {dcf_details['terminal_pv']:.0f}百万円
                ```
                
                **4. 株式価値の算定**
                ```
                企業価値（EV） = 5年間FCF現在価値 + 継続価値現在価値
                               = {dcf_details['fcf_pv']:.0f}百万円 + {dcf_details['terminal_pv']:.0f}百万円
                               = {dcf_details['enterprise_value']:.0f}百万円
                
                株式価値 = 企業価値 - 純有利子負債
                         = {dcf_details['enterprise_value']:.0f}百万円 - {dcf_details['net_debt']:.0f}百万円
                         = {dcf_equity_value:.0f}百万円
                ```
                """)
                
                # 感度分析
                st.markdown("### 🎚️ 感度分析")
                
                st.markdown("WACCと永続成長率が変わった場合の企業価値の変化：")
                
                # 感度分析の計算
                wacc_range = [dcf_details['wacc'] - 2, dcf_details['wacc'] - 1, dcf_details['wacc'], 
                              dcf_details['wacc'] + 1, dcf_details['wacc'] + 2]
                growth_range = [max(0, dcf_details['perpetual_growth'] - 1), 
                               dcf_details['perpetual_growth'], 
                               min(5, dcf_details['perpetual_growth'] + 1)]
                
                sensitivity_data = []
                
                for g in growth_range:
                    row = {'永続成長率': f"{g:.1f}%"}
                    for w in wacc_range:
                        if w > g:
                            # 簡易的な再計算
                            tv = (final_year_fcf * (1 + g/100)) / ((w - g) / 100)
                            pv_tv = tv / ((1 + w/100) ** 5)
                            ev = dcf_details['fcf_pv'] + pv_tv
                            equity = ev - dcf_details['net_debt']
                            row[f'WACC {w:.1f}%'] = f"{equity:.0f}"
                        else:
                            row[f'WACC {w:.1f}%'] = "N/A"
                    sensitivity_data.append(row)
                
                sensitivity_df = pd.DataFrame(sensitivity_data)
                
                # 現在の値をハイライト
                st.dataframe(
                    sensitivity_df,
                    use_container_width=True,
                    hide_index=True
                )
                
                st.info(f"""
                💡 **感度分析の読み方**
                - 中央の値（{dcf_equity_value:.0f}百万円）が現在の前提条件での企業価値
                - WACCが1%上がると企業価値は下がる（割引率が高い = 将来価値が低い）
                - 永続成長率が1%上がると企業価値は上がる（将来の成長期待）
                - 通常、±2%の範囲で企業価値がどう変わるかを見る
                """)
        
        # レンジ表示（レーダーチャート風）
        st.subheader("🎯 妥当価格レンジ")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # 価格レンジをビジュアル化
            fig_range = go.Figure()
            
            fig_range.add_trace(go.Indicator(
                mode = "gauge+number+delta",
                value = median_value,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "企業価値（中央値）"},
                delta = {'reference': net_assets},
                gauge = {
                    'axis': {'range': [None, max_value * 1.2]},
                    'bar': {'color': "#2E86AB"},
                    'steps': [
                        {'range': [0, min_value], 'color': "lightgray"},
                        {'range': [min_value, median_value], 'color': "lightyellow"},
                        {'range': [median_value, max_value], 'color': "lightgreen"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': median_value
                    }
                }
            ))
            
            fig_range.update_layout(height=300)
            st.plotly_chart(fig_range, use_container_width=True)
        
        with col2:
            st.markdown("**💡 解釈ガイド**")
            st.markdown(f"""
            **妥当な価格レンジ：**
            - 下限：{min_value:.0f}百万円
            - 中央値：{median_value:.0f}百万円  
            - 上限：{max_value:.0f}百万円
            
            **推奨：**
            中央値±20%の範囲で交渉
            → {median_value*0.8:.0f}〜{median_value*1.2:.0f}百万円
            """)
        
        # AIによる総合評価
        st.subheader("🤖 AIによる評価コメント")
        
        with st.spinner("AIが算定結果を分析中..."):
            valuation_prompt = f"""
あなたは企業評価の専門家です。以下の算定結果について、経営者向けに分かりやすくコメントしてください。

企業情報:
- 業種: {industry}
- 売上: {revenue}百万円
- 利益: {profit}百万円
- 純資産: {net_assets}百万円
- 成長率: {growth_rate}%

算定結果:
- 最低値: {min_value:.0f}百万円（{list(valuations.keys())[list([v['value'] for v in valuations.values()]).index(min_value)]}）
- 中央値: {median_value:.0f}百万円
- 最高値: {max_value:.0f}百万円（{list(valuations.keys())[list([v['value'] for v in valuations.values()]).index(max_value)]}）

以下の観点でコメントしてください（各80-120文字）：

1. **総合評価**: この企業価値は妥当か
2. **推奨価格**: M&Aの場合、どの価格が現実的か
3. **注意点**: 算定結果を解釈する上での留意点
4. **価値向上のヒント**: 企業価値を高めるために何をすべきか

簡潔に、実践的に。
"""
            
            try:
                client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
                valuation_comment = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=1500,
                    temperature=0.5,
                    messages=[{"role": "user", "content": valuation_prompt}]
                )
                
                st.markdown(valuation_comment.content[0].text)
                
            except Exception as e:
                st.error(f"AI分析でエラー: {str(e)}")
        
        # ダウンロードボタン
        st.markdown("---")
        
        # レポート作成
        report = f"""# 企業価値算定レポート

## 企業情報
- 業種: {industry}
- 年間売上: {revenue}百万円
- 経常利益: {profit}百万円
- 純資産: {net_assets}百万円
- EBITDA: {ebitda}百万円

## 算定結果サマリー
- 最低値: {min_value:.0f}百万円
- 中央値: {median_value:.0f}百万円（推奨）
- 最高値: {max_value:.0f}百万円
- 平均値: {avg_value:.0f}百万円

## 手法別詳細

"""
        for method, data in valuations.items():
            report += f"""
### {method}
- 企業価値: {data['value']:.0f}百万円
- 計算式: {data['formula']}
- 説明: {data['description']}
- 適用性: {data['suitable']}
"""
        
        report += f"""

## 推奨価格レンジ
{median_value*0.8:.0f}〜{median_value*1.2:.0f}百万円

## 注意事項
本レポートは簡易的な算定であり、実際のM&Aや資金調達の際は、
専門家（公認会計士、M&Aアドバイザー等）による詳細なデューデリジェンスが必要です。

作成日: {datetime.now().strftime('%Y年%m月%d日')}
"""
        
        st.download_button(
            label="📥 算定レポートをダウンロード",
            data=report,
            file_name=f"企業価値算定_{industry}_{revenue}百万円売上.md",
            mime="text/markdown"
        )

# ========================================
# タブ2: 選択肢分析（既存機能）
# ========================================
with tab2:
    st.markdown("---")
    
    if st.button("🔍 選択肢を分析する", type="primary", use_container_width=True):
        
        if "ANTHROPIC_API_KEY" not in st.secrets:
            st.error("⚠️ `.streamlit/secrets.toml` にAPIキーを設定してください")
            st.stop()
        
        analysis_prompt = f"""
あなたは日本の企業金融・資本市場に精通したコンサルタントです。日本の中小企業経営者に対して、利用可能な資本市場の選択肢を提案してください。

# 企業情報
- 年間売上高: {revenue}百万円
- 経常利益: {profit}百万円（利益率: {profit/revenue*100 if revenue > 0 else 0:.1f}%）
- 売上成長率: {growth_rate}%
- 設立: {years}年
- 従業員数: {employees}名
- 業種: {industry}
- 所在地: {location}
- 研究開発比率: {rd_ratio}%
- 特許保有: {'あり' if has_patent else 'なし'}
- 高度技術企業: {'認定済' if is_hightech else '未認定'}
- 輸出実績: {'あり' if has_export else 'なし'}

# 経営者のニーズ
- 資金調達ニーズ: {need_money}
- 希望調達額: {funding_amount}百万円
- 株式希薄化: {accept_dilution}
- 希望期間: {timeline}
- 優先事項: {', '.join(priority) if priority else '特になし'}

## 🎯 御社に最適な選択肢 TOP 3

各選択肢について：
1. 概要と適している理由
2. 想定スケジュール
3. 概算コスト
4. メリット・デメリット
5. 次のアクション

を提供してください。

日本市場特有の選択肢（東証グロース、日本政策金融公庫、ものづくり補助金、JAFCO等のVC、事業承継支援等）を優先的に。
"""

        try:
            with st.spinner("🤖 AIが御社の状況を分析中です..."):
                client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
                
                response = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=8000,
                    temperature=0.3,
                    messages=[{"role": "user", "content": analysis_prompt}]
                )
                
                st.success("✅ 分析完了！")
                
                # 分析結果を保存（シミュレーターで使用）
                st.session_state['analysis_result'] = response.content[0].text
                
                st.markdown(response.content[0].text)
                
                st.download_button(
                    label="📥 レポートをダウンロード",
                    data=response.content[0].text,
                    file_name=f"資本市場分析_{industry}_{revenue}百万円売上.md",
                    mime="text/markdown"
                )
                
        except Exception as e:
            st.error(f"❌ エラーが発生しました: {str(e)}")

# ========================================
# タブ3: シミュレーター
# ========================================
with tab3:
    st.header("📈 3年後のシミュレーション")
    st.markdown("異なる選択肢を選んだ場合の3年後をシミュレーションします")
    
    # シナリオ選択
    col1, col2 = st.columns([2, 1])
    
    with col1:
        scenario = st.selectbox(
            "シナリオを選択",
            [
                "シナリオ1: VC調達（株式20%希薄化）",
                "シナリオ2: 銀行融資（無希薄化）",
                "シナリオ3: 自己資金で成長（調達なし）",
                "シナリオ4: 上場準備（複数回調達）",
                "カスタムシナリオ"
            ]
        )
    
    with col2:
        risk_scenario = st.radio(
            "成長見通し",
            ["楽観的", "基本", "悲観的"]
        )
    
    # パラメータ設定
    st.subheader("📊 シミュレーションパラメータ")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if "VC調達" in scenario or "カスタム" in scenario:
            funding_sim = st.slider("調達額（百万円）", 0, 1000, funding_amount, 10)
            equity_dilution = st.slider("株式希薄化（%）", 0, 49, 20, 1)
        elif "銀行融資" in scenario:
            funding_sim = st.slider("融資額（百万円）", 0, 500, funding_amount, 10)
            interest_rate = st.slider("金利（%）", 0.5, 5.0, 2.0, 0.1)
            equity_dilution = 0
        else:
            funding_sim = 0
            equity_dilution = 0
    
    with col2:
        # 成長率の設定（リスクシナリオに応じて）
        base_growth = growth_rate
        if risk_scenario == "楽観的":
            year1_growth = st.slider("1年目成長率（%）", 0, 200, int(base_growth * 1.5), 5)
            year2_growth = st.slider("2年目成長率（%）", 0, 200, int(base_growth * 1.3), 5)
            year3_growth = st.slider("3年目成長率（%）", 0, 200, int(base_growth * 1.2), 5)
        elif risk_scenario == "悲観的":
            year1_growth = st.slider("1年目成長率（%）", -50, 100, int(base_growth * 0.5), 5)
            year2_growth = st.slider("2年目成長率（%）", -50, 100, int(base_growth * 0.6), 5)
            year3_growth = st.slider("3年目成長率（%）", -50, 100, int(base_growth * 0.7), 5)
        else:  # 基本
            year1_growth = st.slider("1年目成長率（%）", -50, 200, base_growth, 5)
            year2_growth = st.slider("2年目成長率（%）", -50, 200, int(base_growth * 0.9), 5)
            year3_growth = st.slider("3年目成長率（%）", -50, 200, int(base_growth * 0.8), 5)
    
    with col3:
        profit_margin_improvement = st.slider(
            "利益率改善（%ポイント/年）", 
            -5, 10, 1, 1
        )
        
        # 業界別のPE倍率
        industry_pe = {
            "製造業": 15,
            "IT・ソフトウェア": 25,
            "医療・ヘルスケア": 20,
            "環境・エネルギー": 18,
            "小売・サービス": 12,
            "建設・不動産": 10,
            "その他": 15
        }
        
        pe_multiple = st.slider(
            "想定PER（倍）",
            5, 50, industry_pe.get(industry, 15), 1
        )
    
    # シミュレーション実行ボタン
    if st.button("🚀 シミュレーション実行", type="primary", use_container_width=True):
        
        # 計算ロジック
        current_profit_margin = profit / revenue if revenue > 0 else 0
        
        # 年次推移の計算
        years_data = []
        current_revenue = revenue
        current_equity = 100  # 初期持株比率100%
        
        # 初期費用の計算
        if "VC調達" in scenario:
            initial_cost = funding_sim * 0.05  # 調達コスト5%
        elif "銀行融資" in scenario:
            initial_cost = funding_sim * 0.02  # 手数料2%
        else:
            initial_cost = 0
        
        for year, growth in enumerate([0, year1_growth, year2_growth, year3_growth], start=0):
            if year == 0:
                # 現在
                year_revenue = current_revenue
                year_profit = profit
                year_equity = current_equity
            else:
                # 未来
                year_revenue = current_revenue * (1 + growth / 100)
                year_profit_margin = current_profit_margin + (profit_margin_improvement * year / 100)
                year_profit = year_revenue * year_profit_margin
                
                # 銀行融資の場合は利息を引く
                if "銀行融資" in scenario and year <= 3:
                    interest_payment = funding_sim * (interest_rate / 100)
                    year_profit -= interest_payment
                
                year_equity = current_equity
                current_revenue = year_revenue
            
            # 企業価値 = 利益 × PER
            company_value = year_profit * pe_multiple
            
            # 株式希薄化の反映
            if year == 1 and equity_dilution > 0:
                year_equity = current_equity * (1 - equity_dilution / 100)
                current_equity = year_equity
            
            # 経営者の持分価値
            owner_value = company_value * (year_equity / 100)
            
            years_data.append({
                'year': f'{year}年後' if year > 0 else '現在',
                'year_num': year,
                'revenue': year_revenue,
                'profit': year_profit,
                'profit_margin': year_profit / year_revenue * 100 if year_revenue > 0 else 0,
                'company_value': company_value,
                'equity': year_equity,
                'owner_value': owner_value
            })
        
        df = pd.DataFrame(years_data)
        
        # 結果の表示
        st.success("✅ シミュレーション完了！")
        
        # メトリクス表示
        st.subheader("📊 3年後の予測")
        
        col1, col2, col3, col4 = st.columns(4)
        
        final_data = df.iloc[-1]
        initial_data = df.iloc[0]
        
        with col1:
            revenue_change = ((final_data['revenue'] - initial_data['revenue']) / initial_data['revenue'] * 100)
            st.metric(
                "売上高",
                f"{final_data['revenue']:.0f}百万円",
                f"{revenue_change:+.1f}%"
            )
        
        with col2:
            st.metric(
                "企業価値",
                f"{final_data['company_value']:.0f}百万円",
                f"{((final_data['company_value'] - initial_data['company_value']) / initial_data['company_value'] * 100):+.1f}%"
            )
        
        with col3:
            st.metric(
                "あなたの持株比率",
                f"{final_data['equity']:.1f}%",
                f"{final_data['equity'] - initial_data['equity']:.1f}%"
            )
        
        with col4:
            st.metric(
                "あなたの株式価値",
                f"{final_data['owner_value']:.0f}百万円",
                f"{((final_data['owner_value'] - initial_data['owner_value']) / initial_data['owner_value'] * 100):+.1f}%"
            )
        
        # グラフ1: 企業価値と持分価値の推移
        st.subheader("📈 企業価値と持分価値の推移")
        
        fig1 = go.Figure()
        
        fig1.add_trace(go.Scatter(
            x=df['year'],
            y=df['company_value'],
            name='企業価値',
            line=dict(color='blue', width=3),
            mode='lines+markers'
        ))
        
        fig1.add_trace(go.Scatter(
            x=df['year'],
            y=df['owner_value'],
            name='あなたの持分価値',
            line=dict(color='green', width=3),
            mode='lines+markers'
        ))
        
        fig1.update_layout(
            xaxis_title="",
            yaxis_title="金額（百万円）",
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig1, use_container_width=True)
        
        # グラフ2: 売上と利益の推移
        st.subheader("💰 売上と利益の推移")
        
        fig2 = go.Figure()
        
        fig2.add_trace(go.Bar(
            x=df['year'],
            y=df['revenue'],
            name='売上高',
            marker_color='lightblue'
        ))
        
        fig2.add_trace(go.Bar(
            x=df['year'],
            y=df['profit'],
            name='経常利益',
            marker_color='lightgreen'
        ))
        
        fig2.update_layout(
            barmode='group',
            xaxis_title="",
            yaxis_title="金額（百万円）",
            height=400
        )
        
        st.plotly_chart(fig2, use_container_width=True)
        
        # グラフ3: 株式構造の変化（円グラフ）
        st.subheader("🥧 株式構造の変化")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**現在**")
            fig3_before = go.Figure(data=[go.Pie(
                labels=['経営者', 'その他'],
                values=[100, 0],
                hole=.3,
                marker_colors=['#2E86AB', '#E0E0E0']
            )])
            fig3_before.update_layout(height=300, showlegend=True)
            st.plotly_chart(fig3_before, use_container_width=True)
        
        with col2:
            st.markdown("**3年後**")
            final_equity = df.iloc[-1]['equity']
            fig3_after = go.Figure(data=[go.Pie(
                labels=['経営者', '投資家'],
                values=[final_equity, 100 - final_equity],
                hole=.3,
                marker_colors=['#2E86AB', '#F18F01']
            )])
            fig3_after.update_layout(height=300, showlegend=True)
            st.plotly_chart(fig3_after, use_container_width=True)
        
        # 詳細データテーブル
        with st.expander("📋 詳細データを表示"):
            display_df = df.copy()
            display_df['revenue'] = display_df['revenue'].apply(lambda x: f"{x:.0f}百万円")
            display_df['profit'] = display_df['profit'].apply(lambda x: f"{x:.0f}百万円")
            display_df['profit_margin'] = display_df['profit_margin'].apply(lambda x: f"{x:.1f}%")
            display_df['company_value'] = display_df['company_value'].apply(lambda x: f"{x:.0f}百万円")
            display_df['equity'] = display_df['equity'].apply(lambda x: f"{x:.1f}%")
            display_df['owner_value'] = display_df['owner_value'].apply(lambda x: f"{x:.0f}百万円")
            
            st.dataframe(
                display_df[['year', 'revenue', 'profit', 'profit_margin', 'company_value', 'equity', 'owner_value']],
                use_container_width=True
            )
        
        # AI による解釈
        st.subheader("🤖 AIによる分析コメント")
        
        with st.spinner("AIがシミュレーション結果を分析中..."):
            interpretation_prompt = f"""
以下のシミュレーション結果について、経営者向けに分かりやすくコメントしてください：

シナリオ: {scenario}
リスクケース: {risk_scenario}

現在の状況:
- 売上: {initial_data['revenue']:.0f}百万円
- 利益: {initial_data['profit']:.0f}百万円
- 企業価値: {initial_data['company_value']:.0f}百万円

3年後の予測:
- 売上: {final_data['revenue']:.0f}百万円（{revenue_change:+.1f}%）
- 利益: {final_data['profit']:.0f}百万円
- 企業価値: {final_data['company_value']:.0f}百万円
- 経営者持株比率: {final_data['equity']:.1f}%
- 経営者持分価値: {final_data['owner_value']:.0f}百万円

以下の観点でコメントしてください（各50-100文字程度）：

1. **全体評価**: このシナリオの妥当性
2. **ポジティブな点**: 何が良いか
3. **リスクと注意点**: 何に気をつけるべきか
4. **推奨アクション**: 次に何をすべきか

簡潔で実践的に。
"""
            
            try:
                client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
                interpretation = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=1500,
                    temperature=0.5,
                    messages=[{"role": "user", "content": interpretation_prompt}]
                )
                
                st.markdown(interpretation.content[0].text)
                
            except Exception as e:
                st.error(f"AI分析でエラー: {str(e)}")

# ========================================
# タブ4: 比較表
# ========================================
with tab4:
    st.header("📊 複数シナリオの比較")
    st.markdown("異なる選択肢を並べて比較します")
    
    # 3つのシナリオを事前計算
    scenarios_to_compare = [
        {
            'name': 'VC調達',
            'funding': funding_amount,
            'dilution': 20,
            'growth': [year1_growth, year2_growth, year3_growth]
        },
        {
            'name': '銀行融資',
            'funding': funding_amount,
            'dilution': 0,
            'growth': [year1_growth * 0.8, year2_growth * 0.8, year3_growth * 0.8]
        },
        {
            'name': '自己資金',
            'funding': 0,
            'dilution': 0,
            'growth': [year1_growth * 0.5, year2_growth * 0.5, year3_growth * 0.5]
        }
    ]
    
    comparison_results = []
    
    for scenario_def in scenarios_to_compare:
        # 簡易計算
        final_revenue = revenue
        for g in scenario_def['growth']:
            final_revenue = final_revenue * (1 + g / 100)
        
        final_profit = final_revenue * (profit / revenue) if revenue > 0 else 0
        company_value = final_profit * industry_pe.get(industry, 15)
        equity = 100 - scenario_def['dilution']
        owner_value = company_value * (equity / 100)
        
        comparison_results.append({
            'シナリオ': scenario_def['name'],
            '調達額': f"{scenario_def['funding']}百万円",
            '株式希薄化': f"{scenario_def['dilution']}%",
            '3年後売上': f"{final_revenue:.0f}百万円",
            '3年後企業価値': f"{company_value:.0f}百万円",
            '経営者持株': f"{equity}%",
            '経営者持分価値': f"{owner_value:.0f}百万円",
            '_owner_value_num': owner_value  # ソート用
        })
    
    comparison_df = pd.DataFrame(comparison_results)
    
    # 表示
    st.dataframe(
        comparison_df.drop('_owner_value_num', axis=1),
        use_container_width=True,
        hide_index=True
    )
    
    # 推奨の表示
    best_scenario = comparison_df.loc[comparison_df['_owner_value_num'].idxmax(), 'シナリオ']
    
    st.info(f"💡 **経営者の持分価値が最大になるのは：{best_scenario}**")
    
    # 比較チャート
    fig_compare = go.Figure()
    
    fig_compare.add_trace(go.Bar(
        name='企業価値',
        x=comparison_df['シナリオ'],
        y=[float(v.replace('百万円', '').replace(',', '')) for v in comparison_df['3年後企業価値']],
        marker_color='lightblue'
    ))
    
    fig_compare.add_trace(go.Bar(
        name='経営者持分価値',
        x=comparison_df['シナリオ'],
        y=[float(v.replace('百万円', '').replace(',', '')) for v in comparison_df['経営者持分価値']],
        marker_color='lightgreen'
    ))
    
    fig_compare.update_layout(
        barmode='group',
        title="シナリオ別の企業価値比較",
        xaxis_title="",
        yaxis_title="金額（百万円）",
        height=400
    )
    
    st.plotly_chart(fig_compare, use_container_width=True)

# フッター
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 0.9em;'>
    <p>💡 シミュレーション結果は参考情報です。実際の意思決定は専門家にご相談ください</p>
    <p>開発：Lily | Claude AIベース</p>
</div>
""", unsafe_allow_html=True)
