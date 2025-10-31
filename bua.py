import streamlit as st

st.title("BUA-berekening")

st.markdown("""
Deze app berekent de BUA-btw-correctie voor kantine en overige verstrekkingen.
- Kantine: 9% btw-correctie indien bevoordeling > €227, anders optellen bij overige verstrekkingen.
- Overige verstrekkingen: 21% btw-correctie indien drempel €227 wordt overschreden.
""")

# Definieer groepen
st.header("Definieer groepen werknemers")
groepen = []
aantal_groepen = st.number_input("Aantal groepen werknemers", min_value=1, step=1)

for i in range(aantal_groepen):
    st.subheader(f"Groep {i+1}")
    naam = st.text_input(f"Naam groep {i+1}", value=f"Groep {i+1}")
    
    # Kantine invoer
    kostprijs_kantine = st.number_input(f"Kostprijs kantine (spijzen/dranken excl. btw) voor {naam}", min_value=0.0, step=10.0)
    eigen_bijdrage_kantine = st.number_input(f"Eigen bijdrage personeel kantine voor {naam}", min_value=0.0, step=10.0)
    
    # Overige verstrekkingen
    overige_verstrekkingen = st.number_input(f"Totale overige verstrekkingen (excl. btw) voor {naam}", min_value=0.0, step=10.0)
    
    aantal_begunstigden = st.number_input(f"Aantal begunstigden in {naam}", min_value=1, step=1)
    
    groepen.append({
        "naam": naam,
        "kostprijs_kantine": kostprijs_kantine,
        "eigen_bijdrage_kantine": eigen_bijdrage_kantine,
        "overige_verstrekkingen": overige_verstrekkingen,
        "begunstigden": aantal_begunstigden
    })

# Berekening
if st.button("Bereken BUA-correctie"):
    drempel = 227.0
    btw_kantine = 0.09
    btw_overige = 0.21
    totaal_correctie = 0.0
    
    st.header("Resultaten per groep")
    
    for g in groepen:
        # Kantineberekening
        theoretische_omzet = g["kostprijs_kantine"] * 1.25
        kantine_bevoordeling = max(theoretische_omzet - g["eigen_bijdrage_kantine"], 0)
        
        if kantine_bevoordeling >= drempel:
            correctie_kantine = kantine_bevoordeling * btw_kantine
            st.write(f"**{g['naam']}**: Kantinebevoordeling ≥ €227")
            st.write(f"Kantinebevoordeling: €{kantine_bevoordeling:.2f}")
            st.write(f"Correctie (9% btw): €{correctie_kantine:.2f}")
        else:
            # Voeg kantinebevoordeling toe bij overige verstrekkingen
            samengevoegd = kantine_bevoordeling + g["overige_verstrekkingen"]
            st.write(f"**{g['naam']}**: Kantinebevoordeling < €227")
            st.write(f"Kantinebevoordeling: €{kantine_bevoordeling:.2f}")
            st.write(f"Samengevoegd met overige verstrekkingen: €{samengevoegd:.2f}")
            
            if samengevoegd > drempel:
                correctie_overige = samengevoegd * btw_overige
                st.write(f"Drempel overschreden, correctie 21% btw: €{correctie_overige:.2f}")
                correctie_kantine = 0
                correctie_overige_total = correctie_overige
            else:
                correctie_kantine = 0
                correctie_overige_total = 0
        # Overige verstrekkingen (indien kantinebevoordeling ≥ drempel, aparte berekening)
        if kantine_bevoordeling >= drempel:
            if g["overige_verstrekkingen"] > drempel:
                correctie_overige = g["overige_verstrekkingen"] * btw_overige
            else:
                correctie_overige = 0
            correctie_overige_total = correctie_overige
        
        totaal_correctie += correctie_kantine + correctie_overige_total
        
        st.write(f"Correctie overige verstrekkingen: €{correctie_overige_total:.2f}")
        st.write(f"Totaal correctie groep: €{(correctie_kantine + correctie_overige_total):.2f}")
        st.write("---")
    
    st.subheader(f"Totaal BUA-btw-correctie: €{totaal_correctie:.2f}")
