import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np # Logaritmik hesaplama için ekledik

# Sayfa Ayarları
st.set_page_config(layout="wide", page_title="LivArea Dashboard 2026")

def normalize_ters(sutun):
    if sutun.max() == sutun.min(): return sutun * 0
    return 1 - (sutun - sutun.min()) / (sutun.max() - sutun.min())

def trend_analizi_cumlesi(v22, v24):
    try:
        degisim = ((float(v24) / float(v22)) - 1) * 100
        yillik = degisim / 2
        if yillik > 0.5: return f"📈 Pozitif büyüme eğilimi (Yıllık ort. %{yillik:.1f})"
        elif yillik < -0.5: return f"📉 Negatif azalış trendi (Yıllık ort. %{abs(yillik):.1f})"
        return "➖ Stabil seyir öngörülüyor."
    except: return "🔍 Analiz hazırlanıyor..."

st.title("🏙️ LivArea: Stratejik Yaşanabilirlik Analiz Platformu")

try:
    df = pd.read_csv('veriseti.csv', sep=None, engine='python')
    df.columns = df.columns.str.replace(' ', '').str.strip() 
    df['il_adı_buyuk'] = df['il_adı'].str.upper()

    # --- ⚙️ ANALİZ PARAMETRELERİ (SİDEBAR) ---
    st.sidebar.markdown("<h1 style='text-align: left; font-size: 55px; margin-bottom: -10px;'>🏠 LivArea</h1>", unsafe_allow_html=True)
    st.sidebar.markdown("### ✨ Yaşanabilir Bölge Analizi")
    st.sidebar.markdown("---")
    
    ongoru_modu = st.sidebar.toggle("💠 LivArea Vision: Akıllı Tahminleme Modu", value=False)
    
    st.sidebar.write("📅 **Veri Dönemi Seçimi:**")
    secilen_yil = st.sidebar.radio("Yıl seçin", [2022, 2023, 2024], index=2, horizontal=True, label_visibility="collapsed")
    y = str(secilen_yil)

    kriter_secimi = st.sidebar.selectbox("🔎 Analiz Kriteri Belirleyin:", 
        ("🏆 Genel Yaşanabilirlik Endeksi", "💰 Konut Maliyet Analizi (Kira)", "🍃 Hava Kalitesi İndeksi", "💼 İş Gücü ve İstihdam", "🧘 Demografik Yoğunluk", "🚗 Trafik Yoğunluğu ve Ulaşım"))
    
    t_kira, t_ist, t_nuf, t_ul = f'ortalama_kira_{y}', f'issizlik_oranı_{y}', f'nufus_{y}', f'arac_sayısı_{y}'
    
    df['kira_26'] = df.apply(lambda r: r['ortalama_kira_2024'] + ((r['ortalama_kira_2024']-r['ortalama_kira_2022'])/2)*2, axis=1)
    df['ist_26'] = df.apply(lambda r: r['issizlik_oranı_2024'] + ((r['issizlik_oranı_2024']-r['issizlik_oranı_2022'])/2)*2, axis=1)
    df['nuf_26'] = df.apply(lambda r: r['nufus_2024'] + ((r['nufus_2024']-r['nufus_2022'])/2)*2, axis=1)
    df['ul_26'] = df.apply(lambda r: r['arac_sayısı_2024'] + ((r['arac_sayısı_2024']-r['arac_sayısı_2022'])/2)*2, axis=1)

    k_o, h_o, i_o, n_o, u_o = df[t_kira].mean(), df['hava_kalitesi_pm25_2024'].mean(), df[t_ist].mean(), df[t_nuf].mean(), df[t_ul].mean()

    def not_uret(row, kriter):
        tr_k, tr_i, tr_n, tr_u = trend_analizi_cumlesi(row['ortalama_kira_2022'], row['ortalama_kira_2024']), trend_analizi_cumlesi(row['issizlik_oranı_2022'], row['issizlik_oranı_2024']), trend_analizi_cumlesi(row['nufus_2022'], row['nufus_2024']), trend_analizi_cumlesi(row['arac_sayısı_2022'], row['arac_sayısı_2024'])
        k, h, i, n, u = f"{'🟢 Maliyet Avantajlı' if row[t_kira] <= k_o else '🔴 Maliyet Riski Yüksek'}", f"{'🟢 Hava Kalitesi İdeal' if row['hava_kalitesi_pm25_2024'] <= h_o else '🔴 Hava Kalitesi Düşük'}", f"{'🟢 İstihdam Potansiyeli Yüksek' if row[t_ist] <= i_o else '🔴 İstihdam Arzı Düşük'}", f"{'🟢 Demografik Yapı Dengeli' if row[t_nuf] <= n_o else '🔴 Nüfus Yoğunluğu Yüksek'}", f"{'🟢 Trafik Akışı Rahat' if row[t_ul] <= u_o else '🔴 Trafik Yoğunluğu Yüksek'}"
        if "Kira" in kriter: return f"{k}<br>↳ {tr_k}" if ongoru_modu else k
        if "Hava" in kriter: return h
        if "İstihdam" in kriter: return f"{i}<br>↳ {tr_i}" if ongoru_modu else i
        if "Demografik" in kriter: return f"{n}<br>↳ {tr_n}" if ongoru_modu else n
        if "Trafik" in kriter: return f"{u}<br>↳ {tr_u}" if ongoru_modu else u
        res = f"{k}<br>{h}<br>{i}<br>{n}<br>{u}"
        if ongoru_modu: res += f"<br><br>🔮 <b>VISION ANALİZİ:</b><br>Maliyet: {tr_k}<br>Demografi: {tr_n}<br>Trafik: {tr_u}"
        return res

    df['analiz_notu'] = df.apply(lambda r: not_uret(r, kriter_secimi), axis=1)

    sk_k, sk_i, sk_n, sk_u = ('kira_26' if ongoru_modu else t_kira), ('ist_26' if ongoru_modu else t_ist), ('nuf_26' if ongoru_modu else t_nuf), ('ul_26' if ongoru_modu else t_ul)
    df['skor'] = ((normalize_ters(df[sk_k]) + normalize_ters(df['hava_kalitesi_pm25_2024']) + normalize_ters(df[sk_i]) + normalize_ters(df[sk_n]) + normalize_ters(df[sk_u])) / 5) * 100

    if "Kira" in kriter_secimi: v, r, h_detay, data_idx = (t_kira if not ongoru_modu else 'kira_26'), "Reds", "💰 Birim Maliyet (TL)", 0
    elif "Hava" in kriter_secimi: v, r, h_detay, data_idx = 'hava_kalitesi_pm25_2024', "Greens_r", "🍃 PM2.5 Değeri", 1
    elif "İstihdam" in kriter_secimi: v, r, h_detay, data_idx = (t_ist if not ongoru_modu else 'ist_26'), "Blues_r", "💼 İstihdam Verisi", 2
    elif "Demografik" in kriter_secimi: v, r, h_detay, data_idx = (t_nuf if not ongoru_modu else 'nuf_26'), "Purples", "🧘 Nüfus Miktarı", 5
    elif "Trafik" in kriter_secimi: v, r, h_detay, data_idx = (t_ul if not ongoru_modu else 'ul_26'), "Oranges", "🚗 Araç Sayısı", 6
    else: v, r, h_detay, data_idx = 'skor', "RdYlGn", "🏆 Endeks Skoru", 4

    # 🔥 CANLANDIRICI DOKUNUŞ: Logaritmik Renk Skalası 🔥
    # Değerleri log tabanına alıyoruz, böylece küçük şehirler de renkleniyor.
    df['color_val'] = np.log10(df[v].replace(0, 1)) 

    fig = px.scatter_mapbox(
        df, lat="enlem", lon="boylam", color='color_val', size=[22] * len(df), color_continuous_scale=r, 
        zoom=5.8, mapbox_style="carto-positron", hover_name="il_adı_buyuk", 
        custom_data=[t_kira, 'hava_kalitesi_pm25_2024', t_ist, 'analiz_notu', 'skor', t_nuf, t_ul], 
        center={"lat": 38.96, "lon": 35.24}, height=700
    )

    fig.update_traces(
        marker=dict(opacity=1.0), 
        # Hoverda logaritmik değeri değil, orijinal değeri gösteriyoruz
        hovertemplate="<b>📍 %{hovertext}</b><br><br>" + h_detay + ": %{customdata[" + str(data_idx) + "]:,.1f}<br><br>🔍 <b>STRATEJİK ANALİZ:</b><br>%{customdata[3]}<extra></extra>"
    )

    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, hoverlabel=dict(bgcolor="black", font_size=13, font_color="white"), coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

    st.write("---")
    top_10 = df.sort_values(v, ascending=(False if "Endeks" in kriter_secimi else True)).head(10)
    fig_bar = px.bar(top_10, x='il_adı_buyuk', y=v, color=v, color_continuous_scale=r, text_auto='.1f', title=f"📈 Performansı En Yüksek 10 Lokasyon", labels={v: 'Endeks Skoru', 'il_adı_buyuk': 'Şehir'})
    fig_bar.update_traces(hovertemplate="<b>Şehir: %{x}</b><br>Skor: %{y:.1f}<extra></extra>")
    fig_bar.update_layout(xaxis_title="Şehir", yaxis_title="Endeks Skoru")
    st.plotly_chart(fig_bar, use_container_width=True)

except Exception as e:
    st.error(f"🚨 Teknik Hata: {e}")