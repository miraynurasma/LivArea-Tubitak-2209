import streamlit as st
import pandas as pd
import plotly.express as px

# Sayfa Ayarları
st.set_page_config(layout="wide", page_title="LivArea Dashboard 2026")

# --- YARDIMCI FONKSİYONLAR ---
def normalize_ters(sutun):
    return 1 - (sutun - sutun.min()) / (sutun.max() - sutun.min())

# --- ✨ SPRINT 3: AKILLI ANALİZ NOTU ---
def get_kriter_yorumu(secim, df):
    if "Kira" in secim:
        en_iyi = df.loc[df['ortalama_kira_2024'].idxmin(), 'il_adı_buyuk']
        return f"🏠 **Ekonomik Analiz:** Konut maliyeti açısından en avantajlı ilimiz **{en_iyi}**. Bütçe dostu yaşam için ideal."
    elif "Hava" in secim:
        en_iyi = df.loc[df['hava_kalitesi_pm25_2024'].idxmin(), 'il_adı_buyuk']
        return f"🌿 **Çevresel Analiz:** En temiz havayı **{en_iyi}** sunuyor. Sağlıklı yaşam için zirvede."
    elif "İstihdam" in secim:
        en_iyi = df.loc[df['issizlik_oranı_2024'].idxmin(), 'il_adı_buyuk']
        return f"💼 **İstihdam Analizi:** İş gücü potansiyeli en yüksek ilimiz **{en_iyi}**."
    elif "Nüfus" in secim:
        en_iyi = df.loc[df['nufus_2024'].idxmin(), 'il_adı_buyuk']
        return f"🧘 **Demografik Analiz:** En sakin ve huzurlu yerleşim alanı **{en_iyi}**."
    elif "Ulaşım" in secim:
        en_iyi = df.loc[df['arac_sayısı_2024'].idxmin(), 'il_adı_buyuk']
        return f"🚗 **Lojistik Analiz:** Trafik yoğunluğunun en az olduğu ilimiz **{en_iyi}**."
    else:
        en_iyi = df.loc[df['gercek_skor'].idxmax(), 'il_adı_buyuk']
        return f"🏆 **Genel Sonuç:** Türkiye'nin yaşanabilirlik şampiyonu **{en_iyi}** seçilmiştir!"

# --- ANA UYGULAMA ---
st.title("🏙️ LivArea: İnteraktif Şehir Analiz Dashboard'u")
st.markdown("### *Veriye Dayalı Yaşanabilirlik Rehberiniz*")

try:
    df = pd.read_csv('veriseti.csv', sep=None, engine='python')
    temiz_sutunlar = ['enlem', 'boylam', 'ortalama_kira_2024', 'hava_kalitesi_pm25_2024', 'issizlik_oranı_2024', 'nufus_2024', 'arac_sayısı_2024']
    df = df.dropna(subset=temiz_sutunlar)
    df['il_adı_buyuk'] = df['il_adı'].str.upper()

    # Skorlama
    df['p1'] = normalize_ters(df['ortalama_kira_2024'])
    df['p2'] = normalize_ters(df['hava_kalitesi_pm25_2024'])
    df['p3'] = normalize_ters(df['issizlik_oranı_2024'])
    df['p4'] = normalize_ters(df['nufus_2024'])
    df['p5'] = normalize_ters(df['arac_sayısı_2024'])
    df['gercek_skor'] = ((df['p1'] + df['p2'] + df['p3'] + df['p4'] + df['p5']) / 5) * 100

    # --- 🎮 KONTROL MERKEZİ ---
    st.sidebar.markdown("# 🎮 Kontrol Merkezi")
    st.sidebar.markdown("---")
    
    kriter_secimi = st.sidebar.selectbox(
        "Kriterinizi Seçin:",
        ("🏆 Genel LivArea Skoru", "💰 Konut Maliyeti (Kira)", "🍃 Hava Kalitesi (PM2.5)", "💼 İstihdam Potansiyeli", "🧘 Sakin Yaşam (Nüfus)", "🚗 Ulaşım Rahatlığı")
    )

    # Analiz Mesajı
    st.info(get_kriter_yorumu(kriter_secimi, df))

    # Değişken ve Etiket Ayarları
    if "Kira" in kriter_secimi:
        v, r, e, s = 'ortalama_kira_2024', "Reds", "Kira Bedeli (TL)", True
    elif "Hava" in kriter_secimi:
        v, r, e, s = 'hava_kalitesi_pm25_2024', "Greens_r", "Hava Kirliliği (PM2.5)", True
    elif "İstihdam" in kriter_secimi:
        v, r, e, s = 'issizlik_oranı_2024', "Blues_r", "İşsizlik Oranı (%)", True
    elif "Nüfus" in kriter_secimi:
        v, r, e, s = 'nufus_2024', "Purples", "Nüfus Yoğunluğu", True
    elif "Ulaşım" in kriter_secimi:
        v, r, e, s = 'arac_sayısı_2024', "Oranges", "Araç Yoğunluğu", True
    else:
        v, r, e, s = 'gercek_skor', "RdYlGn", "Yaşanabilirlik Skoru", False

    # Harita
    fig = px.scatter_mapbox(
        df, lat="enlem", lon="boylam", color=v, size='gercek_skor',
        color_continuous_scale=r, zoom=5, mapbox_style="carto-positron",
        hover_name="il_adı_buyuk",
        hover_data={v: False, 'enlem': False, 'boylam': False, 'gercek_skor': ':.1f'},
        labels={'gercek_skor': 'Skor', v: e},
        center={"lat": 38.96, "lon": 35.24}, height=650
    )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, hoverlabel=dict(bgcolor="black", font_size=16, font_color="white"))
    st.plotly_chart(fig, use_container_width=True)

    # --- 📊 BAR GRAFİĞİ (Rakamları Temizlenmiş Hali) ---
    st.write("---")
    d_eki = "En Avantajlı (En Uygun)" if any(x in kriter_secimi for x in ["Kira", "Hava", "İstihdam"]) else "En Yüksek Skorlu"
    st.subheader(f"📊 {d_eki} İlk 10 İl: {kriter_secimi}")
    
    top_10 = df.sort_values(v, ascending=s).head(10)
    fig_bar = px.bar(
        top_10, x='il_adı_buyuk', y=v, color=v, color_continuous_scale=r,
        labels={'il_adı_buyuk': 'Şehir', v: e}, text=v
    )
    # ✨ BÜTÜN KRİTERLER İÇİN RAKAM TEMİZLEME:
    fig_bar.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
    fig_bar.update_layout(xaxis_tickangle=-45, yaxis=dict(tickformat=",.0f"))
    
    st.plotly_chart(fig_bar, use_container_width=True)

except Exception as e:
    st.error(f"⚠️ Hata: {e}")