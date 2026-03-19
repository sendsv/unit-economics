import streamlit as st
import pandas as pd

# ==========================================
# КОНФИГУРАЦИЯ СТРАНИЦЫ
# ==========================================
st.set_page_config(
    page_title="Калькулятор Юнит-экономики",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# СЛОВАРЬ ТЕРМИНОВ (для всплывающих подсказок)
# ==========================================
TERMS = {
    "Open Rate": "Open Rate (Открываемость) — Доля пользователей в процентах, открывших ваше сообщение или письмо от общего числа доставленных.",
    "CTR": "Click-Through Rate (Кликабельность) — Доля пользователей, кликнувших по ссылке, от числа тех, кто открыл сообщение.",
    "CR": "Conversion Rate (Конверсия в покупку) — Доля пользователей, совершивших реальную покупку, от числа тех, кто кликнул/перешел на сайт.",
    "Revenue": "Revenue (Выручка) — Общий объем денег, полученный от продаж.",
    "COGS": "Cost of Goods Sold (Себестоимость) — Прямые переменные расходы на создание и продажу одной единицы товара/услуги (включает эквайринг, налоги, закупку и т.д.).",
    "CAC": "Customer Acquisition Cost (Стоимость привлечения) — Средние затраты на маркетинг для привлечения одного платящего клиента.",
    "Gross Profit": "Gross Profit (Валовая прибыль) — Выручка минус все переменные расходы (COGS) на весь объем продаж.",
    "Contribution Margin": "Contribution Margin (Маржинальная прибыль) — Валовая прибыль с одной продажи (чека) после вычета переменных расходов (COGS) и стоимости привлечения (CAC).",
    "ROI": "Return on Investment (Окупаемость инвестиций) — Процент возврата вложений. Показывает, сколько прибыли приносит каждый вложенный рубль.",
    "Net Profit": "Net Profit (Чистая прибыль) — Итоговая сумма денег, которая остается после вычета абсолютно всех расходов (COGS, CAC, Постоянные расходы).",
    "Break-even": "Break-even point (Точка безубыточности) — Количество единиц товара/услуг, которое нужно продать, чтобы доходы полностью покрыли все расходы (выйти в ноль)."
}

def create_abbr(text, term_key, color='#2c3e50'):
    """Функция для создания HTML-элемента с пунктирным подчеркиванием и всплывающей подсказкой."""
    tooltip = TERMS.get(term_key, "")
    return f'<span title="{tooltip}" style="border-bottom: 1px dashed {color}; cursor: help; color: {color};">{text}</span>'

# ==========================================
# ИНИЦИАЛИЗАЦИЯ ДАННЫХ ПО УМОЛЧАНИЮ
# ==========================================
def init_session_state():
    default_cogs = pd.DataFrame([
        {"Название": "Закупка товара", "Описание": "Оптовая стоимость единицы", "Сумма, ₽": 500.0},
        {"Название": "Упаковка", "Описание": "Коробка и материалы", "Сумма, ₽": 50.0}
    ])
    default_cac = pd.DataFrame([
        {"Название": "Таргет VK", "Описание": "Рекламный бюджет ВКонтакте", "Сумма, ₽": 15000.0},
        {"Название": "Контекстная реклама", "Описание": "Яндекс.Директ", "Сумма, ₽": 20000.0}
    ])
    
    if "cogs" not in st.session_state: st.session_state["cogs"] = default_cogs.copy()
    if "cac" not in st.session_state: st.session_state["cac"] = default_cac.copy()

init_session_state()

# ==========================================
# ФУНКЦИИ ФОРМАТИРОВАНИЯ И РАСЧЕТА
# ==========================================
def fmt(num, is_int=False):
    if num == float('inf'):
        return "Недостижимо"
    if is_int:
        return f"{int(num):,} ".replace(',', ' ')
    return f"{num:,.2f} ".replace(',', ' ')

def render_dashboard(m):
    roi_color = "#27ae60" if m['roi'] > 0 else "#c0392b"
    net_color = "#27ae60" if m['net_profit'] > 0 else "#c0392b"
    
    html = f"""
    <div style="background-color: #f4f6f9; padding: 20px; border-radius: 8px; color: #333; margin-top: 20px;">
        <h2 style="margin-top: 0; color: #2c3e50; border-bottom: 2px solid #bdc3c7; padding-bottom: 10px;">
            Итоговые метрики
        </h2>
        <div style="display: flex; flex-wrap: wrap; gap: 20px; margin-bottom: 20px;">
            <div style="flex: 1; min-width: 250px; background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
                <h3 style="margin-top: 0; color: #34495e;" title="Объемы">📦 Объемы</h3>
                <p>Покупателей: <b>{fmt(m['buyers'], True)} чел.</b></p>
                <p>Продано единиц: <b>{fmt(m['units_sold'], True)} шт.</b></p>
            </div>
            <div style="flex: 1; min-width: 250px; background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
                <h3 style="margin-top: 0; color: #34495e;" title="{TERMS['Revenue']}">💰 Финансы (база)</h3>
                <p title="{TERMS['Revenue']}">Выручка (Revenue): <b>{fmt(m['revenue'])} ₽</b></p>
                <p title="{TERMS['COGS']}">Всего COGS: <b>{fmt(m['total_cogs'])} ₽</b></p>
                <p title="{TERMS['COGS']}">COGS на 1 шт.: <b>{fmt(m['cogs_per_unit'])} ₽</b></p>
            </div>
            <div style="flex: 1; min-width: 250px; background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
                <h3 style="margin-top: 0; color: #34495e;" title="{TERMS['CAC']}">🎯 Эффективность</h3>
                <p title="{TERMS['CAC']}">Итоговый CAC: <b>{fmt(m['cac'])} ₽</b></p>
                <p title="{TERMS['Gross Profit']}">Gross Profit: <b>{fmt(m['gross_profit'])} ₽</b></p>
                <p title="{TERMS['Contribution Margin']}">Contr. Margin: <b>{fmt(m['contribution_margin'])} ₽ / чек</b></p>
            </div>
        </div>
        <div style="background: white; padding: 20px; border-radius: 8px; border-left: 5px solid {roi_color}; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h3 style="margin-top: 0; color: #2c3e50;">🏆 Главные показатели (Итог проекта)</h3>
            <div style="display: flex; flex-wrap: wrap; gap: 30px;">
                <div title="{TERMS['ROI']}">
                    <span style="font-size: 14px; color: #7f8c8d;">Окупаемость (ROI)</span><br>
                    <span style="font-size: 28px; font-weight: bold; color: {roi_color};">{fmt(m['roi'])} %</span>
                </div>
                <div title="{TERMS['Net Profit']}">
                    <span style="font-size: 14px; color: #7f8c8d;">Чистая прибыль (Net Profit)</span><br>
                    <span style="font-size: 28px; font-weight: bold; color: {net_color};">{fmt(m['net_profit'])} ₽</span>
                </div>
                <div title="{TERMS['Break-even']}">
                    <span style="font-size: 14px; color: #7f8c8d;">Точка безубыточности</span><br>
                    <span style="font-size: 28px; font-weight: bold; color: #2980b9;">{fmt(m['break_even'], True)} шт.</span>
                </div>
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# ==========================================
# ОСНОВНОЙ ИНТЕРФЕЙС
# ==========================================
def render_segment():
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📦 Блок 1: Объем продаж")
        sales_mode = st.radio("Ввод продаж:", ["Через воронку продаж", "Ручной ввод"], key="mode")
        
        if sales_mode == "Через воронку продаж":
            f_base = st.number_input("Размер базы:", min_value=0, value=10000, key="base", help="Общее количество контактов в базе рассылки/рекламы")
            f_or = st.number_input("Open Rate %:", min_value=0.0, max_value=100.0, value=30.0, key="or", help=TERMS['Open Rate'])
            f_ctr = st.number_input("CTR %:", min_value=0.0, max_value=100.0, value=15.0, key="ctr", help=TERMS['CTR'])
            f_cr = st.number_input("CR %:", min_value=0.0, max_value=100.0, value=5.0, key="cr", help=TERMS['CR'])
        else:
            m_units = st.number_input("Продано (шт):", min_value=0, value=100, key="munits", help="Укажите точное количество проданных единиц")
            f_base, f_or, f_ctr, f_cr = 0, 0, 0, 0 # dummy values

    with col2:
        st.markdown(f"#### 💰 Блок 2: Доходы ({create_abbr('Revenue', 'Revenue')})", unsafe_allow_html=True)
        price = st.number_input("Цена 1 шт. ₽:", min_value=0.0, value=1500.0, key="price", help="Цена, по которой мы продаем 1 единицу клиенту")
        tpr = st.number_input("Единиц в чеке:", min_value=0.1, value=1.5, key="tpr", help="Среднее количество товаров/услуг, которое покупает 1 клиент за раз")

    st.divider()
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown(f"#### 📉 Блок 3: Переменные расходы ({create_abbr('COGS', 'COGS')})", unsafe_allow_html=True)
        acq_percent = st.number_input("Эквайринг %:", min_value=0.0, value=2.5, key="acq", help="Комиссия платежной системы в процентах от выручки")
        tax_percent = st.number_input("Налоги %:", min_value=0.0, value=6.0, key="tax", help="Налог с продаж в процентах")
            
        st.write("Дополнительные переменные расходы (на 1 шт.):")
        # Streamlit 1.23+ Data Editor for dynamic lists
        cogs_df = st.data_editor(
            st.session_state["cogs"],
            num_rows="dynamic",
            use_container_width=True,
            key="cogs_editor",
            hide_index=True
        )
        st.session_state["cogs"] = cogs_df

    with col4:
        st.markdown(f"#### 📢 Блок 4: Пост. расходы и Привлечение ({create_abbr('CAC', 'CAC')})", unsafe_allow_html=True)
        fixed_costs = st.number_input("Пост. расходы ₽:", min_value=0.0, value=50000.0, key="fixed", help="Расходы, не зависящие от объема продаж")
        
        st.write("Каналы маркетинга и разовые расходы:")
        cac_df = st.data_editor(
            st.session_state["cac"],
            num_rows="dynamic",
            use_container_width=True,
            key="cac_editor",
            hide_index=True
        )
        st.session_state["cac"] = cac_df

    # ================= РАСЧЕТ МЕТРИК =================
    # Безопасное деление
    tpr = max(tpr, 0.0001)
    
    # Объемы
    if sales_mode == "Через воронку продаж":
        buyers = f_base * (f_or / 100) * (f_ctr / 100) * (f_cr / 100)
        units_sold = buyers * tpr
    else:
        units_sold = m_units
        buyers = units_sold / tpr
        
    # Выручка
    revenue = units_sold * price
    
    # Динамические суммы (защита от пустых значений и None)
    dyn_cogs = cogs_df["Сумма, ₽"].fillna(0).sum() if not cogs_df.empty else 0.0
    dyn_cac = cac_df["Сумма, ₽"].fillna(0).sum() if not cac_df.empty else 0.0
    
    # Расходы
    cogs_per_unit = (price * (acq_percent / 100)) + (price * (tax_percent / 100)) + dyn_cogs
    total_cogs = cogs_per_unit * units_sold
    marketing_total = dyn_cac
    
    # Эффективность
    cac = marketing_total / buyers if buyers > 0 else 0.0
    gross_profit = revenue - total_cogs
    contribution_margin = ((price - cogs_per_unit) * tpr) - cac
    net_profit = gross_profit - marketing_total - fixed_costs
    
    total_investments = total_cogs + marketing_total + fixed_costs
    roi = (net_profit / total_investments * 100) if total_investments > 0 else 0.0
    
    margin_per_unit = price - cogs_per_unit
    break_even_units = (fixed_costs + marketing_total) / margin_per_unit if margin_per_unit > 0 else float('inf')

    metrics = {
        'buyers': buyers, 'units_sold': units_sold, 'revenue': revenue,
        'total_cogs': total_cogs, 'cogs_per_unit': cogs_per_unit,
        'cac': cac, 'gross_profit': gross_profit, 'contribution_margin': contribution_margin,
        'net_profit': net_profit, 'roi': roi, 'break_even': break_even_units
    }
    
    render_dashboard(metrics)

# ==========================================
# ТОЧКА ВХОДА СТРАНИЦЫ
# ==========================================
st.title("📊 Калькулятор Юнит-Экономики")

render_segment()
