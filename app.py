import streamlit as st
import pandas as pd
import io

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
# ФУНКЦИИ ФОРМАТИРОВАНИЯ И ЭКСПОРТА (EXCEL С ФОРМУЛАМИ)
# ==========================================
def fmt(num, is_int=False):
    if num == float('inf'):
        return "Недостижимо"
    if is_int:
        return f"{int(num):,} ".replace(',', ' ')
    return f"{num:,.2f} ".replace(',', ' ')

def export_to_excel(inputs_dict, cogs_df, cac_df):
    """Генерирует умный Excel-файл с графиками и формулами."""
    output = io.BytesIO()
    
    # Используем xlsxwriter как движок, чтобы писать формулы и графики
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book
        worksheet = workbook.add_worksheet('Дашборд Юнит-Экономики')
        worksheet.hide_gridlines(2)

        # Форматы оформления
        h1_fmt = workbook.add_format({'bold': True, 'font_size': 14, 'bg_color': '#2c3e50', 'font_color': 'white', 'valign': 'vcenter', 'align': 'center', 'border': 1})
        h2_fmt = workbook.add_format({'bold': True, 'font_size': 12, 'bg_color': '#ecf0f1', 'border': 1})
        bold_fmt = workbook.add_format({'bold': True, 'border': 1})
        num_fmt = workbook.add_format({'num_format': '#,##0.00', 'border': 1})
        int_fmt = workbook.add_format({'num_format': '#,##0', 'border': 1})
        money_fmt = workbook.add_format({'num_format': '#,##0.00 "₽"', 'border': 1})
        money_bold_fmt = workbook.add_format({'bold': True, 'num_format': '#,##0.00 "₽"', 'border': 1, 'bg_color': '#f9f9f9'})
        pct_fmt = workbook.add_format({'num_format': '0.00%', 'border': 1})
        pct_bold_fmt = workbook.add_format({'bold': True, 'num_format': '0.00%', 'border': 1, 'bg_color': '#f9f9f9'})

        # Настройка ширины колонок
        worksheet.set_column('A:A', 35)
        worksheet.set_column('B:B', 20)
        worksheet.set_column('C:C', 5) # Разделитель
        worksheet.set_column('D:D', 40)
        worksheet.set_column('E:E', 25)

        # === ЛЕВАЯ КОЛОНКА: ВВОДНЫЕ ДАННЫЕ ===
        worksheet.merge_range('A1:B1', 'ВВОДНЫЕ ДАННЫЕ (Можно менять)', h1_fmt)
        
        # Инпуты
        mode_val = 1 if inputs_dict["Режим ввода"] == "Через воронку продаж" else 2
        
        inputs_layout = [
            ("Режим (1-Воронка, 2-Ручной)", mode_val, int_fmt),
            ("Размер базы", inputs_dict["Размер базы"] if mode_val==1 else 0, int_fmt),
            ("Open Rate %", inputs_dict["Open Rate %"] if mode_val==1 else 0, num_fmt),
            ("CTR %", inputs_dict["CTR %"] if mode_val==1 else 0, num_fmt),
            ("CR %", inputs_dict["CR %"] if mode_val==1 else 0, num_fmt),
            ("Продано (ручной ввод), шт", inputs_dict["Продано (ручной ввод)"] if mode_val==2 else 0, int_fmt),
            ("Цена 1 шт. ₽", inputs_dict["Цена 1 шт. ₽"], money_fmt),
            ("Единиц в чеке", inputs_dict["Единиц в чеке"], num_fmt),
            ("Эквайринг %", inputs_dict["Эквайринг %"], num_fmt),
            ("Налоги %", inputs_dict["Налоги %"], num_fmt),
            ("Постоянные расходы ₽", inputs_dict["Постоянные расходы ₽"], money_fmt),
        ]

        row = 1
        for name, val, fmt_type in inputs_layout:
            row += 1
            worksheet.write(f'A{row}', name, h2_fmt)
            worksheet.write(f'B{row}', val, fmt_type)

        row += 2
        worksheet.merge_range(f'A{row}:B{row}', 'ДОП. ПЕРЕМЕННЫЕ РАСХОДЫ (COGS)', h1_fmt)
        row += 1
        worksheet.write(f'A{row}', 'Название', h2_fmt)
        worksheet.write(f'B{row}', 'Сумма, ₽', h2_fmt)
        
        cogs_start = row + 1
        for idx, item in cogs_df.iterrows():
            row += 1
            worksheet.write(f'A{row}', item['Название'], bold_fmt)
            worksheet.write(f'B{row}', item['Сумма, ₽'], money_fmt)
        if cogs_df.empty:
            row += 1
            worksheet.write(f'A{row}', '-', bold_fmt)
            worksheet.write(f'B{row}', 0, money_fmt)
            
        row += 1
        cogs_sum_row = row
        worksheet.write(f'A{row}', 'ИТОГО ДОП. COGS:', bold_fmt)
        worksheet.write_formula(f'B{row}', f'=SUM(B{cogs_start}:B{row-1})', money_bold_fmt)

        row += 2
        worksheet.merge_range(f'A{row}:B{row}', 'МАРКЕТИНГ И РАЗОВЫЕ РАСХОДЫ (CAC)', h1_fmt)
        row += 1
        worksheet.write(f'A{row}', 'Название', h2_fmt)
        worksheet.write(f'B{row}', 'Сумма, ₽', h2_fmt)
        
        cac_start = row + 1
        for idx, item in cac_df.iterrows():
            row += 1
            worksheet.write(f'A{row}', item['Название'], bold_fmt)
            worksheet.write(f'B{row}', item['Сумма, ₽'], money_fmt)
        if cac_df.empty:
            row += 1
            worksheet.write(f'A{row}', '-', bold_fmt)
            worksheet.write(f'B{row}', 0, money_fmt)

        row += 1
        cac_sum_row = row
        worksheet.write(f'A{row}', 'ИТОГО МАРКЕТИНГ:', bold_fmt)
        worksheet.write_formula(f'B{row}', f'=SUM(B{cac_start}:B{row-1})', money_bold_fmt)

        # === ПРАВАЯ КОЛОНКА: РАСЧЕТЫ (ФОРМУЛЫ) ===
        worksheet.merge_range('D1:E1', 'ИТОГОВЫЕ МЕТРИКИ (Авторасчет)', h1_fmt)
        
        metrics_layout = [
            ("Покупателей (чел)", '=IF(B2=1, B3*(B4/100)*(B5/100)*(B6/100), B7/B9)', int_fmt),
            ("Продано единиц (шт)", '=IF(B2=1, E2*B9, B7)', int_fmt),
            ("Выручка (Revenue)", '=E3*B8', money_bold_fmt),
            ("COGS на 1 шт.", f'=(B8*(B10/100)) + (B8*(B11/100)) + B{cogs_sum_row}', money_fmt),
            ("Общая себестоимость (Total COGS)", '=E5*E3', money_bold_fmt),
            ("Стоимость привлечения (Итоговый CAC)", f'=IF(E2>0, B{cac_sum_row}/E2, 0)', money_fmt),
            ("Валовая прибыль (Gross Profit)", '=E4-E6', money_bold_fmt),
            ("Маржинальная прибыль (С 1 чека)", f'=(B8-E5)*B9 - E7', money_bold_fmt),
            ("Чистая прибыль (Net Profit)", f'=E8 - B{cac_sum_row} - B12', money_bold_fmt),
            ("Окупаемость (ROI)", f'=IF((E6+B{cac_sum_row}+B12)>0, E10/(E6+B{cac_sum_row}+B12), 0)', pct_bold_fmt),
            ("Точка безубыточности (Break-even), шт", f'=IF((B8-E5)>0, (B12+B{cac_sum_row})/(B8-E5), "Недостижимо")', int_fmt),
        ]

        r_metrics = 1
        for name, formula, fmt_type in metrics_layout:
            r_metrics += 1
            worksheet.write(f'D{r_metrics}', name, h2_fmt)
            worksheet.write_formula(f'E{r_metrics}', formula, fmt_type)

        # === ДАННЫЕ ДЛЯ ГРАФИКА ТОЧКИ БЕЗУБЫТОЧНОСТИ (Скрытые колонки) ===
        worksheet.set_column('AA:AC', None, None, {'hidden': 1})
        worksheet.write('AA1', 'Объем')
        worksheet.write('AB1', 'Выручка')
        worksheet.write('AC1', 'Расходы')

        # Формируем точки: 0, 0.5 BEP, BEP, 1.5 BEP, 2 BEP
        worksheet.write('AA2', 0)
        worksheet.write_formula('AA3', '=IFERROR(E12*0.5, 0)')
        worksheet.write_formula('AA4', '=IFERROR(E12, 0)')
        worksheet.write_formula('AA5', '=IFERROR(E12*1.5, 0)')
        worksheet.write_formula('AA6', '=IFERROR(E12*2, 0)')

        for r_chart in range(2, 7):
            worksheet.write_formula(f'AB{r_chart}', f'=AA{r_chart}*B8')
            worksheet.write_formula(f'AC{r_chart}', f'=B12+B{cac_sum_row} + AA{r_chart}*E5')

        # === ПОСТРОЕНИЕ ГРАФИКА ===
        chart = workbook.add_chart({'type': 'line'})
        chart.add_series({
            'name': 'Выручка',
            'categories': '=Дашборд Юнит-Экономики!$AA$2:$AA$6',
            'values': '=Дашборд Юнит-Экономики!$AB$2:$AB$6',
            'line': {'color': '#27ae60', 'width': 2.5}
        })
        chart.add_series({
            'name': 'Общие расходы',
            'categories': '=Дашборд Юнит-Экономики!$AA$2:$AA$6',
            'values': '=Дашборд Юнит-Экономики!$AC$2:$AC$6',
            'line': {'color': '#c0392b', 'width': 2.5}
        })
        chart.set_title({'name': 'График Точки Безубыточности', 'name_font': {'size': 14, 'bold': True}})
        chart.set_x_axis({'name': 'Объем продаж (шт)', 'major_gridlines': {'visible': True, 'line': {'color': '#E0E0E0'}}})
        chart.set_y_axis({'name': 'Деньги (₽)', 'major_gridlines': {'visible': True, 'line': {'color': '#E0E0E0'}}})
        chart.set_legend({'position': 'bottom'})

        worksheet.insert_chart('G2', chart, {'x_scale': 1.6, 'y_scale': 1.4})

    return output.getvalue()

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
            m_units = 0
        else:
            m_units = st.number_input("Продано (шт):", min_value=0, value=100, key="munits", help="Укажите точное количество проданных единиц")
            f_base, f_or, f_ctr, f_cr = 0, 0, 0, 0 

    with col2:
        st.markdown(f"#### 💰 Блок 2: Доходы ({create_abbr('Revenue', 'Revenue')})", unsafe_allow_html=True)
        price = st.number_input("Цена 1 шт. ₽:", min_value=0.0, value=1500.0, key="price", help="Цена, по которой мы продаем 1 единицу клиенту")
        tpr = st.number_input("Единиц в чеке:", min_value=0.1, value=1.5, key="tpr", help="Среднее количество товаров/услуг, которое покупает 1 клиент за раз")
        
        # Выравнивание по высоте: добавляем пустые блоки в зависимости от режима ввода
        if sales_mode == "Через воронку продаж":
            st.markdown("<div style='min-height: 250px;'></div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='min-height: 20px;'></div>", unsafe_allow_html=True)

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

    # Собираем все введенные данные для выгрузки в Excel
    inputs_dict = {
        "Режим ввода": sales_mode,
        "Размер базы": f_base if sales_mode == "Через воронку продаж" else 0,
        "Open Rate %": f_or if sales_mode == "Через воронку продаж" else 0,
        "CTR %": f_ctr if sales_mode == "Через воронку продаж" else 0,
        "CR %": f_cr if sales_mode == "Через воронку продаж" else 0,
        "Продано (ручной ввод)": m_units if sales_mode == "Ручной ввод" else 0,
        "Цена 1 шт. ₽": price,
        "Единиц в чеке": tpr,
        "Эквайринг %": acq_percent,
        "Налоги %": tax_percent,
        "Постоянные расходы ₽": fixed_costs
    }

    # ================= РАСЧЕТ МЕТРИК =================
    # Безопасное деление
    safe_tpr = max(tpr, 0.0001)
    
    # Объемы
    if sales_mode == "Через воронку продаж":
        buyers = f_base * (f_or / 100) * (f_ctr / 100) * (f_cr / 100)
        units_sold = buyers * safe_tpr
    else:
        units_sold = m_units
        buyers = units_sold / safe_tpr
        
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
    contribution_margin = ((price - cogs_per_unit) * safe_tpr) - cac
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
    
    # Отрисовка дашборда
    render_dashboard(metrics)

    # ================= БЛОК ЭКСПОРТА =================
    st.divider()
    st.markdown("### 💾 Умный экспорт результатов")
    
    col_export1, col_export2 = st.columns([1, 2])
    with col_export1:
        # Генерируем Excel
        excel_data = export_to_excel(inputs_dict, cogs_df, cac_df)
        st.download_button(
            label="📥 Скачать интерактивный Excel (с формулами и графиком)",
            data=excel_data,
            file_name="unit_economics_dashboard.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    with col_export2:
        st.info("💡 **Что внутри Excel?** Мы собрали все данные на один лист, прописали классические Excel-формулы для метрик и построили график точки безубыточности. Вы можете менять ячейки с вводными данными прямо в Excel, и все результаты моментально пересчитаются!")

# ==========================================
# ТОЧКА ВХОДА СТРАНИЦЫ
# ==========================================
st.title("📊 Калькулятор Юнит-Экономики")

render_segment()
